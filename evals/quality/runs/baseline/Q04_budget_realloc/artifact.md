# Apex E-Commerce — Byudjet qayta taqsimlash rejasi (TAKLIF / DRAFT)

Manba: examples/demo-brand/BRIEF.md + assets/meta_performance.json, google_search_terms.json, telegram_campaigns.json (30 kunlik oynalar) · Sana: 2026-11-12.
Bu faqat taklif: hech qanday hisobga o'zgartirish kiritilmaydi, barcha o'zgarishlar mutation gate tasdig'isiz DRAFT bo'lib qoladi.

## 1. Asos: unit ekonomika (BRIEF.md)
- Break-even CPA: $15.84 (198,000 UZS) · Break-even ROAS: 1.77x
- Target CPA: ~$11.20 (140,000 UZS) · Target ROAS: 2.50x+
- Jami sarf (eksportlar bo'yicha, 30 kun): $6,660.50 = Meta $3,480.50 + Google $1,980.00 + Telegram $1,200.00

## 2. Joriy holat vs break-even
| Kanal | CPA/CAC | ROAS | Break-even bo'yicha holat |
|---|---|---|---|
| Meta blended | $14.20 | 1.95x | Break-even ostida, lekin target CPA ($11.20) ustida |
| Meta cmp_02 (ASC) | $12.99 | 2.15x | Blended dan yaxshi, lekin byudjeti atigi 25% (manba) |
| Meta cmp_01 | $14.66 | 1.88x | LEARNING_LIMITED, 8 ad set, fatigue (FTIR 54.2%, Freq 3.12) |
| Google blended | $17.84 | 1.57x | Break-even ROAS 1.77x dan PAST — zarar zonasi |
| Google High-Intent EXACT/PHRASE | $9.95–$12.46 | — | Target CPA ($11.20) atrofida va ostida |
| Telegram blended | $12.12 (CAC) | 2.65x | Yagona target ROAS 2.50x dan yuqori kanal |
| @kulgu_va_memlar | CPL $3.40 | — | 85% drop-off, manbada "KILL_CANDIDATE" |

## 3. Qayta taqsimlash: qayerdan olindi → qayerga berildi (jami $0 o'zgarish)
| # | Olindi | Berildi | Summa/oy | Sabab (break-even CPA/ROAS bilan) |
|---|---|---|---|---|
| R1 | Google BROAD axlat so'rovlar (266 click, 0 konversiya) | Google High-Intent EXACT/PHRASE guruhlari | $478.80 | Blended CPA $17.84 > break-even $15.84; EXACT CPA $9.95–$12.46 < target $11.20 — sarf zarar zonasidan foyda zonasiga ko'chadi (BRIEF DoD #2: 45 negativ) |
| R2 | Meta cmp_01 (LEARNING_LIMITED, fatigue) | Meta cmp_02 ASC | ~$300 (taklif: ASC ulushi 25% → ~34%) | ASC CPA $12.99 < cmp_01 $14.66, ROAS 2.15 > 1.88; 1-5-5 CBO konsolidatsiyasi o'rganish fazasini tiklaydi (BRIEF DoD #1) |
| R3 | @kulgu_va_memlar (CPL $3.40, 85% drop-off) | @toshkent_bozori (CPL $1.25, WINNER_SCALE) | $200 | Manba to'xtatishni tavsiya qilgan; xuddi shu $200 CPL $3.40 da ~59 lead, CPL $1.25 da ~160 lead beradi |
| R4 (shartli) | Google | Telegram @toshkent_bozori | $300 | Faqat R1+negativlardan keyin 14 kunda Google blended CPA hali > break-even $15.84 bo'lsa; Telegram ROAS 2.65 > target 2.50 (BRIEF DoD #3 bilan parallel) |

Jami: $6,660.50 sarf o'zgarmaydi — faqat yo'naltiriladi. R1–R3 ichki qayta taqsimot, R4 — shartli kesma o'tkazma.

## 4. Spend-Guard eslatmasi (majburiy, har o'zgarish uchun)
- R1–R4 har biri hisob o'zgarishi: mutation gate bosqichlari — Preview (nimaga o'zgarishi) → foydalanuvchidan aniq "ha" → idempotency kaliti → o'zgarishdan keyin o'lchov → audit yozuvi → rollback ([[40-xavfsizlik-va-hisob]] §1).
- @toshkent_bozori ga "+15%/hafta" scaling (manba taklifi) va R4 o'tkazmasi Spend-Guard 20% learning-phase xavfsizlik chegarasiga tekshiriladi; chegaradan oshsa — bosqichma-bosqich oshiriladi.
- Meta CBO konsolidatsiyasi o'rganish fazasini qayta ochadi: R2 dan keyin kamida 1-2 konversiya sikli baholash oynasi kerak.

## 5. Rollback (teskari qadam)
| O'zgarish | Qaytarish sharti (taklif) | Qaytarish amali |
|---|---|---|
| R1 negativlar | Negativlardan keyin 30 kunlik konversiyalar 111 dan >20% kamaysa | Saqlangan eksportdan qo'shilgan negativ ro'yxatini olib tashlash |
| R2 Meta konsolidatsiya | ASC 7 kun ketma-ket CPA > $15.84 yoki ROAS < 1.77 | Change Packet orqali oldingi 8 ad set struktura/byudjet bo'linishini tiklash |
| R3 Telegram kill | @toshkent_bozori CPL > $3.40 (kill qilingan kanal darajasidan yomon) yoki CAC > $15.84, 7 kun | @kulgu_va_memlar ni $200 byudjet bilan qayta yoqish |
| R4 Google→Telegram | Telegram CAC > $15.84 14 kun davomida | $300 ni Google EXACT guruhlariga qaytarish |

## 6. Yetishmayotgan ma'lumot (missing_inputs)
- Google kanal darajasidagi ROAS yo'q (faqat blended 1.57x) — R1 dan keyingi ROAS effekti: unknown.
- Telegram buyurtmalar kanallar bo'yicha bo'linmagan — @toshkent_bozori aniq CAC: unknown.
- Meta CAPI deduplikatsiyasi yo'q (BRIEF) — konversiya ishonchliligi tekshirilmaguncha R2 o'lchovi taxminiy qoladi.

Manba: BRIEF.md + meta_performance.json + google_search_terms.json + telegram_campaigns.json · oyna: 30 kun · yozilgan: 2026-11-12
