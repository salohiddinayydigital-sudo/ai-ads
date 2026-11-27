---
name: budget
description: "Byudjet matematikasi: break-even CPA/ROAS, MER, pacing, taqsimlash, 20% masshtablash qoidasi, kill/keep/scale. Quyidagilar uchun ishlating: 'byudjet', 'break-even', 'roas', 'scale', 'qancha sarflay', бюджет, масштабирование."
triggers:
- "unit ekonomika"
- "unit economics"
- "break-even roas"
- "target cpa"
- "romi"
- "cac"
- "ltv"
- "marja hisobi"
- "юнит экономика"
- "окупаемость"
- "ҳисоб-китоб"
- "byudjet"
- "budget"
- "byudjet taqsimoti"
- "spend allocation"
- "pacing"
- "scaling budget"
- "бюджет"
- "распределение бюджета"
- "бюджет режаси"
aliases:
- "media-math"
- "breakeven"
- "roas-calc"
- "unit-economics"
- "ads-math"
- "budget-plan"
- "spend-allocation"
- "media-budget"
- "ads-budget"
domains:
- "budget"
- "finance"
- "analytics"
- "strategy"
platforms:
- "multi-platform"
attached_agents: [budget-analyst, strategist]
related_skills: []
references:
- "skills/budget/references/ads-budget.md"
- "skills/budget/references/ads-math.md"
risk_level: high
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

# budget

Byudjet matematikasi: break-even CPA/ROAS, MER, pacing, taqsimlash, 20% masshtablash qoidasi, kill/keep/scale. Quyidagilar uchun ishlating: 'byudjet', 'break-even', 'roas', 'scale', 'qancha sarflay', бюджет, масштабирование.

## Qoidalar
Matematika `tools/calculator.py` orqali; byudjet > +20% o'zgarish — Spend-Guard.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-math` | `skills/budget/references/ads-math.md` | Pullik media CPA, CPL, CPC, CPM, ROAS, MER, break-even maqsadlar, hissa marjasi, LTV:CAC, impression-share imkoniyati, byudjetlarni hisoblash va modellashtirish… |
| `ads-budget` | `skills/budget/references/ads-budget.md` | Pullik media byudjetlari, bidding, pacing, marginal daromad, prognozlar, CPA, ROAS, MER, LTV:CAC, cheklovlar va qo'llab-quvvatlanadigan platformalar bo'yicha taqsimotni rejalash va ko'rib chiqish… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
