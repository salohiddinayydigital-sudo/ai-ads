# Meta Pixel EMQ oshirish rejasi: 6.2/10 → match sifatini oshirish

Manba: `examples/demo-brand/assets/tracking_health.json` · 2026-11-12 + umumiy CAPI bilimi (Meta Conversions API normalizatsiya qoidalari).

## Hozirgi holat (manba fayldan)

- EMQ: **6.2/10** — pixel_id `84729103847192`, status ACTIVE, brauzer hodisalari yonilgan.
- CAPI: `gateway.apexstore.uz`, ACTIVE, `hashing_compliance: true` — hashlash mavjud, demak muammo ko'proq **normalizatsiya sifati** va **match kalitlar qamrovi**da bo'lishi mumkin (taxmin, fakt emas).
- `event_id_deduplication: false` (~15% double counting) — EMQga bevosita aloqasi yo'q, alohida kritik tuzatish bo'lib qoladi.

## Reja: maydon → normallashtirish → SHA-256 → EMQga ta'siri

| Maydon | CAPI kodi | SHA-256 oldidan normallashtirish | EMQga ta'siri |
|---|---|---|---|
| Telefon | `ph` | Faqat raqamlar, davlat kodi bilan; `+`, probel, defis, qavs olib tashlanadi (UZ misol: `998901234567`) | EMQning eng kuchli signalidan biri; format noto'g'ri bo'lsa match umuman o'tmaydi |
| Email | `em` | Bosh/oxir probel olib tashlanadi, barcha belgilar kichik harfga | Asosiy match kaliti; bir xil mijozning har xil yozilishi emailni yo'q qiladi |
| Ism | `fn` | Kichik harflar, raqam/simvol/ponktuatsiya olib tashlanadi, trim | Match aniqligini oshiradi; mustaqil kuchi o'rtacha |
| Familiya | `ln` | `fn` bilan bir xil qoida | `fn` bilan birga match probasini mustahkamlaydi |
| Shahar | `ct` | Kichik harflar, faqat `a-z` harflar, probel/simvol yo'q (`tashkent`) | Yordamchi signal: yolg'iz kuchi kichik, boshqa maydonlar bilan birga hisobga qo'shiladi |
| Viloyat | `st` | Kichik harflar, standart qisqa format | Yordamchi signal |
| Indeks | `zp` | Trim, kichik harflar | Yordamchi signal |
| Davlat | `country` | ISO 3166-1 alpha-2, kichik (`uz`) | Barqaror yordamchi signal |
| Tug'ilgan sana | `db` | `YYYYMMDD` | Kuchli yordamchi; bor bo'lsa match aniqligi sezilarli oshadi |
| Jins | `ge` | `f` yoki `m` (kichik) | Yordamchi signal |
| Tashqi ID | `external_id` | CRM/bot user ID, hashlangan holda | Server-side match uchun muhim — brauzer cookiesiz kirsa ham mijozni bog'laydi |
| Cookie qiymatlari | `fbp`, `fbc` | `_fbp`/`_fbc` qiymati hashlanmaydi, xom yuboriladi | Brauzer-matchning asosi; yetishmasa EMQ tushadi |

## Umumiy bajarilish qoidalari

- PII maydonlar (`em`, `ph`, `fn`, `ln`, `ct`, `st`, `zp`, `country`, `db`, `ge`, `external_id`) **avval normallashtiriladi, keyin SHA-256** bilan hashlanadi (kichik harfli hex string); xom PII tizimda saqlanmaydi.
- `fbp`, `fbc`, `client_ip`, `user_agent` hashlanmaydi.
- Normalizatsiyani yagona server funksiyasi bajarsin — pixel va CAPI bir xil qiymatni bir xil hashlasin; ikki tomonda har xil hash = match yo'q.

## Ochiq chegara (00-manba bo'yicha)

- Meta maydonlar orasidagi aniq ball vaznini oshkor qilmaydi: har maydon EMQga necha punkt qo'shadi — **ma'lumot yo'q**. Shuning uchun prognoz ball kiritilmadi va manbadagi 6.2 hisobiga o'zgartirish kiritilmadi.
- Umumiy tamoyil: bo'sh maydon < noto'g'ri formatdagi maydon < to'g'ri normallashtirilgan maydon; `em`, `ph`, `external_id` + `fbp`/`fbc` EMQga eng katta ta'sir qiluvchi guruh.

## Manba

- `examples/demo-brand/assets/tracking_health.json` — EMQ 6.2, pixel/CAPI statuslari, `hashing_compliance`, dedup holati (2026-11-12).
- Meta Conversions API dokumentatsiyasi (umumiy bilim) — normalizatsiya qoidalari va match kalitlari ro'yxati.
