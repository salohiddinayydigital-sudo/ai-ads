<!-- v8.2 Charter v2: data-analyst metodologiyasi (yangi). Ref: agents/data-analyst.md, rules/00-manba.md -->

# Data Analyst Playbook — eksportdan qarorgacha

> Maqsad: har raqam kod bilan hisoblanadi, har xulosa tanlama hajmi va atributsiya oynasi bilan cheklanadi. Raqam "xayolda" hisoblanmaydi.

## 1. Kirish va `metrics.v1` validatsiyasi

1. Xom fayl (`clients/<slug>/data/raw/`) → `python3 tools/normalize.py` → `metrics.v1` (`schemas/metrics.v1.json`).
2. Tekshir: ustunlar (spend, impressions, clicks, results, revenue), valyuta, sana oralig'i, takroriy qatorlar, bo'sh/nol maxrajlar, timezone.
3. Validatsiya xatosi bo'lsa — tahlil to'xtaydi, `needs_input` + xato ro'yxati. "Taxminiy to'ldirish" yo'q.

## 2. Tanlama hajmi va statistik ishonchlilik darvozasi

| Qaror | Minimal dalil (`HEURISTIC_PRIOR_MODEL`) |
|---|---|
| Kreativ/ad g'olibini e'lon qilish | Har variantda >= 50 konversiya **yoki** >= 2× maqsadli CPA sarf + 7 kun; aks holda `inconclusive` |
| CTR/hook rate farqi | Har variantda >= 1 000 impression; farq ishonch oralig'idan tashqarida |
| Konversiya darajasi farqi | Ikki proporsiya z-testi (`tools/experiments.py`), p < 0.05 va oldindan belgilangan MDE |
| Trend (pasayish/o'sish) | >= 3 ta solishtiriladigan davr; bitta kunlik sakrash trend emas |

Erta to'xtatish (peeking) taqiqlanadi: test muddati va to'xtash qoidasi oldindan yoziladi.

## 3. Atributsiya oynasi va solishtirish

- Davrlar bir xil oyna (masalan, 7-day click / 1-day view) va bir xil hisobot vaqtida (impression vs conversion time) solishtiriladi.
- Platforma natijasi ↔ CRM/biznes daromadi (MER) alohida ustunda; farq > 20% bo'lsa — `tracking-specialist` ga marshrut.
- Kechikkan konversiyalar: oxirgi 1–3 kun "pishmagan" deb belgilanadi.

## 4. Anomaliya triage (ketma-ketlik)

1. **Tracking uzilishi?** Natija 0 yoki keskin tushdi, lekin klik/sessiya bor → tracking.
2. **Pacing?** Byudjet o'zgargan, learning qayta boshlangan, auksion (CPM) sakragan.
3. **Kreativ charchog'i?** Frequency ↑, CTR/hook rate ↓ — `creative-strategist`.
4. **Konversiya (CVR) muammosi?** CTR sog'lom, CVR tushgan — landing/Direct/offer.
5. **Haqiqiy bozor o'zgarishi** — faqat yuqoridagilar istisno qilingandan keyin.

## 5. Manba ajratish

| Yorliq | Qachon |
|---|---|
| `MEASURED_ACCOUNT_DATA` | Asbob tomonidan eksport/MCP snapshotdan hisoblangan |
| `USER_PROVIDED` | Foydalanuvchi aytgan, tekshirilmagan raqam |
| `HEURISTIC_PRIOR_MODEL` | Benchmark, chegara, ekspert qoidasi |
| `ASSUMPTION` | Ochiq taxmin (masalan, marja 30%) |

## 6. Asboblar

`tools/normalize.py` · `tools/ad-export-analyzer.py --metrics` · `tools/pulse.py` · `tools/experiments.py` · `tools/creative-analytics.py` · `tools/report-html.py` · MCP: `tyrion_breakdown_effect`, `tyrion_media_calculator`.
