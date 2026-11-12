#!/usr/bin/env python3
"""Stdlib-only qator qamrovi (line coverage) o'lchagichi va minimal chegara darvozasi (yangi tashqi kutubxonasiz).

Ishlatish (ombor ildizidan):
  python3 tests/coverage_gate.py --min 55                 # unittest'larni o'lchab, chegaradan past bo'lsa exit 1
  python3 tests/coverage_gate.py --min 55 --json out.json # per-fayl hisobot

Nima o'lchanadi: `tools/*.py` va `hooks/*.py` (ijro etiladigan qator = kod obyektlaridagi `co_lines`).
Nima o'lchanMAYDI: alohida subprocess'da ishga tushadigan kod (masalan, hook'ni `subprocess.run` bilan chaqiruvchi
testlar) — ular qamrovga kirmaydi, shuning uchun raqam pastroq (konservativ) bo'ladi.
Chiqish kodi: 0 — chegara bajarildi va testlar o'tdi; 1 — chegaradan past yoki testlar yiqildi.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = [*sorted((ROOT / "tools").glob("*.py")), *sorted((ROOT / "hooks").glob("*.py"))]


def executable_lines(path: Path) -> set[int]:
    try:
        code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    except (SyntaxError, UnicodeDecodeError, ValueError):
        return set()
    lines: set[int] = set()
    stack = [code]
    while stack:
        co = stack.pop()
        lines.update(ln for _s, _e, ln in co.co_lines() if ln is not None and ln > 0)
        stack.extend(c for c in co.co_consts if hasattr(c, "co_lines"))
    # `def`/`class` sarlavhalari import vaqtida bajariladi; hujjat qatorlari (docstring) ham kiradi — bu standart.
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Stdlib line-coverage gate for tools/ and hooks/")
    ap.add_argument("--min", type=float, default=0.0, help="minimal umumiy qamrov foizi")
    ap.add_argument("--json", default="", help="per-fayl hisobotni yozish yo'li")
    ap.add_argument("--pattern", default="test*.py")
    args = ap.parse_args(argv)

    wanted = {str(p) for p in TARGETS}
    hits: dict[str, set[int]] = {w: set() for w in wanted}

    def tracer(frame, event, arg):  # noqa: ANN001
        fn = frame.f_code.co_filename
        if fn not in wanted:
            return None
        bucket = hits[fn]
        bucket.add(frame.f_lineno)

        def local(frame, event, arg):  # noqa: ANN001
            if event == "line":
                bucket.add(frame.f_lineno)
            return local

        return local

    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "tools"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern=args.pattern, top_level_dir=str(ROOT))
    threading.settrace(tracer)
    sys.settrace(tracer)
    try:
        result = unittest.TextTestRunner(verbosity=0, stream=sys.stderr).run(suite)
    finally:
        sys.settrace(None)
        threading.settrace(None)

    per_file = {}
    total_exec = total_hit = 0
    for p in TARGETS:
        ex = executable_lines(p)
        # import vaqtida bajariladigan qatorlar (def/class/import) testlar import qilganda yoqiladi; hits da bor
        covered = len(ex & hits[str(p)])
        per_file[p.relative_to(ROOT).as_posix()] = {"executable": len(ex), "covered": covered, "pct": round(100.0 * covered / len(ex), 1) if ex else 100.0}
        total_exec += len(ex)
        total_hit += covered
    pct = round(100.0 * total_hit / total_exec, 2) if total_exec else 100.0

    print(f"\n{'fayl':44} {'qator':>6} {'qamrov':>7}")
    for rel, d in sorted(per_file.items(), key=lambda kv: kv[1]["pct"]):
        print(f"{rel:44} {d['executable']:6d} {d['pct']:6.1f}%")
    print(f"\nUMUMIY QAMROV (tools/ + hooks/, jarayon ichidagi testlar): {pct}% ({total_hit}/{total_exec}) — minimal chegara: {args.min}%")
    if args.json:
        Path(args.json).write_text(json.dumps({"total_pct": pct, "min": args.min, "files": per_file}, indent=2), encoding="utf-8")
    if not result.wasSuccessful():
        print("✗ testlar yiqildi")
        return 1
    if pct < args.min:
        print(f"✗ qamrov {pct}% < {args.min}%")
        return 1
    print("✓ qamrov darvozasi o'tdi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
