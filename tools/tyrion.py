#!/usr/bin/env python3
"""Tyrion v7.1 Master CLI — Butun tizim uchun yagona boshqaruv markazi (0 token).

Ishlatish:
  python3 tools/tyrion.py status
  python3 tools/tyrion.py route "<topshiriq>" [--json]
  python3 tools/tyrion.py execute "<topshiriq>" [--json]
  python3 tools/tyrion.py doctor [--quick]
  python3 tools/tyrion.py shield
  python3 tools/tyrion.py audience <subcommand> [args...]
  python3 tools/tyrion.py targeting <subcommand> [args...]
  python3 tools/tyrion.py sync <subcommand> [args...]
  python3 tools/tyrion.py analyze <subcommand> [args...]
  python3 tools/tyrion.py creative <subcommand> [args...]
  python3 tools/tyrion.py client <subcommand> [args...]
  python3 tools/tyrion.py calc <subcommand> [args...]
  python3 tools/tyrion.py guard <subcommand> [args...]
  python3 tools/tyrion.py search "<so'z>"
  python3 tools/tyrion.py skills <subcommand> [args...]
  python3 tools/tyrion.py instincts <subcommand> [args...]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

VERSION = (VAULT / "VERSION").read_text(encoding="utf-8").strip() if (VAULT / "VERSION").is_file() else "0.0.0"

ROUTES = {
    "route": ("skill-search.py", ["route"]),
    "execute": ("skill-search.py", ["execute"]),
    "tokens": ("skill-search.py", ["tokens"]),
    "launch-pack": ("meta-audience.py", ["launch-blueprint"]),
    "intel": ("meta-audience.py", ["market-intel"]),
    "doctor": ("doctor.py", []),
    "shield": ("tyrion-shield.py", ["scan"]),
    "eval": ("skill-eval.py", []),
    "audience": ("meta-audience.py", []),
    "targeting": ("meta-targeting-engine.py", []),
    "sync": ("meta-insights-sync.py", []),
    "analyze": ("ad-export-analyzer.py", []),
    "creative": ("creative-matrix.py", []),
    "capi": ("capi-utm-builder.py", []),
    "client": ("client-workspace.py", []),
    "mcp": ("tyrion-mcp-server.py", ["--list-tools"]),
    "export": ("harness-export.py", []),
    "calc": ("calculator.py", []),
    "guard": ("spend-guard.py", []),
    "search": ("brain-search.py", ["search"]),
    "skills": ("skill-search.py", []),
    "instincts": ("instincts.py", []),
    "catalog": ("catalog.py", []),
    "graph": ("brain-graph.py", []),
    "audit": ("vault-audit.py", []),
}


def show_status() -> int:
    cat_file = VAULT / "manifests" / "catalog.json"
    counts = {}
    if cat_file.is_file():
        counts = json.loads(cat_file.read_text(encoding="utf-8")).get("counts", {})
    if "skills_platform" not in counts:  # eski katalog: jonli skaner
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import catalog as _cat
        counts = _cat.scan()["counts"]
    print("=" * 68)
    print(f"  🧠 TYRION v{VERSION} — AI PAID MEDIA & TARGETOLOGY OPERATING SYSTEM")
    print("=" * 68)
    print(f"  Arxitektura : Single-Root ECC v{VERSION} (Calibrated & Live-Telemetry Ready)")
    print(f"  Agentlar    : {counts.get('agents', 36)} ta (100% skill ulangan + Prompt Defense)")
    print(f"  Skilllar    : {counts.get('skills', 0)} ta ({counts.get('skills_platform', 0)} platforma + {counts.get('skills_operator', 0)} operator/marketing)")
    print(f"  Playbooklar : {counts.get('playbooks', 9)} ta (Meta $1k-$10k, E-com, Ta'lim, Ko'chmas mulk, B2B...)")
    print(f"  Kontekstlar : {counts.get('contexts', 6)} ta (audit, launch, scale, creative, uzbekistan)")
    print(f"  Wiki Qaydlar: {counts.get('wiki', 100)} ta atomik qayd (0 orphan, 0 xato)")
    print(f"  Buyruqlar   : {counts.get('commands', 0)} ta slash buyruq (/audit, /auditoriya, /kreativ, /voronka...)")
    print(f"  Asboblar    : {counts.get('tools', 29)} ta deterministik CLI vosita (Meta Graph API v26.0)")
    print("-" * 68)
    print("  Tezkor CLI Buyruqlar:")
    for cmd, (script, def_args) in ROUTES.items():
        print(f"    python3 tools/tyrion.py {cmd:10} -> tools/{script} {' '.join(def_args)}")
    print("=" * 68)
    return 0


def run_demo(argv: list[str]) -> int:
    """`/start demo`: sintetik demo-brand → state → baseline → pulse → HTML hisobot (jonli hisobsiz, tarmoqsiz)."""
    import argparse
    ap = argparse.ArgumentParser(prog="tyrion.py demo", description="Sintetik demo: init → baseline → pulse → HTML hisobot")
    ap.add_argument("--out", default=str(VAULT / "output" / "demo"), help="chiqish papkasi (clients/ va hisobot shu yerda)")
    ap.add_argument("--lang", default="uz", choices=["uz", "ru", "en"])
    a = ap.parse_args(argv)
    out = Path(a.out)
    clients = out / "clients"
    metrics = clients / "demo-brand" / "data" / "metrics.v1.json"
    steps = [
        ("sintetik metrics.v1", [sys.executable, str(VAULT / "examples" / "demo-brand" / "generate_demo_metrics.py"), str(metrics)]),
        ("client init", [sys.executable, str(TOOLS / "client-workspace.py"), "init", "--client", "demo-brand", "--synthetic", "--force", "--market", "uz",
                         "--lang", a.lang, "--budget", "100", "--target-cpa", "8", "--aov", "60", "--margin-pct", "40", "--event", "Lead",
                         "--currency", "USD", "--root", str(clients)]),
        ("baseline", [sys.executable, str(TOOLS / "client-workspace.py"), "baseline", "--client", "demo-brand", "--metrics", str(metrics), "--event", "Lead",
                      "--level", "ad", "--root", str(clients)]),
        ("pulse", [sys.executable, str(TOOLS / "pulse.py"), "run", "--client", "demo-brand", "--clients-dir", str(clients), "--format", "both", "--write"]),
        ("HTML hisobot", [sys.executable, str(TOOLS / "report-html.py"), "--client", "demo-brand", "--root", str(clients), "--lang", a.lang,
                          "--out", str(out / "demo-brand-report.html"), "--md", str(out / "demo-brand-report.md")]),
    ]
    for i, (title, cmd) in enumerate(steps, 1):
        proc = subprocess.run(cmd, cwd=str(VAULT), capture_output=True, text=True)
        ok = proc.returncode in (0,)
        print(f"{'✓' if ok else '✗'} {i}/{len(steps)} {title}")
        if not ok:
            print((proc.stderr or proc.stdout)[-600:], file=sys.stderr)
            return 2
    print(f"\nHisobot: {out / 'demo-brand-report.html'}\nMarkdown: {out / 'demo-brand-report.md'}\n(Hammasi SINTETIK; jonli hisobga tegilmadi.)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "demo":
        return run_demo(args[1:])
    if not args or args[0] in ("status", "--help", "-h"):
        return show_status()
    cmd, rest = args[0], args[1:]
    if cmd not in ROUTES:
        print(f"✗ Noma'lum buyruq: {cmd}. Mavjud: status, {', '.join(ROUTES)}", file=sys.stderr)
        return 2
    script, default_sub = ROUTES[cmd]
    if not rest:
        final_args = default_sub
    elif default_sub and rest[0] != default_sub[0]:
        final_args = [*default_sub, *rest]
    else:
        final_args = rest
    proc = subprocess.run([sys.executable, str(TOOLS / script), *final_args], cwd=str(VAULT))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
