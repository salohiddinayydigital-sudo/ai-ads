<!-- v8.3 Targetolog Copilot Pack: account-recovery-specialist metodologiyasi (faqat white-hat). Ref: agents/account-recovery-specialist.md, rules/40-xavfsizlik-va-hisob.md -->

# Rad etilish va blokirovkadan tiklanish — faqat white-hat

> **Qat'iy chegara:** cloaking, soxta hujjat, sotib olingan/farm/o'g'irlangan akkauntlar, "toza" BM ijarasi, VPN orqali identifikatsiyani yashirish, policy filtrlarini aldash uchun so'zlarni buzib yozish — **hech qachon** tavsiya qilinmaydi. Bunday so'rovga javob: rad etish + qonuniy yo'l.

## 1. Rad etilish (Rejected) ildiz sababi triage'i

| Belgi | Ehtimoliy policy bandi | Xavfsiz tuzatish |
|---|---|---|
| "Siz ...misiz?", "Sizning qarzingiz..." | Personal Attributes | 2-shaxsdan umumiy formulaga: "Ko'pchilik ... duch keladi" |
| Oldin/keyin foto, tana o'zgarishi | Before/After, body image | Jarayon yoki mahsulotni ko'rsatish; natija kafolatisiz |
| "100% davolaydi", "oyiga $3000" | Health / Financial claims, misleading | Tasdiqlangan, cheklangan da'vo yoki olib tashlash |
| Landing reklamadan boshqacha, redirect zanjiri | Circumventing Systems / destination mismatch | Landing = reklama va'dasi; to'g'ridan-to'g'ri URL |
| Kripto, kredit, uy-joy, ish | Restricted / Special Ad Category | Kategoriyani e'lon qilish, ruxsat/litsenziya |
| Mualliflik musiqasi/logotip | IP | Litsenziyalangan aktiv |

Rasmiy manba (Meta Advertising Standards, TikTok Ad Policies, Google Ads policies) URL + tekshirilgan sana; topilmasa — `unverified`.

**Hech qachon:** o'zgartirilmagan kreativni qayta-qayta yuborish — takroriy rad etish akkaunt/BM cheklovi xavfini oshiradi.

## 2. Apellyatsiya (Request Review) shabloni

**EN:**
> Hello, our ad [ID] was rejected under [policy]. We have reviewed the policy [URL]. The ad promotes [product], a [legal/licensed] [category]. [If edited: We removed X and replaced it with Y.] We believe it complies with [section] because [1–2 factual reasons]. Supporting documents: [license/registration]. Thank you for reviewing.

**RU:**
> Здравствуйте! Объявление [ID] отклонено по правилу [policy]. Мы ознакомились с правилами [URL]. Объявление рекламирует [продукт] — [законную/лицензированную] [категорию]. [Если изменено: мы удалили X и заменили на Y.] Считаем, что объявление соответствует [пункт], потому что [1–2 факта]. Документы: [лицензия/регистрация]. Спасибо.

Ohang: xotirjam, faktli, qisqa; ayblov, tahdid, emotsiya yo'q. Bitta apellyatsiya — bitta masala.

## 3. Akkaunt / BM cheklovi — tiklash ketma-ketligi

1. **Account Quality** (Meta Business Support Home) — aniq sabab va "Request review" mavjudmi.
2. Shaxsni tasdiqlash (ID verification) va BM verifikatsiyasi (biznes hujjatlari) — haqiqiy hujjatlar bilan.
3. Bog'liq aktivlar (Page, Pixel, to'lov) holatini tekshirish; zarar ko'rgan aktivni ajratish.
4. Apellyatsiya → javob kutish (odatda 24–72 soat, `HEURISTIC_PRIOR_MODEL`) → rad bo'lsa qo'shimcha dalil bilan ikkinchi ko'rib chiqish.
5. To'lov ushlanishi: karta egasi tasdig'i, balans, bank 3-D Secure; qarz bo'lsa to'lash.

## 4. White-hat infratuzilma gigiyenasi

- BM'da **≥ 2 haqiqiy admin** (2FA yoqilgan, alohida qurilmalar).
- BM va domen tasdiqlangan; Pixel/Dataset BM egaligida.
- To'lov kartalari kompaniya nomida, limitlar aniq.
- Yangi akkauntni "qizdirish": kichik byudjet, policy-toza kreativ, to'g'ri kategoriya, bosqichma-bosqich o'sish (keskin sakrashsiz).
- Zaxira: **qonuniy** ikkinchi BM/akkaunt faqat haqiqiy biznes ehtiyoji uchun va bir xil shaxs/hujjatlar bilan — cheklovni aylanib o'tish uchun emas.
