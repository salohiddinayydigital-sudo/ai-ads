# Google Ads qidiruv so'rovlari auditi — google_ads_482_910_3301

**Holat:** QORALAMA (draft) — hisobga hech qanday o'zgartirish kiritilmagan. Bu faqat o'qish rejimidagi (read-only) dalil auditi.
**Hisob:** `google_ads_482_910_3301` · Valyuta: USD · Davr: oxirgi 30 kun (aniq sana oralig'i va timezone eksportda ko'rsatilmagan)
**Manba:** `examples/demo-brand/assets/google_search_terms.json` (Google Ads qidiruv so'rovlari eksporti) · 2026-11-12
**Qoida:** `rules/00-manba.md` — manbasiz fakt yo'q. Barcha raqamlar eksportdan; eksport raqamlaridan olingan arifmetika "hisoblangan" deb belgilangan.

---

## 1. Ma'lumot holati

**Bor (eksportda mavjud):**
- 30 kunlik umumiy sarf, klik, konversiya, o'rtacha CPC/CPA, CVR, ROAS;
- 3 ta yuqori niyatli konversiyali so'rov (sarf, klik, konversiya, CPA, CVR bilan);
- 4 ta bekorchi so'rov (0 konversiya, har biriga salbiy amal tavsiyasi bilan);
- waste xulosasi (umumiy bekorchi klik/sarf, ulush, oylik tejamlik, tavsiya matni).

**Yo'q (eksportda ko'rsatilmagan):**
- kampaniya va ad group darajasidagi bog'liqlik (qaysi so'rov qaysi guruhdan keldi) — ma'lumot yo'q;
- aniq sana oralig'i va timezone — ma'lumot yo'q;
- eksport matnida tilga olingan 45 ta salbiy kalit so'zning to'liq ro'yxati (faylda faqat 4 tasi bor) — ma'lumot yo'q;
- keyword darajasi, Quality Score, konversiya qiymati (revenue) taqsimoti, brend/umumiy ajratish — ma'lumot yo'q.

Natija: konversiya kuzatuvi (tracking) va strukturaviy boshqaruvlar bu eksport bo'yicha `unknown` — baholanmadi, taxmin qilinmadi.

## 2. Umumiy ko'rsatkichlar — MEASURED_ACCOUNT_DATA

| Ko'rsatkich | Qiymat |
|---|---|
| Umumiy sarf (30 kun) | $1,980.00 |
| Umumiy kliklar | 1,100 |
| O'rtacha CPC | $1.80 |
| Konversiyalar | 111 |
| O'rtacha CPA | $17.84 |
| Konversiya darajasi | 10.09% |
| ROAS | 1.57 (eksportda jamlanma sifatida; revenue taqsimoti eksportda yo'q) |

## 3. Bekorchi sarf — MEASURED_ACCOUNT_DATA

Eksport bo'yicha 4 ta so'rov 0 konversiya bilan sarf yaratgan; hammasi BROAD moslash orqali match bo'lgan:

| So'rov | Moslash (eksport) | Klik | Sarf | Konversiya | Eksportdagi amal |
|---|---|---|---|---|---|
| bepul kiyim andozasi pdf | BROAD | 85 | $153.00 | 0 | ADD_NEGATIVE_EXACT |
| ikkinchi qo'l kiyimlar optom | BROAD | 92 | $165.60 | 0 | ADD_NEGATIVE_PHRASE |
| kurtka qanday tikiladi video dars | BROAD | 54 | $97.20 | 0 | ADD_NEGATIVE_PHRASE |
| arzon kiyim tushda ko'rsa nima bo'ladi | BROAD | 35 | $63.00 | 0 | ADD_NEGATIVE_BROAD |
| **Jami** | — | **266** | **$478.80** | **0** | — |

**Hisoblangan (eksport raqamlaridan arifmetika):**
- $478.80 = umumiy sarfning 24.18% (eksportdagi `wasted_spend_share_pct` bilan mos);
- 266 klik × $1.80 o'rtacha CPC = $478.80 — eksport jamlanmasi bilan ichki mos;
- Yuqori niyatli 3 so'rov: $963.00 sarf (sarfning 48.6%), 88 konversiya (konversiyalarning 79.3%), CPA ≈ $10.94;
- Qolgan (ro'yxatga kiritilmagan) so'rovlar uchun qoldiq: $1,980.00 − $963.00 − $478.80 = $438.20 va 23 konversiya → CPA ≈ $19.05 (hisoblangan; eksport boshqa so'rovlarni sanab o'tmaydi).

## 4. Salbiy kalit so'zlar — qoralama ro'yxat (eksportdagi `action` maydonlari bo'yicha)

Hisobga qo'shish uchun TAYYOR EMAS — faqat qoralama. Har bir band eksportdagi amal maydonidan ko'chirilgan, hech biri to'qilmagan:

1. `bepul kiyim andozasi pdf` — **salbiy EXACT** (eksport: ADD_NEGATIVE_EXACT)
2. `ikkinchi qo'l kiyimlar optom` — **salbiy PHRASE** (eksport: ADD_NEGATIVE_PHRASE)
3. `kurtka qanday tikiladi video dars` — **salbiy PHRASE** (eksport: ADD_NEGATIVE_PHRASE)
4. `arzon kiyim tushda ko'rsa nima bo'ladi` — **salbiy BROAD** (eksport: ADD_NEGATIVE_BROAD)

**Overblocking tekshiruvi zarur — HEURISTIC_PRIOR_MODEL (uslub eslatmasi, eksportdagi fakt emas):**
- Salbiy PHRASE ushbu iborani o'z ichiga olgan barcha so'rovlarni to'sadi. Masalan, "optom" iborasi bilan bog'liq har qanday so'rov to'asiladi; eksportda bu brend uchun qonuniy optom xaridorlari mavjudligi haqida ma'lumot yo'q — bu qaror egasi bilan ko'rilishi shart.
- Salbiy BROAD eng keng to'siq — "tushda ko'rsa" kabi iboralarga tegishli so'rovlar bloklanadi; noqulay yon ta'sir bo'lsa, PHRASE ga kamaytirish mumkin (qaytariladigan o'zgarish).

**Eksportdagi tavsiya (MEASURED_ACCOUNT_DATA):** aniqlangan salbiy kalit so'zlarni account-level ro'yxatiga qo'shish. Eksportda "45 ta salbiy kalit so'z" deyilgan, lekin faylda faqat 4 tasi keltirilgan — qolgan 41 tasi eksportda yo'q (qarang: Ziddiyatlar).

## 5. Tejalgan mablag'ni yo'naltirish

**Eksport tavsiyasi (MEASURED_ACCOUNT_DATA):** tejalgan $478.80 (oyiga, 30 kunlik oyna bilan bir xil) High-Intent EXACT guruhlariga yo'naltirish.

**Yo'naltirish maqsadi — yuqori niyatli so'rovlar (MEASURED_ACCOUNT_DATA):**

| So'rov | Moslash (eksport) | Klik | Sarf | Konv. | CPA | CVR |
|---|---|---|---|---|---|---|
| erkaklar kiyimi toshkent sotib olish | EXACT | 210 | $378.00 | 38 | $9.95 | 18.1% |
| premium charm kurtka narxi | PHRASE | 145 | $261.00 | 24 | $10.88 | 16.5% |
| klassik erkaklar kostyumi do'koni | PHRASE | 180 | $324.00 | 26 | $12.46 | 14.4% |
| **Jami (hisoblangan)** | — | **535** | **$963.00** | **88** | **≈$10.94** | **≈16.4%** |

**Moliyaviy mantiq (hisoblangan):** yuqori niyatli CPA ≈ $10.94 — akkaunt o'rtachasi $17.84 dan ~39% past; bu so'rovlar sarfning 48.6% dan konversiyalarning 79.3% ini beradi. Shuning uchun eksport tavsiyasi bekorchi 24.18% sarfni shu guruhlarga qaytarishni asoslaydi.

**Illyustrativ stsenariy — HEURISTIC_PRIOR_MODEL (taxmin, kafolat emas):** agar yo'naltirilgan $478.80 yuqori niyatli guruhlarda hozirgi CPA (≈$10.94) bilan konversiya qilsa ≈ 44 qo'shimcha konversiya. Bu chiziqli masshtab va CPC o'zgarmasligini faraz qiladi — o'lchanadigan gipoteza sifatida keyingi 30 kunlik hisobotda tekshiriladi, reja sifatida emas.

## 6. Ziddiyatlar

1. Eksport tavsiyasida "45 ta aniqlangan salbiy kalit so'z" deyilgan, lekin eksportda faqat 4 tasi ro'yxatda — qolgan 41 tasi faylda yo'q. To'liq ro'yxat keltirilmaguncha salbiy ro'yxat to'liq emas.
2. Eksport tavsiyasi mablag'ni "High-Intent EXACT guruhlariga" yo'naltirishni so'raydi, lekin ro'yxatdagi 3 ta yuqori niyatli so'rovdan faqat 1 tasi EXACT, 2 tasi PHRASE moslashda; so'rovlar qaysi guruhlarga tegishliligi eksportda ko'rsatilmagan.

## 7. Yetishmayotgan ma'lumotlar (missing_inputs)

- Kampaniya/ad group darajasidagi bog'lanish va guruh nomlari;
- Aniq sana oralig'i, timezone;
- 45 ta salbiy kalit so'zning to'liq ro'yxati;
- Konversiya qiymati (revenue) taqsimoti va ROAS tarkibi;
- Keyword darajasi, Quality Score, konversiya kuzatuv holati (tracking boshqaruvlari) — eksport bo'yicha baholanmadi.

## 8. Mutatsiya chegarasi (Spend-Guard)

Salbiy kalit so'zlarni hisobga qo'shish — live mutatsiya; faqat egasining aniq tasdiqlidan keyin bajariladi. Bu audit faqat qoralama. Reversibel qadam: account-level salbiy ro'yxatga qo'shish (olib tashlash orqali rollback mumkin). O'lchash oynasi: keyingi 30 kunlik qidiruv so'rovlari hisobotida bekorchi sarf ulushi va CPA.

## 9. Nativa (output contract)

```json
{
  "status": "ok",
  "platform": "google",
  "account_id": "google_ads_482_910_3301",
  "window_days": 30,
  "currency": "USD",
  "findings": [
    {
      "id": "F1",
      "control_intent": "G16 - material irrelevant search-term spend",
      "evidence": "MEASURED_ACCOUNT_DATA",
      "observation": "4 ta bekorchi so'rov: 266 klik, $478.80 sarf, 0 konversiya - umumiy sarfning 24.18%",
      "severity": "high",
      "confidence": "high",
      "recommendation": "Eksport amal maydonlari bo'yicha 4 salbiy kalit so'z qoralamasi; qo'llashdan oldin overblocking ko'rivi va egasining tasdiqligi"
    },
    {
      "id": "F2",
      "control_intent": "G14 - negative-keyword governance",
      "evidence": "MEASURED_ACCOUNT_DATA",
      "observation": "Eksport tavsiyasi: salbiylar account-level ro'yxatga qo'shilsin; eksportda 45 ta salbiy deyilgan, faqat 4 tasi keltirilgan",
      "severity": "medium",
      "confidence": "high",
      "recommendation": "To'liq 45 ta ro'yxatni so'rash; qo'shish faqat mutatsiya gate'dan keyin"
    },
    {
      "id": "F3",
      "control_intent": "G17 - broad-match control",
      "evidence": "MEASURED_ACCOUNT_DATA",
      "observation": "Barcha bekorchi so'rovlar BROAD moslash orqali match bo'lgan",
      "severity": "medium",
      "confidence": "high",
      "recommendation": "Broad match doirasi va salbiylar bilan qoplanishini keyingi 30 kunlik hisobotda kuzatish"
    },
    {
      "id": "F4",
      "control_intent": "G08 - budget allocation matches priority",
      "evidence": "MEASURED_ACCOUNT_DATA + hisoblangan",
      "observation": "Yuqori niyatli 3 so'rov: $963.00 sarf (48.6%), 88 konversiya (79.3%), CPA ~$10.94 vs akkaunt CPA $17.84",
      "severity": "medium",
      "confidence": "medium",
      "recommendation": "Tejalgan $478.80 ni High-Intent guruhlarga yo'naltirish (eksport tavsiyasi); stsenariy ~44 qo'shimcha konversiya - HEURISTIC_PRIOR_MODEL, tekshiriladigan gipoteza"
    }
  ],
  "contradictions": [
    "Eksportda 45 ta salbiy kalit so'z aytilgan, faylda faqat 4 tasi bor",
    "Tavsiya 'High-Intent EXACT guruhlari' deydi, lekin yuqori niyatli ro'yxatda 2/3 so'rov PHRASE; guruh bog'lanishi eksportda yo'q"
  ],
  "missing_inputs": [
    "kampaniya/ad group bog'lanishi",
    "aniq sana oralig'i va timezone",
    "to'liq 45 ta salbiy ro'yxat",
    "revenue/ROAS taqsimoti",
    "tracking va Quality Score holati"
  ]
}
```

---

Manba: `examples/demo-brand/assets/google_search_terms.json` (Google Ads qidiruv so'rovlari eksporti, google_ads_482_910_3301) · 30 kunlik oyna · 2026-11-12
