#!/usr/bin/env python3
"""spend_gate.py — MCP yozish asboblari uchun PreToolUse darvozasi (Spend-Guard hook'ining yadrosi).

Hook (`hooks/tyrion-hook.py spend`) Claude Code stdin payload'ini shu yerga beradi. Qaror:

  read-only asbob / minimal profil / darvoza o'chirilgan  -> allow (jim o'tkazadi, normal ruxsat oqimi davom etadi)
  tasdiqlangan, yangi, mos change packet bor            -> allow
  packet yo'q yoki yaroqsiz                              -> strict: deny · standard: ask

Packet: `clients/<slug>/changes/<id>.json`, sxema `change-packet.v1` (`experiments.py packet` shu formatni yasaydi):
  approved_by_user: true · 24 soatdan yangi (approved_at, yo'q bo'lsa created_at) · rollback matni majburiy ·
  entity payload'dagi id bilan mos (yaratish asboblari uchun proposed_tool == asbob nomi) ·
  `spend-guard.py packet` tekshiruvidan o'tadi.

HALOL CHEGARA: `approved_by_user` — fayldagi belgi; uni model ham yozishi mumkin. Gate inson tasdig'ini
kriptografik isbotlay olmaydi: u "tasdiqsiz yozish" xatosini ushlaydi, haqiqiy rozilik esa Claude Code'ning
o'z ruxsat so'rovi (biz "allow" qaytarmaymiz, shuning uchun u saqlanadi). Rasmiy Meta MCP'da undo yo'q.
"""

from __future__ import annotations

import datetime as dt
import importlib
import json
import os
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

MAX_AGE_HOURS = 24
FUTURE_SKEW_MIN = 5

# Meta (ads_*) va Google Ads MCP (assets_*, labels_manage_*) yozish asboblari.
WRITE_RE = re.compile(
    r"(?:^|__)(?:ads_(?:create|update|activate|duplicate|delete|boost|finalize|"
    r"creative_(?:create|update|delete|upload)|"
    r"catalog_(?:create|update|delete|product_create|product_feed_delete|product_set_delete|event_source_(?:connect|disconnect))|"
    r"pixel_(?:event|parameter)_(?:create|update|delete)|dataset_(?:create|update)|"
    r"experiment_(?:abtest|lift)_(?:create|update)|permission_preview_set)|"
    r"assets_(?:create|upload)|labels_manage)\w*$"
)
CREATE_RE = re.compile(r"ads_(?:create|duplicate|boost|experiment_|catalog_create|catalog_product_create|dataset_create|pixel_)|assets_(?:create|upload)")
ID_KEY_RE = re.compile(r"(?:^|_)(?:id|ids)$", re.I)


def base_tool_name(tool_name: str) -> str:
    return (tool_name or "").split("__")[-1]


def is_write_tool(tool_name: str) -> bool:
    return bool(WRITE_RE.search(tool_name or ""))


def _collect_ids(obj, out: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if ID_KEY_RE.search(str(k)):
                if isinstance(v, (str, int)):
                    out.add(str(v))
                elif isinstance(v, list):
                    out.update(str(x) for x in v if isinstance(x, (str, int)))
            _collect_ids(v, out)
    elif isinstance(obj, list):
        for x in obj:
            _collect_ids(x, out)


def payload_entity_ids(tool_input) -> set[str]:
    ids: set[str] = set()
    _collect_ids(tool_input, ids)
    return ids


def _parse_ts(value) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    s = value.strip().replace("Z", "+00:00")
    try:
        d = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def _spend_guard():
    return importlib.import_module("spend-guard")


def validate_packet(packet: dict, tool_name: str, ids: set[str], now: dt.datetime) -> list[str]:
    """Bo'sh ro'yxat = packet shu chaqiruv uchun yaroqli; aks holda sabablar."""
    why: list[str] = []
    if packet.get("schema") != "change-packet.v1":
        return ["schema != change-packet.v1"]
    if packet.get("approved_by_user") is not True:
        why.append("approved_by_user: true emas")
    ts = _parse_ts(packet.get("approved_at")) or _parse_ts(packet.get("created_at"))
    if ts is None:
        why.append("approved_at/created_at yo'q")
    else:
        age = now - ts
        if age > dt.timedelta(hours=MAX_AGE_HOURS):
            why.append(f"packet eskirgan ({age.total_seconds() / 3600:.0f} soat > {MAX_AGE_HOURS})")
        if age < -dt.timedelta(minutes=FUTURE_SKEW_MIN):
            why.append("packet vaqti kelajakda")
    if not str(packet.get("rollback") or "").strip():
        why.append("rollback rejasi yo'q (rasmiy Meta MCP'da undo yo'q)")
    entity = packet.get("entity")
    entities = {str(e) for e in (entity if isinstance(entity, list) else [entity]) if e not in (None, "")}
    base = base_tool_name(tool_name)
    if not entities:
        why.append("entity ko'rsatilmagan")
    elif not (entities & ids):
        creating = bool(CREATE_RE.search(base))
        if not (creating and packet.get("proposed_tool") == base):
            why.append(f"entity mos emas (packet: {sorted(entities)[:3]}, chaqiruv: {sorted(ids)[:3] or 'id yo`q'})")
    if not why:
        try:
            sg = _spend_guard().check_change_packet(json.dumps(packet, ensure_ascii=False))
            if not sg.get("passed"):
                why.extend("spend-guard: " + e for e in sg.get("errors", []))
            prop = packet.get("proposal") or {}
            cur, new = prop.get("current_daily"), prop.get("proposed_daily")
            if isinstance(cur, (int, float)) and isinstance(new, (int, float)) and cur > 0:
                bd = _spend_guard().check_budget_change(float(cur), float(new))
                if not bd.get("passed"):
                    why.extend("budget: " + e for e in bd.get("errors", []))
        except Exception as exc:  # noqa: BLE001 — darvoza yopiq tomonga xato qiladi
            why.append(f"spend-guard tekshiruvi bajarilmadi: {exc}")
    return why


def find_packets(roots: list[Path]) -> list[tuple[Path, dict]]:
    found: list[tuple[Path, dict]] = []
    for root in roots:
        for p in sorted(root.glob("*/changes/*.json")):
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(doc, dict):
                found.append((p, doc))
    return found


def evaluate(payload: dict, profile: str = "standard", now: dt.datetime | None = None, clients_dir: Path | None = None) -> dict:
    """Qaytaradi: {decision: allow|ask|deny, reason, packet?}."""
    tool = str(payload.get("tool_name") or "")
    if profile == "minimal" or not is_write_tool(tool):
        return {"decision": "allow", "reason": "yozish asbobi emas yoki darvoza o'chirilgan"}
    now = now or dt.datetime.now(dt.timezone.utc)
    ids = payload_entity_ids(payload.get("tool_input") or {})
    cwd = Path(payload.get("cwd") or os.getcwd())
    env_dir = os.environ.get("TYRION_CLIENTS_DIR")
    roots = [clients_dir] if clients_dir else ([Path(env_dir)] if env_dir else [cwd / "clients"])
    reasons: list[str] = []
    for path, packet in find_packets([r for r in roots if r.is_dir()]):
        why = validate_packet(packet, tool, ids, now)
        if not why:
            return {"decision": "allow", "reason": f"tasdiqlangan change packet: {path.parent.parent.name}/{path.name}", "packet": str(path)}
        reasons.append(f"{path.name}: {'; '.join(why)}")
    base = (f"Spend-Guard: '{base_tool_name(tool)}' hisobni o'zgartiradi, lekin tasdiqlangan change packet topilmadi "
            f"(clients/<slug>/changes/<id>.json: approved_by_user, <{MAX_AGE_HOURS}s, rollback, entity). "
            f"Avval `python3 tools/spend-guard.py packet <fayl>` va foydalanuvchi tasdig'i.")
    if reasons:
        base += " Rad etilgan: " + " | ".join(reasons[:3])
    return {"decision": "deny" if profile == "strict" else "ask", "reason": base}


def hook_output(result: dict) -> dict | None:
    """Claude Code PreToolUse stdout JSON'i; allow = chiqish yo'q (normal ruxsat oqimi saqlanadi)."""
    if result["decision"] == "allow":
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": result["decision"],
                                   "permissionDecisionReason": result["reason"]}}


def main(argv: list[str] | None = None) -> int:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        payload = json.loads(raw) if raw.strip().startswith("{") else {}
    except ValueError:
        payload = {}
    profile = os.environ.get("TYRION_HOOK_PROFILE", "standard").strip().lower()
    out = hook_output(evaluate(payload, profile if profile in ("minimal", "standard", "strict") else "standard"))
    if out:
        print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows cp1252 konsolida --help/hisobotdagi '→' kabi belgilar yiqilmasin
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
