# Q06 — Apex E-Commerce: Break-even CPA hisob-kitobi

- **Agent:** audit-budget (charter: `agents/audit-budget.md`)
- **Manba fayl:** `examples/demo-brand/BRIEF.md` (§1 "Iqtisodiy ko'rsatkichlar")
- **Sana:** 2026-11-12
- **Evidence darajasi:** barcha kirituvchilar — mijoz brifi ma'lumoti (`MEASURED_ACCOUNT_DATA`); valyuta kursi — brifdan hosil qilingan (`DERIVED`); breakeven formulasi — `HEURISTIC_PRIOR_MODEL` (standart unit-ekonomika formulasi).

## 1. Bor/yo'q ma'lumot (rules/00-manba)

| Ma'lumot | Holat |
|---|---|
| AOV, COGS, fulfillment, to'lov komissiyasi | Bor (brif §1) |
| Break-even ROAS, Target ROAS/CPA | Bor (brif §1) |
| CPA hisoblangan davr, conversion window, akkaunt valyutasi | **Ma'lumot yo'q** (brifda yozilmagan) |

## 2. Bosqichma-bosqich hisob (AOV → yalpi foyda → break-even CPA)

Kurs: brifda 350,000 UZS ≈ $28 → **12,500 UZS/USD** (brifdan hosil qilingan, `DERIVED`).

| # | Bosqich | UZS | USD | Manba |
|---|---------|-----|-----|-------|
| 1 | O'rtacha chek (AOV) | 350,000 | $28.00 | brif §1 |
| 2 | − Tannarx (COGS) | 120,000 | $9.60 | brif §1 |
| 3 | − Yetkazib berish (fulfillment) | 25,000 | $2.00 | brif §1 |
| 4 | − To'lov komissiyasi (Payme/Click, 2.0% × AOV) | 7,000 | $0.56 | brif §1 |
| 5 | **= Sof yalpi foyda (bir dona uchun)** | **198,000** | **$15.84** | hisob: 350,000−120,000−25,000−7,000 |

**Break-even CPA = bir donadan sof yalpi foyda = 198,000 UZS (~$15.84).**
Bu — mijoz kampaniyaga to'lashi mumkin bo'lgan maksimal acquisition xarajati; undan yuqorisi loss beradi.

Tekshiruv (bosqichlar mustaqil tasdiqlandi):
- Brif §1 o'zi 198,000 UZS / $15.8 deb yozgan — hisob bilan mos ($15.84 → brif $15.8 ga yaxlitlagan).
- Tyrion media-calculator: gross profit 198,000, break-even ROAS 1.77x, marja 56.6% — mos.
- Break-even ROAS = AOV / yalpi foyda = 350,000 / 198,000 = **1.77x** (brif §1 bilan mos).

## 3. Natijalar jadvali (UZS va USD)

| Ko'rsatkich | UZS | USD | Izoh |
|---|---|---|---|
| Break-even CPA | 198,000 | ~$15.84 | chegaraviy — foyda 0 |
| Break-even ROAS | — (1.77x) | — (1.77x) | nisbat, valyutadan mustaqil |
| Target CPA | 140,000 | ~$11.20 | brif §1, foyda marjasi bilan |
| Target ROAS | — (2.50x+) | — | brif §1 |

Platformalar joriy CPA bilan solishtirish (brif §2): Meta $14.20, Google $17.80, Telegram $10.50 — breakeven $15.84 bo'yicha Google breakeven'dan yuqorida, Meta chegara ustida, Telegram barqaror.

## 4. Spend-Guard darvoza holati

- **Gate: DRAFT / mutatsiya yo'q.** Bu faqat hisob-kitob; akkauntga byudjet o'zgartirishi, pauza yoki yangi kampaniya taklif qilinmadi ([[40-xavfsizlik-va-hisob]]).
- **Rollback chegarasi (breakeven asosida):** amaldagi CPA davomli ravishda 198,000 UZS ($15.84) dan oshsa — birlik foyda manfiy; Target CPA 140,000 UZS ($11.20) esa xavfsiz ish zonasining yuqori chegarasi sifatida kuzatiladi.

---
Manba: `examples/demo-brand/BRIEF.md` §1–§2 · 2026-11-12; hisob tekshiruvi: tyrion media-calculator (price 350,000 / cogs 120,000 / shipping 25,000 / fee 7,000) · 2026-11-12.
