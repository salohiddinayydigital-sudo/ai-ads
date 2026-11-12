# Apex E-Commerce — Qisqa hisobot seksiyasi (byudjet audit)

Manba qoidasi: `rules/00-manba.md` — har raqam oldida manba belgisi turadi:
- **[MEASURED_ACCOUNT_DATA]** — akkaunt eksporti: `examples/demo-brand/assets/meta_performance.json` (30 kunlik oynacha, akkaunt act_88291048201)
- **[HEURISTIC_PRIOR_MODEL]** — hisob-kitob: BRIEF.md dagi unit economics asosida hisoblangan chegara qiymatlari

## Meta Ads — asosiy raqamlar (30 kun)
- [MEASURED_ACCOUNT_DATA] Umumiy sarf: $3,480.50
- [MEASURED_ACCOUNT_DATA] Xaridlar: 245 ta
- [MEASURED_ACCOUNT_DATA] O'rtacha CPA: $14.20
- [MEASURED_ACCOUNT_DATA] Tushum: $6,787.00 · ROAS: 1.95
- [MEASURED_ACCOUNT_DATA] CTR: 1.90%

## Kampaniyalar bo'yicha
- [MEASURED_ACCOUNT_DATA] cmp_01 "BOF_Prospecting_Interests_Split" (ABO, LEARNING_LIMITED): sarf $2,610.00 · 178 xarid · CPA $14.66 · ROAS 1.88 · FTIR 54.2% · freq 3.12 · fatigue_flag=true (kreativ charchash belgisi)
- [MEASURED_ACCOUNT_DATA] cmp_02 "ASC_Advantage_Shopping" (ASC, LEARNING): sarf $870.50 · 67 xarid · CPA $12.99 · ROAS 2.15 · FTIR 72.0% · freq 1.85

## Break-even chegaralar (hisob-kitob, o'lchov emas)
- [HEURISTIC_PRIOR_MODEL] Break-even CPA: $15.84 (≈198,000 UZS) — BRIEF.md dagi yalpi foyda qiymatidan olingan
- [HEURISTIC_PRIOR_MODEL] Break-even ROAS: 1.77x — kontribusiya marjasi formulasi bo'yicha hisoblangan

## Diagnostika (faqat o'lchangan raqamlarga tayanadi)
- [MEASURED_ACCOUNT_DATA] O'rtacha CPA $14.20 — break-even CPA $15.84 dan past: har xarid hisobiga yalpi foyda hozircha ijobiy.
- [MEASURED_ACCOUNT_DATA] cmp_01 sarfning ~75% ini yutadi ($2,610.00 / $3,480.50) va LEARNING_LIMITED holatida — ad set konsolidatsiyasi masalasi ko'riladi; bu DRAFT tavsiya, o'zgarish emas (Spend-Guard darvozasi hali o'tmagan).

## Cheklovlar / ma'lumot yo'q
- Google Ads va Telegram Ads raqamlari uchun eksport/ma'lumot yo'q (faqat BRIEF.md jadvalida keltirilgan) — shuning uchun bu hisobotda ishlatilmadi.
- meta_performance.json da oynaning aniq boshlanish/tugash sanasi ko'rsatilmagan — "ma'lumot yo'q".

Manba: examples/demo-brand/assets/meta_performance.json (30 kunlik eksport) · examples/demo-brand/BRIEF.md · hisobot tuzilgan: 2026-11-12
