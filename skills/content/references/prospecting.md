<!-- v8: eski skill `prospecting` (v7.1) matni; tavsif: Foydalanuvchi B2B SaaS, umumiy B2B yoki mahalliy kichik bizneslar bo'yicha murojaat qilish uchun prospektlarni topish, malakalash va ro'yxat tuzishni xohlaganda ishlating. 'prospecting', 'prospekt ro'yxati tuz', 'lidlar top', 'lid generatsiya ro'yxati', 'SaaS kompaniyalarni top' kabi so'rovlarda ham ishga tushadi. -->

# Prospecting (prospektlarni qidirish)

Siz to'rtta yo'nalish bo'yicha malakalangan prospekt ro'yxatlarini tuzish bo'yicha ekspertsiz: B2B SaaS, umumiy B2B, mahalliy kichik bizneslar va erta bosqichdagi talab-signali kashfi (birinchi mijozlaringizni ommaviy og'riq signallaridan topish). Maqsadingiz — ICP ta'rifini tekshirilgan, ballangan va murojaatga tayyor lid jadvaliga aylantirish, har bir yo'nalish uchun to'g'ri ma'lumot manbalari, malakalash signallari va compliance holatidan foydalangan holda.

## Boshlashdan oldin

**Avval mahsulot marketing kontekstini tekshiring:**
Agar `.agents/product-marketing.md` (yoki `.claude/product-marketing.md`, yoki eski sozlamalarda eski `product-marketing-context.md` fayl nomi) mavjud bo'lsa, savol berishdan oldin uni o'qing. Shu kontekstdan foydalaning va faqat qamrab olinmagan yoki shu vazifaga xos ma'lumotni so'rang.

## Yo'nalishni tanlang

Prospecting yo'nalishlari bir-biridan shunchalik farq qiladiki, ish jarayoni qabul qilish bosqichida ikkiga bo'linadi. Foydalanuvchi kimga sotayotganiga qarab **bitta** yo'nalishni tanlang:

| Yo'nalish | Kimga sotiladi | "Malakalangan" nimani anglatadi | Asosiy manbalar |
|--------|---------|----------------------------|----------------|
| **SaaS** | Boshqa SaaS kompaniyalari / raqamli bizneslar | ICP mosligi + tech stack mosligi + o'sish signallari (investitsiya, yollash, mahsulot tezligi) | LinkedIn, BuiltWith, Crunchbase, Apollo, Clay, Clearbit, ProductHunt |
| **B2B** | SaaS bo'lmagan B2B (xizmatlar, ishlab chiqaruvchilar, korporatsiyalar, o'rta bozor) | Soha + hajm + geografik moslik + xarid signallari (trigger hodisalar, vendor almashtirish) | Apollo, ZoomInfo, Clay, Clearbit, LinkedIn Sales Nav, soha kataloglari |
| **Local SMB** | Mahalliy kichik bizneslar (do'konlar, sport zallari, restoranlar, klinikalar, salonlar, xizmatlar) | Faol biznes + veb-sayt holati + yaqinlik + qaror qabul qiluvchiga kirish | Google Maps, Yelp, mahalliy kataloglar, Facebook, biznes saytlari |
| **Demand-signal** | Erta bosqich: birinchi mijozlaringiz, dizayn hamkorlari yoki beta foydalanuvchilar | Aynan og'riq/talab/vaqt signalining dalili — firmografik moslik emas, keltirilgan ommaviy manba | Forumlar, hamjamiyatlar, sharhlar, GitHub issue'lari, ish e'lonlari, launch e'lonlari (last30days, social-fetch, scraping orqali) |

Agar foydalanuvchi gibrid yo'nalishni tasvirlasa (masalan, "SaaS ham bo'lgan SMB'lar"), asosiy yo'nalishni tanlang va boshqasidan malakalash signallarini oling. Agar foydalanuvchi erta bosqichda bo'lib, ro'yxat qamroviga emas, talab dalillariga asoslangan *birinchi* mijozlari yoki dizayn hamkorlari kerak bo'lsa — **Demand-signal** yo'nalishidan foydalaning.

Yo'nalishga xos chuqur tahlillar:
- **SaaS** → [references/saas-prospecting.md](references/saas-prospecting.md) ga qarang
- **B2B** → [references/b2b-prospecting.md](references/b2b-prospecting.md) ga qarang
- **Local SMB** → [references/local-prospecting.md](references/local-prospecting.md) ga qarang
- **Demand-signal** (birinchi mijozlaringizni toping) → [references/demand-signals.md](references/demand-signals.md) ga qarang

---

## Umumiy freymvork (barcha yo'nalishlar)

Har bir prospecting loyihasi bir xil besh bosqichdan o'tadi. Asboblar va malakalash signallari yo'nalishga qarab o'zgaradi; bosqichlar o'zgarmaydi.

### 1-bosqich — ICP'ni aniqlash

Mavjud bo'lsa, `product-marketing.md` dan oling. Aks holda yig'ing:

1. **Firmografik moslik** — soha, kompaniya hajmi, daromad diapazoni, geografiya, biznes modeli
2. **Texnografik moslik** (SaaS yo'nalishi) — ular allaqachon qaysi asboblardan foydalanadi, nimasi yetishmaydi
3. **Xarid signali** — nega hozir? (trigger hodisa, investitsiya, yollash, yangi tashabbus, joriy vendordan norozilik, yaqinda ko'chish/kengayish)
4. **Qaror qabul qiluvchi profili** — lavozim, senioritet, nimaga e'tibor beradi
5. **Diskvalifikatorlar** — prospektni aniq "o'tkazib yuborish"ga nima olib keladi

ICP'ni bir paragraf bayonot va o'tdi/o'tmadi mezonlari cheklisti sifatida chiqaring. Bularsiz kashfga o'tmang.

### 2-bosqich — Nomzodlar ro'yxatini tuzish (kashf)

Yakuniy ro'yxatda foydalanuvchi xohlaganidan 2–3 baravar ko'p nomzod toping — malakalash qattiq saralaydi.

- **SaaS / B2B**: o'zaro tekshirish uchun 2–3 manbani birlashtiring. Firmografika uchun Apollo yoki ZoomInfo; boyitish uchun Clearbit yoki Clay; qaror qabul qiluvchilarni xaritalash uchun LinkedIn Sales Nav.
- **Local SMB**: maqsadli hududdagi maqsadli kategoriya uchun Google Maps'dan boshlanadigan brauzer-yordamli tadqiqot; Yelp, biznes veb-sayti, ijtimoiy sahifalar va ommaviy kataloglar bilan o'zaro tekshiring.

Agar foydalanuvchining ro'yxat sifati talabi yuqori bo'lsa, kichikroq yaxshiroq. 25 ta tekshirilgan lid 250 ta asosan keraksiz lidlardan yaxshi.

### 3-bosqich — Har bir nomzodni malakalash

Har bir nomzodni ICP cheklistiga qarshi ballang. Har bir malakalash uchun **dalil** (bir-ikkita manba URL) qo'shing — dalilsiz hech narsani tasdiqlamang.

**Ishonch darajalari** (barcha yo'nalishlarda ishlatiladi):
- **Yuqori**: kamida ikkita mustaqil manba yoki rasmiy biznes sahifasi bilan tasdiqlangan
- **O'rta**: bitta ishonchli manba plyus izchil qidiruv dalillari
- **Past**: to'liq bo'lmagan yoki noaniq dalillar — nima noaniq qolganini belgilang

Email kontaktlar uchun (B2B / SaaS yo'nalishlari) yakuniy ro'yxatga qo'shishdan oldin **doim deliverability'ni tekshiring** — [references/data-sources.md](references/data-sources.md) dagi Truelist integratsiyasiga qarang. Yaroqsiz yoki xavfli emaillar bilan lidlarni topshirmang.

### 4-bosqich — Ballash va ustuvorlashtirish

Bu rubrikani **SaaS, B2B va Local SMB** yo'nalishlari uchun qo'llang. **Demand-signal** yo'nalishi boshqacha ballanadi — Hot/Warm/Cold emas, 0–100 talab-moslik — [references/demand-signals.md](references/demand-signals.md) ga qarang.

| Ball | Ta'rif |
|-------|------------|
| **Hot** | Kuchli ICP mosligi + aniq xarid signali + qaror qabul qiluvchiga kirish mumkin + tekshirilgan kontakt |
| **Warm** | ICP mosligi + yumshoqroq yoki eskiroq signal + kontakt tekshirilishi mumkin |
| **Cold** | Bo'sh ICP mosligi YOKI aniq signal yo'q YOKI kontakt tekshirilmagan |
| **Skip** | Diskvalifikator ishga tushdi (ICP'dan tashqari, yopilgan biznes, dublikat, aloqasiz, past ishonch) |

Yo'nalishga xos signallar ballashni aniqlashtiradi — har bir reference faylga qarang. Standart nisbat maqsadi: ~20% Hot, ~30% Warm, qolgani Cold/Skip.

### 5-bosqich — Lid jadvalini chiqarish

(SaaS / B2B / Local SMB. **Demand-signal** yo'nalishi o'rniga dalillar hisobotini yetkazadi — [references/demand-signals.md](references/demand-signals.md) ga qarang.)

Standart bo'yicha chatda markdown jadval. Ro'yxat >25 qator bo'lsa yoki foydalanuvchi aniq fayl so'rasa, CSV'ga o'ting.

Jadvaldan keyin doim **"Top outreach targets"** (eng muhim murojaat nishonlari) qo'shing — eng yaxshi 3–5 ta hot lid, har biri uchun nega birinchi navbatda murojaat qilish kerakligi haqida bittadan gap.

Ustunlar yo'nalishga qarab farq qiladi (reference fayllarga qarang), lekin har bir lid jadvali quyidagilarni o'z ichiga oladi:
- ball, biznes/kompaniya nomi, kontakt (mos bo'lsa), nima uchun prospekt, manba(lar), ishonch, oxirgi tekshirilgan sana

---

## Compliance himoya chegaralari

Bular barcha yo'nalishlarga tegishli. **Har bir loyihada avval o'qing.**

1. LinkedIn, Google Maps, pullik saytlar yoki rate-limitli API'lardan **ommaviy scraping yo'q**. Brauzer — yordamchi tadqiqot vositasi, scraper emas.
2. **CAPTCHA, login devori yoki bot himoyasini aylanib o'tish yo'q.** Sayt buni talab qilsa, ommaviy ko'rinadigan narsa bilan ishlang.
3. **Faqat ommaviy biznes kontakt kanallari.** Biznesning o'z saytida e'lon qilingan info@, hello@, contact@ va nomlangan rol emaillaridan (asoschi, egasi) foydalaning. Shaxsiy/maxfiy emaillar qonuniy asosni talab qiladi (mavjud munosabat, opt-in va h.k.).
4. **GDPR / CAN-SPAM / CASL'ni hisobga oling.** Ro'yxatga qo'shgan har bir kontakt uchun manba URL va sanani saqlang — keyingi murojaat compliance uchun majburiy.
5. Google Maps, LinkedIn yoki shartlari taqiqlaydigan har qanday platformadan **olingan ma'lumotlarni qayta sotmang.** Foydalanuvchining o'z murojaati uchun ro'yxat tuzish mumkin; ro'yxatni sotish uchun mahsulotlashtirish mumkin emas.
6. **O'zingizni rate-limit qiling.** Ommaviy manbalarda ham so'rovlar orasida pauza qiling. Bot sifatida aniqlanmang.
7. **Buzilgan, sizib chiqqan yoki manbasiz ma'lumotlar yo'q.** Prospektlarni buzilgan datasetlar, scrape qilingan kontakt bozorlari yoki manba izi yo'q list broker'lardan olmang. Litsenziyalangan B2B ma'lumot provayderlari (Apollo, ZoomInfo, Clearbit, Clay) ToS doirasida va qonuniy asos bilan ishlatilsa — mumkin; taqiq noqonuniy/manbasiz ma'lumotlarga, qonuniy boyitish vendorlariga emas.
8. **Sezgir belgilarni hech qachon nishonga olmang yoki taxmin qilmang.** Salomatlik, moliyaviy qiyinchilik, siyosiy e'tiqod, jinsiy mayl, din yoki boshqa himoyalangan/sezgir atributlar bo'yicha malakalamang, segmentlamang yoki shaxsiylashtirmang — ommaviy post ularni oshkor qilgan taqdirda ham.

To'liq compliance referensi uchun (GDPR, CAN-SPAM, CASL, LinkedIn ToS, Google Maps ToS, Clay/Apollo/ZoomInfo foydalanish cheklovlari): [references/compliance.md](references/compliance.md) ga qarang.

---

## To'plash kerak bo'lgan kirishlar

Yetishmasa, bir marta so'rang, so'ng oqilona standartlarni taxmin qilib davom eting:

- **Yo'nalish** (SaaS / B2B / Local SMB / Demand-signal) — odatda kontekstdan aniqlanadi; birinchi mijozlarni topadigan erta bosqich uchun Demand-signal'ni tanlang
- **ICP tavsifi** — mavjud bo'lsa `product-marketing.md` dan oling
- **Maqsadli soni** — SaaS / B2B uchun standart 25, Local SMB uchun 15
- **Geografiya** (Local SMB uchun muhim; B2B uchun foydali; SaaS uchun kamroq muhim)
- **Foydalanuvchida mavjud asboblar** — Apollo? Clay? ZoomInfo? Hunter? Truelist? Standart: bepul + brauzer
- **Chiqish formati** — chat jadvali (standart) yoki CSV
- **Xarid signali afzalligi** — qaysi triggerlarga ustuvorlik berish kerak? (investitsiya raundlari, yollash, yaqinda ko'chish va h.k.)

---

## Asboblarni tanlash bo'yicha tezkor tavsiyalar

To'liq tahlil [references/data-sources.md](references/data-sources.md) da. Tezkor tavsiyalar:

| Foydalanuvchida mavjud bo'lsa... | Nima uchun ishlatish |
|------------------------------|------------|
| **Apollo** | B2B / SaaS firmografik + kontakt kashfi |
| **Clay** | Ko'p manbali boyitish, waterfall qidiruvlari, maxsus ballash |
| **Clearbit** | Emaildan kompaniyaga va kompaniya boyitish |
| **ZoomInfo** | Enterprise B2B kontakt + intent ma'lumotlari |
| **Hunter yoki Snov** | Email naqshini taxmin qilish va tekshirish |
| **Truelist** | Email deliverability validatsiyasi (murojaat ro'yxatiga qo'shishdan oldin) |
| **LinkedIn Sales Navigator** | Qaror qabul qiluvchilarni xaritalash (qo'lda, scraping yo'q) |
| **BuiltWith / Wappalyzer** | Tech stack malakalash (SaaS yo'nalishi) |
| **Crunchbase** | Investitsiya signallari (SaaS yo'nalishi) |
| **GitHub** | Raqobatchi yoki yondosh repo'larning stargazer'lari / fork'lari (dev-tool SaaS yo'nalishi) |
| **Google Maps + brauzer** | Local SMB kashfi |
| **Firecrawl / Browserbase** | Alohida prospekt saytlaridan dasturiy ajratib olish — hech qachon platformalardan emas |

**Foydalanuvchida boyitish asboblari bo'lmasa**: ommaviy manbalar bilan brauzer-yordamli tadqiqotga tayaning — kompaniya veb-sayti, About sahifasi, LinkedIn kompaniya sahifasi, yangiliklarda eslatmalar. Sekinroq, lekin ishlaydi.

---

## Chiqish formatlari

### Standart — chat jadvali

SaaS / B2B uchun (≤25 qator):

```
| Score | Company | Industry | Size | Signal | Contact | Email status | Source | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

Local SMB uchun (≤15 qator) — local-prospector referensidan:

```
| Score | Business | Category | Area | Website status | Website/Social | Phone | Why it's a prospect | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
```

### CSV — >25 qator bo'lsa yoki foydalanuvchi fayl so'rasa

SaaS / B2B ustunlari:

```csv
score,company,domain,industry,size_band,country,signal,contact_name,contact_title,contact_email,email_status,linkedin,source_urls,why_prospect,confidence,verified_date,notes
```

Local SMB ustunlari:

```csv
score,business,category,area,distance_km,website_status,website_url,social_urls,phone,email,source_urls,why_prospect,confidence,verified_date,notes
```

### Jadvaldan keyin doim qo'shing

- **Top outreach targets**: eng yaxshi 3–5 ta hot lid, har biri uchun bir gaplik murojaat asosi
- **Qidiruv parametrlari**: yo'nalish, ICP, joylashuv/radius, maqsadli soni, yaratilgan sana
- **Ochiq savollar**: tekshira olmagan va foydalanuvchi ko'rib chiqishi kerak bo'lgan har qanday narsa

---

## Sifat tekshiruvlari (yakunlashdan oldin)

- [ ] Dublikatlarni olib tashlang (SaaS/B2B uchun domen bo'yicha, Local SMB uchun biznes + manzil bo'yicha)
- [ ] Har bir "Hot" lidda tekshirilgan kontakt + kamida bitta manba URL bor
- [ ] Hech bir lidning emaili Truelist (yoki validatoringiz) tekshiruvidan o'tmay qolmagan — alohida "yaroqsiz" guruhga ko'chiring va foydalanuvchiga belgilang
- [ ] "Hot" deb belgilangan lidlarning birortasi aniq xarid signalisiz emas
- [ ] Ishonch darajalari halol — "Yuqori" 2 ta mustaqil manbani talab qiladi, o'zingizning ikkita qidiruvingizni emas
- [ ] Hech bir lid taqiqlangan scraping'dan (LinkedIn'dan ommaviy, Google Maps'dan ommaviy ajratib olish va h.k.) olinmagan
- [ ] Har bir kontakt uchun manba URL + sana saqlangan (GDPR / CAN-SPAM izi)
- [ ] Yakuniy son foydalanuvchi so'raganiga mos keladi yoki nega kamroq ekanini tushuntirdingiz (sifat talabi)

---

## Keng tarqalgan xatolar

1. **ICP'siz kashfni boshlash.** Noaniq mezonlar bo'yicha nomzodlar tuzsangiz, noto'g'ri narsalarni malakalaysiz.
2. **Ma'lumot manbalariga o'zaro tekshiruvsiz ishonish.** Apollo va ZoomInfo ko'pincha eskirgan bo'ladi; "Hot" deb ballashdan oldin tekshiring.
3. **Email tekshiruvisiz kontaktlarni qo'shish.** Bounce'lar bilan cold email obro'si tez tushadi — doim validatsiya qiling.
4. **LinkedIn yoki Google Maps'dan ommaviy scraping.** Haqiqiy xavf: akkaunt to'xtatilishi + ToS buzilishi. Brauzer faqat yordamchi vosita sifatida.
5. **Yo'nalishlarni aralashtirish.** Local SMB ballashini (veb-sayt holati) B2B SaaS prospektga yoki aksincha qo'llamang.
6. **Xarid signalisiz "Hot" belgilar.** Faqat ICP mosligi yetarli emas — signal vaqtni to'g'ri qiladi.
7. **Manba URL'lar yo'q.** Har bir da'vo ommaviy manbaga izlanishi mumkin bo'lishi kerak. Keyingi murojaat shu izga bog'liq.
8. Keyingi murojaatni (cold-email'ga topshirish) rejalashtirishda **tinch soatlar / vaqt zonasini e'tiborsiz qoldirish.**
9. **Rozilik / iz yozuvlarini saqlashni unutish.** GDPR DSAR va CAN-SPAM auditlari uchun majburiy.

---

## Vazifaga xos savollar

1. Qaysi yo'nalish — SaaS, B2B, Local SMB yoki Demand-signal (erta bosqich, birinchi mijozlaringizni topish)?
2. ICP'ingiz qanday? (Yoki: product-marketing kontekstingizdan olaymi?)
3. Nechta malakalangan lid xohlaysiz?
4. Qaysi asboblardan foydalana olasiz (Apollo / Clay / ZoomInfo / Hunter / Truelist / faqat brauzer)?
5. Eng ko'p qiziqtiradigan trigger xarid signali qaysi?
6. Geografiya yoki radius (Local SMB / B2B)?
7. Chat jadvali yoki CSV?

---

## Asbob integratsiyalari

Joriy qilish uchun [tools registry](../../tools/REGISTRY.md) ga qarang. Asosiy prospecting asboblari:

| Asbob | Eng mos | MCP | Qo'llanma |
|------|----------|:---:|-------|
| **Apollo** | B2B / SaaS firmografik + kontakt kashfi | - | [apollo.md](../../tools/integrations/apollo.md) |
| **Clay** | Ko'p manbali boyitish + waterfall | ✓ | [clay.md](../../tools/integrations/clay.md) |
| **Clearbit** | Emaildan kompaniyaga boyitish | - | [clearbit.md](../../tools/integrations/clearbit.md) |
| **ZoomInfo** | Enterprise B2B kontakt + intent | ✓ | [zoominfo.md](../../tools/integrations/zoominfo.md) |
| **Hunter** | Email naqshi + tekshirish | - | [hunter.md](../../tools/integrations/hunter.md) |
| **Snov** | Email topuvchi + tekshiruvchi | - | [snov.md](../../tools/integrations/snov.md) |
| **Truelist** | Email deliverability validatsiyasi | - | [truelist.md](../../tools/integrations/truelist.md) |
| **Outreach** | Sales engagement (ro'yxatdan keyin) | ✓ | [outreach.md](../../tools/integrations/outreach.md) |
| **RB2B** | Tashrifchini identifikatsiya (iliq intent) | - | [rb2b.md](../../tools/integrations/rb2b.md) |
| **GitHub** | Stargazer/fork/watcher'lar — dasturchi intent signali | - | [github.md](../../tools/integrations/github.md) |
| **Firecrawl** | Bitta nishonli sayt ajratib olish (prospektning o'z veb-sayti) | ✓ | [firecrawl.md](../../tools/integrations/firecrawl.md) |
| **Browserbase** | Render yoki o'zaro ta'sir kerak bo'lganda haqiqiy brauzerda sayt tadqiqoti | ✓ | [browserbase.md](../../tools/integrations/browserbase.md) |

---

## Bog'liq skilllar

- **cold-email**: Malakalangan ro'yxatga qarshi outbound ketma-ketliklarni yozish uchun (prospectingdan keyingi tabiiy qadam)
- **customer-research**: Joriy mijozlar nega sotib olishini tushunish uchun — ICP ta'rifini xabardor qiladi
- **competitor-profiling**: Alohida akkauntlar bo'yicha chuqurroq tadqiqot uchun (ro'yxat tuzish malakalashidan farq qiladi)
- **revops**: Prospectingdan keyin lid marshrutlash, hayot sikli va CRM'ga topshirish uchun
- **sales-enablement**: Murojaatda ishlatiladigan battle card va one-pager'lar uchun
- **directory-submissions**: Inbound kashf yuzalari uchun (prospektlar sizni teskari topishi mumkin)
- **product-marketing**: Har bir prospecting loyihasini langarlaydigan ICP ta'rifi uchun

---

## Operator qatlami (Tyrion lokal bilimi)

> Bu bo'lim — Tyrion (Saloxiddin, O'zbekiston targetolog agentligi) uchun lokal moslashuv. Vendor metodika o'zgarishsiz.

### Qachon ishlatiladi (UZ triggerlari)
- "mijoz top" · "prospekt ro'yxat qur" · "kimga yozamiz" · "ICP bo'yicha ro'yxat" · "lokal bizneslarni top"

### UZ amaliyot qoidalari (manbalardan)
1. Kanal tanlash: LinkedIn juda tor — faqat xalqaro/IT B2B uchun; mahalliy biznesda Telegram birlamchi kommunikatsiya kanali (manba: `local\ozbekiston-konteksti.md` §1)
2. Aloqa tili segmentga qarab alohida: Toshkent B2B/korporativ — ruscha; mintaqa/B2C — o'zbekcha (lotin); kirill auditoriya alohida yuritiladi (manba: `local\ozbekiston-konteksti.md` §3)
3. B2B xizmat (agentlik/konsalting/IT/marketing): sovuq ro'yxatdan oldin kontent orqali ishlash; eng kuchli vosita — real mijoz, real natija, raqamli case study (manba: `local\wiki\b2b-xizmatlar-strategiyasi.md`)
4. Lokal nishalarda ishlaydigan kirish offerlari: bepul diagnostika (avtoservis MOF), bepul audit (lead magnet), free trial/diagnostika/scholarship (xususiy maktab — 6 parallel kanal) — ro'yxat va taklif shu naqshda quriladi (manba: `local\wiki\nisha-playbooklar.md` §3,5; `local\wiki\b2b-xizmatlar-strategiyasi.md`)
5. Outreach vaqtini bozor mavsumlariga moslash: dekabr — eng katta savdo oyi, 1-sentabr — ta'lim/kiyim, Navro'z (21-mart) — kuchli oyna; kampaniya/outreach shu oynalardan oldin tayyorlanadi (manba: `local\ozbekiston-konteksti.md` §6)
6. Ro'yxat tuzilgach taslim bo'lmaslik: lid→mijoz o'rtacha **8 marta aloqa** talab qiladi — bitta urinish bilan to'xtamaslik; har urinishga tez javob (5 daqiqa qoidasi) (manba: `wiki/sotuv-va-retention.md`)
7. O'z statistikasini muddatidan oldin baholamaslik: dastlabki 30 ta uchrashuvdan oldin konversiya me'yori hisoblanmaydi (manba: `wiki/sotuv-va-retention.md`)
8. ICP mezonlari custdev asosida tasdiqlanadi: 10+ respondent, bir xil savol, "nega" savollari ≤5; qo'rquv bloki (firibgarlik, sifat, qaytarish) so'raladi (manba: `local\wiki\custdev-shablonlar.md` §1–2)

### Bog'liq lokal fayllar
- `local\ozbekiston-konteksti.md` — kanal ustuvorligi, til segmentlari, mavsumiylik (repo ildizi)
- `local\wiki\b2b-xizmatlar-strategiyasi.md` — case study + bepul audit strategiyasi (repo ildizi)
- `local\wiki\nisha-playbooklar.md` — nisha bo'yicha ishlagan voronkalar
- `local\wiki\custdev-shablonlar.md` — ICP tasdiqlash intervyulari
- `wiki/sotuv-va-retention.md` — 8 aloqa, 30 uchrashuv qoidasi (vault: `wiki`)
- `memory.md` — operator profili va bozor eslatmasi (repo ildizi)
