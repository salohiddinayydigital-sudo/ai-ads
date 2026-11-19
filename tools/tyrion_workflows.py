#!/usr/bin/env python3
"""Tyrion Workflow Layer — yagona routing manbasi (`manifests/workflows.json`).

Vazifasi:
  * oddiy tildagi so'rovni cross-agent oqimga (workflow) moslash (uz lotin/kirill, ru, en);
  * oqimni DAG ko'rinishidagi bajarish rejasiga (parallel darajalar) aylantirish;
  * harness imkoniyatiga qarab halol delegatsiya rejimini belgilash (native sub-agent yoki single-conductor);
  * rekursiv marshrutlash va dublikat ishni oldini olish;
  * manifestni agentlar/skilllar/asboblar bilan solishtirib tekshirish (`check`).

0 token, faqat standart kutubxona. Router (`skill-search.py`) bu modulni `route_task` ichida chaqiradi.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VAULT = Path(__file__).resolve().parent.parent
WORKFLOWS_PATH = VAULT / "manifests" / "workflows.json"

_APOS = str.maketrans({"ʻ": "'", "ʼ": "'", "’": "'", "‘": "'", "`": "'", "´": "'"})
_CYR_TO_LAT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "j", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "x", "ц": "ts", "ч": "ch", "ш": "sh", "ъ": "'", "ь": "", "э": "e", "ю": "yu",
    "я": "ya", "ў": "o'", "қ": "q", "ғ": "g'", "ҳ": "h", "ы": "i",
})

_cache: dict[str, Any] = {}


def normalize(text: str) -> str:
    low = str(text or "").lower().translate(_APOS)
    if re.search(r"[а-яёўқғҳ]", low):
        low = f"{low} {low.translate(_CYR_TO_LAT)}"
    return f" {low} "


def load_workflows(force: bool = False) -> dict[str, Any]:
    if force or "wf" not in _cache:
        cfg = json.loads(WORKFLOWS_PATH.read_text(encoding="utf-8"))
        by_id = {w["id"]: w for w in cfg["workflows"]}
        resolved = []
        for w in cfg["workflows"]:
            if "extends" in w:
                base = json.loads(json.dumps(by_id[w["extends"]]))  # deep copy
                merged = {**base, **{k: v for k, v in w.items() if k not in ("extends", "stage_overrides")}}
                for st in merged["stages"]:
                    st.update(w.get("stage_overrides", {}).get(st["id"], {}))
                merged["extended_from"] = w["extends"]
                w = merged
            resolved.append(w)
        cfg["workflows"] = resolved
        _cache["wf"] = cfg
    return _cache["wf"]


def _group_hits(norm_q: str, group: list[str]) -> list[str]:
    hits = []
    for raw in group:
        p = normalize(raw).strip()
        # kirill iboralar uchun faqat asl (kirill) va lotin qismlar alohida tekshiriladi
        variants = {p}
        if " " in p and re.search(r"[а-яёўқғҳ]", raw.lower()):
            variants.add(raw.lower().translate(_APOS))
            variants.add(raw.lower().translate(_APOS).translate(_CYR_TO_LAT))
        if any(v and v in norm_q for v in variants):
            hits.append(raw)
    return hits


def match_workflow(query: str) -> dict[str, Any] | None:
    """Eng yuqori ustuvorlikdagi mos workflow'ni qaytaradi (yoki None)."""
    cfg = load_workflows()
    norm_q = normalize(query)
    best: tuple[int, int, dict[str, Any], list[str]] | None = None
    for wf in cfg["workflows"]:
        m = wf["match"]
        matched: list[str] = []
        ok = True
        for group in m.get("all_of", []):
            hits = _group_hits(norm_q, group)
            if not hits:
                ok = False
                break
            matched.extend(hits)
        if not ok:
            continue
        unless = m.get("none_of_unless_any")
        exempt = bool(unless and _group_hits(norm_q, unless))
        if not exempt and any(_group_hits(norm_q, g) for g in m.get("none_of", [])):
            continue
        if wf.get("meta_only") and detect_platform(query) not in ("", "meta"):
            continue
        key = (int(wf.get("priority", 0)), len(matched))
        if best is None or key > (best[0], best[1]):
            best = (key[0], key[1], wf, matched)
    if not best:
        return None
    return {"workflow": best[2], "matched_phrases": best[3]}


def detect_platform(query: str) -> str:
    """Aniq nomlangan platformani qaytaradi (Meta ochiq nomlangan bo'lsa Meta ustun; keyin boshqalar)."""
    cfg = load_workflows()
    norm_q = normalize(query)
    plats = cfg["platform_agents"]
    explicit_meta = ["meta ads", "meta reklama", "meta", "facebook", "instagram", "фейсбук", "инстаграм", "fb ads"]
    others = [p for p in plats if p != "meta"]
    named_others = [p for p in others if _group_hits(norm_q, plats[p]["words"])]
    if _group_hits(norm_q, explicit_meta) and not [p for p in named_others if p == "vk"]:
        return "meta"
    if named_others:
        return named_others[0]
    return ""


def _levels(stages: list[dict[str, Any]]) -> list[list[str]]:
    """Kahn algoritmi: parallel bajariladigan darajalar. Sikl bo'lsa ValueError."""
    needs = {s["id"]: set(s.get("needs", [])) for s in stages}
    done: set[str] = set()
    levels: list[list[str]] = []
    remaining = dict(needs)
    while remaining:
        ready = sorted(sid for sid, n in remaining.items() if n <= done)
        if not ready:
            raise ValueError(f"Workflow DAG'da sikl bor: {sorted(remaining)}")
        levels.append(ready)
        done.update(ready)
        for sid in ready:
            remaining.pop(sid)
    return levels


def build_execution_plan(
    query: str,
    harness_caps: dict[str, Any] | None = None,
    agents: dict[str, dict[str, Any]] | None = None,
    caller: str = "user",
) -> dict[str, Any] | None:
    """So'rovga mos workflow bo'lsa to'liq bajarish rejasini qaytaradi; bo'lmasa None."""
    found = match_workflow(query)
    if not found:
        return None
    wf = found["workflow"]
    platform = detect_platform(query)
    cfg = load_workflows()
    stages = [dict(s) for s in wf["stages"]]

    # Platformaga qarab audit agentini almashtirish (masalan Google uchun audit-google)
    if wf.get("primary_agent_by_platform") and platform and platform != "meta":
        target = cfg["platform_agents"][platform]["audit_agent"]
        for s in stages:
            if s["agent"] == "platform-auditor":
                s["agent"] = target
                if agents and target in agents:
                    s["skills"] = list(agents[target].get("skills", []))[:2]
                s["tools"] = [t for t in s.get("tools", []) if "meta-" not in t]
        primary = target
    else:
        primary = wf["primary_agent"]

    levels = _levels(stages)
    by_id = {s["id"]: s for s in stages}

    caps = harness_caps or {}
    native = bool(caps.get("supports_native_subagents"))
    harness = caps.get("active_harness", "cli_standalone")
    specialist_stages = [s for s in stages if s["agent"] != "conductor"]

    seen: set[tuple[str, str]] = set()
    plan_stages = []
    for lvl_idx, lvl in enumerate(levels):
        for sid in lvl:
            s = by_id[sid]
            key = (s["agent"], s["output"])
            duplicate = key in seen
            seen.add(key)
            is_spec = s["agent"] != "conductor"
            plan_stages.append({
                "id": sid,
                "level": lvl_idx + 1,
                "title": s["title"],
                "agent": s["agent"],
                "skills": s.get("skills", []),
                "tools": s.get("tools", []),
                "needs": s.get("needs", []),
                "output": s["output"],
                "optional": bool(s.get("optional_when")),
                "skip_when": s.get("optional_when", ""),
                "ask_only_if_missing": s.get("ask_only_if_missing", []),
                "execution": (
                    "native_subagent" if (is_spec and native)
                    else ("conductor_inline_as_specialist" if is_spec else "conductor")
                ),
                "duplicate_of_previous": duplicate,
            })

    return {
        "schema": "tyrion.execution_plan/v1",
        "workflow_id": wf["id"],
        "title": wf["title"],
        "deliverable": wf["deliverable"],
        "deliverable_reference": wf.get("reference", ""),
        "matched_phrases": found["matched_phrases"],
        "platform": platform or ("meta" if wf["id"] in ("meta_strategy",) else ""),
        "primary_agent": primary,
        "stages": plan_stages,
        "parallel_levels": levels,
        "delegation": {
            "harness": harness,
            "mode": "native_subagents" if native else "single_conductor_fallback",
            "specialist_stage_count": len(specialist_stages),
            "subagents_actually_spawned": False,
            "honesty_clause": (
                "Router agent YARATMAYDI. Conductor har bir mutaxassis bosqichi uchun haqiqatan sub-agent chaqirgan bo'lsagina "
                "'delegatsiya qilindi' deydi; aks holda bosqichni o'zi, tegishli charter va skillni o'qib bajaradi va "
                "'single-conductor fallback' deb belgilaydi."
            ),
            "parallel_rule": "Bir darajadagi (level) bosqichlar bir-biriga bog'liq emas: native rejimda bitta xabarda parallel chaqiriladi.",
        },
        "guards": {
            **cfg["guards"],
            "caller": caller,
            "delegation_allowed": caller != "specialist",
            "unique_stage_outputs": len({p["output"] for p in plan_stages}) == len(plan_stages),
        },
        "quality_gate": [
            "Har bosqich natijasi manba/taxmin belgisiga ega (MEASURED_ACCOUNT_DATA | HEURISTIC_PRIOR_MODEL | ASSUMPTION)",
            "Hisob-kitoblar tools/calculator.py orqali (taxminlar ochiq)",
            "Targeting: har bir interest 6-status tekshiruvidan o'tgan yoki 'gipoteza' deb belgilangan",
            "Mutaxassislar o'rtasidagi ziddiyat sintezda hal qilinadi yoki ochiq ko'rsatiladi",
            "Yakuniy javob yagona hujjat; mutaxassis javoblarini yopishtirish taqiqlangan",
        ],
    }


def validate_workflows(
    agents: dict[str, Any], skills: list[dict[str, Any]] | dict[str, Any], vault: Path = VAULT
) -> tuple[list[str], list[str]]:
    """Manifestni haqiqiy agent/skill/asbob fayllari bilan solishtiradi. (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []
    skill_names = set(skills.keys()) if isinstance(skills, dict) else {s["name"] for s in skills}
    cfg = load_workflows(force=True)
    guards = cfg["guards"]
    orch = guards["orchestrator"]
    ids: set[str] = set()
    for plat, meta in cfg["platform_agents"].items():
        if meta["audit_agent"] not in agents:
            errors.append(f"platform_agents.{plat}: agent topilmadi: {meta['audit_agent']}")
    for wf in cfg["workflows"]:
        wid = wf["id"]
        if wid in ids:
            errors.append(f"Dublikat workflow id: {wid}")
        ids.add(wid)
        if wf["primary_agent"] not in agents:
            errors.append(f"{wid}: primary_agent topilmadi: {wf['primary_agent']}")
        if wf["primary_agent"] not in {s["agent"] for s in wf["stages"]} and not wf.get("primary_agent_by_platform"):
            errors.append(f"{wid}: primary_agent ({wf['primary_agent']}) hech bir bosqichda ishlatilmagan")
        if wf.get("reference") and not (vault / wf["reference"]).is_file():
            errors.append(f"{wid}: reference fayli yo'q: {wf['reference']}")
        stage_ids = [s["id"] for s in wf["stages"]]
        if len(stage_ids) != len(set(stage_ids)):
            errors.append(f"{wid}: bosqich id'lari takrorlangan")
        outputs = [s["output"] for s in wf["stages"]]
        if len(outputs) != len(set(outputs)):
            errors.append(f"{wid}: ikki bosqich bir xil output beradi (dublikat ish)")
        for s in wf["stages"]:
            if s["agent"] != "conductor" and s["agent"] not in agents:
                errors.append(f"{wid}/{s['id']}: agent topilmadi: {s['agent']}")
            if s["agent"] == orch or orch in s.get("skills", []):
                errors.append(f"{wid}/{s['id']}: mutaxassis bosqichida '{orch}' bo'lishi mumkin emas (rekursiya)")
            for sk in s.get("skills", []):
                if sk not in skill_names:
                    errors.append(f"{wid}/{s['id']}: skill topilmadi: {sk}")
                elif s["agent"] in agents and sk not in agents[s["agent"]].get("skills", []):
                    warnings.append(f"{wid}/{s['id']}: `{sk}` skilli `{s['agent']}` agentiga biriktirilmagan (conductor o'zi o'qishi kerak)")
            for t in s.get("tools", []):
                if not (vault / t).is_file():
                    errors.append(f"{wid}/{s['id']}: asbob yo'q: {t}")
            for n in s.get("needs", []):
                if n not in stage_ids:
                    errors.append(f"{wid}/{s['id']}: noma'lum bog'liqlik: {n}")
        try:
            _levels(wf["stages"])
        except ValueError as exc:
            errors.append(f"{wid}: {exc}")
    return errors, warnings


def _cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tyrion workflow qatlami")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="workflows.json ni agent/skill/asbob bilan tekshirish")
    pm = sub.add_parser("match", help="so'rov qaysi workflow'ga tushishini ko'rsatish")
    pm.add_argument("query")
    pm.add_argument("--json", action="store_true")
    sub.add_parser("list", help="workflow ro'yxati")
    args = ap.parse_args(argv)

    if args.cmd == "list":
        for wf in load_workflows()["workflows"]:
            print(f"{wf['id']:22} p={wf['priority']:<3} {len(wf['stages'])} bosqich -> {wf['primary_agent']}")
        return 0
    if args.cmd == "match":
        plan = build_execution_plan(args.query)
        if args.json:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
        elif plan:
            print(f"{plan['workflow_id']} -> {plan['primary_agent']}  levels={plan['parallel_levels']}")
        else:
            print("workflow mos kelmadi (oddiy skill reytingi ishlatiladi)")
        return 0

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("skill_search", Path(__file__).resolve().parent / "skill-search.py")
    ss = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(ss)  # type: ignore[union-attr]
    errors, warnings = validate_workflows(ss.load_agents(force_reload=True), ss.load_skills(force_reload=True))
    for w in warnings:
        print(f"  ~ {w}")
    for e in errors:
        print(f"  ✗ {e}")
    print(f"workflows: {len(load_workflows()['workflows'])} · xato={len(errors)} · ogohlantirish={len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(_cli())
