# Apex E-Commerce — Jami oylik sarf va Blended ROAS (qisqa hisobot)

- **Sana:** 2026-11-12
- **Valyuta:** USD (barcha 3 manbada bir xil)
- **Oyna:** 30 kun (barcha 3 manbada `window_days: 30`)
- **Dalil darajasi:** MEASURED_ACCOUNT_DATA (hisob eksport fayllari)

## Manbalar jadvali

| Kanal | Sarf (USD) | Daromad (USD) | ROAS | Manba fayl |
|---|---|---|---|---|
| Meta Ads | 3480.50 | 6787.00 | 1.95 | `examples/demo-brand/assets/meta_performance.json` (`summary.total_spend`, `summary.total_revenue`, `summary.roas`; `account_id: act_88291048201`) |
| Google Ads | 1980.00 | 3108.60 *(hisoblangan)* | 1.57 | `examples/demo-brand/assets/google_search_terms.json` (`summary.total_spend`, `summary.roas`; `account_id: google_ads_482_910_3301`) |
| Telegram Ads | 1200.00 | 3180.00 | 2.65 | `examples/demo-brand/assets/telegram_campaigns.json` (`summary.total_spend`, `summary.revenue`, `summary.roas`; `account_id: tg_ads_fragment_8819`) |
| **Jami** | **6660.50** | **13075.60** | **1.96 (blended)** | — |

## Hisob (qadam-baqadam)

1. **Jami oylik sarf** = 3480.50 (Meta) + 1980.00 (Google) + 1200.00 (Telegram) = **6660.50 USD**
2. **Google daromadi** = sarf x roas = 1980.00 x 1.57 = **3108.60 USD** — faylda daromad raqami yo'q, faqat `roas: 1.57` bor; shuning uchun topshiriqqa muvofiq sarfdan hisoblangan qiymat.
3. **Jami daromad** = 6787.00 (Meta, fayldan) + 3108.60 (Google, hisoblangan) + 3180.00 (Telegram, fayldan) = **13075.60 USD**
4. **Blended ROAS** = 13075.60 / 6660.50 = **1.96** (aniq: 1.9632)

## Izohlar (kuzatuv / hisob ajratilgan holda)

- Meta va Telegram daromadlari to'g'ridan-to'g'ri fayllardan olingan; Google daromadi o'lchangan roas (1.57) asosida chiqarilgan hisoblangan qiymat, alohida belgilangan.
- Barcha 3 manbada valyuta USD va 30 kunlik oyna bir xil, shuning uchun yig'indilash to'g'ri (window/currency ziddiyati yo'q).
- Kuzatuv: eng yuqori ROAS Telegram'da (2.65), eng pasti Google'da (1.57) — barchasi `summary.roas` maydonlaridan, o'zgartirish tavsiya qilinmaydi (tahlil chegarasi).

Manba: examples/demo-brand/assets/meta_performance.json · examples/demo-brand/assets/google_search_terms.json · examples/demo-brand/assets/telegram_campaigns.json · 2026-11-12 (window_days: 30)
