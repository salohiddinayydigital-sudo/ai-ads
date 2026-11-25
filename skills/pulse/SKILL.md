---
name: pulse
description: "Daily account watch from metrics.v1: pacing, CPA/ROAS drift, fatigue, tracking breaks, spend spikes. Report only, never acts. Use for 'pulse', 'kunlik tekshiruv', 'monitoring', 'ogohlantirish', мониторинг."
triggers:
- "pulse"
- "kunlik tekshiruv"
- "monitoring"
- "ogohlantirish"
- "мониторинг"
- "anomaly"
- "ertalabki triage"
- "cpl oshib ketdi"
- "вырос cpl"
- "morning triage"
aliases: []
domains:
- monitoring
platforms:
- meta
attached_agents: [daily-optimizer, data-analyst]
related_skills: []
references:
- "skills/pulse/references/scheduling.md"
risk_level: medium
output_contract: "Structured deliverable with evidence labels and honest execution report"
---

## Ish tartibi

1. Mijoz `clients/<slug>/state.json` o'qiladi (`python3 tools/client-workspace.py state get`): maqsad CPA/ROAS, `pulse_config` chegaralari.
2. Ma'lumot: `metrics.v1` (snapshot + `tools/normalize.py`). Rasmiy `ads_insights_anomaly_signal` mavjud bo'lsa, natijasi JSON qilib `--anomaly-signal` ga beriladi (qo'shimcha dalil).
3. `python3 tools/pulse.py run --client <slug> --format both`.
4. Tekshiruvlar: pacing, CPA/ROAS drift (minimal konversiya va statistik test; kichik namunada "ma'lumot yetarli emas"), frequency↑ + CTR↓ (charchoq), tracking uzilishi (sarf bor, konversiya keskin tushgan), sarf sakrashi, learning-limited/rad etilgan reklamalar (ma'lumot bo'lsa).
5. Har topilma: `severity`, dalil, keyingi qadam, `needs_approval`. Standart chegaralar `HEURISTIC_PRIOR_MODEL`; mijoz tarixi bilan almashtiriladi.
6. Hech narsa bajarilmaydi. O'zgartirish kerak bo'lsa: Spend-Guard change packet ([[40-xavfsizlik-va-hisob]]).

## Manbalar

| Fayl | Mazmun |
|---|---|
| `skills/pulse/references/scheduling.md` | `/loop`, cron, Task Scheduler, GitHub Actions |
