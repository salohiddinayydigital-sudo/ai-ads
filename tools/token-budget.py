#!/usr/bin/env python3
"""token-budget.py — model har sessiyada doim ko'radigan tavsiflar narxini o'lchaydi.

Hisoblanadi: skill (`skills/*/SKILL.md`), agent (`agents/*.md`) va model chaqira oladigan
buyruqlar (`commands/*.md`, `disable-model-invocation: true` bo'lmaganlari) `description`
belgilari. Taxminiy token = belgilar / 4 (konservativ evristika, `HEURISTIC_PRIOR_MODEL`).

    python3 tools/token-budget.py                    # hisobot
    python3 tools/token-budget.py --json             # mashina o'qiydigan chiqish
    python3 tools/token-budget.py --max-tokens 3500  # oshsa exit 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from catalog import read_frontmatter  # noqa: E402

CHARS_PER_TOKEN = 4


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "yes", "1"}


def _entry(kind: str, path: Path, root: Path, name_hint: str) -> dict | None:
    fm = read_frontmatter(path)
    desc = fm.get("description", "")
    if not isinstance(desc, str):
        desc = str(desc or "")
    desc = " ".join(desc.split())
    hidden = _truthy(fm.get("disable-model-invocation", False))
    return {
        "kind": kind,
        "name": str(fm.get("name") or name_hint),
        "path": path.relative_to(root).as_posix(),
        "chars": len(desc),
        "tokens": (len(desc) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN,
        "model_visible": not hidden,
    }


def collect(root: Path = ROOT) -> list[dict]:
    items: list[dict] = []
    for p in sorted((root / "skills").glob("*/SKILL.md")):
        e = _entry("skill", p, root, p.parent.name)
        if e:
            items.append(e)
    for p in sorted((root / "agents").glob("*.md")):
        if p.name.lower() == "readme.md":
            continue
        e = _entry("agent", p, root, p.stem)
        if e:
            items.append(e)
    for p in sorted((root / "commands").glob("*.md")):
        e = _entry("command", p, root, p.stem)
        if e:
            items.append(e)
    return items


def summarize(items: list[dict], top: int = 10) -> dict:
    visible = [i for i in items if i["model_visible"]]
    by_kind: dict[str, dict] = {}
    for kind in ("skill", "agent", "command"):
        sel = [i for i in visible if i["kind"] == kind]
        by_kind[kind] = {
            "count": sum(1 for i in items if i["kind"] == kind),
            "model_visible": len(sel),
            "chars": sum(i["chars"] for i in sel),
            "tokens": sum(i["tokens"] for i in sel),
        }
    return {
        "label": "HEURISTIC_PRIOR_MODEL (tokens ~ chars/4)",
        "total_chars": sum(i["chars"] for i in visible),
        "total_tokens": sum(i["tokens"] for i in visible),
        "by_kind": by_kind,
        "top": sorted(visible, key=lambda i: -i["chars"])[:top],
        "over_300_chars": [i["path"] for i in visible if i["chars"] > 300],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Doimiy ko'rinadigan description narxi")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=None, help="oshsa exit 1")
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not (root / "skills").is_dir():
        print(f"xato: {root}/skills topilmadi", file=sys.stderr)
        return 2
    rep = summarize(collect(root), args.top)
    gate_ok = args.max_tokens is None or rep["total_tokens"] <= args.max_tokens
    rep["max_tokens"] = args.max_tokens
    rep["gate_passed"] = gate_ok
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"Doimiy description narxi: {rep['total_chars']} belgi ≈ {rep['total_tokens']} token  [{rep['label']}]")
        for k, v in rep["by_kind"].items():
            print(f"  {k:8} {v['model_visible']:>3}/{v['count']:<3} ko'rinadi · {v['chars']:>6} belgi · {v['tokens']:>5} token")
        print(f"Eng qimmat {len(rep['top'])}:")
        for i in rep["top"]:
            print(f"  {i['chars']:>5}  {i['kind']:7} {i['name']}")
        if rep["over_300_chars"]:
            print(f"300 belgidan uzun: {len(rep['over_300_chars'])} ta")
        if args.max_tokens is not None:
            print(("OK" if gate_ok else "BLOKLANDI") + f": {rep['total_tokens']} / {args.max_tokens} token")
    return 0 if gate_ok else 1


if __name__ == "__main__":
    sys.exit(main())
