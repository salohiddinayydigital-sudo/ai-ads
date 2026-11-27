# Prospecting Compliance bo'yicha reference

Prospekt ro'yxatlarini tuzishga tegishli huquqiy va platforma-ToS cheklovlari. Har bir loyihada avval o'qing.

> Operatsion yo'riqnoma, yuridik maslahat emas. Yuqori hajmli dasturlar yoki EU/UK rezidentlariga tegadigan dasturlar uchun sozlamangizni maxfiylik bo'yicha advokatga ko'rsating.

---

## Qo'shma Shtatlar — CAN-SPAM (keyingi bosqich)

CAN-SPAM ro'yxat tuzishni emas, cold email **yuborishni** tartibga soladi. Lekin ro'yxat tuzish baribir muhim, chunki:

- Murojaat qilgan har bir email manzilining manbasini aniqlay olishingiz kerak (e'tiroz bo'lsa, majburiy)
- "From" qatori va email mazmuni qoidalari yuborish vaqtida qo'llanadi — lekin kontaktni qanday olganingiz haqida yolg'on gapira olmaysiz
- Opt-out so'rovlari 10 ish kuni ichida bajarilishi va kuzatilishi kerak

**Prospecting uchun xususan**: ro'yxatga qo'shgan har bir kontakt uchun manba URL + sanani saqlang. CAN-SPAM buni aniq talab qilmaydi, lekin yuborish amaliyotingizni himoya qilish uchun kerak.

---

## EU / UK — GDPR

Eng qattiq amaldagi freymvork. Quyidagi hollarda ishga tushadi:

- Prospektingiz EU/UK'da yashaydi
- Shaxsiy ma'lumotlarni qayta ishlayapsiz (har qanday identifikatsiya qilinadigan ma'lumot, jumladan nomlangan shaxsga bog'langan biznes emaillari)

### Cold B2B murojaat uchun qonuniy asoslar

Sizda uchta ishonchli variant bor:

1. **Legitimate interest** (qonuniy manfaat) (B2B uchun eng keng tarqalgan). Talab qiladi:
   - Kontakt takliflaringizga qiziqishi mumkin bo'lgan biznes rolida
   - Ma'lumot ommaviy, biznes kontekstidagi manbadan yig'ilgan
   - Aniq opt-out beriladi
   - Qonuniy manfaat testini yozma ravishda ifodalay olasiz

2. **Rozilik** — cold murojaat uchun odatda mumkin emas (birinchi kontaktdan oldin rozilik yo'q)

3. **Mavjud mijoz munosabati** — faqat joriy mijozlarga tegishli, prospektlarga emas

### Nima qilishingiz kerak

- Har bir kontakt uchun **manba + sana + qonuniy asos**ni saqlang
- Ma'lumot sub'ekti kirish so'rovlarini (DSAR) bajaring — so'rov bo'yicha oshkor qilish, tuzatish yoki o'chirishga qodir bo'lishingiz kerak
- Birinchi murojaatga maxfiylik xabari / opt-out kiriting
- Shaxsiy ma'lumotlarni qonuniy manfaat uchun zarur bo'lganidan uzoqroq saqlamang

### Ro'yxatni nima diskvalifikatsiya qiladi

- LinkedIn'dan ommaviy scrape qilingan ma'lumotlar — aniq ToS buzilishi + GDPR xavfi
- Manba izisiz list broker'dan sotib olingan email manzillar
- Tekshiruvsiz yuborilgan "bu domendagi istalgan kishi" taxminiy emaillar (xavf + bounce'larni ko'paytiradi)

---

## Kanada — CASL

CAN-SPAM'dan qattiqroq. Cold B2B murojaat talab qiladi:

- **Aniq rozilik** (explicit opt-in) — cold prospecting uchun odatda mavjud emas
- **YOKI nazarda tutilgan rozilik** — 24 oy ichidagi mavjud biznes munosabati, YOKI biznes manzili kompaniyaning o'z saytida shunday xabarlarni olish maqsadida ommaviy e'lon qilingan

**Kanadalik prospektlar uchun amaliy xulosa**: ommaviy e'lon qilingan manzil istisnosiga tayanish Kanadada cold prospecting uchun eng himoyalanuvchi asos. Har bir xabarda jo'natuvchi identifikatsiyasi, pochta manzili va obunani bekor qilish mexanizmi bo'lishi kerak.

---

## Platforma Terms of Service

### LinkedIn

- **Sales Navigator** tadqiqot vositasi sifatida: yaxshi
- **LinkedIn'ni har qanday ko'lamda scrape qilish**: aniq ToS buzilishi. Bloklangan akkauntlar doimiy. Qilmang.
- **Apollo, Clay va ZoomInfo** turli qonuniy kanallar orqali LinkedIn bilan kesishuvchi ma'lumotlarni da'vo qiladi — compliance deb taxmin qilishdan oldin ularning ma'lumot manbalarini tekshiring
- **InMail va Connection So'rovlari**: CAN-SPAM/GDPR emas, LinkedIn'ning o'z xabar yuborish qoidalari bilan boshqariladi (chunki LinkedIn ichida)

### Google Maps

- ToS Maps ma'lumotlarini ommaviy ajratib olish yoki mahsulotlashtirishni taqiqlaydi
- Kashf yordamchisi sifatida brauzer-yordamli tadqiqot: maqbul
- Place ID'larni yoki katta tuzilgan Maps ma'lumotlarini CRM'ingizda saqlash: aniq ToS taqiqi
- Mahalliy bizneslarni **topish** uchun Maps'dan foydalaning, so'ng saqlaydigan ma'lumotlar uchun biznesning o'z saytidan o'zaro manba qiling

### Apollo / ZoomInfo / Clearbit

- Hammasida qayta sotish, keyingi ulashish va foydalanish holatlarini cheklaydigan o'z ToS bor
- Shartnomangizni o'qing — odatda ma'lumotlardan o'z murojaatingiz uchun foydalanishingiz mumkin, lekin ularni mahsulotlashtira olmaysiz
- Ajratib olingan ma'lumotlarni ommaviy ulashmang (masalan, leaderboard'da, ommaviy hisobotda)

### Crunchbase

- Bepul tarif shaxsiy foydalanish uchun faqat o'qish
- Pullik tarif shartnoma doirasida kengroq foydalanishga ruxsat beradi
- API kirish pullik Pro+ tarifni talab qiladi

---

## Anti-patternlar (Qilmang)

1. **LinkedIn / Google Maps / Yelp'dan ommaviy scraping**. Brauzer-yordamli tadqiqot OK; shu platformalarga yo'naltirilgan avtomatik scraper'lar esa yo'q. **Firecrawl va Browserbase alohida prospektning o'z veb-sayti uchun mos** (qo'lda kashf orqali topilgan URL) — prospektlarni joylashtiruvchi platformalar uchun emas.
2. **Manba izisiz tasodifiy vendorlardan ro'yxat sotib olish**. Ularning huquqiy xavfini meros qilib olasiz.
3. **Emailni taxmin qilib, tekshirmasdan yuborish**. 2% dan yuqori bounce darajasi jo'natuvchi obro'sini yo'q qiladi; huquqiy jihatdan o'zingiz to'qigan email uchun "legitimate interest" asosini da'vo qila olmaysiz.
4. Ommaviy profillardan **shaxsiy email manzillarini yig'ish** (Gmail, shaxsiy Outlook va h.k.). Shaxsiy manzillar GDPR xavfini sezilarli oshiradi.
5. **Kerak bo'lmagan ma'lumotlarni saqlash**. Saqlashni minimallashtiring. Prospekt ro'yxatlarini abadiy saqlamang — GDPR o'chirish huquqi qo'llanadi.
6. **Qonuniy asos hujjatlashtirishini o'tkazib yuborish**. E'tiroz bildirilsa, ishingizni ko'rsata olishingiz kerak. Har bir kontakt uchun manba URL + yig'ish sanasini saqlang.
7. **Prospekt ro'yxatlarini qayta sotish**. Ularni keyingi tomonlarga ulashish huquqingiz bo'lmasligi mumkin. Ma'lumot provayderi shartnomalarini o'qing.
8. **CAPTCHA / login devorini aylanib o'tish**. Texnik jihatdan mumkin bo'lsa ham, bu bot xatti-harakatini bildiradi va deyarli har bir ToS'ni buzadi.

---

## Tezkor audit cheklisti

Ro'yxatni foydalanuvchiga (yoki keyingi bosqichda cold-email'ga) topshirishdan oldin:

- [ ] Har bir kontaktda manba URL + yig'ish sanasi bor
- [ ] Hech bir kontakt scrape qilingan LinkedIn ma'lumotlaridan olinmagan
- [ ] Google Maps Place ID'lari yoki katta Maps-tuzilgan ma'lumotlar saqlanmagan
- [ ] Qonuniy asos hujjatlashtirilgan (B2B uchun legitimate interest testi yoki tegishli muqobil)
- [ ] Email manzillar tekshirilgan (murojaatdan oldin deliverability tekshiruvi)
- [ ] Shaxsiy manzillar (Gmail va h.k.) belgilangan yoki chiqarib tashlangan
- [ ] Manba provayder shartnomalari mo'ljallangan foydalanish holatiga ruxsat beradi
- [ ] Saqlash rejasi hujjatlashtirilgan (qachon o'chirish)
- [ ] Birinchi murojaat obunani bekor qilish + maxfiylik xabarini o'z ichiga oladi (cold-email skilli uchun keyingi bosqich masalasi, lekin hozir eslating)
