#!/usr/bin/env python3
"""Tyrion v5.0 Master CLI — Butun tizim uchun yagona boshqaruv markazi (0 token).

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
sys.path.insert(0, str(TOOLS))
import tyrion_core as tcore  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

VERSION = "7.0.0"

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
    print("=" * 68)
    print(f"  🧠 TYRION v{VERSION} — AI PAID MEDIA & TARGETOLOGY OPERATING SYSTEM")
    print("=" * 68)
    print(f"  Arxitektura : Single-Root ECC v{VERSION} (Calibrated & Live-Telemetry Ready)")
    print(f"  Agentlar    : {counts.get('agents', 36)} ta (100% skill ulangan + Prompt Defense)")
    print(f"  Skilllar    : {counts.get('skills', 62)} ta (36 platforma + 26 operator/marketing)")
    print(f"  Playbooklar : {counts.get('playbooks', 9)} ta (Meta $1k-$10k, E-com, Ta'lim, Ko'chmas mulk, B2B...)")
    print(f"  Kontekstlar : {counts.get('contexts', 6)} ta (audit, launch, scale, creative, uzbekistan)")
    print(f"  Wiki Qaydlar: {counts.get('wiki', 100)} ta atomik qayd (0 orphan, 0 xato)")
    print(f"  Buyruqlar   : {counts.get('commands', 18)} ta slash buyruq (/audit, /auditoriya, /kreativ, /voronka...)")
    print(f"  Asboblar    : {counts.get('tools', 29)} ta deterministik CLI vosita (Meta Graph API v26.0)")
    print("-" * 68)
    print("  Tezkor CLI Buyruqlar:")
    for cmd, (script, def_args) in ROUTES.items():
        print(f"    python3 tools/tyrion.py {cmd:10} -> tools/{script} {' '.join(def_args)}")
    print("    python3 tools/tyrion.py paths      -> ildiz, xotira va ish papkasi yo'llari")
    print("=" * 68)
    return 0


def show_paths() -> int:
    """Where this copy lives and where it keeps state — the answer differs between a git
    checkout and an installed plugin, so it is printed rather than assumed."""
    print(json.dumps({
        "root": VAULT.resolve().as_posix(),
        "installed_plugin": tcore.is_installed_plugin(VAULT),
        "state_dir": tcore.state_dir(VAULT).as_posix(),
        "memory": tcore.state_path(VAULT, "memory").as_posix(),
        "instincts": tcore.state_path(VAULT, "instincts").as_posix(),
        "work_root": tcore.work_root(VAULT).as_posix(),
    }, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("status", "--help", "-h"):
        return show_status()
    if args[0] == "paths":
        return show_paths()
    cmd, rest = args[0], args[1:]
    if cmd not in ROUTES:
        print(f"✗ Noma'lum buyruq: {cmd}. Mavjud: status, paths, {', '.join(ROUTES)}", file=sys.stderr)
        return 2
    script, default_sub = ROUTES[cmd]
    if not rest:
        final_args = default_sub
    elif default_sub and rest[0] != default_sub[0]:
        final_args = [*default_sub, *rest]
    else:
        final_args = rest
    # The caller's cwd is kept: file arguments (`--file export.csv`) and new client
    # workspaces belong to the user's project, not to the directory Tyrion is installed in.
    proc = subprocess.run([sys.executable, str(TOOLS / script), *final_args])
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
