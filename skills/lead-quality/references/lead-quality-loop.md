# Lid sifati sikli: CRM → CAPI

Maqsad: Meta lid emas, **sifatli lid** uchun optimallashsin. CRM bosqichlari hodisaga aylanib Meta'ga qaytadi.

## 1. Bosqichlarni moslash (`stage_map`)

CRM bosqichi → `Lead | QualifiedLead | Appointment | Shown | Purchase | ignore`. Namuna: `tests/fixtures/crm/stage_map.json` (sintetik). Purchase uchun qiymat (summa) CRM'dan olinadi.

## 2. crm-bridge (`python3 tools/crm-bridge.py <report|payload|send> --input F --format amocrm|bitrix24|csv --stage-map M.json [--currency] [--out] [--dataset-id] [--confirm]`)

- `report` — lead→qualified konversiyasi campaign/adset/ad/forma bo'yicha (creative-analytics va pulse'ga kirish).
- `payload` — CAPI batch payload (SHA-256 hash, `+998` telefon normalizatsiyasi, `event_id`/`lead_id` dedup, consent bo'lmasa tashlanadi).
- `send` — faqat `--confirm` va env'dagi token bilan; aks holda dry-run. PII log qilinmaydi.
- `action_source` va CRM-lead hodisa maydonlari: `source_status: unverified` (rasmiy hujjat bu muhitda tekshirilmagan; yuborishdan oldin Meta hujjatida tasdiqlang).

## 3. Meta tomoni (tekshirilmagan, hujjatda tasdiqlang)

- Lead formada "yuqori niyat" rejimi (Higher Intent) va qo'shimcha saralash savollari lid hajmini kamaytirib, sifatini oshirishi mumkin: bu — gipoteza, `HEURISTIC_PRIOR_MODEL`; o'z hisobingizda A/B bilan tekshiring (`skills/experiments/SKILL.md`).
- Conversion-leads (CRM hodisalari bo'yicha optimallashtirish) uchun yetarli hodisa hajmi kerak; minimal chegara rasmiy hujjatdan olinadi (`unverified`).

## 4. Saralash savollari (forma / bot)

Byudjet oralig'i, muddat ("qachon kerak?"), shahar/hudud, qaror qabul qiluvchimi, aloqa kanali. 3–5 savoldan oshmasin.

## 5. Telegram bot orqali kvalifikatsiya

Lid → bot (`?start=<lead_id>` deep-link, `capi-utm-builder.py`) → 3 ta savol → bahoga qarab CRM'da `QualifiedLead` bosqichi. Bot Pixel ma'lumotini bermaydi: `lead_id`/`event_id` ni CRM'ga yozib qo'ying.

## 6. AmoCRM pipeline namunasi (misol)

`Yangi → Bog'lanildi → Saralandi (QualifiedLead) → Uchrashuv belgilandi (Appointment) → Keldi (Shown) → Sotuv (Purchase)`; `Spam/Yo'q` → `ignore`. Bitrix24 da ham shu mantiq.

## 7. UZ amaliyoti

- Telefon `+998XXXXXXXXX`; to'lov Payme/Click/Uzum — Purchase qiymatini haqiqiy to'langan summadan oling.
- Til: UZ va RU segmentlari alohida (`rules/30-ozbekiston-konteksti.md`).
- Rozilik (consent) bo'lmagan lid payload'ga kirmaydi; PII commit qilinmaydi.
