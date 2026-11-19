# Tyrion v8 — progress (davom ettirish uchun shu fayldan boshlang)

Branch: `claude/tyrion-v8-upgrade-2sk89s` · PR ochilmaydi (so'ralmaguncha).
Darvoza: `pytest -q tests` · `doctor.py` · `catalog.py check` · `catalog.py drift` · `vault-audit.py . --gate` · `token-budget.py`.

| # | Bosqich | Holat | Oxirgi commit |
|---|---|---|---|
| 0 | Baseline: token-budget.py, docs/v8-baseline.md | bajarildi | (shu commit) |
| 1 | Lean Core (skill 61→~20, agent 36→~12, buyruq ≤12, migratsiya) | kutmoqda | — |
| 2 | Ma'lumot qatlami: metrics.v1, normalize, Spend-Guard hook, Client Brain | kutmoqda | — |
| 3 | Pulse + Experiment Ledger | kutmoqda | — |
| 4 | crm-bridge, creative-analytics, adlib-mine | kutmoqda | — |
| 5 | Bilim yangilash + audit_scoring | kutmoqda | — |
| 6 | report-html, /start, README | kutmoqda | — |
| 7 | Evals, coverage, reliz | kutmoqda | — |

## Jurnal
- 2026-11-19: boot o'qildi; baseline yashil; `docs/v8-roadmap.md` yo'q.
