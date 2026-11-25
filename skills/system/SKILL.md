---
name: system
description: "Tyrion maintenance: doctor, shield, learn, SOP lookup, release validation, skill checks. Use for 'doctor', 'shield', 'learn', 'sop', 'tizim holati', 'validate', проверка системы."
triggers:
- "policy tekshiruvi"
- "reklama qoidalari"
- "blokirovka"
- "ad rejected"
- "special ad category"
- "compliance"
- "модерация рекламы"
- "блокировка рекламного кабинета"
- "apellyatsiya"
- "akkaunt bloklandi"
- "аккаунт заблокирован"
- "ad account restricted"
aliases:
- "policy-check"
- "compliance"
- "ad-moderation"
- "ads-validate"
domains:
- "compliance"
- "policy"
- "validation"
platforms:
- "multi-platform"
attached_agents: [account-recovery-specialist, compliance-reviewer, release-verifier]
related_skills: []
references:
- "skills/system/references/ads-validate.md"
risk_level: medium
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

# system

Tyrion maintenance: doctor, shield, learn, SOP lookup, release validation, skill checks. Use for 'doctor', 'shield', 'learn', 'sop', 'tizim holati', 'validate', проверка системы.

## Qoidalar
Testni o'chirish/kuchsizlantirish taqiqlangan; darvoza qizil bo'lsa tuzat.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-validate` | `skills/system/references/ads-validate.md` | Validate Claude Ads contracts, scoring inputs, run bundles, capabilities, source freshness, safety, installation, uninstall, or release readiness. Use… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
