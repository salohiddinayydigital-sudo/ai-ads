---
name: system
description: "Tyrion texnik xizmati: doctor, shield, learn, SOP qidiruvi, reliz validatsiyasi, skill tekshiruvlari. Quyidagilar uchun ishlating: 'doctor', 'shield', 'learn', 'sop', 'tizim holati', 'validate', проверка системы."
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

Tyrion texnik xizmati: doctor, shield, learn, SOP qidiruvi, reliz validatsiyasi, skill tekshiruvlari. Quyidagilar uchun ishlating: 'doctor', 'shield', 'learn', 'sop', 'tizim holati', 'validate', проверка системы.

## Qoidalar
Testni o'chirish/kuchsizlantirish taqiqlangan; darvoza qizil bo'lsa tuzat.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-validate` | `skills/system/references/ads-validate.md` | Claude Ads kontraktlari, ball kirishlari, run bundle'lar, imkoniyatlar, manba yangiligi, xavfsizlik, o'rnatish, o'chirish yoki reliz tayyorligini tekshirish… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
