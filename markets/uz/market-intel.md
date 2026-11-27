---
name: uzbekistan-market-intel
description: O'zbekiston raqamli reklama bozori intellekti — Toshkent va viloyatlar auditoriya segmentatsiyasi, 3 tilli (O'zbek lotin, kirill, rus) mentalitet, Telegram Bot/ManyChat/AmoCRM voronkasi, Payme/Click/Uzum Nasiya psixologiyasi va to'lov qobiliyati (solventnost) filtrlari. O'zbekiston bizneslari uchun reklamani rejalashtirish, audit qilish yoki yozishda ishlating.
triggers:
- o'zbekiston bozori
- toshkent
- viloyatlar
- uzum nasiya
- alif nasiya
- payme
- click
- telegram bot voronka
- узбекистан рынок
- ташкент реклама
- ўзбекистон бозори
aliases:
- uz-market
- tashkent
- solventnost-uz
- nasiya
domains:
- market-intel
- audience
- copywriting
- strategy
platforms:
- meta
- telegram
- google
- instagram
attached_agents: [platform-auditor, platform-auditor, strategist, creative-strategist, audience-architect]
related_skills:
- ads-meta-audience
- ads-telegram
- copywriting
references: []
risk_level: low
output_contract: O'zbekiston bozori lokalizatsiya qatlamlari (Toshkent va viloyatlar ajratilishi, UZ/RU til izolyatsiyasi, Nasiya to'lov ankerlari, TG Bot + AmoCRM voronkasi)
---

# O'zbekiston bozori intellekti (`uzbekistan-market-intel`)

## Qachon yoqiladi
- O'zbekiston (`Toshkent` yoki viloyat bozorlari) uchun Meta Ads, Telegram Ads, Google Ads yoki TikTok Ads'ni rejalashtirish, audit qilish yoki masshtablash.
- **Telegram botlar**, **ManyChat Instagram DM avtomatlashtirishi** va **AmoCRM / Bitrix24** asosida lid generatsiyasi yoki e-commerce voronkalarini loyihalash.
- Takliflarni mahalliy BNPL / bo'lib to'lash tizimlari bilan tuzish (**Uzum Nasiya, Alif Nasiya, Payme, Click, ZoodPay**).
- Qimmat segment auditoriyalarini (*Novostroyka*, xususiy maktablar, klinikalar, B2B, avto, mebel) xarid qobiliyati (*solventnost*) bo'yicha filtrlash.

## Asosiy bozor qoidalari
1. **Telegram-birinchi voronka arxitekturasi:** O'zbekistonda B2C segmentda email drip kampaniyalarining ochilish ko'rsatkichi `<2%`. Trafikni doim `Instagram DM (ManyChat kalit so'z)` yoki `Telegram Bot (?start=utm_payload)` -> `Kontakt ulashish` -> `AmoCRM` -> `15 daqiqa ichida qo'ng'iroq` yo'nalishiga yo'naltiring.
2. **Geografik ajratish (bir ad set'da hech qachon aralashtirmang):**
   - **Toshkent shahri:** CPM yuqori ($2.50–$6.00+), AOV yuqori, ikki tilli kuchli talab (`UZ` + `RU` alohida ad set'larda).
   - **Viloyatlar (Samarqand, Farg'ona, Andijon, Namangan, Buxoro va h.k.):** CPM past ($0.80–$2.20), qamrov katta; agar CBO/Broad'da Toshkent bilan exclusion'siz aralashtirilsa, Meta byudjetning 80% ini xarid qobiliyati pastroq arzon viloyat ko'rsatuvlariga sarflaydi.
3. **3 tilli tabiiy matn yozish (`[[10-til-va-uslub]]`):**
   - Ruscha reklama matnini o'zbekchaga hech qachon mashina tarjimasi bilan o'tkazmang. Tabiiy o'zbek (lotin), o'zbek (35+ auditoriya uchun kirill) va rus hooklarini alohida yozing.
4. **BNPL / bo'lib to'lash framing'i:** `>$50` bo'lgan har qanday taklif uchun oylik to'lov narxini **Uzum Nasiya / Alif Nasiya** orqali ko'rsatish (`"Oyiga atigi 149,000 so'mdan — boshlang'ich to'lovsiz"`) konversiya darajasini `1.6x–2.4x` oshiradi.

## Anti-patternlar
- **NOTO'G'RI:** Butun O'zbekiston bo'ylab bitta kampaniyani "Link Clicks" (`Traffic`) uchun sekin veb-sayt formasiga yo'naltirib yuritish.
- **TO'G'RI:** Toshkent va viloyatlarni `Pixel + CAPI` yoki Instant Form (2 ta saralovchi savol) + Telegram Bot warmup bilan alohida Conversion/Lead ad set'larga ajratish.

## Bog'liq skilllar va playbooklar
- `skills/audience/references/ads-meta-audience.md`
- `playbooks/meta-ads-1k-10k-uz.md`
- `playbooks/telegram-bot-amocrm-voronka.md`


## Deterministik CLI va asboblar integratsiyasi (`0 token`)
`uzbekistan-market-intel` bo'yicha tavsiyalar yaratish yoki rejalarni o'zgartirishdan oldin tegishli Tyrion v8.3 deterministik tekshiruvlarini ishga tushiring:
- **Unit-iqtisodiyot va break-even:** `python3 tools/calculator.py breakeven --price <AOV> --cogs <COGS>`
- **Meta auditoriya va voronka diagnostikasi:** `python3 tools/meta-audience.py architect --niche <niche> --budget <daily_usd>`
- **CSV/JSON eksport va Breakdown Effect:** `python3 tools/ad-export-analyzer.py analyze --file <export.csv>`
- **CAPI v22 SHA-256 va Telegram Bot UTM:** `python3 tools/capi-utm-builder.py utm --url <url> --platform meta`
- **Spend-Guard darvozasi:** `python3 tools/spend-guard.py budget --current <old> --proposed <new> --max-cap <cap>`

## Anti-patternlar (`NOTO'G'RI` va `TO'G'RI`)
| Holat | ❌ XATO (`NOTO'G'RI`) | ✅ TO'G'RI (`TO'G'RI`) |
|---|---|---|
| **Benchmark da'volari** | Akkaunt tarixi yoki break-even hisobisiz umumiy global CTR/CPA o'rtachalarini keltirish. | Avval `tools/calculator.py` orqali aniq `Break-Even ROAS = 1 / Margin` va `Target CPA` ni hisoblash (`[[00-manba]]`). |
| **Byudjetni masshtablash** | Faol ad set byudjetini bir kechada ikki baravar (+100%) oshirib, Learning Phase'ni nolga tushirish. | Vertikal masshtablashda **har 48–72 soatda ko'pi bilan +20%** (`tools/spend-guard.py`) yoki g'olib angle'larni gorizontal klonlash (`[[learning-phase-qoidalari]]`). |
| **Auditoriya izolyatsiyasi** | Cold prospecting (`TOF`) ni `Purchase 180d`, `Leads 30d` va `Active DM 14d` ni chiqarmasdan yuritish. | 4 qatlamli Exclusion matritsasini `tools/meta-audience.py architect` orqali majburiy qilish (`[[meta-auditoriya-arxitekturasi]]`). |
| **Placement'larni qisqartirish** | Yuqori hajmli placement'larni (masalan Instagram Reels) faqat o'rtacha CPA yuqori bo'lgani uchun pauza qilish (*Breakdown Effect*). | Marginal CPA ta'sirini baholash uchun `tools/ad-export-analyzer.py breakdown-effect` ni ishga tushirish (`[[meta-breakdown-effekti]]`). |
