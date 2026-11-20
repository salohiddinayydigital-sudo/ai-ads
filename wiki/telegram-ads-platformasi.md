---
name: telegram-ads-platformasi
description: "Telegram Ads rasmiy platformasi (ads.telegram.org / Fragment), kanallarni tanlash, 160 belgili matn andozalari, bot voronkasi va server-side konversiya o'lchash tizimi"
tags: [telegram, ads, platforma, voronka, marketing]
source: "Telegram Ads official documentation & local operator playbooks"
source_status: unverified
updated: 2026-11-19
---

# Telegram Ads rasmiy platformasi va konversiya voronkasi

> Bog'lanishlar: [[telegram-voronka-va-email-minimum]] · [[30-ozbekiston-konteksti]] · [[voronka-metrikalari]] · [[blended-roas-net-cash]]

Telegram Ads — O'zbekiston va MDH bozorida eng yuqori diqqat va o'qilish darajasiga ega bo'lgan rasmiy reklama platformasi hisoblanadi.

---

## 1. Platforma xususiyatlari va kirish

- **Boshqaruv:** `ads.telegram.org` yoki `Fragment` (TON / Telegram Stars orqali to'g'ridan-to'g'ri to'lov).
- **Format:** Matnli e'lon (maksimal 160 ta belgi).
- **Harakatga chaqiruv (CTA):** Tugma ko'rinishida (`Kanalga o'tish`, `Botni ochish`, `Postni ko'rish` yoki tashqi veb-sayt havolasi).
- **Auksion:** CPM (har 1,000 ko'rsatish uchun narx) modeli.

---

## 2. Targetlash turlari va kanal tanlash

Telegram Ads'da ikkita asosiy targetlash usuli mavjud:

1. **Aniq kanallar bo'yicha (Channel-Specific Targeting) — TAVSIYA ETILADI:**
   - Reklama faqat qo'lda tanlangan, tasdiqlangan kanallarda chiqadi.
   - Tanlov mezoni: obunachilar $\ge 1,000$, Engagement Rate on Reach (ERR) $\ge 15\%$, auditoriya mavzusi mahsulotga to'g'ridan-to'g'ri mos. *(manba ko'rsatilmagan — `unverified`; ads.telegram.org dan tasdiqlang)*
   - Soxta (nakrutka) qilingan yoki nofaol kanallar darhol chiqarib tashlanadi (Negative Channels).
2. **Keng mavzular bo'yicha (Topic/Category Targeting):**
   - Moliya, IT, Ko'chmas mulk, Ta'lim kabi sohalar bo'yicha.
   - Ehtiyotkorlik: Keng mavzular byudjetni tez yeydi, konversiya aniq kanallarga nisbatan 2-3 barobar past bo'lishi mumkin.

---

## 3. 160 Belgili Sotuvchi Matn Formulalari

Telegram moderatsiyasi juda qat'iy:
- **Taqiqlanadi:** ALL CAPS so'zlar, bittadan ortiq emoji, yolg'on va'dalar ("100% kafolat", "$10,000 daromad"), agressiv clickbait.
- **Ruxsat etiladi:** Aniq fakt, xolis taklif, muammo va yechim.

### Ishlaydigan 3 ta formula:
1. **Muammo $\to$ Aniq Yechim:**
   `Qimmat reklamadan charchadingizmi? Telegram Ads orqali lid narxini 2x arzonlashtiring. Bepul qo'llanmani oling:`
2. **Keys / Ijtimoiy dalil:**
   `Toshkentdagi 40+ kompaniya Telegram bot orqali qanday sotuv qildi? Amaliy keysni botdan o'qing:`
3. **Auditoriyani chaqirish:**
   `Kompaniya rahbarlari uchun: biznes jarayonlarini avtomatlashtirish bo'yicha 5 ta tayyor shablon. Yuklab oling:`

---

## 4. Konversiya va Bot Voronkasi

Telegram'da brauzer piksellari ishlamagani uchun voronka bot orqali o'lchanadi:

```
Telegram Reklama (160 belgi)
        ↓
Bot Deep Link (t.me/BrandBot?start=tgads_reklama1)
        ↓
Avtomatik xush kelibsiz xabari (< 10 soniyada) + Lead Magnit
        ↓
3-5 kunlik ishonch kontenti (avtomatik xabarlar)
        ↓
Menejer bilan shaxsiy muloqot (DM) $\to$ Sotuv
```

**Telemetriya:**
Bot backendidan CRM tizimiga (AmoCRM, Bitrix24) har bir `/start`, lead magnit yuklash va kontakt qoldirish hodisasi **webhook** orqali uzatiladi. Natijada har bir Telegram kanalidan tushgan **sof tushum (Net Revenue)** aniq o'lchanadi.

---

## 2026 yangilanishlari (tekshiruv: 2026-11-19)

**Rasmiy manbadan o'qildi (`verified`)** — ads.telegram.org bosh sahifasi, `/tos`, `/guidelines` (2026-11-19):
- Reklama matni 160 belgigacha, Telegram havolasi va joylashtiriladigan kanallar belgilanadi; kanallarni qo'lda tanlash mumkin.
- To'lov Gram kriptovalyutasida; kanal egalariga reklama daromadining 50% beriladi.
- Shartlar (ToS): joylashtirish **auksion** orqali, eng yaxshi taklif qilingan CPM bo'yicha; reklama uchun **Maximum Budget** belgilanadi va unga yetganda reklama to'xtatib qo'yiladi (`on hold`); Telegram **minimal CPM** va mavjud joylashtirish joylarini istalgan vaqtda o'zgartirish huquqini saqlab qoladi.

**Rasmiy sahifalarda topilmadi (`unverified`, ikkilamchi manbalar, zid):**
- "Gram kabineti" qayta nomlanishi va koinning 2026-06-15 da Toncoin → Gram bo'lishi: bosh sahifada faqat "Gram" yoziladi; qayta nomlash e'loni o'qilgan sahifalarda yo'q.
- Minimal CPM raqamlari: bir manba "0.1 Gram", boshqasi EUR kabinetida ~30% pasayish (€1 → €0.7), uchinchisi 2026-08-28 dan Rossiya hisoblari uchun €0.60/€0.30/€0.75 deydi. ToS/FAQ/Guidelines'da hech qanday raqam yo'q (ToS faqat minimal CPM mavjudligini va uni Telegram o'zgartirishini aytadi). Kabinetda ko'rinadigan stavkani foydalanuvchidan oling.
- Foydalanuvchi o'z kabinetidagi stavkani `USER_PROVIDED` deb beradi; global CPM benchmarklari o'ylab topilmaydi.

## Manbalar
- `skills/audit/references/ads/telegram-audit.md`
- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md`
