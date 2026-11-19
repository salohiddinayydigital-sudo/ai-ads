#!/usr/bin/env python3
"""Tyrion Client Workspace Scaffolder — Mijoz loyihasini 1 buyruqda tayyor hisob-kitoblar bilan ochish (0 token).

Buyruqlar:
  python3 tools/client-workspace.py new --client "nur-residence" --niche real-estate --budget 3000 --aov 45000 --margin-pct 25 --geo tashkent
  python3 tools/client-workspace.py list

v2 (Client Brain, `clients/<slug>/state.json`, schema `schemas/client-state.v1.json`):
  python3 tools/client-workspace.py init --client "Nur Residence" --niche real-estate --market uz --lang uz --target-cpa 8 --budget 1500
  python3 tools/client-workspace.py state get [key.path] --client nur-residence
  python3 tools/client-workspace.py state set goals.target_cpa 9 --client nur-residence
  python3 tools/client-workspace.py state validate --client nur-residence
  python3 tools/client-workspace.py baseline --client nur-residence --metrics metrics.json   # oxirgi 28 kun medianalari
  python3 tools/client-workspace.py decision add "Byudjet +15%" --why "CPA < target" --owner media-buyer --metric CPA --client nur-residence
  python3 tools/client-workspace.py decision list --client nur-residence
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import statistics
import sys
import tyrion_core as tcore
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
DEFAULT_CLIENTS_ROOT = VAULT / "clients"
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def slugify(value: str) -> str:
    return tcore.safe_slug(value, fallback="client-project")


def scaffold_client(
    client: str,
    niche: str,
    monthly_budget: float,
    aov: float,
    margin_pct: float,
    geo: str,
    root: Path,
    dry_run: bool = False,
) -> dict:
    ma = importlib.import_module("meta-audience")
    cm = importlib.import_module("creative-matrix")

    slug = slugify(client)
    cdir = tcore.validate_safe_path(root / slug, allowed_root=root)
    daily_budget = round(monthly_budget / 30.0, 2)
    gross_profit = round(aov * (margin_pct / 100.0), 2)
    breakeven_roas = round(100.0 / max(margin_pct, 1.0), 2)
    target_cpa = round(gross_profit * 0.5, 2)

    arch = ma.build_architecture(
        niche=niche if niche in ma.NICHE_TAXONOMY else "ecom",
        daily_budget=daily_budget,
        geo=geo if geo in getattr(ma, 'GEO_SEGMENTS', {'tashkent': 1, 'regions': 1, 'uzbekistan': 1}) else "tashkent",
        has_pixel=True,
        has_crm=True,
        target_cpa= max(target_cpa, 5.0),
    )
    mat = cm.build_matrix(niche=niche, product=client, price=aov)

    files_to_write = {
        "BRIEF.md": f"""# 📋 MIJOZ BRIFI VA UNIT-IQTISODIYOT: {client.upper()}

- **Sana:** {date.today().isoformat()}
- **Yo'nalish (Nisha):** `{niche}`
- **Geografiya:** `{geo}`
- **Oylik Reklama Byudjeti:** `${monthly_budget:,.2f}` (Kunlik: `${daily_budget:,.2f}`)
- **O'rtacha Chek (AOV):** `${aov:,.2f}` (Marja: `{margin_pct:.1f}%` -> Yalpi foyda: `${gross_profit:,.2f}`)
- **Break-Even ROAS:** `{breakeven_roas:.2f}x` | **Target CPA (50% marja chegarasi):** `${target_cpa:,.2f}`

## 70 / 20 / 10 Byudjet Taqsimoti
- **70% Scaling Core:** `${round(monthly_budget * 0.70, 2):,.2f}/oy` (`${round(daily_budget * 0.70, 2):,.2f}/kun`)
- **20% 1-5-5 ABO Sandbox:** `${round(monthly_budget * 0.20, 2):,.2f}/oy` (`${round(daily_budget * 0.20, 2):,.2f}/kun`)
- **10% BOF Retargeting:** `${round(monthly_budget * 0.10, 2):,.2f}/oy` (`${round(daily_budget * 0.10, 2):,.2f}/kun`)
""",
        "AUDIENCE-MAP.md": f"""# 🎯 META ADS 4-QATLAMLI AUDITORIYA XARITASI: {client.upper()}

```json
{json.dumps(arch, ensure_ascii=False, indent=2)}
```
""",
        "CREATIVE-MATRIX.md": f"""# 🎨 ANDROMEDA 2 KREATIV MATRITSASI (3x3): {client.upper()}

```json
{json.dumps(mat, ensure_ascii=False, indent=2)}
```
""",
        "TRACKING-CHECKLIST.md": f"""# 📡 TRACKING VA VORONKA DARVOZASI: {client.upper()}

- [ ] Meta Pixel o'rnatilgan va asosiy hodisalar (`Lead` / `Purchase`) yonmoqda
- [ ] Conversions API (`CAPI`) ulangan va `event_id` deduplikatsiyasi (`>=95%`) tekshirilgan
- [ ] Event Match Quality (`EMQ`) balli `>= 6.5/10` (telefon + ism + fbc/fbp)
- [ ] Telegram Bot `?start=utm` zanjiri va AmoCRM/Bitrix24 avto-sdelka integratsiyasi sinovdan o'tgan
- [ ] Sotuv bo'limi javob tezligi (Speed-to-Lead) `<= 15 daqiqa`
""",
        "journal.md": f"""# 📓 KAMPANIYA JURNALI: {client.upper()}

| Sana | Qadam / O'zgarish | Asosiy Metrikalar | Qaror (Kill/Keep/Scale) |
|---|---|---|---|
| {date.today().isoformat()} | Loyiha ish maydoni ochildi (`client-workspace.py`) | Byudjet=${monthly_budget}/oy, Break-even ROAS={breakeven_roas}x | Preflight & Sandbox Start |
""",
    }

    if not dry_run:
        (cdir / "outputs").mkdir(parents=True, exist_ok=True)
        (cdir / "assets").mkdir(parents=True, exist_ok=True)
        for fname, content in files_to_write.items():
            target = cdir / fname
            if not target.exists():
                tcore.atomic_write_text(target, content)

    return {
        "client": client,
        "slug": slug,
        "workspace_dir": str(cdir),
        "dry_run": dry_run,
        "unit_economics": {
            "monthly_budget_usd": monthly_budget,
            "daily_budget_usd": daily_budget,
            "aov_usd": aov,
            "margin_pct": margin_pct,
            "breakeven_roas": breakeven_roas,
            "target_cpa_usd": target_cpa,
        },
        "files": list(files_to_write.keys()),
    }


# --------------------------------------------------------------------------------------
# v2 — Client Brain (state.json, baseline, decision log)
# --------------------------------------------------------------------------------------
STATE_SCHEMA = "client-state.v1"
LANGS = ("uz", "ru", "en", "uz_cyrillic")
BASELINE_DAYS = 28
BASELINE_LABEL = "MEASURED_ACCOUNT_DATA"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def client_dir(slug: str, root: Path) -> Path:
    return tcore.validate_safe_path(root / slugify(slug), allowed_root=root)


def state_path(slug: str, root: Path) -> Path:
    return client_dir(slug, root) / "state.json"


def load_state(slug: str, root: Path) -> dict:
    p = state_path(slug, root)
    if not p.is_file():
        raise FileNotFoundError(f"state.json topilmadi: {p} (avval `init`)")
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(slug: str, root: Path, state: dict) -> Path:
    state["updated"] = _now()
    p = state_path(slug, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tcore.atomic_write_json(p, state)
    return p


def init_client(client: str, root: Path, niche: str = "ecom", market: str = "uz", language: str = "uz",
                budget: float | None = None, target_cpa: float | None = None, aov: float | None = None,
                margin_pct: float | None = None, primary_event: str = "Lead", currency: str = "USD",
                channels: list[str] | None = None, synthetic: bool = False, force: bool = False) -> dict:
    slug = slugify(client)
    cdir = client_dir(slug, root)
    sp = cdir / "state.json"
    if sp.exists() and not force:
        return load_state(slug, root)
    for sub in ("data/raw", "changes", "outputs", "assets"):
        (cdir / sub).mkdir(parents=True, exist_ok=True)
    goals: dict = {"primary_event": primary_event, "currency": currency}
    if budget is not None:
        goals["monthly_budget"] = budget
    if target_cpa is not None:
        goals["target_cpa"] = target_cpa
    econ: dict = {}
    if aov is not None:
        econ["aov"] = aov
    if margin_pct is not None:
        econ["margin_pct"] = margin_pct
        econ["breakeven_roas"] = round(100.0 / max(margin_pct, 1.0), 2)
        if aov is not None:
            econ["breakeven_cpa"] = round(aov * margin_pct / 100.0, 2)
    state = {
        "schema": STATE_SCHEMA, "slug": slug, "name": client, "language": language, "market": market,
        "business": {"niche": niche, "currency": currency}, "economics": econ, "goals": goals,
        "channels": channels or [], "connectors": {}, "pulse_config": {}, "baseline": {}, "next_steps": [],
    }
    if synthetic:
        state["synthetic"] = True
    save_state(slug, root, state)
    return state


def validate_state(state: object) -> list[str]:
    """Qo'lda (stdlib) tekshiruv — `schemas/client-state.v1.json` ning muhim qismi."""
    errs: list[str] = []
    if not isinstance(state, dict):
        return ["state obyekt emas"]
    for k in ("schema", "slug", "name", "language", "market", "goals", "updated"):
        if k not in state:
            errs.append(f"majburiy maydon yo'q: {k}")
    if state.get("schema") != STATE_SCHEMA:
        errs.append(f"schema {STATE_SCHEMA!r} bo'lishi shart")
    if "slug" in state and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(state["slug"])):
        errs.append("slug [a-z0-9-] bo'lishi shart")
    if "language" in state and state["language"] not in LANGS:
        errs.append(f"language {LANGS} dan biri bo'lishi shart")
    for sect in ("goals", "economics", "business", "baseline", "connectors", "pulse_config"):
        if sect in state and not isinstance(state[sect], dict):
            errs.append(f"{sect} obyekt bo'lishi shart")
    for sect, keys in (("goals", ("target_cpa", "target_roas", "monthly_budget")), ("economics", ("aov", "margin_pct", "breakeven_roas", "breakeven_cpa"))):
        for k in keys:
            v = (state.get(sect) or {}).get(k) if isinstance(state.get(sect), dict) else None
            if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0):
                errs.append(f"{sect}.{k} manfiy bo'lmagan son bo'lishi shart")
    if isinstance(state.get("economics"), dict) and (state["economics"].get("margin_pct") or 0) > 100:
        errs.append("economics.margin_pct <= 100 bo'lishi shart")
    for i, st in enumerate(state.get("next_steps") or []):
        if not isinstance(st, dict) or not all(st.get(k) for k in ("action", "owner", "metric")):
            errs.append(f"next_steps[{i}] da action/owner/metric majburiy")
    return errs


def _get_path(obj: object, path: str) -> object:
    for part in [p for p in path.split(".") if p]:
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        elif isinstance(obj, list) and part.isdigit() and int(part) < len(obj):
            obj = obj[int(part)]
        else:
            raise KeyError(path)
    return obj


def _set_path(obj: dict, path: str, value: object) -> None:
    parts = [p for p in path.split(".") if p]
    if not parts:
        raise KeyError("bo'sh kalit")
    for part in parts[:-1]:
        nxt = obj.get(part)
        if not isinstance(nxt, dict):
            nxt = obj[part] = {}
        obj = nxt
    obj[parts[-1]] = value


def _parse_value(raw: str) -> object:
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def _load_metrics_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError("metrics.v1 'rows' massivi topilmadi")
    return [r for r in rows if isinstance(r, dict)]


def _num(v: object) -> float:
    try:
        f = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return f if f == f and abs(f) != float("inf") else 0.0


def compute_baseline(rows: list[dict], event: str | None = None, level: str | None = None,
                     window_days: int = BASELINE_DAYS) -> dict:
    """Oxirgi `window_days` kun (ma'lumotdagi eng so'nggi sanadan) bo'yicha kunlik qiymatlar medianasi."""
    rows = [r for r in rows if isinstance(r.get("date"), str)]
    if not rows:
        return {"error": "metrics bo'sh yoki 'date' yo'q"}
    if level is None:
        present = {r.get("level") for r in rows}
        level = next((lv for lv in ("campaign", "adset", "ad") if lv in present), str(rows[0].get("level") or "campaign"))
    rows = [r for r in rows if r.get("level") == level]
    last = max(datetime.strptime(r["date"], "%Y-%m-%d").date() for r in rows)
    start = last - timedelta(days=window_days - 1)
    days: dict[str, dict] = {}
    for r in rows:
        d = datetime.strptime(r["date"], "%Y-%m-%d").date()
        if d < start:
            continue
        a = days.setdefault(r["date"], dict(spend=0.0, imp=0.0, clk=0.0, conv=0.0, freq_w=0.0))
        a["spend"] += _num(r.get("spend"))
        imp = _num(r.get("impressions"))
        a["imp"] += imp
        a["clk"] += _num(r.get("link_clicks")) or _num(r.get("clicks"))
        convs = r.get("conversions") if isinstance(r.get("conversions"), dict) else {}
        a["conv"] += _num(convs.get(event)) if event else sum(_num(v) for v in convs.values())
        a["freq_w"] += _num(r.get("frequency")) * imp
    series: dict[str, list[float]] = {k: [] for k in ("cpa", "ctr", "cvr", "cpm", "frequency")}
    for a in days.values():
        if a["conv"] > 0:
            series["cpa"].append(a["spend"] / a["conv"])
        if a["imp"] > 0:
            series["ctr"].append(a["clk"] / a["imp"])
            series["cpm"].append(a["spend"] / a["imp"] * 1000.0)
            if a["freq_w"] > 0:
                series["frequency"].append(a["freq_w"] / a["imp"])
        if a["clk"] > 0:
            series["cvr"].append(a["conv"] / a["clk"])
    out: dict = {"window_days": window_days, "as_of": last.isoformat(), "level": level, "days_used": len(days),
                 "event": event or "all", "evidence_label": BASELINE_LABEL}
    for k, vals in series.items():
        out[k] = round(statistics.median(vals), 6) if vals else None
    return out


def _decisions_path(slug: str, root: Path) -> Path:
    return client_dir(slug, root) / "decisions.jsonl"


def decision_add(slug: str, root: Path, what: str, why: str = "", owner: str = "", metric: str = "",
                 evidence_label: str = "UNVERIFIED") -> dict:
    rec = {"ts": _now(), "decision": what, "why": why, "owner": owner, "metric": metric, "evidence_label": evidence_label}
    p = _decisions_path(slug, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def decision_list(slug: str, root: Path) -> list[dict]:
    p = _decisions_path(slug, root)
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def _emit(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _main_v2(args: argparse.Namespace) -> int:
    root = Path(args.root)
    try:
        if args.command == "init":
            st = init_client(args.client, root, niche=args.niche, market=args.market, language=args.lang,
                             budget=args.budget, target_cpa=args.target_cpa, aov=args.aov, margin_pct=args.margin_pct,
                             primary_event=args.event, currency=args.currency, synthetic=args.synthetic, force=args.force)
            if args.scaffold:
                scaffold_client(args.client, args.niche, args.budget or 1500.0, args.aov or 100.0,
                                args.margin_pct if args.margin_pct is not None else 40.0, "tashkent", root)
            _emit({"slug": st["slug"], "state": str(state_path(st["slug"], root))})
            return 0
        if args.command == "state":
            if args.action == "validate":
                errs = validate_state(load_state(args.client, root))
                _emit({"valid": not errs, "errors": errs})
                return 0 if not errs else 2
            st = load_state(args.client, root)
            if args.action == "get":
                _emit(_get_path(st, args.key) if args.key else st)
                return 0
            _set_path(st, args.key, _parse_value(args.value))
            errs = validate_state(st)
            if errs:
                _emit({"valid": False, "errors": errs})
                return 2
            save_state(args.client, root, st)
            _emit({"ok": True, "key": args.key})
            return 0
        if args.command == "baseline":
            st = load_state(args.client, root)
            _cd = client_dir(args.client, root) / "data"
            mp = Path(args.metrics) if args.metrics else (_cd / "metrics.v1.json" if (_cd / "metrics.v1.json").is_file() else _cd / "metrics.json")
            base = compute_baseline(_load_metrics_rows(mp), event=args.event or (st.get("goals") or {}).get("primary_event") if args.event != "all" else None,
                                    level=args.level)
            if base.get("error"):
                _emit(base)
                return 2
            st["baseline"] = base
            if not args.dry_run:
                save_state(args.client, root, st)
            _emit(base)
            return 0
        if args.command == "decision":
            if args.action == "add":
                _emit(decision_add(args.client, root, args.text, args.why, args.owner, args.metric, args.evidence))
            else:
                _emit(decision_list(args.client, root))
            return 0
    except (FileNotFoundError, KeyError, ValueError, OSError) as exc:
        print(f"xato: {exc}", file=sys.stderr)
        return 2
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="client-workspace.py", description="Mijoz ish maydonini yaratish")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Yangi mijoz ish maydonini ochish")
    p_new.add_argument("--client", required=True)
    p_new.add_argument("--niche", default="ecom")
    p_new.add_argument("--budget", type=tcore.positive_float, default=1500.0)
    p_new.add_argument("--aov", type=tcore.positive_float, default=100.0)
    p_new.add_argument("--margin-pct", type=tcore.non_negative_float, default=40.0)
    p_new.add_argument("--geo", default="tashkent")
    p_new.add_argument("--root", default=str(DEFAULT_CLIENTS_ROOT))
    p_new.add_argument("--dry-run", action="store_true")
    p_new.add_argument("--json", action="store_true")

    p_list = sub.add_parser("list", help="Mavjud mijoz ish maydonlari ro'yxati")
    p_list.add_argument("--root", default=str(DEFAULT_CLIENTS_ROOT))

    root_default = str(DEFAULT_CLIENTS_ROOT)
    p_init = sub.add_parser("init", help="state.json (Client Brain) yaratish")
    p_init.add_argument("--client", required=True)
    p_init.add_argument("--niche", default="ecom")
    p_init.add_argument("--market", default="uz")
    p_init.add_argument("--lang", default="uz", choices=LANGS)
    p_init.add_argument("--budget", type=tcore.positive_float, default=None)
    p_init.add_argument("--target-cpa", type=tcore.positive_float, default=None)
    p_init.add_argument("--aov", type=tcore.positive_float, default=None)
    p_init.add_argument("--margin-pct", type=tcore.non_negative_float, default=None)
    p_init.add_argument("--event", default="Lead")
    p_init.add_argument("--currency", default="USD")
    p_init.add_argument("--synthetic", action="store_true")
    p_init.add_argument("--force", action="store_true")
    p_init.add_argument("--scaffold", action="store_true", help="BRIEF/AUDIENCE-MAP fayllarini ham yaratish")
    p_init.add_argument("--root", default=root_default)

    p_state = sub.add_parser("state", help="state get|set|validate")
    p_state.add_argument("action", choices=["get", "set", "validate"])
    p_state.add_argument("key", nargs="?", default=None)
    p_state.add_argument("value", nargs="?", default=None)
    p_state.add_argument("--client", required=True)
    p_state.add_argument("--root", default=root_default)

    p_base = sub.add_parser("baseline", help="metrics.v1 dan oxirgi 28 kun medianalari -> state.baseline")
    p_base.add_argument("--client", required=True)
    p_base.add_argument("--metrics", default=None)
    p_base.add_argument("--event", default=None, help="konversiya hodisasi ('all' = hammasi)")
    p_base.add_argument("--level", choices=["campaign", "adset", "ad"], default=None)
    p_base.add_argument("--dry-run", action="store_true")
    p_base.add_argument("--root", default=root_default)

    p_dec = sub.add_parser("decision", help="decision add|list (decisions.jsonl)")
    p_dec.add_argument("action", choices=["add", "list"])
    p_dec.add_argument("text", nargs="?", default="")
    p_dec.add_argument("--why", default="")
    p_dec.add_argument("--owner", default="")
    p_dec.add_argument("--metric", default="")
    p_dec.add_argument("--evidence", default="UNVERIFIED")
    p_dec.add_argument("--client", required=True)
    p_dec.add_argument("--root", default=root_default)

    args = parser.parse_args(argv)
    if args.command in ("init", "state", "baseline", "decision"):
        return _main_v2(args)
    if args.command == "new":
        res = scaffold_client(
            client=args.client,
            niche=args.niche,
            monthly_budget=args.budget,
            aov=args.aov,
            margin_pct=args.margin_pct,
            geo=args.geo,
            root=Path(args.root),
            dry_run=args.dry_run,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            head = "REJA (dry-run)" if args.dry_run else "YARATILDI"
            print(f"✓ {head}: {res['workspace_dir']}")
            print(f"  Break-even ROAS: {res['unit_economics']['breakeven_roas']}x · Target CPA: ${res['unit_economics']['target_cpa_usd']}")
            print(f"  Fayllar: {', '.join(res['files'])}")
        return 0

    if args.command == "list":
        root = Path(args.root)
        if not root.is_dir():
            print("Mijozlar papkasi hali bo'sh.")
            return 0
        clients = sorted(p.name for p in root.iterdir() if p.is_dir())
        print(f"Mijoz ish maydonlari ({len(clients)}): " + (", ".join(clients) or "yo'q"))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
