# Google Ads qidiruv so'rovlari auditi — google_ads_482_910_3301

- **Manba:** `examples/demo-brand/assets/google_search_terms.json` · 30 kunlik oyna · USD
- **Sana:** 2026-11-12 · **Holat:** faqat tahlil; hisobga o'zgartirish kiritilmagan, barcha tavsiyalar draft.

## 1. Ma'lumot holati

- **Bor (manba fayldan):** umumiy sarf/klik/CPC/konversiya/CPA/CVR/ROAS; 3 ta yuqori-intent so'rov; 4 ta bekorchi so'rov; salbiy so'zlar xulosasi.
- **Yo'q — `unknown`:** kampaniya va ad-group tuzilmasi; konversiya kuzatuv sozlamalari; ROAS (1.57) hisoblash asosi; geografiya/qurilma kesimi; 45 ta salbiy so'zning to'liq ro'yxati (faylda faqat 4 namuna qatori bor); oyna tugash sanasi.

## 2. Kuzatuvlar (faktlar — manba fayldan)

Umumiy: $1,980.00 sarf, 1,100 klik, o'rtacha CPC $1.80, 111 konversiya, o'rtacha CPA $17.84, CVR 10.09%, ROAS 1.57.

Yuqori-intent, konversiyali so'rovlar:

| So'rov | Match | Klik | Sarf | Konv. | CPA | CVR |
|---|---|---|---|---|---|---|
| erkaklar kiyimi toshkent sotib olish | EXACT | 210 | $378.00 | 38 | $9.95 | 18.1% |
| premium charm kurtka narxi | PHRASE | 145 | $261.00 | 24 | $10.88 | 16.5% |
| klassik erkaklar kostyumi do'koni | PHRASE | 180 | $324.00 | 26 | $12.46 | 14.4% |

Bekorchi so'rovlar (0 konversiya):

| So'rov | Match | Klik | Sarf | Manba tavsiyasi |
|---|---|---|---|---|
| bepul kiyim andozasi pdf | BROAD | 85 | $153.00 | ADD_NEGATIVE_EXACT |
| ikkinchi qo'l kiyimlar optom | BROAD | 92 | $165.60 | ADD_NEGATIVE_PHRASE |
| kurtka qanday tikiladi video dars | BROAD | 54 | $97.20 | ADD_NEGATIVE_PHRASE |
| arzon kiyim tushda ko'rsa nima bo'ladi | BROAD | 35 | $63.00 | ADD_NEGATIVE_BROAD |

## 3. Tashxis (nazorat belgilari bo'yicha)

- **G16 — material bekorchi sarf: `fail`.** $478.80 (266 klik, 0 konversiya) umumiy sarfning 24.18% — manba `negative_waste_summary` maydoni.
- **G17 — broad-match nazorati: `fail`.** Barcha bekorchi so'rovlar BROAD match ostida; yuqori-intent so'rovlar EXACT/PHRASE.
- **G14/G15 — salbiy so'zlar boshqaruvi: `fail` (tavsiya mavjud, amalga oshirilmagan).** Manba 45 ta salbiy so'zni account-level ro'yxatga qo'shishni tavsiya qiladi; sarf bu so'rovlarga davom etgan.
- **G-WS1 — konversiyasiz so'rov tekshiruvi:** 4 ta BROAD so'rov 266 klikkacha konversiyasiz ishlagan. G18 (close variant) va G19 (visibility) uchun dalil yo'q — `unknown`.
- **Intent chegarasi (hisob-kitob):** yuqori-intent CPA $9.95–$12.46, blended $10.94 ($963.00 / 88 konv.) — akkaunt o'rtacha CPA $17.84 dan ~30–44% past; bekorchi 4 turkum intent: bepul/hozirlik, ikkinchi qo'l/optom, o'rganish kontenti, tush talqini.

## 4. Salbiy kalit so'zlar ro'yxati (manba tavsiyasiga ko'ra)

1. `bepul kiyim andozasi pdf` — negative EXACT
2. `ikkinchi qo'l kiyimlar optom` — negative PHRASE
3. `kurtka qanday tikiladi video dars` — negative PHRASE
4. `arzon kiyim tushda ko'rsa nima bo'ladi` — negative BROAD

Qolgan 41 so'z (45 dan) manba faylda yo'q — to'liq ro'yxat uchun export kerak (`missing_inputs`).

## 5. Tejalgan mablag'ni yo'naltirish

Manba tavsiyasi: $478.80 oylik tejalgan mablag' High-Intent EXACT guruhlariga yo'naltiriladi. Shartli hisob-kitob (taxminiy proyeksiya, fakt emas): mablag' eng yaxshi EXACT CPA ($9.95) bilan ishlasa ~48 qo'shimcha konversiya potensiali ($478.80 / $9.95). O'lchov oynasi va rollback sharti manbada ko'rsatilmagan.

## 6. Chegaralar

- Hisobga o'zgartirish kiritilmagan; har qanday amal Spend-Guard mutation gate tasdiqlanmaguncha draft qoladi.
- Barcha raqamlar yuqoridagi manba fayldan; tashqi benchmark ko'chirilmagan (rules/00-manba).
