# OVERNIGHT REPORT — `chore/v8.0.2-hardening`

Branched from `main` @ `3295dfe`. No force-push, no commits to `main`. Version intentionally left at **8.0.1** (`VERSION` and every manifest unchanged); the CHANGELOG entry is `[Unreleased]`.

## (a) Before / after

| Check | Before | After |
|---|---|---|
| `python3 -m unittest discover -s tests -t .` | 547 tests, OK (1 skipped) | **639 tests**, OK (1 skipped) — also verified on Python 3.11 and 3.12 |
| `tools/doctor.py` | 19/19 ok | 21 checks: 20 ok, 0 errors (1 warning only while the tree is dirty) |
| `tools/tyrion-shield.py scan` | 6/6 ok | 6/6 ok |
| `tools/vault-audit.py --gate` | 0 issues | 0 issues |
| `tools/token-budget.py` | 2003 / 3500 | 2003 / 3500 (unchanged) |
| `npm test`, `npm run skills:check` | pass | pass |
| `catalog check` / `drift`, `skill-eval` | pass | pass |
| Coverage gate (min 75%) | 75.75% (measured mid-work) | passes |
| Run with PyYAML blocked | `skill-search check` **failed** | passes (fixed, see below) |

All steps of `.github/workflows/tyrion-ci.yml` were reproduced locally (catalog, vault gate, router smoke, token budget, v8 smoke steps, shield, eval, unittest, doctor --quick, coverage). Only Python 3.11–3.13 were available locally; 3.10 and Windows/macOS were not run (new tests avoid 3.11-only APIs: `tomllib` has a fallback).

## (b) Files changed and why

**Real bug fixes**
- `tools/spend_gate.py` — a change packet whose `proposal.current_daily` was `NaN`, `0`, a string, or only one side present skipped the +20% budget rule entirely (e.g. 0 → 9999 passed). Now any budget field triggers the full `check_budget_change`, failing closed. Regression tests added.
- `tools/skill-search.py` — the PyYAML-free frontmatter fallback read `related_skills: []` as the string `"[]"`, so `skills:check` failed without PyYAML. Inline lists are now parsed.

**Packaging / runtime**
- `package.json` — added `"engines": {"node": ">=18.0.0"}`; scripts untouched.
- `pyproject.toml` (new) — `tyrion-ai` 8.0.1, `requires-python >=3.10,<3.14`, no dependencies, ruff config (`E9,F`).
- `tools/doctor.py` — new `check_runtime` (Python 3.10–3.13, Node >=18; missing Node = warning, old Node/Python = fail).

**Cleanup (no CLI flag or MCP schema changes)**
- English docstrings/comments: `tools/tyrion.py`, `tools/tyrion_core.py`, `tools/spend_gate.py`, `tools/spend-guard.py`.
- Removed dead imports / unused variable / placeholder-less f-strings: `ad-export-analyzer.py`, `brain-graph.py`, `brain-search.py`, `capi-utm-builder.py`, `calculator.py`, `creative-matrix.py`, `meta-audience.py`, `hooks/tyrion-hook.py`.
- `manifests/catalog.json` — regenerated (`catalog.py build`) because tool fingerprints changed.
- `CHANGELOG.md` — `[Unreleased]` entry.

**Tests added (92)**: `tests/test_core_hardening.py` (28), `tests/test_mcp_server_hardening.py` (25), `tests/test_spend_boundaries.py` (31), `tests/test_runtime_checks.py` (8).

**Deliberately NOT changed**
- `graphify-out/` and `LOG.md`/`MEMORY.md`: not safe to gitignore or archive — `hooks/tyrion-hook.py` protects `graphify-out/graph.json`, and the vault delivery gate requires `LOG.md`. They are tracked inputs, not stray artifacts.
- Plugin manifests, `README.md`, `README.uz.md`, `locales/`, runtime user-facing messages (Uzbek CLI/error strings are tested product output).
- **Remaining Uzbek docstrings/comments** in ~30 other `tools/*.py` files (largest: `catalog.py`, `skill-search.py`, `doctor.py`, `tyrion-shield.py`, `tyrion_workflows.py`). Scope was the named files plus the spend modules; the rest is a follow-up.
- `tools/skill-search.py` has 12 repeated dict keys (ruff F601, lines ~116–256). Later keys silently win; cleaning them could change routing, so they need a deliberate review with the routing evals.
- CI installs PyYAML although code works without it; harmless, left as is.

## (c) Stale remote items — recommended for MANUAL closure (nothing was closed or deleted)

- **PR #1** "Tyrion 7.0.1 trust hotfix + v7.1/v7.2 code-level follow-ups" (`claude/determined-lamport-5hb945`) — open since 2026-11-11, base is pre-7.0.1 `main`; superseded by merged PRs #2–#12.
- Branches whose PRs are already merged (safe to delete after confirming): `claude/determined-lamport-5hb945` (after closing #1), `claude/eager-mendel-egdynh`, `claude/festive-heisenberg-0cg466` (#5), `claude/friendly-mccarthy-93mqz2`, `claude/gifted-hawking-s42dhx`, `claude/inspiring-davinci-y8mh9x` (#7), `claude/jolly-heisenberg-bpc4aj`, `claude/new-session-363v1s`, `claude/tyrion-v7-fixes-03j63p` (#2–#4), `claude/tyrion-v8-upgrade-2sk89s` (#9–#12), `feat/universal-meta-creative-upgrade` (#6), `fix/plugin-readiness` (#8). Branches without a listed PR (`eager-mendel`, `friendly-mccarthy`, `gifted-hawking`, `jolly-heisenberg`, `new-session`) should be checked with `git log main..origin/<branch>` first.
- `claude/sweet-hamilton-busdpa` is this session's working branch (no changes of its own).

## (d) Merge into `main`

```bash
git fetch origin
git checkout main && git pull --ff-only origin main
git merge --no-ff origin/chore/v8.0.2-hardening -m "chore: v8.0.2 hardening (spend-gate fix, runtime checks, +92 tests)"
git push origin main
```
Prefer opening a PR so CI (3 OS x 4 Python versions) runs first. To release as 8.0.2, bump `VERSION` and run `python3 tools/catalog.py version-sync` afterwards.
