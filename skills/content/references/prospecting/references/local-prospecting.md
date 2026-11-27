# Local SMB Prospecting bo'yicha reference

Foydalanuvchi mahalliy kichik bizneslarga sotganda — do'konlar, sport zallari, restoranlar, salonlar, klinikalar, professional xizmatlar, pudratchilar, ko'chmas mulk, fitnes studiyalari, stomatologiya klinikalari.

local-client-prospector naqshidan (brauzer-yordamli kashf + veb-sayt holati tasnifi + yaqinlik ballashi) moslashtirilgan va undan kengaytirilgan.

---

## Muhim ICP signallari (Local SMB yo'nalishi)

### Operatsion signallar

- **Faol biznes** — Google Business Profile yangilangan, yaqinda sharhlar, ish vaqti yaqinda yangilangan
- **So'nggi faollik** — hozir ochiq, muntazam ish vaqti ko'rsatilgan, egasi yaqinda rasm yuklagan
- **Mijozlar bilan aloqa** — egasi sharhlarga javob beradi, ijtimoiy tarmoqda post qo'yadi, faol kalendar (xizmat bizneslari uchun)

### Onlayn mavjudlik signallari (SMB malakalashning asosiy o'qi)

local-client-prospector skilli **veb-sayt holatini** asosiy malakalash sifatida ishlatadi — buni to'g'ridan-to'g'ri o'tkazing. To'rtta tasnif:

| Holat | Ta'rif | Odatiy natija |
|--------|-----------|-----------------|
| **Sayt topilmadi** | O'zaro tekshirilgan qidiruvdan keyin ishonchli mustaqil veb-sayt yo'q | Veb/marketing xizmati uchun **Hot prospekt** |
| **Faqat ijtimoiy tarmoq** | Faqat Facebook, Instagram, WhatsApp, Linktree, bron portali, marketpleys sahifasi — mustaqil sayt yo'q | Veb/marketing xizmati uchun **Hot prospekt** |
| **Zaif sayt** | Mustaqil sayt bor, lekin eskirgan, buzilgan, juda yupqa, mobil uchun qulay emas yoki aniq kontakt/konversiya oqimi yo'q | Yangilash / qayta qurish xizmati uchun **Warm prospekt** |
| **Sayt bor** | Ishonchli, zamonaviy mustaqil sayt mavjud | Boshqa signallar bo'lmasa (masalan, yomon SEO, zaif konversiya dizayni) **past prospekt** |

### Yaqinlik signallari

- Foydalanuvchining joylashuvi yoki xizmat hududidan **masofa**
- **Zichlik** — bir hududda o'xshash bizneslar klasterlari = mahalla bo'yicha nishonga olish imkoniyati
- **Sayohat vaqti** — shaxsan kashf, o'rnatish yoki xizmat ko'rsatish talab qilinganda foydali

### Pasayish signallari

- Butunlay yopilgan (Google Maps bannerida)
- Sharhlar to'xtagan yoki biznes ro'yxati yopilgan deb xabar qilingan
- Oxirgi faollik (sharh, post) >12 oy oldin

---

## Kashf manbalari (Local SMB yo'nalishi)

### Asosiy

- **Google Maps** (brauzer, qo'lda) — "[joylashuv] yaqinidagi kategoriya" deb qidiring va ko'rinadigan natijalarni ko'rib chiqing. Tafsilotlarni o'zaro tekshiring. Ommaviy ajratib olmang.
- **Yelp** — ikkilamchi tekshiruv; to'ldiruvchi kategoriyalar
- **Bing Local / Apple Maps** — kichikroq bizneslar bo'yicha boshqacha qamrov
- **Facebook Pages qidiruvi** — ko'pgina SMB'lar faqat Facebook'da

### O'zaro tekshirish

- **Biznesning o'z veb-sayti** (bo'lsa)
- **Soha kataloglari** (masalan, tibbiyot uchun Healthgrades, restoranlar uchun OpenTable, huquq uchun Avvo)
- **Mahalliy Savdo palatasi ro'yxatlari**
- Yuridik shaxs holati uchun **davlat biznes reestrlari**
- Maps'dan tashqari mavjudlikni aniqlash uchun **"[biznes nomi] [shahar]" qidiruv natijalari**

---

## Brauzer tadqiqoti ish jarayoni

1. Brauzerni oching va `base_location` yaqinidagi kategoriya uchun Google Maps'da qidiring
2. Ko'rinadigan mahalliy natijalar, qidiruv natijalari va ommaviy kataloglardan nomzodlar ro'yxatini tuzing
3. Har bir nomzod uchun kerakli maydonlarni to'ldirish uchun ommaviy manbalarni ko'rib chiqing
4. Mustaqil veb-sayt mavjudligini tekshirish uchun aniq biznes nomi plyus shahar/qishloqni qidiring
5. Veb-sayt holatini yuqoridagi jadvalga muvofiq tasniflang
6. Ishonchni belgilang: Yuqori (2+ manba), O'rta (1 manba + izchil dalil), Past (to'liq bo'lmagan/noaniq)

Foydalanuvchi subagentlarni aniq so'rasa VA subagentlar mavjud bo'lsa, nomzodlarni kesishmaydigan partiyalarga bo'ling va har bir subagentdan faqat veb-sayt/ijtimoiy tarmoq/kontakt holatini tekshirishni so'rang. Asosiy qidiruv uchun, agar bu jarayonni sekinlashtirsa, subagentlardan foydalanmang.

### Ixtiyoriy: Firecrawl yoki Browserbase bilan dasturiy tekshiruv

Nomzodning veb-sayt URL'ini olgach (qo'lda Maps/Yelp kashfi orqali topilgan), URL'ga dasturiy murojaat qilib veb-sayt holati tasnifini tezlashtirishingiz mumkin:

- **Firecrawl** — oddiy "bu sayt jonlimi, zamonaviymi, mobil uchun qulaymi, konversiya oqimi bormi" o'qishlari uchun — ko'rib chiqsa bo'ladigan toza markdown qaytaradi
- **Browserbase** — nomzod sayti JS rendering talab qilganda, cookie rozilik oynasi bo'lganda yoki sessiya holati kerak bo'lganda

**Qat'iy chegara**: bularni alohida biznesning URL'ida ishlating. Google Maps, Yelp yoki shartlari ommaviy ajratib olishni taqiqlaydigan har qanday platformaga **yo'naltirmang** — kashf qo'lda qoladi.

Sozlash tafsilotlari uchun [data-sources.md](data-sources.md) ga qarang.

---

## Malakalash cheklisti (Local SMB yo'nalishi)

- [ ] Biznes faol (so'nggi 6 oyda yangi sharhlar yoki faollik)
- [ ] Kategoriya foydalanuvchining xizmat taklifiga mos
- [ ] Masofa / yaqinlik maqsadli radius ichida
- [ ] Veb-sayt holati tasniflangan
- [ ] Telefon yoki kontakt kanali tekshirilgan
- [ ] Kamida bitta o'zaro manba biznes ko'rsatilgan manzilda ishlashini tasdiqlaydi
- [ ] Dublikat / tarmoq filiali / mavzudan tashqari kategoriya emas
- [ ] Butunlay yopilmagan

---

## Lid ballash (Local SMB)

Ushbu oddiy rubrikadan foydalaning (local-client-prospector naqshiga mos):

| Ball | Mezonlar |
|-------|----------|
| **Hot** | Sayt topilmadi YOKI faqat ijtimoiy tarmoq + telefon mavjud + faol biznes + maqsadli radius ichida |
| **Warm** | Zaif sayt, yomon onlayn taqdimot yoki faqat marketpleys/bron sahifasi |
| **Cold** | Yaxshi veb-sayt allaqachon mavjud YOKI past ishonch |
| **Skip** | Yopilgan, dublikat, radiusdan tashqari, aloqasiz kategoriya yoki biznes prospekti emas |

---

## Chiqish ustunlari (Local SMB yo'nalishi)

Chat jadvali (≤15 qator):

```
| Score | Business | Category | Area | Distance | Website status | Website/Social | Phone | Why it's a prospect | Confidence |
```

CSV:

```csv
score,business,category,area,distance_km,website_status,website_url,social_urls,phone,email,source_urls,why_prospect,confidence,verified_date,notes
```

Qoidalar:
- "Why it's a prospect" ni qisqa va amaliy saqlang
- Maydonlarni bo'sh qoldirish o'rniga `Not found` ishlating
- Manba havolalarini tejamkorlik bilan qo'shing, hammasini emas
- Jadvaldan keyin eng yaxshi 3 ta lid va har biri uchun bitta amaliy sabab bilan **Best first outreach targets** qo'shing
- Ishonch past bo'lsa, nima noaniq qolganini aniq ayting

---

## Top outreach nishonlarini tanlash (Local SMB)

Eng yaxshi 3 ta hot lid uchun ustuvorlik:

1. **Sayt yo'q / faqat ijtimoiy tarmoq + telefon mavjud** = eng aniq xizmat imkoniyati
2. **Ko'p sharhlar soni** = haqiqiy mijozlari bor faol, mustahkam biznes
3. **Egasi javob bergan sharhlar** = jalb qilingan ega = vendorni baholashga ko'proq moyil
4. **Sizning xizmat ixtisosligingizga soha mosligi** umumiy kategoriya mosligidan yaxshi

Har bir top nishon asoslamasi bo'shliq va signalni nomlaydigan bir gap bo'lishi kerak: "Mustaqil veb-sayt yo'q (o'zaro tekshirilgan); egasi javob bergan 80+ Google sharhi; maqsadli hududdan 2 km."

---

## Compliance eslatmalari (Local SMB'ga xos)

Mahalliy yo'nalish uchta yo'nalish ichida scrapingga eng sezgir. Xususan:

- **Google Maps Terms of Service** ommaviy ajratib olishni taqiqlaydi. Brauzer tashriflarini ma'lumot olish emas, tadqiqot deb hisoblang.
- **To'liq Google Maps Place ID'larini CRM'ingizda saqlamang** — ToS Maps ma'lumotlarini saqlashni cheklaydi.
- **Faqat ommaviy biznes kontakt kanallari**: e'lon qilingan telefon, kontakt formasi, info@ email. Alohida xodimlarga ularning shaxsiy kanallari orqali murojaat qilmang.
- **Biznesning o'z saytida e'lon qilingan ega/operator ismidan** foydalanish mumkin. Agar uni faqat LinkedIn'dan olgan bo'lsangiz, manbani belgilang.

---

## Keng tarqalgan xatolar (Local SMB)

1. **Google Maps'dan ommaviy scraping** — ToS'ni buzish va tadqiqot kanalini yo'qotishning eng tez yo'li.
2. **Google Maps ma'lumotlarini haqiqat deb hisoblash** — ro'yxatlar eskiradi. Ish vaqti, holat va sharhlarni o'zaro tekshiring.
3. **Veb-sayt holatini o'zaro tekshirishni o'tkazib yuborish** — Maps'da "sayt yo'q" topilishi sayt mavjud emasligini anglatmaydi; tasniflashdan oldin aniq nom bo'yicha veb-qidiruv qiling.
4. **Faqat eng yirik bizneslarni nishonga olish** — ular allaqachon boshqa provayderlar bilan qoplangan. 2–5 xodimli SMB'lar — xizmat ko'rsatilmayotgan imkoniyat.
5. **Barcha hot lidlarga umumiy murojaat** — mahalliy SMB'lar umumiy pitchlarga qaraganda aniq bo'shliqlarini nomlaydigan murojaatga ("menyuingiz mobilda ko'rinmayotganini payqadim") yaxshiroq javob beradi.
6. **Tarmoqlar va franshizalarni Skip deb e'tiborsiz qoldirish** — ba'zan franshiza egasi xaridor bo'ladi va mahalliy marketing vakolatiga ega. O'tkazib yuborishdan oldin tekshiring.
