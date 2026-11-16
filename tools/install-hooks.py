#!/usr/bin/env python3
"""Tyrion hook va buyruqlarini harness sozlamalariga o'rnatadi (idempotent).

Kanonik manba: `hooks/hooks.json` va `commands/*.md`. Bu skript `{{VAULT}}` o'rniga haqiqiy
yo'lni qo'yadi, `<target>/.claude/settings.json` ga hook'larni **qo'shadi** (mavjudlarini
o'chirmaydi, o'zinikini takrorlamaydi) va buyruqlarni `<target>/.claude/commands/` ga
ko'chiradi. Yozishdan oldin `settings.json.bak` nusxasi olinadi.

Ishlatish:
  py -3 tools\\install-hooks.py --dry-run          # nima o'zgarishini ko'rsatadi
  py -3 tools\\install-hooks.py                    # vault .claude/
  py -3 tools\\install-hooks.py --target <papka>   # boshqa loyiha (masalan claude-ads-main)

Chiqish kodi: 0 — o'rnatildi yoki allaqachon bor, 1 — xato.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
HOOKS_JSON = VAULT / "hooks" / "hooks.json"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass



def detect_python_launcher() -> str:
    """Operatsion tizimga (Windows, macOS, Linux) mos portativ Python launcher'ni aniqlaydi (qotirilgan yo'lsiz)."""
    if sys.platform == "win32":
        if shutil.which("py"):
            return "py -3"
        return "python"
    if shutil.which("python3"):
        return "python3"
    if shutil.which("python"):
        return "python"
    return "py -3"


def _substitute(node: object, needle: str, value: str) -> object:
    """Tuzilmadagi matnlarda `needle` ni almashtiradi.

    MUHIM: almashtirish **parse qilingandan keyin** bajariladi, xom matnda emas.
    Xom matnda qilinsa `path\\to\\vault` JSON ichida qo'yilganda `\\t` TAB belgisiga aylanadi
    (2026-09-16 da dry-run aynan shuni tutdi — YAML frontmatter'dagi xatoning bir turi).
    """
    if isinstance(node, str):
        return node.replace(needle, value)
    if isinstance(node, dict):
        return {key: _substitute(item, needle, value) for key, item in node.items()}
    if isinstance(node, list):
        return [_substitute(item, needle, value) for item in node]
    return node


def build_config(target_root: Path, vault: Path) -> dict:
    """Kanonik hook'larni o'qib, `${CLAUDE_PLUGIN_ROOT}` va `{{VAULT}}` ni almashtiradi."""
    try:
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"✗ hooks/hooks.json buzilgan: {exc}")
    py_cmd = detect_python_launcher()
    sub_v = _substitute(data, "{{VAULT}}", str(vault))
    sub_v = _substitute(sub_v, "${CLAUDE_PLUGIN_ROOT}", str(vault))
    return _substitute(sub_v, "py -3", py_cmd)  # type: ignore[return-value]


def merge(settings: dict, canonical: dict) -> tuple[dict, list[str]]:
    """Mavjud sozlamalarga hook'larni qo'shadi. Qaytaradi: (yangi sozlama, qo'shilganlar)."""
    added: list[str] = []
    hooks = settings.setdefault("hooks", {})

    for event, groups in canonical.get("hooks", {}).items():
        existing: list[dict] = hooks.setdefault(event, [])
        known = {
            hook.get("command")
            for group in existing
            for hook in group.get("hooks", [])
        }
        for group in groups:
            new_hooks = [h for h in group.get("hooks", []) if h.get("command") not in known]
            if not new_hooks:
                continue
            existing.append({"matcher": group.get("matcher", ""), "hooks": new_hooks})
            for hook in new_hooks:
                added.append(f"{event}: {hook['command']}")
                known.add(hook.get("command"))

    return settings, added


def sync_commands(target_root: Path, dry_run: bool) -> list[str]:
    """`commands/*.md` ni `<target>/.claude/commands/` ga ko'chiradi (kanonik → nusxa).

    Nusxa bir xil bo'lsa tegmaydi (idempotent). Qaytaradi: o'zgargan fayllar ro'yxati.
    """
    source = VAULT / "commands"
    if not source.is_dir():
        return []
    destination = target_root / ".claude" / "commands"
    changed: list[str] = []
    for path in sorted(source.glob("*.md")):
        target = destination / path.name
        # Bayt-aniq taqqoslash: `write_text` Windows'da \n ni \r\n ga aylantirib,
        # nusxani "farqli" qilib ko'rsatardi (drift noto'g'ri signali).
        if target.is_file() and target.read_bytes().replace(b'\r\n', b'\n') == path.read_bytes().replace(b'\r\n', b'\n'):
            continue
        changed.append(f"commands/{path.name}")
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return changed


# `None` = barcha `agents/*.md` mirror qilinadi (2-bosqich tugadi). Filtr kerak bo'lsa nomlar to'plami.
MIRRORED_AGENTS: frozenset[str] | None = None
_ALL = object()


def _plugin_name() -> str:
    try:
        return str(json.loads((VAULT / "plugin.json").read_text(encoding="utf-8"))["name"])
    except (OSError, ValueError, KeyError):
        return "tyrion"


def render_project_agent(text: str, plugin_name: str, source_name: str) -> str:
    """Kanonik (plugin rejimi) charterni loyiha rejimi sub-agentiga aylantiradi.

    1. MCP asbob nomi: `mcp__plugin_<plugin>_<server>__<tool>` -> `mcp__<server>__<tool>`
       (`.mcp.json` loyiha serveri sifatida ulanganda prefiks shunday).
    2. `skills:` olib tashlanadi: kanonik skill nomlari loyiha rejimida Claude Code skilli
       sifatida ro'yxatdan o'tmagan; kontekst `tyrion_universal_router` orqali yuklanadi
       (preload butun skill matnini kiritib, token gigiyenasini buzardi).
    """
    out = text.replace(f"mcp__plugin_{plugin_name}_", "mcp__")
    lines = out.split("\n")
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            kept: list[str] = []
            skipping = False
            for line in lines[1:end]:
                if line.startswith("skills:"):
                    skipping = True
                    continue
                if skipping and (line.startswith("- ") or line.startswith(" ")):
                    continue
                skipping = False
                kept.append(line)
            note = f"<!-- GENERATED from agents/{source_name} by tools/install-hooks.py - qo'lda tahrirlanmaydi -->"
            lines = [lines[0], *kept, lines[end], note, *lines[end + 1:]]
    return "\n".join(lines)


def sync_agents(target_root: Path, dry_run: bool, names: object = _ALL) -> list[str]:
    """`agents/*.md` -> `<target>/.claude/agents/` (generatsiya; qo'lda nusxalanmaydi).

    Idempotent. `names` berilmasa `MIRRORED_AGENTS` ishlatiladi (None = hammasi).
    """
    source = VAULT / "agents"
    if not source.is_dir():
        return []
    allowed = MIRRORED_AGENTS if names is _ALL else names
    plugin = _plugin_name()
    destination = target_root / ".claude" / "agents"
    changed: list[str] = []
    for path in sorted(source.glob("*.md")):
        if allowed is not None and path.stem not in allowed:
            continue
        rendered = render_project_agent(path.read_bytes().decode("utf-8").replace("\r\n", "\n"), plugin, path.name)
        target = destination / path.name
        if target.is_file() and target.read_bytes().decode("utf-8").replace("\r\n", "\n") == rendered:
            continue
        changed.append(f"agents/{path.name}")
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)
            target.write_bytes(rendered.encode("utf-8"))
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="install-hooks.py", description="Tyrion hook'larini o'rnatish")
    parser.add_argument("--target", default=str(VAULT), help="loyiha ildizi (default: vault)")
    parser.add_argument("--dry-run", action="store_true", help="yozmasdan ko'rsatadi")
    parser.add_argument("--vault", default=str(VAULT), help="Tyrion ildizi (hook yo'llari uchun)")
    parser.add_argument("--no-commands", action="store_true", help="commands/ ni ko'chirmaslik")
    parser.add_argument("--no-agents", action="store_true", help="agents/ dan .claude/agents/ generatsiya qilmaslik")
    parser.add_argument("--agents-only", action="store_true", help="faqat .claude/agents/ ni generatsiya qiladi (settings.json va buyruqlarga tegmaydi)")
    args = parser.parse_args(argv)

    if args.agents_only:
        changed_agents = sync_agents(Path(args.target).resolve(), args.dry_run)
        print(("· --dry-run: " if args.dry_run else "✓ ") + (f"agentlar ({len(changed_agents)}): " + ", ".join(changed_agents) if changed_agents else "agentlar allaqachon joyida"))
        return 0

    if not HOOKS_JSON.is_file():
        print(f"✗ {HOOKS_JSON} topilmadi")
        return 1

    target_root = Path(args.target).resolve()
    settings_path = target_root / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings: dict = {}
    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"✗ mavjud settings.json buzilgan ({exc}) — qo'lda tuzating")
            return 1

    canonical = build_config(target_root, Path(args.vault).resolve())
    updated, added = merge(settings, canonical)
    commands = [] if args.no_commands else sync_commands(target_root, args.dry_run)
    commands = commands + ([] if args.no_agents else sync_agents(target_root, args.dry_run))

    if not added and not commands:
        print(f"✓ hook va buyruqlar allaqachon joyida: {target_root}")
        return 0

    if added:
        print(f"Qo'shiladigan hook'lar ({len(added)}):")
        for line in added:
            print(f"  + {line}")
    if commands:
        print(f"Ko'chiriladigan buyruqlar ({len(commands)}): " + ", ".join(commands))

    if args.dry_run:
        print(f"\n· --dry-run: {target_root} ichida hech narsa yozilmadi")
        return 0

    if added:
        if settings_path.is_file():
            backup = settings_path.with_suffix(".json.bak")
            shutil.copy2(settings_path, backup)
            print(f"\n· nusxa: {backup.name}")
        settings_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✓ settings yozildi: {settings_path}")
    print("✓ tayyor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
