# MEMORY.md — Operator Workspace Memory & Active Hypotheses

> **Rule:** Keep this file concise (`<= 90` lines). Store reusable cross-client patterns in `manifests/instincts.json` (`/learn`) and client-specific data in `clients/<slug>/`.

## 1. Active Workspace Configuration
- **Default Market Pack:** `global` (override per client via `--market uz|us|eu|uk|mena|latam|sea|in` or `TYRION_MARKET`).
- **Default Currency:** Account-native ISO 4217 (`USD`, `EUR`, `GBP`, `JPY`, `BRL`, `INR`, `AED`, `UZS`).
- **Hook Profile:** `standard` (`TYRION_HOOK_PROFILE=minimal|standard|strict`).

## 2. Active Campaign Hypotheses (Template)
| Date | Client / Account | Hypothesis | Target Metric | Status |
|---|---|---|---|---|
| 2026-10-21 | `_template_` | Test 3x3 Angle x Format matrix against control ad set | Thumbstop >= 25%, CPA <= Target | `PENDING` |

## 3. Verified Account Learnings Log
- Record validated post-mortem findings here or promote them via `python3 tools/instincts.py add`.
