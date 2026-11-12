# Q05 — @toshkent_bozori kanali byudjetini haftasiga +30% oshirish taklifi (DRAFT)

Hisob: tg_ads_fragment_8819 · Valyuta: USD · Oynа: 30 kun · Sana: 2026-11-12
Holat: **FAQAT TAKLIF — hisobga hozir o'zgartirish kiritilmadi** (Spend-Guard darvoza yopiq).

## 1. Faktlar (manba: examples/demo-brand/assets/telegram_campaigns.json)

- @toshkent_bozori: sarf $450.00/30 kun → $15.00/kun, $105.00/hafta.
- Kanal metrikalari: CPM $3.00, CTR 1.45%, CPL $1.25 (hisobdagi eng past).
- Status: WINNER_SCALE — "Haftasiga +15% byudjet oshirish mumkin".
- Hisob umumiy: CPL $1.45, CAC $12.12, ROAS 2.65.

## 2. Taklif (o'zgarish paketi)

- Obyekt: @toshkent_bozori kanal byudjeti.
- Hozirgi: $15.00/kun ($105.00/hafta) → Taklif: $19.50/kun ($136.50/hafta, +$31.50/hafta).
- Asos: eng past CPL ($1.25) va yuqori CTR (1.45%) — WINNER_SCALE status.
- Kutilayotgan effekt: qo'shimcha ~25 qualified lead/hafta (CPL $1.25 da) — taxmin, kafolat emas.
- Noaniqlik: kanal darajasidagi CAC/ROAS manbada yo'q; hisob o'rtachasiga tenglashadi deb qaralmaydi.

## 3. Spend-Guard tekshiruvi — NATIJA: FAIL

- Tekshiruv: $15.00 → $19.50 = **+30%**. Ruxsat etilgan chegara: **+20%** (≤ $18.00/kun).
- Xato: "+30% (> 20%) — o'rganish faza (learning phase) reset bo'ladi; maksimal +20%".
- Shuningdek, manba topilmasi +15%/hafta cheklovini ko'rsatadi — +30% ikkala chegarani ham buzadi.

## 4. Tasdiq talabi (mutation gate)

- +20% chegaradan yuqori o'zgarish **foydalanuvchining aniq "ha" javobisiz bajarilmaydi**.
- Variantlar: (a) +15% → $120.75/hafta (manba tavsiyasi, avtomatik yo'l); (b) +20% → $126.00/hafta (Spend-Guard ceiling); (c) +30% → $136.50/hafta (faqat tasdiqdan keyin).
- Tasdiqlanganda bajarilish tartibi: preview → aniq tasdiq → idempotent yozuv → 7 kunlik tekshiruv oynasi → audit jurnaliga yozuv.

## 5. Rollback ko'rsatmasi

- Qaytarish: kunlik byudjetni darhol $15.00 ($105.00/hafta) ga qaytarish — bitta teskari yozuv, idempotent kalit: `toshkent_bozori_budget_rollback_20261112`.
- Rollback trigggerlari (taklif, tasdiq talab qiladi): CPL $1.45 (hisob o'rtachasi) dan yuqoriga chiqsa; bot drop-off keskin oshsa; ROAS 2.65 hisob o'rtachasidan sezilarli pastga tushsa (2 kun ketma-ket).
- Qaytarilgandan keyin natija journal'ga yoziladi.
