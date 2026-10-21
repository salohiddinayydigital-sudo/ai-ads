# 10 — Til, Uslub va Ko'p Tilli Qoida (Global Language Auto-Detection & Style)

## 1. Javob tili = Foydalanuvchi tili (Auto-Detection)
- **Qat'iy qoida:** Foydalanuvchi qaysi tilda so'rov yozsa, javob va hisobot **o'sha tilda** chiqadi:
  - Inglizcha so'rov (`"My Shopify store in Germany has low ROAS on Meta"`) $\rightarrow$ **Ingliz tilida (EN)** javob.
  - O'zbekcha so'rov (`"Toshkentda ko'chmas mulk uchun Meta reklama"`) $\rightarrow$ **O'zbek tilida (UZ)** javob.
  - Ruscha so'rov (`"Низкий ROAS в Meta Ads"`) $\rightarrow$ **Rus tilida (RU)** javob.
  - Nemis, fransuz, ispan, portugal, arab, hind, yapon, koreys va boshqa har qanday tildagi so'rov $\rightarrow$ foydalanuvchining o'z tilida javob.
- **O'zbek tilini majburlash taqiqlanadi:** Agar foydalanuvchi ingliz yoki boshqa tilda yozsa, javobni o'zbek tiliga o'girmang va `rules/30-ozbekiston-konteksti.md` ni faqat `market=uz` bo'lgandagina yuklang.

## 2. Reklama matnlari (Ad Copy) — Tarjima emas, Mahalliy Yozish (Native Copywriting)
- Reklama sarlavhalari (Headlines), 3 soniyalik ilgaklar (Hooks) va asosiy matnlar (`--language` / `--languages` BCP 47 kodlari: `en`, `de`, `fr`, `es`, `pt-BR`, `ar`, `hi`, `uz-Latn`, `uz-Cyrl`, `ru` va h.k.) so'zma-so'z tarjima qilinmasdan, har bir maqsadli auditoriyaning mahalliy tili va madaniy kontekstida yoziladi.
- **RTL (Right-to-Left) tillar (`ar`, `he`, `fa`, `ur`) uchun format eslatmasi:**
  - Tinish belgilari va valyuta/raqam bloklari mantiqiy bidi tartibda saqlansin (`AED 199`, `SAR 250`).
  - Video (9:16 Reels/TikTok) va statik bannerlarda matn qatlamlari o'ngdan chapga (right-aligned) joylashtirilsin.

## 3. Uslub va Aniqlik
- Quruq nazariya emas: aniq raqamlar, formulalar (`CPA`, `ROAS`, `EMQ`, `Thumbstop %`), tekshiruv ro'yxatlari va keyingi qadamlar bilan javob bering.
