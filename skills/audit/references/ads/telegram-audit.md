# Telegram Ads audit referensi

Bu reference rasmiy **Telegram Ads** platformasi (`ads.telegram.org` / Fragment) uchun dalil nazoratlari, akkaunt
tuzilmalari, targeting modellari, matn spetsifikatsiyalari va o'lchov standartlarini belgilaydi.

---

## 1. Qamrov va qo'llanilish

Telegram Ads — ommaviy Telegram kanallari va botlarida ishlaydigan, maxfiylikni birinchi o'ringa qo'yadigan, to'g'ridan-to'g'ri
javob va kanal o'sishiga mo'ljallangan reklama platformasi.

Telegram Ads'ni audit qilish yoki tavsiya qilishdan oldin:
- Akkaunt valyutasini aniqlang (TON, Telegram Stars yoki Fragment/vakolatli resellerlar orqali EUR).
- Kampaniya manzilini aniqlang (`t.me/channel`, `t.me/bot`, aniq `t.me/post` yoki tashqi veb URL).
- Kunlik byudjet shifti, maksimal CPM bid, maqsadli til va geografik targetni tasdiqlang.

---

## 2. Asosiy audit nazoratlari (T01 - T15)

### Kanal va auditoriya sifati
- **T01 — Maqsadli kanal yaqinligi va obunachilar sifati:**
  - Qo'lda tanlangan ommaviy kanallarda faol, haqiqiy obunachilar borligini baholaydi (platforma >1 000 obunachini talab qiladi).
  - Engagement Rate (ERR = post ko'rishlari / jami obunachilar) >15% bo'lishi kerak.
  - Bot obunachilar soni oshirilgan o'lik kanallar yoki to'satdan norganik sakrashlar chiqarib tashlanishi shart.
- **T02 — Aniq kanallar va keng mavzular:**
  - *Pass:* Asosiy konversiya kampaniyalarida aniq kanal targetingi ishlatiladi.
  - *Xavf:* Aniq kanal whitelist'isiz keng mavzuviy kategoriyalarga (masalan, umumiy "Moliya" yoki "IT") haddan tashqari tayanish byudjet sizib ketishiga olib keladi.
- **T03 — Kanal tili va geografik moslik:**
  - O'zbek yoki rus tilidagi reklamalar faqat asosiy auditoriyasi va tili mos kanallarga targetlanishini ta'minlaydi.
  - Tegishli bo'lmagan mintaqaviy kanallarni chiqarib tashlang.

### Reklama matni va kreativ formatlash
- **T04 — 160 belgilik qat'iy chegara:**
  - Matn qat'iy $\le 160$ belgi bo'lishi kerak (probellar bilan).
  - Aniq Value Proposition + ochiq Call to Action bo'lishi shart.
- **T05 — Kontent moderatsiyasi va policy'ga muvofiqlik:**
  - **Clickbait yo'q:** Undovli sensatsiyalar ("SHOCKING", "YOU WON'T BELIEVE") darhol rad etilishiga olib keladi.
  - **Bosh harflar:** BARCHA BOSH HARFLI so'zlar ro'yxatdan o'tgan savdo belgilari yoki standart qisqartmalar (masalan, B2B, AI, CRM) bo'lmasa taqiqlanadi.
  - **Emoji siyosati:** Reklamada ko'pi bilan 1 ta emoji, kontekstga qat'iy mos; takroriy yoki ko'zni qamashtiruvchi emoji ketma-ketliklari yo'q.
  - **Reklamada haqiqat:** Tekshirib bo'lmaydigan da'volar, daromad kafolatlari ("Oyiga $10k ishlang") yoki bo'rttirilgan superlativlar ("Dunyodagi №1 eng yaxshi") yo'q.

### Suhbatli voronka va telemetriya
- **T06 — Deep Linking arxitekturasi:**
  - Botga yo'naltirilgan har bir reklama tuzilgan kampaniya parametrlarini uzatishi shart:
    `https://t.me/BrandBot?start=utm_source_campaign_angle`
- **T07 — Bot javob tezligi:**
  - Avtomatik salomlashuv xabari va va'da qilingan lead magnet `/start` bosilgandan keyin $<10$ soniya ichida ishga tushishi kerak.
  - Bot kechikishi 15 soniyadan oshsa, foydalanuvchilar tez ketadi.
- **T08 — Server-side telemetriya va event webhooklar:**
  - Telegram uchinchi tomon treking pixellarini qo'llab-quvvatlamagani uchun bot backend'i CRM / Analytics'ga quyidagilar bo'yicha webhooklar yuborishi kerak:
    1. `/start` (kirish / ko'rishdan lidga)
    2. Lead magnet yuklab olish (faollashtirish)
    3. Aloqa formasi / telefon yuborish (MQL)
    4. Sotuv malakasi (SQL)
    5. To'lov / bitim yopilishi (daromad)

### Bidding, pacing va unit-iqtisodiyot
- **T09 — CPM auksion optimallashtirishi:**
  - CPM bid va yutuvchi ko'rsatuv ulushini kuzating.
  - Yuqori talabli kanallar raqobatbardosh bidlarni talab qiladi (€2.50 - €5.00+ CPM / 1-3+ TON).
  - Past-bid ochligi: reklama 24 soatdan keyin 0 ko'rsatuv bersa, bid auksion tozalash chegarasidan past.
- **T10 — Kunlik sarf himoyasi va pacing:**
  - Katta kanallarda tez tugab qolmasligi uchun kunlik sarf chegarasi o'rnatilishi shart.

---

## 3. Yuqori konversiyali 160 belgilik matn formulalari

1. **Muammo $\to$ to'g'ridan-to'g'ri yechim:**
   `Qimmat marketingdan charchadingizmi? Telegram Ads orqali har bir lid narxini 2x arzonlashtiring. Bepul audit oling:`
2. **Ijtimoiy isbot $\to$ qiziqish:**
   `Toshkentdagi 40+ kompaniya qanday qilib Telegram botdan oyiga $50,000+ sotuv qildi? Case study'ni o'qing:`
3. **To'g'ridan-to'g'ri murojaat $\to$ qiymat hooki:**
   `Targetologlar uchun: Andromeda va Google Ads bo'yicha 84 ta tayyor SOP va amaliy darslik. Botdan yuklab oling:`
