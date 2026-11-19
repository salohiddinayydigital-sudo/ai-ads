#!/usr/bin/env python3
"""Tyrion Multi-Harness Exporter — Claude Code, Codex, Cursor (.mdc) va Windsurf (.windsurfrules) adapteri (0 token).

Har bir qo'llab-quvvatlanadigan AI harness uchun haqiqiy integratsiya yo'lini yaratadi va tekshiradi:
  - Claude Code : `.claude/commands/*.md`, `.claude-plugin/plugin.json`, `.claude/settings.json`, `CLAUDE.md`, `.mcp.json`
  - Codex       : `.codex-plugin/plugin.json`, `AGENTS.md`, `skills/*/SKILL.md`, `.mcp.json`
  - Cursor      : `.cursor/rules/tyrion-*.mdc`, `AGENTS.md`, `.mcp.json`
  - Windsurf    : `.windsurfrules`, `AGENTS.md`, `.mcp.json`

Ishlatish:
  python3 tools/harness-export.py --target cursor [--dry-run]
  python3 tools/harness-export.py --target windsurf [--dry-run]
  python3 tools/harness-export.py --target claude [--dry-run]
  python3 tools/harness-export.py --target codex [--dry-run]
  python3 tools/harness-export.py --target all [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def strip_fm(text: str) -> tuple[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    desc_m = re.search(r'^description:\s*"?(.*?)"?\s*$', m.group(1), re.M)
    desc = desc_m.group(1) if desc_m else "Tyrion rule"
    return desc, text[m.end():]


ENTRY_RULE = """# TYRION ENTRY POINT (single conductor, no sub-agents in this harness)

Treat every marketing, advertising, targeting, creative, video-script, tracking, budget or client-strategy request in plain language (Uzbek, Russian or English) as a task for the Tyrion conductor. The user never picks agents, skills or tools.

1. Route once: call the MCP tool `tyrion_universal_router` with `query` = the user's request and `context_mode: "manifest"` (or run `python3 tools/skill-search.py route "<request>" --context-mode manifest --json`).
2. Read `skills/tyrion/references/conductor-v7.md` and follow its protocol. Read in full every skill, charter and reference you will rely on (see `loaded_context.read_in_full_before_claiming` and `execution_plan`); never say a skill was applied if you only saw its name.
3. This harness has no native sub-agents: run each stage of `execution_plan` yourself, in dependency order, by reading the stage agent's charter in `agents/<name>.md` and its skills, and label it `executed_by: conductor_as_<agent>` (single_conductor_fallback). Never claim an agent was spawned.
4. Use deterministic tools from `tools/` (run `<tool> --help` first) for calculations, Meta targeting verification, audience architecture, creative matrices and export analysis.
5. Validate every stage output (sources labelled, no invented stats/interests/testimonials, no guaranteed results), then deliver one synthesized document. Never change a live ad account; plans only.
"""


def export_cursor(out_root: Path, dry_run: bool) -> list[str]:
    cursor_rules = out_root / ".cursor" / "rules"
    written: list[str] = []
    if not dry_run:
        cursor_rules.mkdir(parents=True, exist_ok=True)
    entry_dst = cursor_rules / "tyrion-00-entry.mdc"
    written.append(entry_dst.relative_to(out_root).as_posix())
    if not dry_run:
        entry_dst.write_text(
            f"---\ndescription: Tyrion entry point: route marketing requests through the tyrion-universal conductor\nglobs: *\nalwaysApply: true\n---\n\n{ENTRY_RULE}",
            encoding="utf-8",
        )
    for rule_md in sorted((VAULT / "rules").glob("[0-9]*.md")):
        desc, body = strip_fm(rule_md.read_text(encoding="utf-8"))
        mdc_content = f"---\ndescription: {desc}\nglobs: *\nalwaysApply: true\n---\n\n{body.lstrip()}"
        dst = cursor_rules / f"tyrion-{rule_md.stem}.mdc"
        written.append(dst.relative_to(out_root).as_posix())
        if not dry_run:
            dst.write_text(mdc_content, encoding="utf-8")
    return written


def export_windsurf(out_root: Path, dry_run: bool) -> list[str]:
    parts = ["# TYRION v8.0 — WINDSURF PAID MEDIA & TARGETOLOGY RULES\n", ENTRY_RULE.strip() + "\n"]
    for rule_md in sorted((VAULT / "rules").glob("[0-9]*.md")):
        _desc, body = strip_fm(rule_md.read_text(encoding="utf-8"))
        parts.append(body.strip() + "\n")
    dst = out_root / ".windsurfrules"
    if not dry_run:
        dst.write_text("\n\n".join(parts), encoding="utf-8")
    return [dst.relative_to(out_root).as_posix()]


def export_claude(out_root: Path, dry_run: bool) -> list[str]:
    cmd_dst = out_root / ".claude" / "commands"
    written: list[str] = []
    if not dry_run:
        cmd_dst.mkdir(parents=True, exist_ok=True)
    for cmd_md in sorted((VAULT / "commands").glob("*.md")):
        target = cmd_dst / cmd_md.name
        written.append(target.relative_to(out_root).as_posix())
        if not dry_run:
            target.write_bytes(cmd_md.read_bytes().replace(b"\r\n", b"\n"))
    return written


def export_codex(out_root: Path, dry_run: bool) -> list[str]:
    codex_dir = out_root / ".codex-plugin"
    dst = codex_dir / "plugin.json"
    src_plugin = VAULT / "plugin.json"
    if not dry_run:
        codex_dir.mkdir(parents=True, exist_ok=True)
        if src_plugin.is_file():
            dst.write_bytes(src_plugin.read_bytes().replace(b"\r\n", b"\n"))
    return [dst.relative_to(out_root).as_posix()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harness-export.py", description="ECC Multi-Harness Exporter (Claude, Codex, Cursor, Windsurf)")
    parser.add_argument("--target", required=True, choices=["cursor", "windsurf", "claude", "codex", "all"])
    parser.add_argument("--out", default=str(VAULT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    out_root = Path(args.out)
    files: list[str] = []
    targets = ["cursor", "windsurf", "claude", "codex"] if args.target == "all" else [args.target]
    for t in targets:
        if t == "cursor":
            files.extend(export_cursor(out_root, args.dry_run))
        elif t == "windsurf":
            files.extend(export_windsurf(out_root, args.dry_run))
        elif t == "claude":
            files.extend(export_claude(out_root, args.dry_run))
        elif t == "codex":
            files.extend(export_codex(out_root, args.dry_run))

    res = {"target": args.target, "dry_run": args.dry_run, "exported_count": len(files), "files": files}
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        mode = "REJA (dry-run)" if args.dry_run else "EKSPORT QILINDI"
        print(f"✓ {mode} ({args.target}): {len(files)} ta fayl -> {', '.join(files[:8])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
