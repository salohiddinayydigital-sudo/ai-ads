# Meta Ads audit — act_88291048201 (30 kunlik hisobot)

- Manbalar: `examples/demo-brand/assets/meta_performance.json` · `examples/demo-brand/assets/tracking_health.json`
- Qoida: `rules/00-manba` — manbasiz fakt yo'q; benchmark ko'chirilmaydi.
- Cheklov: hisobga hech qanday o'zgartirish kiritilmadi; barcha tavsiyalar — faqat tahlil va tavsiya matni (qoralama), ijro uchun emas.
- Hisob: `act_88291048201` · valyuta USD · oyna 30 kun (manba fayl sarlavhasidan).

## 1. Ma'lumot ro'yxati (bor / yo'q)

- Bor: sarlavha metrikalari (spend, impression, click, CTR, xaridlar, CPA, revenue, ROAS), 2 kampaniya tafsiloti, Pixel/CAPI/GA4 holati, Telegram bot telemetriyasi.
- Yo'q (`unknown` deb belgilandi): COGS/marja (break-even ROAS hisoblanmaydi), atributsiya oynasi, timezone, kampaniya objective yozuvi, placement breakdown, ad set darajasidagi xaridlar taqsimoti, auditoriya overlap, ASC existing-customer cap qiymati, EMQ maydon tafsiloti.

## 2. Sarlavha skaner (manba: meta_performance.json)

- Spend $3,480.50 · Impressions 482,900 · Clicks 9,180 · CTR 1.90% · Purchases 245 · CPA $14.20 · Revenue $6,787.00 · ROAS 1.95.
- Ichki arifmetika o'zaro mos: 178 + 67 = 245 xarid; $2,610.00 / 178 = $14.66; $870.50 / 67 = $12.99; $3,480.50 / 245 = $14.20; $6,787.00 / $3,480.50 = 1.95. Ziddiyat yo'q.
- Byudjet ulushi: cmp_01 $2,610.00 (75%) · cmp_02 $870.50 (25%).
- ROAS 1.95 ni "yaxshi/yomon" deyilmaydi: marja ma'lumot yo'q, break-even noma'lum (00-manba: benchmark ko'chirilmaydi, faqat akkaunt o'z tarixi bilan solishtiriladi — o'tgan davr exporti ham yo'q).

## 3. Topilmalar

### T1 · Struktura: 8 ta ad setli ABO signal fragmentatsiyasi — LEARNING_LIMITED

- Manba fayl: `meta_performance.json` → campaigns[cmp_01] "BOF_Prospecting_Interests_Split" (ABO, ACTIVE).
- Kuzatuv: 8 ta ad set, `learning_status: LEARNING_LIMITED`, spend $2,610.00, 178 xarid, CPA $14.66, ROAS 1.88.
- Ziddiyat (fayl ichida, alohida ko'rsatiladi): fayl matni "har ad set haftasiga ~15 xarid" deydi, lekin o'z raqamlaridan 178 / 8 / 30 kun hisoblansa ≈ 5 xarid/hafta/ad set chiqadi. Ikkala qiymat ham learning phase bo'sag'asi (~50 xarid/hafta/ad set, `wiki/learning-phase-qoidalari`) dan ancha past — tashxis o'zgarmaydi, aniq qiymat `unknown`.
- Tashxis: signal ad setlar bo'ylab maydalangan, har biri learning bo'sag'asidan uzoq — LEARNING_LIMITED holati tuzilma sababli, taklif sifati haqida bu ma'lumotdan xulosa chiqarmaymiz.
- Tavsiya (qoralama): ad setlarni 3-5 tagacha konsolidatsiya varianti sifatida ko'rib chiqish; qaror uchun ad set darajasidagi breakdown kerak — bu exportda yo'q (`unknown`, so'ralishi kerak). O'lchov oynasi: keyingi 2-4 hafta; rollback: konsolidatsiyadan oldingi struktura nusxasi saqlanadi.

### T2 · Kreativ charchash (fatigue) — cmp_01

- Manba fayl: `meta_performance.json` → campaigns[cmp_01].
- Kuzatuv: FTIR 54.2% · avg_frequency 3.12 · `fatigue_flag: true`. Faylning o'z mezoni: FTIR < 60% va Freq > 3.0 = charchash; ikkala shart ham bajarilgan.
- Qiyosiy dalil: cmp_02 da FTIR 72.0%, Freq 1.85, `fatigue_flag: false` — charchash cmp_01 ga xos.
- Tashxis: 75% byudjet charchagan kreativlarda aylanmoqda; frekans o'sishda davom etsa samaradorlik pasayishi kutiladi (kuzatiladigan dalil, prognoz emas).
- Tavsiya (qoralama): yangi kreativ zaxirasini yangi ad setda sinovga chiqarish rejasi (7 kunlik minimum byudjet bilan — Andromeda scaling signal); eski kreativlarni o'chirmaslik, faqat yangisini qo'shish — reversible qadam. O'lchov: FTIR va frekans haftasiga kuzatiladi.

### T3 · CAPI `event_id` dedup yo'q — ~15% double counting

- Manba fayl: `tracking_health.json` → tracking_audit.meta_capi.
- Kuzatuv: `event_id_deduplication: false`; Pixel (id 84729103847192) va CAPI (gateway.apexstore.uz) ikkalasi ACTIVE, xaridni yuboradi, lekin `event_id` bir xil emas → fayl matniga ko'ra ~15% buyurtmalar ikki marta (double counting) qayd etiladi. `hashing_compliance: true`.
- Tashxis: hisobotdagi 245 xarid takrorlarni ham o'z ichiga olishi mumkin — CPA va ROAS buzilgan. Aniq buzilish yo'nalishi qo'shimcha hisobga bog'liq — `unknown`.
- Qo'shimcha kuzatuv: EMQ 6.2 (fayl bo'yicha); maydon tafsiloti yo'q — chuqur tashxis `unknown`. EMQ va dedup — ikkita alohida muammo (Q12 bilan bog'liq).
- Tavsiya (qoralama): Pixel va CAPI tomonida bir xil `event_id` generatsiya qilish (dedup yoqish) — bu tracking-specialist domeni, conductor orqali reroute qilinadi. O'lchov: dedup yoqilgach Events Manager'da takror foizi kamayishi.

### T4 · Byudjet taqsimoti: samarali ASC 25% ulushda

- Manba fayl: `meta_performance.json` → campaigns[cmp_02] "ASC_Advantage_Shopping".
- Kuzatuv: ASC spend $870.50 (25%), CPA $12.99 (cmp_01: $14.66), ROAS 2.15 (cmp_01: 1.88), FTIR 72.0%, Freq 1.85, `learning_status: LEARNING`, fatigue_flag false.
- Tashxis: faylning o'z xulosasi — "yaxshi ishlayapti, lekin CBO ga qaraganda kam byudjet berilgan (25%)". Statistik ishonch uchun 67 xarid namunasi kichik; o'tgan davrlar taqqoslanmaydi (tarix exporti yo'q).
- Tavsiya (qoralama): byudjet qayta taqsimlash varianti faqat audit-matn sifatida ko'rsatiladi va ikki shartga bog'lanadi: (1) avval T3 dedup tuzatilishi — noto'g'ri xarid hisobida qayta taqsimlash xato qarorga olib keladi; (2) Spend-Guard darvozasidan o'tishi. Rollback: byudjet eski ulushga qaytariladi.

### T5 · Atributsiya uzilishi: Meta → Telegram funnelida UTM yo'q

- Manba fayl: `tracking_health.json` → tracking_audit.telegram_bot_telemetry.
- Kuzatuv: `utm_tagging_present: false`; `crm_webhook_active: true`; bot javob latensiyasi 18 soniya (fayl bo'yicha ideal < 5 soniya), 35% mijoz kutish sababli botni tark etadi.
- Tashxis: lokal funnel normasi Meta Ads → Telegram (charter, `local/ozbekiston-konteksti`); UTM'siz bot buyurtmalari Meta kampaniyalariga bog'lanmaydi — Meta tomonida attributsiya rasmi to'liq emas. 18s latensiya funnel yo'qotishi bo'lib, audit-meta domeni emas — reroute: tracking-specialist/CRO (conductor qarori).
- Tavsiya (qoralama): bot havolalariga UTM belgilash joriy etilishi; Pixel/CAPI to'liq ishlamaguncha Meta rasmi cheklanganligi mijozga boshida ochiq aytiladi (charter konteksti).

## 4. Cheklovlar va missing_inputs

- Hisobga hech qanday o'zgartirish kiritilmadi va kiritish tavsiya qilinmaydi; barcha tavsiyalar qoralama — Spend-Guard darvozasidan o'tmaguncha ijro etilmaydi (charter authority_boundary).
- missing_inputs: COGS/marja, timezone, atributsiya oynasi, objective yozuvi, placement breakdown, ad set darajasidagi xaridlar, auditoriya overlap, ASC existing-customer cap qiymati, EMQ maydon tafsiloti, o'tgan davr exporti.
- Benchmark (CPA/CTR/ROAS normasi jadvallari) keltirilmadi; faqat fayllardagi ichki mezonlar va akkaunt o'z raqamlari ishlatildi (00-manba #3-#4).
