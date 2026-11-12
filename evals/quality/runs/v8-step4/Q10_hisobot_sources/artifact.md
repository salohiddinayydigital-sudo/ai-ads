# Apex E-Commerce — Meta Ads Performance Hisobot (qisqacha seksiya)

**Akkaunt:** act_88291048201 [MEASURED_ACCOUNT_DATA] · **Davr:** 30 kunlik oyna [MEASURED_ACCOUNT_DATA] · **Valyuta:** USD [MEASURED_ACCOUNT_DATA]

**Mavjud/yo'q ma'lumot (tahlil boshida):** Meta Ads eksporti bor; Google Ads va Telegram Ads natijalari bu eksportda yo'q — `missing_inputs`. Shu sababli bu seksiyada faqat Meta ko'rsatkichlari ko'rsatilgan.

## 1. Blended ko'rsatkichlar (30 kun)

- [MEASURED_ACCOUNT_DATA] Umumiy sarf: $3,480.50
- [MEASURED_ACCOUNT_DATA] Xaridlar soni: 245 ta
- [MEASURED_ACCOUNT_DATA] Blended CPA: $14.20
- [MEASURED_ACCOUNT_DATA] Blended ROAS: 1.95x (umumiy daromad $6,787.00)
- [MEASURED_ACCOUNT_DATA] O'rtacha CTR: 1.90%

## 2. Break-even chegara (hisob-kitobdan)

- [HEURISTIC_PRIOR_MODEL] Break-even CPA: $15.84 — brief unit economics hisobidan (sof yalpi foyda $15.8/birlik; AOV $28, COGS $9.6 asosida).
- [HEURISTIC_PRIOR_MODEL] Break-even ROAS: 1.77x; maqsadli ROAS: 2.50x+.
- Xulosa: o'lchangan CPA $14.20 [MEASURED_ACCOUNT_DATA] break-even chegara ($15.84) ostida; o'lchangan ROAS 1.95x [MEASURED_ACCOUNT_DATA] break-even (1.77x) ustida, ammo maqsadli (2.50x) ostida.

## 3. Segmentlar (marginal ko'rsatkich)

- [MEASURED_ACCOUNT_DATA] cmp_01 "BOF_Prospecting_Interests_Split" (ABO): sarf $2,610.00, 178 xarid, CPA $14.66, ROAS 1.88x; FTIR 54.2%, frequency 3.12, LEARNING_LIMITED, fatigue_flag = true.
- [MEASURED_ACCOUNT_DATA] cmp_02 "ASC_Advantage_Shopping" (ASC): sarf $870.50, 67 xarid, CPA $12.99, ROAS 2.15x; FTIR 72.0%, frequency 1.85, fatigue_flag = false.

## 4. Breakdown-effect tekshiruvi

- [MEASURED_ACCOUNT_DATA] Sarf ulushi: cmp_01 ≈ 75.0%, cmp_02 ≈ 25.0%.
- [HEURISTIC_PRIOR_MODEL] Tuzoq aniqlandi (Breakdown Effect): cmp_02 ning pastroq o'rtacha CPA'si ($12.99) kichik hajmdagi eng arzon auktsionlar hisobidan; dominat segment (cmp_01) to'xtatilsa, blended CPA $14.20 dan ~$19.61 ga yomonlashishi prognoz qilinadi (model hisobi — o'lchangan raqam emas).

## 5. Kuzatuv va tashxis (ajratilgan)

- Kuzatuv [MEASURED_ACCOUNT_DATA]: cmp_01 da 8 ta ad set mavjud, har biri haftasiga o'rtacha ~15 ta xarid olmoqda; kreativ charchash belgilari bor (FTIR < 60%, Freq > 3.0).
- Tashxis [HEURISTIC_PRIOR_MODEL]: kampaniyani o'chirish tavsiya etilmaydi (breakdown tuzog'i, 4-bo'lim); hajm konsolidatsiyasi (1-5-5 CBO yo'nalishi) va yangi kreativ burchaklari CPA ni tushirishga eng yaqin variant. Bunday o'zgarishlar media-buyer qoralamasi va Spend-Guard gatesi orqali, foydalanuvchi tasdig'i bilan amalga oshiriladi.
- [missing_inputs] CAPI deduplikatsiyasi holati, Google Ads va Telegram Ads natijalari eksportda yo'q — alohida tekshiruv talab qilinadi.

---

Manba: examples/demo-brand/assets/meta_performance.json (Meta Ads eksporti, 30 kunlik oyna) · examples/demo-brand/BRIEF.md (unit economics) · 2026-11-12
