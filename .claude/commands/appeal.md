---
disable-model-invocation: true
description: Rad etilgan reklama yoki cheklangan akkaunt/BM — white-hat sabab tahlili, xavfsiz qayta yozish, EN/RU apellyatsiya matni va infratuzilma gigiyenasi
argument-hint: <rad etish xabari, matn/kreativ, landing> [rejection_triage|appeal_draft|infra_hygiene]
---

# /appeal — rad etilish va blokirovkadan tiklanish (`account-recovery-specialist`)

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/40-xavfsizlik-va-hisob.md` — **faqat white-hat**: cloaking, soxta hujjat, farm/ijara/o'g'irlangan akkaunt, policy'ni aldash qat'iyan taqiqlanadi.
2. Agent: `agents/account-recovery-specialist.md`; o'qi: `skills/audit/references/account-recovery-whitehat.md`.

## Ijro

1. Incident turi va ehtimoliy policy bandi (rasmiy manba URL + sana yoki `unverified`).
2. Safe rewrite — buzilishni olib tashlaydigan variant (o'zgartirilmagan kreativni qayta yuborish yo'q).
3. Xotirjam, faktli EN/RU apellyatsiya + hujjatlar ro'yxati; tiklash ketma-ketligi.
4. Yuridik savol → `compliance-reviewer`.

## Natija

`recovery_action_packet` (`white_hat_only: true`) + Self-Audit (Pass/Fail). Mijozga inqiroz xabari → `/client-update`.
