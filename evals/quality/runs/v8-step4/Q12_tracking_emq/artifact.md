# Meta Pixel EMQ 6.2/10 — SHA-256 normallashtirish va hashlash rejasi (Q12)

**Rol:** tracking-specialist (Meta CAPI v26.0 / Pixel) · **Sana:** 2026-11-12
**Manba:** `examples/demo-brand/assets/tracking_health.json` · 2026-11-12
**Cheklov:** faqat manba fayli ma'lumotlari + umumiy CAPI bilimi. EMQ hisobiga o'zgartirish kiritilmadi — 6.2 qiymati o'zgarmagan holatda qoladi, yangi raqam prognozi yozilmaydi.

## 1. Holat — MEASURED_ACCOUNT_DATA (manba fayldan)

- Meta Pixel: o'rnatilgan, `ACTIVE`, `pixel_id: 84729103847192`, `emq_score: 6.2`, brauser eventlari yonib (`browser_event_firing: true`).
- Meta CAPI: o'rnatilgan, `ACTIVE`, endpoint `gateway.apexstore.uz`, `hashing_compliance: true`, `event_id_deduplication: false`.
- Manbada yozilgan critical risk: Pixel va CAPI ikkalasi ham xaridni yubormoqda, lekin `event_id` bir xil emas — hisobotlarda ~15% buyurtmalar ikki marta qayd etilmoqda (double counting).
- Google Enhanced Conversions (`ACTIVE`, Purchase) va Telegram bot telemetry ham faylda bor, lekin EMQ rejasiga to'g'ridan-to'g'ri kirmaydi.

## 2. Ma'lumot yo'q (noma'lum — taxmin yozilmaydi)

- Hozir qaysi customer information maydonlari (`em`, `ph`, `fn`, `ln`, `ct`, `st`, `zp`, `country`, `external_id`, `fbp`, `fbc`) yuborilayotgani — manba faylda yo'q.
- EMQ 6.2 ning maydonlar bo'yicha yemirilishi (breakdown/coverage) — ma'lumot yo'q. 1-qadamda Events Manager EMQ panelidan olinadi.
- Shu sababli reja maydonlar bo'yicha to'liq ro'yxat sifatida tuziladi, "qaysi maydon yetishmayapti" degan da'vo qilinmaydi.

## 3. Umumiy qoida (umumiy CAPI bilimi)

Har bir mijoz maydoni uchun tartib: **normalizatsiya → SHA-256 (UTF-8, kichik harflarda hex) → faqat hash yuboriladi**. Xom PII hech qanday log, payload yoki kanalga yozilmaydi (charter: raw unhashed PII saqlanmaydi). Hashlash **normalizatsiyadan keyin** bajariladi: agar bir xil mijoz har safar turli ko'rinishda (katta/kichik harf, probel, `+998`/`998`) hashlansa, hashlar mos kelmaydi va match sifati pasayadi — EMQ o'smaydi.

## 4. Maydonlar bo'yicha normalizatsiya va EMQ ta'siri

| CAPI maydon | Normalizatsiya qoidalari | Misol (ilustrativ) | EMQ ta'siri (yo'nalish) |
|---|---|---|---|
| `em` (email) | Bosh/oxir probel olib tashlanadi, kichik harflarga o'tkaziladi | `Alisher@Example.uz` → `alisher@example.uz` → SHA-256: `6c9b072f...f8790e4d` | **Yuqori** — eng kuchli shaxsiy match kalitlaridan biri |
| `ph` (telefon) | `+`, probel, chiziq, qavslar olib tashlanadi; mamlakat kodi bilan faqat raqamlar qoladi | `+998 90 123 45 67` → `998901234567` → SHA-256: `172443bc...82054f2d3` | **Yuqori** — `em` bilan bir qatordagi asosiy match kaliti |
| `fn` (ism) | Bosh/oxir probel olib tashlanadi, kichik harflarga | `Alisher` → `alisher` → SHA-256: `5d1dacd9...5e80727243` | **O'rta–yuqori** — `em`/`ph` bilan birga ishlaydi |
| `ln` (familiya) | Bosh/oxir probel olib tashlanadi, kichik harflarga | `Karimov` → `karimov` | **O'rta–yuqori** — `fn` bilan birga |
| `ct` (shahar) | Probel, tire va tinish belgilari olib tashlanadi, kichik harflarga | `Toshkent` → `toshkent` | **Past–o'rta** — manzil klasterini to'ldiradi |
| `st` (viloyat) | Kichik harflarga, probel normallashtiriladi | `Toshkent viloyati` → `toshkent viloyati` | **Past** — qo'shimcha match signali |
| `zp` (pochta indeksi) | Probel olib tashlanadi, kichik harflarga | `100000` → `100000` | **Past–o'rta** |
| `country` | ISO 3166-1 alpha-2, kichik harflarda, 2 belgi | `UZ` → `uz` | **Kontekst** — manzil maydonlari klasteri uchun shart |
| `external_id` | CRM/buyurtma ID izchil formatda yuboriladi (hashlash tavsiya etiladi) | `ORD-10231` → izchil, har eventda bir xil | **O'rta** — CAPI va Pixel identifikatsiyasini bog'laydi, takroriy mijozni barqaror taniydi |
| `fbp`, `fbc` | Hashlanmaydi, as-is yuboriladi (brauser identifikatorlari) | `_fbp=...`, `_fbc=...` | **Brauser match** — Pixel/CAPI mosligi uchun |
| `client_ip_address`, `client_user_agent` | Hashlanmaydi, as-is (server eventida yuboriladi) | — | **Kontekst** — server eventlarida match sifatini oshiradi |

**Evidence belgisi:** jadvaldagi "EMQ ta'siri" ustuni umumiy CAPI bilimi (`HEURISTIC_PRIOR_MODEL`) — yo'nalish sifatida; har bir maydonga aniq ochko qiymati Meta tomonidan ochiq e'lon qilinmaydi, o'lchov Events Manager EMQ coverage panelida ko'rinadi. Manba faylidagi faktlar esa `MEASURED_ACCOUNT_DATA`.

## 5. Bajarish tartibi

1. **O'lchov:** Events Manager → Pixel `84729103847192` → EMQ coverage jadvali olinadi (qaysi maydon bo'sh yoki past — hozir manbada yo'q).
2. **Normalizatsiya:** yuqoridagi qoidalar server tomonda, CAPI endpoint `gateway.apexstore.uz` dan chiqishdan oldin birlashtiriladi (bir joyda, takrorlanmaydigan funksiya).
3. **Hashlash:** SHA-256 (UTF-8, kichik harf hex). Tekshiruv: hash uzunligi 64 hex belgi, kichik harf; xom PII payload'da ko'rinmaydi.
4. **To'ldirish:** har bir event (Purchase va b.) uchun mavjud bo'lgan maydonlar yuboriladi — bo'sh maydon yuborilmaydi, soxta qiymat ham yozilmaydi.
5. **Test:** Test Events'da payload ko'rib chiqiladi, keyin 7–14 kun o'zgartirishdan oldingi va keyingi EMQ o'z akkaunt tarixi bilan solishtiriladi (benchmark ko'chirilmaydi — [[00-manba]] 4-qoida).

## 6. EMQ'dan tashqari, manbada belgilangan alohida tuzatish

- `event_id_deduplication: false` → Pixel va CAPI'da **bir xil `event_id` + `event_name`** yuborish joriy etilishi kerak (manba: critical_risk, ~15% double counting). Bu EMQ ko'rsatkichi bilan bog'liq emas — alohida dedup tuzatish ro'yxati sifatida chiqariladi, hisobot aniqligini tiklaydi.
- Manba faylidagi `hashing_compliance: true` shuni ko'rsatadiki, hashlash siyosati allaqachon bajarilgan — shu rejaning asosiy mohiyati hashlashdan **oldingi normalizatsiya qoidalarini bir xillashtirish** va maydonlar coverage'sini kengaytirishdir.

---

**Manba satri:** Manba: `examples/demo-brand/assets/tracking_health.json` · 2026-11-12 · umumiy CAPI bilimi (Meta CAPI v26.0 dokumentatsiyasi amaliyoti) sifatida belgilangan qatorlar `HEURISTIC_PRIOR_MODEL`.
