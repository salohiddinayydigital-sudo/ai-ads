---
name: client
description: "Mijoz ish maydoni va holati: onboarding, brif, unit-iqtisodiyot, treking va o'zgartirish himoya chegaralari, qarorlar. Quyidagilar uchun ishlating: 'mijoz', 'yangi mijoz', 'onboarding', 'brief', 'client state', новый клиент."
triggers:
- "akkaunt sozlash"
- "account setup"
- "onboarding"
- "utm tuzish"
- "pixel o'rnatish"
- "настройка аккаунта"
- "онбординг клиента"
- "mijozga javob"
- "mijoz e'tirozi"
- "mijozga telegram hisobot"
- "inqiroz xabari"
- "отчет клиенту"
- "client update"
- "yangi mijoz brif"
- "бриф клиента"
aliases:
- "onboarding"
- "account-setup"
- "utm-setup"
- "ads-setup"
domains:
- "setup"
- "tracking"
- "launch"
platforms:
- "multi-platform"
attached_agents: [client-comms-lead, client-onboarder]
related_skills: []
references:
- "skills/client/references/ads-setup.md"
risk_level: medium
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

# client

Mijoz ish maydoni va holati: onboarding, brif, unit-iqtisodiyot, treking va o'zgartirish himoya chegaralari, qarorlar. Quyidagilar uchun ishlating: 'mijoz', 'yangi mijoz', 'onboarding', 'brief', 'client state', новый клиент.

## Qoidalar
Mijoz holati `clients/<slug>/state.json` da; sir va PII commit qilinmaydi.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-setup` | `skills/client/references/ads-setup.md` | Claude Ads uchun pullik media mijozi, brend, akkaunt, ma'lumot manbasi, maxfiylik va o'zgartirish himoya profilini sozlash. Onboarding, dastlabki konfiguratsiya… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
