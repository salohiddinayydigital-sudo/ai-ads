# Tyrion v8 — progress (davom ettirish uchun shu fayldan boshlang)

Branch: `claude/tyrion-v8-upgrade-2sk89s` · PR ochilmaydi (so'ralmaguncha).
Darvoza: `pytest -q tests` · `doctor.py` · `catalog.py check` · `catalog.py drift` · `vault-audit.py . --gate` · `token-budget.py`.

| # | Bosqich | Holat | Oxirgi commit |
|---|---|---|---|
| 0 | Baseline: token-budget.py, docs/v8-baseline.md | bajarildi | (shu commit) |
| 1 | Lean Core: skill 19, agent 12, model-ko'rinadigan buyruq 12, migratsiya, token 1999/3500 | bajarildi (router 30% qisqartirish — kechiktirildi, D5) | (shu commit) |
| 2 | metrics.v1, normalize, client-workspace v2, Spend-Guard PreToolUse hook (spend_gate.py), `--metrics` eski asboblarda, connect skill, integrations.md, PLATFORM_BENCHMARK | bajarildi | (shu commit) |
| 3 | pulse.py, experiments.py, pulse/experiments skill + scheduling.md | bajarildi | (shu commit) |
| 4 | crm-bridge, creative-analytics, adlib-mine, lead-quality skill, production-pipeline.md | bajarildi | (shu commit) |
| 5 | audit_scoring.py, ChatGPT Ads reference (CG01–CG09), Telegram 2026/Meta MCP/Advantage+ qaydlari (manbalar `url_cited`/`unverified`) | bajarildi (rasmiy sahifalar bu muhitdan ochilmadi) | (shu commit) |
| 6 | report-html.py, `/start` wizard, `tyrion.py demo`, README/README.uz | bajarildi | (shu commit) |
| 7 | 29 golden eval (ishga tushirilmagan), coverage 76.5% (gate 75), CI, VERSION 8.0.0, CHANGELOG, AGENTS/CLAUDE/INDEX | bajarildi; release-verifier: 8 mezondan 7 PASS, 1 (sintetik belgi) tuzatildi | (shu commit) |

## Jurnal
- 2026-11-19: boot o'qildi; baseline yashil; `docs/v8-roadmap.md` yo'q.

- 2026-11-19: `/start demo` qo'lda tekshirildi: `python3 tools/tyrion.py demo --out /tmp/demo_t/out` → 5/5 qadam ✓, `demo-brand-report.html` (inline SVG, CDN yo'q), pulse: cpa_drift(critical), tracking_break(critical), fatigue(warning). Avtomat test: tests/test_demo_flow.py.
- Qoldi: Bosqich 7 (golden evals, coverage ≥75%, CI, VERSION 8.0.0, CHANGELOG, AGENTS/CLAUDE/INDEX, release-verifier).
