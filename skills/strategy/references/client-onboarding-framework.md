<!-- v8.3 Targetolog Copilot Pack: client-onboarder metodologiyasi. Ref: agents/client-onboarder.md, rules/60-loyiha-papkasi.md -->

# Mijozni qabul qilish (Client Onboarding) freymvorki

> Maqsad: tartibsiz mijoz xabaridan 24 soat ichida strukturali brif, tayyorlik hukmi (Go / Fix-First / No-Go), ruxsatlar cheklisti va kickoff taklifi. KPI va'dasi faqat unit-ekonomikadan keyin.

## 1. Intake brif — 8 majburiy biznes parametri

| # | Parametr | Nega kerak | Yo'q bo'lsa |
|---|---|---|---|
| 1 | Mahsulot/xizmat va asosiy offer | angle va kanal | savol |
| 2 | O'rtacha chek (UZS/USD) | break-even CPA | savol |
| 3 | Marja (%) yoki tannarx | break-even CPA/ROAS | savol (`ASSUMPTION` faqat ochiq belgilansa) |
| 4 | ICP (kim, qayerda, qanday og'riq) | auditoriya | savol |
| 5 | Geo (shahar/viloyat, yetkazib berish radiusi) | targeting | savol |
| 6 | Oylik reklama byudjeti | kanal soni, test muddati | savol |
| 7 | Maqsadli CPL/CPA yoki "qancha lid kerak" | KPI | break-even'dan hisoblanadi |
| 8 | Oldingi tajriba (kanal, natija, nima ishlamadi) | takroriy xatoni oldini olish | "yo'q" deb qayd |

Yetishmagan parametrlar mijozga **oddiy tilda** savollar ro'yxati sifatida qaytariladi (`missing_inputs`), texnik jargon yo'q.

## 2. Tayyorlik filtri — Go / Fix-First / No-Go

| Omil | Go | Fix-First | No-Go |
|---|---|---|---|
| Instagram/Telegram qadoqlash | 9+ post, aniq bio, narx/manzil, highlight'lar | profil bor, lekin ishonch bloklari yo'q | profil/kanal yo'q, 1–2 post |
| Sotuv bo'limi javob tezligi (SLA) | ≤ 15 daqiqa ish vaqtida | 1–3 soat | javob beruvchi yo'q |
| Minimal test byudjeti | ≥ 14 kun × (2–3 × maqsadli CPA) / kun | yarmi | undan kam |
| Unit-ekonomika | break-even CPA ≥ bozor CPA taxmini | chegarada | marja reklamani ko'tarmaydi |
| Offer | aniq, raqobatbardosh | noaniq | yo'q / noqonuniy |

Bitta No-Go omili → "targetga tayyor emas" + aniq tuzatish ro'yxati. Halollik mijozni yo'qotishdan arzon.

## 3. Ruxsatlar cheklisti (mijozga yuboriladigan UZ/RU ko'rsatma)

1. **Meta Business Manager:** mijoz BM'si → Sozlamalar → Hamkorlar → targetolog BM ID'si qo'shiladi (shaxsiy akkaunt paroli **hech qachon** so'ralmaydi).
2. **Ad Account:** hamkorga "Manage campaigns" ruxsati; to'lov usuli mijoz nomida.
3. **Pixel / Dataset:** hamkorga ulashish; domen tasdiqlash (DNS TXT).
4. **Instagram / Facebook Page:** BM'ga ulangan, hamkorga ruxsat.
5. **Telegram Ads / kanal:** kanal admini, Telegram Ads akkaunti (Fragment/TON yoki agentlik orqali).
6. **CRM / lid oqimi:** lidlar qayerga tushadi (amoCRM, Bitrix24, Google Sheets, Telegram bot), kim javob beradi.
7. **Sayt / landing:** admin yoki GTM ruxsati (agar CAPI kerak bo'lsa → `tracking-specialist`).

Ruxsat holati: `granted | pending | missing`.

## 4. Kickoff taklifi (14–30 kunlik test)

- **Scope:** kanallar (1–2), kreativ soni, hisobot chastotasi.
- **Kutilmalar:** 1-hafta — learning va signal yig'ish; 2-hafta — birinchi kill/scale qarorlari; natija prognozi `HEURISTIC_PRIOR_MODEL`.
- **Mas'uliyat chegarasi:** targetolog — sozlash, optimizatsiya, hisobot; mijoz — offer, narx, sotuv bo'limi javobi, kontent materiali, to'lov.
- **Taqiq:** "kafolatlangan sotuv/lid soni" va'dasi.

## 5. Asboblar

`tyrion_media_calculator` (break-even), `python3 tools/client-workspace.py` (mijoz papkasi: `BRIEF`, `AUDIENCE-MAP`, `journal`), `tyrion_brain_search` (nisha playbooklari).
