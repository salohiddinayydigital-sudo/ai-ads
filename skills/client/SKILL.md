---
name: client
description: "Client workspace and state: onboarding, brief, unit economics, tracking and mutation guardrails, decisions. Use for 'mijoz', 'yangi mijoz', 'onboarding', 'brief', 'client state', новый клиент."
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

Client workspace and state: onboarding, brief, unit economics, tracking and mutation guardrails, decisions. Use for 'mijoz', 'yangi mijoz', 'onboarding', 'brief', 'client state', новый клиент.

## Qoidalar
Mijoz holati `clients/<slug>/state.json` da; sir va PII commit qilinmaydi.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-setup` | `skills/client/references/ads-setup.md` | Set up a paid-media client, brand, account, data-source, privacy, and mutation-guardrail profile for Claude Ads. Use for onboarding, initial configura… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
