# Q05 — @toshkent_bozori kanali byudjetini haftasiga +30% oshirish taklifi

- **Status:** DRAFT TAKLIF — hisobga hozir hech qanday o'zgartirish kiritilmagan (read-only, [[rules/40-xavfsizlik-va-hisob]] §1).
- **Hisob:** `tg_ads_fragment_8819` · Valyuta: USD · Ma'lumot oynasi: 30 kun.
- **Manba (MEASURED_ACCOUNT_DATA):** `examples/demo-brand/assets/telegram_campaigns.json` (2026-11-12 ko'rildi).
- **Agent:** audit-budget — faqat moliyaviy modellashtirish va Spend-Guard tekshiruvi; canli mutatsiya yo'q ([[agents/audit-budget]] authority_boundary).

## 1. Unit economics jadvali (manbadan o'lchangan)

| Ko'rsatkich | Qiymat | Manba |
|---|---|---|
| Umumiy xarajat (30 kun) | $1,200.00 | JSON summary |
| Impressions / Clicks / CTR | 352,940 / 4,235 / 1.20% | JSON summary |
| Qualified leads / CPL | 825 / $1.45 | JSON summary |
| Orders / CAC | 99 / $12.12 | JSON summary |
| Revenue / ROAS | $3,180.00 / 2.65 | JSON summary |
| **@toshkent_bozori** | **$450.00 · CPM $3.00 · CTR 1.45% · CPL $1.25** | JSON channels_performance |
| Status | `WINNER_SCALE` | JSON |

Kanal darajasidagi eng kuchli ko'rsatkich — CPL $1.25 (hisob o'rtachasi $1.45 dan 14% arzon) va eng yuqori CTR 1.45%.

## 2. Taklif: haftasiga +30% oshirish (hisob-kitob)

| Miqdor | Hozirgi | Taklif (+30%) |
|---|---|---|
| Kunlik byudjet | $15.00 (=$450 / 30 kun) | $19.50 |
| Haftalik byudjet | $105.00 (=$15 × 7) | $136.50 |
| Qo'shimcha xarajat | — | +$31.50 / hafta |

**Proyeksiya (HEURISTIC_PRIOR_MODEL — kafolat emas):** CPL $1.25 saqlansa, +$31.50/hafta ≈ 25 qo'shimcha qualified lead va ≈ 2–3 qo'shimcha order/hafta (CAC $12.12 asosida). Bu taxmin; real natija learning phase resetidan keyin og'ishi mumkin.

**Diqqat:** manbadagi `finding` maydoni o'zi faqat **"haftasiga +15%"** tavsiya qiladi. +30% manba tavsiyasidan ham, Spend-Guard chegarasidan ham yuqori — shu ikki sababga qo'shimcha ehtiyotkorlik talab qilinadi.

## 3. Spend-Guard tekshiruvi — GATE: FAILED

`tyrion_spend_guard(current_daily=15.00, proposed_daily=19.50)` natijasi:

```
passed: false · percent_change: 30.0% · max_daily_cap: $500.00 (o'tdi)
ERROR: Byudjet oshishi +30.0% (> 20%). Learning phase / Smart Bidding qaytadan
boshlanadi (reset). Maksimal ruxsat: +20% (≤ $18.00/kun).
```

Xulosa: **bir qadamda +30% mutatsiya ruxsat etilmaydi.** Ikki variant:

- **Variant A (gate'ga mos, tavsiya etiladi):** ikki bosqichli o'sish — 1-hafta +15% ($17.25/kun, 7 kun kuzatuv), so'ng 2-bosqich +13% ($17.25 → $19.50/kun). Har bir qadam ≤ +20%, yakuniy holat bir xil (+30%).
- **Variant B (asl topshiriq):** bir qadamda $19.50/kun — faqat to'liq mutation gate + foydalanuvchining aniq tasdig'i bilan.

## 4. Mutation gate holati ([[rules/40-xavfsizlik-va-hisob]] §1)

| Bosqich | Holat |
|---|---|
| 1. Preview | ✅ — ushbu taklifda aniq ko'rsatildi: $15.00 → $19.50/kun (yoki Variant A bo'yicha bosqichma-bosqich) |
| 2. Tasdiq | ❌ — **foydalanuvchidan aniq "ha" javobi shart**; tasdiqsiz o'zgarish bajarilmaydi |
| 3. Idempotentlik | ⬜ — o'zgarish bir marta qo'llanadi; takroriy buyruq ta'sir qilmaydi |
| 4. Tekshiruv | ⬜ — o'zgarishdan keyin 7 kun CPL/CTR/ROAS o'lchanadi (§5 chegaralar) |
| 5. Audit yozuvi | ⬜ — nima, qachon, nega `journal/` ga yoziladi |
| 6. Rollback | ✅ — qaytarish yo'li §6 da oldindan yozilgan |

Gate to'liq yopilmaguncha hisob **read-only** rejimda qoladi.

## 5. Monitoring chegaralari (o'zgarishdan keyingi tekshiruv, 7 kunlik oyna)

- Kanal CPL: $1.25 bazadan **+25% gacha** ($1.56) — normal; undan yuqorida — signal.
- Hisob ROAS: 2.65 baza; **< 2.0** ga tushsa — signal.
- Kanal CTR: 1.45% baza; **< 1.0%** ga tushsa — signal.

## 6. Rollback ko'rsatmasi

- **Trigger:** §5 dagi istalgan signal buzilsa (masalan, CPL $1.56+ yoki ROAS < 2.0).
- **Amal:** byudjetni o'zgarishdan oldingi holatga qaytarish — **$15.00/kun ($105.00/hafta)**; Variant A bo'lsa — so'nggi tasdiqlangan bosqich qiymati.
- **Tartib:** qaytarish ham mutatsiya — bir marta (idempotent) qo'llanadi, natija tekshiriladi, `journal/` ga audit yozuvi tushadi; learning phase reset xavfi qaytarishda ham mavjud — shu sababli Variant A (kichik qadamlar) afzal ko'riladi.

## 7. allocation tradeoff (qo'shimcha izoh, HEURISTIC_PRIOR_MODEL)

Manbadagi `@kulgu_va_memlar` ($200 xarajat, CPL $3.40, `KILL_CANDIDATE`) — `@toshkent_bozori` ni tekin byudjet manbasi bo'lishi mumkin edi: kanalni to'xtatib, aylanayotgan $200/30 kun ($6.67/kun) qayta taqsimlash yangi pul jalb qilmasdan +30% ga yaqin o'sish beradi. Bu alohida taklif; bu yerda faqat izoh sifatida qoldirildi.

---

**Yakuniy holat:** hisob o'zgarmagan. Har qanday amal faqat 2-bosqich (aniq tasdiq) dan keyin boshlanadi.
