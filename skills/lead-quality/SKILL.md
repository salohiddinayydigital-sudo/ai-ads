---
name: lead-quality
description: "Lead quality loop: CRM stages to Meta CAPI events, conversion-leads, Higher Intent forms, Telegram qualification, AmoCRM/Bitrix. Use for 'lid sifati', 'sifatsiz lid', 'crm', 'amocrm', 'capi lead', качество лидов."
triggers:
- "lid sifati"
- "sifatsiz lid"
- "crm"
- "amocrm"
- "bitrix"
- "capi lead"
- "качество лидов"
- "conversion leads"
aliases: []
domains:
- lead-quality
- crm
platforms:
- meta
attached_agents:
- tracking-specialist
related_skills: []
references:
- "skills/lead-quality/references/lead-quality-loop.md"
risk_level: medium
output_contract: "Structured deliverable with evidence labels and honest execution report"
---

## Ish tartibi

1. Muammoni aniqla: sifatsiz lid — forma, auditoriya, kreativ yoki ta'qib (CRM) muammosimi? Avval CRM eksportini so'ra (AmoCRM/Bitrix24 JSON yoki CSV).
2. `stage_map` ni foydalanuvchi bilan tasdiqla (qaysi bosqich "saralangan"?).
3. `python3 tools/crm-bridge.py report ...` — lead→qualified campaign/adset/ad/forma bo'yicha. Kichik namunada xulosa qilma.
4. Tuzatish gipotezalari: saralash savollari, Higher Intent forma, Telegram bot kvalifikatsiyasi, kreativ filtri (narx/shart oldindan aytiladi). Har biri `experiments` bilan tekshiriladi.
5. CAPI: avval `payload` (dry-run), consent va dedup tekshiriladi; `send` faqat foydalanuvchi `--confirm` desa.
6. Sotuvchi qo'ng'iroq transkriptlari bo'lsa: `python3 tools/call-insights.py report --input <papka|fayl> --group-by ad` (reklama bo'yicha e'tirozlar) va `brief` (kreativ burchak nomzodlari). Audio→matn tashqarida qilinadi; consent yo'q yozuvlar tashlanadi, PII chop etilmaydi; natija HEURISTIC, `--min-calls` dan kichik namunada xulosa yo'q.
7. Natijani `pulse` va `creative-analytics.py` ga ber (qaysi kreativ sifatli lid keltiradi).

Rasmiy Meta maydonlari (`action_source`, CRM-lead hodisa maydonlari, Higher Intent shartlari) tasdiqlanmaguncha `unverified`.

## Manbalar

| Fayl | Mazmun |
|---|---|
| `skills/lead-quality/references/lead-quality-loop.md` | stage_map, crm-bridge, forma, bot, AmoCRM, UZ amaliyoti |
