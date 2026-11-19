---
name: analyze
description: "Analyze exports and account data via code: wasted spend, Breakdown Effect, CPA diagnosis, optimization drafts, monitoring. Use for 'eksport', 'csv tahlil', 'nega qimmat', 'optimizatsiya', анализ выгрузки."
triggers:
- "optimizatsiya"
- "optimize"
- "kill keep scale"
- "byudjet oshirish"
- "masshtablash"
- "scaling"
- "оптимизация кампании"
- "масштабирование"
- "бюджетни ошириш"
- "monitoring"
- "kunlik nazorat"
- "pacing check"
- "spend anomaly"
- "kpi tushib ketdi"
- "мониторинг рекламы"
- "кунлик назорат"
aliases:
- "scale"
- "kill-keep-scale"
- "campaign-optimization"
- "ads-optimize"
- "pacing"
- "anomaly-detection"
- "daily-check"
- "ads-monitor"
domains:
- "optimization"
- "budget"
- "scaling"
- "monitoring"
- "audit"
platforms:
- "meta"
- "google"
- "telegram"
- "tiktok"
- "multi-platform"
attached_agents: [budget-analyst, creative-strategist, data-analyst]
related_skills: []
references:
- "skills/analyze/references/ads-monitor.md"
- "skills/analyze/references/ads-optimize.md"
risk_level: high
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

# analyze

Analyze exports and account data via code: wasted spend, Breakdown Effect, CPA diagnosis, optimization drafts, monitoring. Use for 'eksport', 'csv tahlil', 'nega qimmat', 'optimizatsiya', анализ выгрузки.

## Qoidalar
Tahlil `ad-export-analyzer.py` / `--metrics metrics.v1` orqali; Breakdown Effect hukmdan oldin tekshiriladi.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-optimize` | `skills/analyze/references/ads-optimize.md` | Diagnose and draft or explicitly apply paid-ad optimizations using evidence, financial constraints, experiments, and capability-gated adapters. Use fo… |
| `ads-monitor` | `skills/analyze/references/ads-monitor.md` | Monitor paid-ad account pacing, delivery, performance, creative fatigue, tracking, policy, and data quality across supported platforms. Use for daily … |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
