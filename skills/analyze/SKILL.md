---
name: analyze
description: "Eksport va akkaunt ma'lumotlarini kod orqali tahlil qilish: behuda sarf, Breakdown Effect, CPA diagnostikasi, optimizatsiya qoralamalari, monitoring. Quyidagilar uchun ishlating: 'eksport', 'csv tahlil', 'nega qimmat', 'optimizatsiya', анализ выгрузки."
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

Eksport va akkaunt ma'lumotlarini kod orqali tahlil qilish: behuda sarf, Breakdown Effect, CPA diagnostikasi, optimizatsiya qoralamalari, monitoring. Quyidagilar uchun ishlating: 'eksport', 'csv tahlil', 'nega qimmat', 'optimizatsiya', анализ выгрузки.

## Qoidalar
Tahlil `ad-export-analyzer.py` / `--metrics metrics.v1` orqali; Breakdown Effect hukmdan oldin tekshiriladi.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-optimize` | `skills/analyze/references/ads-optimize.md` | Dalillar, moliyaviy cheklovlar, eksperimentlar va imkoniyat bilan cheklangan adapterlar asosida pullik reklama optimizatsiyalarini diagnostika qilish hamda qoralama qilish yoki aniq qo'llash… |
| `ads-monitor` | `skills/analyze/references/ads-monitor.md` | Qo'llab-quvvatlanadigan platformalarda pullik reklama akkaunti pacing, yetkazib berish, natija, kreativ charchoq, treking, policy va ma'lumot sifatini kuzatish. Kunlik… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
