# Q09 — Apex E-Commerce: jami oylik sarf va blended ROAS

Hisobot sanasi: 2026-11-12. Ma'lumot oynasi: 30 kun (uchala faylda `window_days: 30`).

## Manbalar (rules/00-manba.md bo'yicha)

| Fayl | Manba tavsifi |
|------|----------------|
| examples/demo-brand/assets/meta_performance.json | Meta Ads eksport, act_88291048201, USD |
| examples/demo-brand/assets/google_search_terms.json | Google Ads eksport, google_ads_482_910_3301, USD |
| examples/demo-brand/assets/telegram_campaigns.json | Telegram Ads fragment, tg_ads_fragment_8819, USD |

## 1. Jami oylik sarf

| Platforma | Sarf (USD) | Manba (fayl → maydon) |
|-----------|-----------|------------------------|
| Meta | 3480.50 | meta_performance.json → summary.total_spend |
| Google | 1980.00 | google_search_terms.json → summary.total_spend |
| Telegram | 1200.00 | telegram_campaigns.json → summary.total_spend |
| **Jami** | **6660.50** | yig'indi |

Sarf ulushi: Meta 52.3%, Google 29.7%, Telegram 18.0% (6660.50 ga nisbatan).

## 2. Daromad va blended ROAS

| Platforma | Daromad (USD) | ROAS | Hisob usuli va manbasi |
|-----------|---------------|------|------------------------|
| Meta | 6787.00 | 1.95 | fayldan: meta_performance.json → summary.total_revenue, summary.roas |
| Google | 3108.60 | 1.57 | hisoblangan: 1980.00 sarf x 1.57 roas; roas manbasi google_search_terms.json → summary.roas |
| Telegram | 3180.00 | 2.65 | fayldan: telegram_campaigns.json → summary.revenue, summary.roas |
| **Jami** | **13075.60** | **1.96** | blended = 13075.60 / 6660.50 |

Blended ROAS = umumiy daromad / umumiy sarf = 13075.60 / 6660.50 = 1.963 ≈ **1.96**.

## 3. Qisqacha xulosa (faqat manbadagi faktlar)

1. Jami oylik sarf $6,660.50 uch platforma bo'yicha; eng katta ulush Meta'da ($3,480.50).
2. Blended ROAS 1.96. Eng yuqori platforma ROAS — Telegram (2.65), eng pasti — Google (1.57).
3. Google'da fayl bo'yicha sarfning 24.18% ($478.80, 266 klik) natijasiz search term'larga ketgan; tavsiya: negative kalit so'zlar qo'shish va tejalmi High-Intent EXACT guruhlarga yo'naltirish (google_search_terms.json → negative_waste_summary).
4. Telegram'da @kulgu_va_memlar kanali KILL_CANDIDATE ($200 sarf, CPL 3.40), @toshkent_bozori esa WINNER_SCALE ($450 sarf, CPL 1.25) (telegram_campaigns.json → channels_performance).
5. Meta'da charchash belgilari: BOF kampaniyasida FTIR 54.2%, frequency 3.12, fatigue_flag: true (meta_performance.json → cmp_01); ASC kampaniyasi ijobiy (ROAS 2.15, fatigue_flag: false).

## 4. Cheklovlar va yetishmayotgan ma'lumot

- Google daromadi faylda alohida maydon sifatida yo'q; vazifa bo'yicha roas (1.57) x sarf (1980.00) orqali hisoblandi: $3,108.60. Bu taxmin emas, aniq hisob.
- Marja/COGS, buypotsional aylanma va qaytarimlar fayllarda yo'q → break-even ROAS hisoblanmadi ("ma'lumot yo'q").
- Fayllarda aniq sana yozilmagan; 30 kunlik oyna fayl maydonidan olindi.

Manba: meta_performance.json, google_search_terms.json, telegram_campaigns.json (demo-brand eksportlar) · 30 kunlik oyna · hisobot 2026-11-12
