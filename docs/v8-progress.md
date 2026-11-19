# Tyrion v8 — progress (davom ettirish uchun shu fayldan boshlang)

Branch: `claude/tyrion-v8-upgrade-2sk89s` · PR ochilmaydi (so'ralmaguncha).
Darvoza: `pytest -q tests` · `doctor.py` · `catalog.py check` · `catalog.py drift` · `vault-audit.py . --gate` · `token-budget.py`.

| # | Bosqich | Holat | Oxirgi commit |
|---|---|---|---|
| 0 | Baseline: token-budget.py, docs/v8-baseline.md | bajarildi | (shu commit) |
| 1 | Lean Core: skill 19, agent 12, model-ko'rinadigan buyruq 12, migratsiya, token 1999/3500 | bajarildi (router 30% qisqartirish — kechiktirildi, D5) | (shu commit) |
| 2 | metrics.v1 + normalize.py + client-workspace v2: BAJARILDI (fork). QOLDI: Spend-Guard PreToolUse hook, `--metrics` eski asboblarda, connect skill/integrations.md, PLATFORM_BENCHMARK yorlig'i | qisman | (shu commit) |
| 3 | pulse.py + experiments.py + testlar: BAJARILDI (fork). QOLDI: pulse/experiments skill matni, scheduling hujjati | qisman | (shu commit) |
| 4 | crm-bridge, creative-analytics, adlib-mine asboblari: BAJARILDI (fork). QOLDI: lead-quality skill matni, production-pipeline.md | qisman | (shu commit) |
| 5 | audit_scoring.py: BAJARILDI (fork). QOLDI: ChatGPT Ads/Telegram 2026/Meta MCP bilim yangilash | qisman | (shu commit) |
| 6 | report-html.py: BAJARILDI (fork). QOLDI: /start wizard, demo, README | qisman | (shu commit) |
| 7 | Evals, coverage, reliz | kutmoqda | — |

## Jurnal
- 2026-11-19: boot o'qildi; baseline yashil; `docs/v8-roadmap.md` yo'q.
