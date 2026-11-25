---
disable-model-invocation: true
description: Mijoz bilan muloqot — 30 soniyalik Telegram hisobot, e'tirozga ayblovsiz javob, byudjet oshirish/upsell taklifi yoki inqiroz xabari (faqat tasdiqlangan raqamlar)
argument-hint: <raqamlar yoki e'tiroz matni> [telegram_digest|objection_handler|budget_upsell_pitch|crisis_update]
---

# /client-update — mijozga xabar (`client-comms-lead`)

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/10-til-va-uslub.md` + `rules/00-manba.md` (manbasiz raqam va kafolat yo'q).
2. Agent: `agents/client-comms-lead.md`; o'qi: `skills/report/references/client-comms-playbooks.md`.

## Ijro

1. Raqamlar faqat `data-analyst` / `budget-analyst` / `daily-optimizer` paketidan yoki foydalanuvchidan; yo'q bo'lsa — so'ra.
2. Mijoz tili (UZ/RU), jargonsiz, ko'pi bilan 4 raqam; aniq keyingi qadam + muddat.
3. Byudjet ta'siri diapazoni kerak bo'lsa: `python3 tools/calculator.py` (`HEURISTIC_PRIOR_MODEL`).

## Natija

`client_comms_packet` + Self-Audit (>= 85/100). Xabarni foydalanuvchi tasdiqlab o'zi yuboradi.
