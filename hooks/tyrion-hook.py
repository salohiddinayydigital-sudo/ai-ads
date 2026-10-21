#!/usr/bin/env python3
"""Tyrion hook'lari — deterministik nazorat va ECC hook profillari (LLM hukmisiz).

Qo'llab-quvvatlanadigan muhit o'zgaruvchilari (ECC 2.2 mos):
  TYRION_HOOK_PROFILE   : minimal | standard | strict (default: standard)
  TYRION_DISABLED_HOOKS : vergul bilan ajratilgan hook ID ro'yxati (session:brief,pre:guard,post:ingest,stop:dod)

Buyruqlar:
  python3 hooks/tyrion-hook.py brief     # sessiya boshi: holat + instinktlar (SessionStart, ID: session:brief)
  python3 hooks/tyrion-hook.py guard     # muhim konfiguratsiya himoyasi (PreToolUse, ID: pre:guard)
  python3 hooks/tyrion-hook.py ingest    # ingest protokoli: INDEX/LOG/graf (PostToolUse, ID: post:ingest)
  python3 hooks/tyrion-hook.py dod       # topshirish darvozasi: doctor + ingest + gate (Stop, ID: stop:dod)

Chiqish kodi: 0 — joyida, 1 — qoida buzilgan (hook bloklaydi), 2 — xato.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
VAULT = HOOKS.parent
TOOLS = VAULT / "tools"

sys.path.insert(0, str(TOOLS))
import catalog as cat  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass



def is_maintainer_mode() -> bool:
    if os.environ.get("TYRION_DEV", "").strip().lower() in ("1", "true", "yes"):
        return True
    try:
        return Path.cwd().resolve() == VAULT.resolve()
    except Exception:
        return False


def get_profile() -> str:
    raw = os.environ.get("TYRION_HOOK_PROFILE", "standard").strip().lower()
    return raw if raw in ("minimal", "standard", "strict") else "standard"


def is_disabled(hook_id: str) -> bool:
    disabled = {
        x.strip().lower()
        for x in os.environ.get("TYRION_DISABLED_HOOKS", "").split(",")
        if x.strip()
    }
    if hook_id.lower() in disabled:
        return True
    profile = get_profile()
    if profile == "minimal" and hook_id in ("post:ingest", "pre:guard"):
        return True
    return False


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(VAULT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


# --------------------------------------------------------------------------- #
# brief — sessiya boshi (ID: session:brief)
# --------------------------------------------------------------------------- #

def cmd_brief(_args: argparse.Namespace) -> int:
    if is_disabled("session:brief"):
        return 0
    data = cat.scan()
    notes = [VAULT / i["path"] for i in data["items"]["wiki"]]
    total_skills = data["counts"].get("skills", 0) + data["counts"].get("skills.marketing", 0)
    instincts_path = VAULT / "manifests" / "instincts.json"
    instincts_count = 0
    if instincts_path.is_file():
        try:
            instincts_count = len(json.loads(instincts_path.read_text(encoding="utf-8")).get("instincts", []))
        except Exception:
            pass

    bits: list[str] = [
        f"Tyrion: wiki {data['counts']['wiki']} · agent {data['counts']['agents']} · "
        f"skill {total_skills} · instinkt {instincts_count} · profil {get_profile()}"
    ]

    graph = VAULT / "graphify-out" / "graph.json"
    if graph.is_file():
        newest = max((p.stat().st_mtime for p in notes if p.is_file()), default=0)
        if newest > graph.stat().st_mtime:
            days = (newest - graph.stat().st_mtime) / 86400
            bits.append(f"graf {days:.0f} kun eski → `python3 tools/brain-graph.py build`")

    drift = [m for m in data["mirrors"] if m["status"] != "identical"]
    if drift:
        bits.append(f"⚠ {len(drift)} nusxada drift → `catalog.py sync-mirrors`")

    print(" | ".join(bits))
    return 0


# --------------------------------------------------------------------------- #
# guard — konfiguratsiya va generatsiya reestrini himoya qilish (ID: pre:guard)
# --------------------------------------------------------------------------- #

PROTECTED_GENERATED = {"manifests/catalog.json", "graphify-out/graph.json"}


def cmd_guard(args: argparse.Namespace) -> int:
    if is_disabled("pre:guard"):
        return 0
    raw_target = (args.target or "").strip()
    if not raw_target and not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read().strip()
            if stdin_data.startswith("{"):
                payload = json.loads(stdin_data)
                t_in = payload.get("tool_input") or payload.get("input") or {}
                raw_target = str(t_in.get("file_path") or t_in.get("path") or t_in.get("target_file") or "")
        except Exception:
            raw_target = ""
    target = raw_target.replace("\\", "/").strip()
    # If target is an absolute path outside VAULT, never block user files in another project
    if target and Path(raw_target).is_absolute():
        try:
            resolved_target = Path(raw_target).resolve()
            if VAULT.resolve() not in resolved_target.parents and resolved_target != VAULT.resolve():
                return 0
        except Exception:
            return 0
    if any(target.endswith(p) for p in PROTECTED_GENERATED):
        msg = f"⚠ HIMOYA (pre:guard): '{target}' generatsiya fayli — qo'lda tahrirlamang (`catalog.py build` / `brain-graph.py build` ishlating)."
        print(msg)
        if get_profile() == "strict":
            return 2
        return 0 if args.warn_only else 2
    if not args.quiet:
        print("✓ pre:guard: ruxsat berildi")
    return 0


# --------------------------------------------------------------------------- #
# ingest — CLAUDE.md ingest protokoli nazorati (ID: post:ingest)
# --------------------------------------------------------------------------- #

def _today() -> str:
    return date.today().isoformat()


def cmd_ingest(args: argparse.Namespace) -> int:
    if is_disabled("post:ingest") or not is_maintainer_mode():
        return 0
    problems: list[str] = []
    data = cat.scan()
    notes = data["items"]["wiki"]

    index_path = VAULT / "INDEX.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    not_indexed = [n["name"] for n in notes if n["name"] not in index_text]

    log_path = VAULT / "LOG.md"
    log_text = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    today = _today()

    today_notes = []
    for n in notes:
        n_path = VAULT / n["path"]
        if n_path.is_file():
            raw_txt = n_path.read_text(encoding="utf-8", errors="replace")
            m_upd = re.search(r"^updated:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?\s*$", raw_txt, re.M)
            if m_upd and m_upd.group(1) == today:
                today_notes.append(n)
    if today_notes and today not in log_text:
        problems.append(f"bugun {len(today_notes)} qayd yozilgan, LOG.md da '{today}' qatori yo'q")

    for name in not_indexed:
        problems.append(f"INDEX.md da yo'q: {name}")

    if not problems:
        script = TOOLS / "brain-graph.py"
        if script.is_file():
            try:
                run([sys.executable, str(script), "build"], timeout=60)
            except Exception:
                pass
        if not args.quiet:
            print(f"✓ ingest protokoli joyida ({len(notes)} qayd, INDEX qamrovi to'liq; graf yangilandi)")
        return 0

    print("⚠ INGEST PROTOKOLI BUZILGAN (CLAUDE.md: raw → wiki → INDEX → LOG):")
    for line in problems[:8]:
        print(f"  - {line}")
    if len(problems) > 8:
        print(f"  ... yana {len(problems) - 8} ta")
    print("  Tuzatish: `python3 tools/vault-audit.py --write` va LOG.md tepasiga sana muhrlang.")
    strict = (get_profile() == "strict") and not args.warn_only
    return 1 if (not args.warn_only or strict) else 0


# --------------------------------------------------------------------------- #
# dod — topshirish darvozasi (doctor + ingest + vault-audit --gate, ID: stop:dod)
# --------------------------------------------------------------------------- #

def cmd_dod(args: argparse.Namespace) -> int:
    if is_disabled("stop:dod") or not is_maintainer_mode():
        return 0
    failures: list[str] = []

    try:
        proc = run([sys.executable, str(TOOLS / "doctor.py"), "--quick", "--json"], timeout=180)
        payload = json.loads(proc.stdout or "{}")
        checks = payload.get("checks", [])
        if not checks and proc.returncode != 0:
            failures.append(f"doctor xato kodi bilan tugadi (rc={proc.returncode})")
        for check in checks:
            if check["status"] == "fail":
                failures.append(f"{check['check']}: {check['detail']}")
    except Exception as exc:
        failures.append(f"doctor ishga tushmadi: {exc}")

    try:
        shield_proc = run([sys.executable, str(TOOLS / "tyrion-shield.py"), "scan", "--json"], timeout=60)
        sh_payload = json.loads(shield_proc.stdout or "{}")
        if sh_payload.get("summary", {}).get("errors", 0) > 0 or shield_proc.returncode != 0:
            failures.append("TyrionShield xavfsizlik tekshiruvida xato topildi")
    except Exception as exc:
        failures.append(f"TyrionShield ishga tushmadi: {exc}")

    ingest = cmd_ingest(argparse.Namespace(warn_only=True, quiet=True))
    if ingest != 0:
        failures.append("ingest protokoli buzilgan (batafsil: hooks/tyrion-hook.py ingest)")

    gate_proc = run([sys.executable, str(TOOLS / "vault-audit.py"), str(VAULT), "--gate"], timeout=120)
    if gate_proc.returncode != 0:
        failures.append("vault-audit --gate: bilim qatlami yoki LOG.md delivery gate yopiq")

    if not failures:
        print("✓ topshirish darvozasi: to'siq yo'q")
        return 0

    print("✗ TOPSHIRISH DARVOZASI YOPIQ:")
    for line in failures:
        print(f"  - {line}")
    if get_profile() == "strict" and not args.warn_only:
        return 1
    return 0 if args.warn_only else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tyrion-hook.py", description="Tyrion deterministik hook'lari")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("brief", help="sessiya boshi holati (session:brief)").set_defaults(func=cmd_brief)

    guard = sub.add_parser("guard", help="generatsiya va config himoyasi (pre:guard)")
    guard.add_argument("--target", default="", help="tekshirilayotgan fayl yo'li")
    guard.add_argument("--warn-only", action="store_true")
    guard.add_argument("--quiet", action="store_true")
    guard.set_defaults(func=cmd_guard)

    ingest = sub.add_parser("ingest", help="ingest protokoli nazorati (post:ingest)")
    ingest.add_argument("--warn-only", action="store_true", help="xato kodisiz, faqat ogohlantirish")
    ingest.add_argument("--quiet", action="store_true", help="muammo bo'lmasa jim turadi")
    ingest.set_defaults(func=cmd_ingest)

    dod = sub.add_parser("dod", help="topshirish darvozasi (stop:dod)")
    dod.add_argument("--warn-only", action="store_true",
                     help="faqat ogohlantiradi (Stop hook uchun — ishni bloklamaydi)")
    dod.set_defaults(func=cmd_dod)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"⚠ tyrion-hook warning: {exc} (non-blocking)", file=sys.stderr)
        return 2 if get_profile() == "strict" else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as _exc:
        print(f"⚠ tyrion-hook warning: {_exc} (non-blocking)", file=sys.stderr)
        raise SystemExit(2 if get_profile() == "strict" else 0)
