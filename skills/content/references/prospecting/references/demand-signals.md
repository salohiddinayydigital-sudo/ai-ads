# Demand-Signal kashfi (birinchi mijozlaringizni toping)

Qolgan uchta yo'nalish ro'yxatni kim *mos kelishi* bo'yicha tuzadi (firmografika, texnografika, yaqinlik). Bu yo'nalish ro'yxatni kim *allaqachon og'riqni ko'rsatayotgani* bo'yicha tuzadi — sizda mahsulot va taxmin bor, lekin hali mijozlar bazasi yo'q va dastlabki o'nta haqiqiy suhbat kerak bo'lgan erta bosqich harakati. Siz ma'lumotlar bazasini filtrlamaysiz; siz aynan siz hal qiladigan muammoni tasvirlayotgan odamlarni topish uchun so'nggi ommaviy muhokamalarni qazib olasiz va har bir prospektni dalillarga bog'laysiz.

Foydalanuvchi product-market-fit'dan oldin bo'lsa, yangi narsani ishga tushirayotgan bo'lsa yoki masshtablangan outbound ro'yxati emas, **dizayn hamkorlari, beta foydalanuvchilar yoki birinchi mijozlar** qidirayotgan bo'lsa, shu yo'nalishdan foydalaning. U SKILL.md dagi umumiy besh bosqichni va barcha compliance himoya chegaralarini qayta ishlatadi; o'zgaradigani — qayerga qarash, qanday ballash va nimani yetkazish.

Naqsh manbasi: bu yerdagi freymvork ochiq manbali `first-customer-finder` Codex skilli (Kappaemme, MIT) dan qayta ifodalangan va bizning jonli-yangilik asboblarimiz bilan kengaytirilgan.

## Bu yo'nalishni nima farqlaydi

| | Ro'yxat tuzish yo'nalishlari (SaaS / B2B / SMB) | Demand-signal kashfi |
|---|---|---|
| Boshlanish nuqtasi | Firmografik ICP | Tasvirlangan muammo |
| Manbalar | Kontakt ma'lumotlar bazalari (Apollo, ZoomInfo, Clay) | Ommaviy muhokamalar (forumlar, sharhlar, issue'lar, postlar) |
| Kontakt bosqichi | Boyitish + email deliverability'ni tekshirish | Yo'q — ularga allaqachon post qo'ygan joyda yeting |
| Yutuq asosi | Masshtabdagi qamrov | Uzun ro'yxatdan ko'ra dalilga asoslangan 10 ta kuchli moslik |
| Natija | Ballangan lid jadvali | Dalillar hisoboti + qo'lda murojaat rejasi |

Keltirilgan og'riq, ehtiyoj yoki vaqt signalisiz prospekt bu yerda taxminiy moslikdir — u asosiy qisqa ro'yxatga **kirmaydi**. Dalil — kirish chiptasi.

## 1-qadam — Mahsulot brifi (har qanday qidiruvdan oldin)

Zaif mosliklarni *rad etish* uchun yetarlicha aniq belgilang:

- mahsulot va va'da qilingan natija
- asosiy foydalanuvchi va iqtisodiy xaridor (ko'pincha boshqa)
- shoshilinch bajariladigan ish (job to be done)
- almashtiriladigan joriy muqobil yoki vaqtinchalik yechim
- ehtimoliy qabul qilish triggeri (nima hozirni lahzaga aylantiradi)
- geografiya / til cheklovi
- aniq diskvalifikatorlar

Brif aniq bo'lmaguncha keng yig'ishni boshlamang. `.agents/product-marketing.md` mavjud bo'lsa, undan oling.

## 2-qadam — Besh signal guruhini qazib oling

Bitta so'rovni takrorlamasdan, bir nechta burchakdan qidiring. Formulirovkani auditoriya aslida qanday gaplashishiga moslang (avval ularning lug'atini organik kontentdan oling — xuddi shu g'oya uchun ad-creative hook-system'ning organik til eslatmasiga qarang).

1. **Aniq talab** — "looking for," "recommend a tool for," "alternative to [X]," "does anything exist that," "how do you all handle."
2. **Og'riq** — "takes hours," "so manual," "hate that," "keeps breaking," "biggest frustration with," "why is there no."
3. **Vaqtinchalik yechim (workaround)** — jadvallar, copy-paste, VA, Zapier zanjiri, skript, shablon, mahsulotingiz almashtiradigan har qanday takroriy qo'lda qadam.
4. **O'tish** — bekor qilish, migratsiya, "moving off [competitor]," yetishmayotgan funksiya, narx haqida shikoyat, raqobatchidan norozilik.
5. **Vaqt (timing)** — ommaviy launch, tegishli funksiya uchun yangi yollash, kengayish, yangi ish jarayoni yoki tartibga solish, integratsiya e'lon qilinishi — mahsulotni hozir tegishli qiladigan *joriy* hodisa.

**Jonli-yangilik ustunligimizdan foydalaning.** Umumiy skill veb-qidiruv nima ko'rsatsa, shunga tayanadi; sizda yaxshiroq vositalar bor:
- **last30days** — so'nggi 30 kundagi Reddit, Hacker News, X, YouTube va veb signallar. Bu yo'nalish uchun eng qimmatli yagona vosita: yangilikning o'zi — vaqt signali.
- **social-fetch** — topgan aniq post/thread'ning to'liq mazmunini normallashtirilgan holda torting.
- **scraping** / **Firecrawl** / **Browserbase** — asl ommaviy sahifani (forum thread, GitHub issue, sharh) o'qing, hech qachon faqat qidiruv snippetidan malakalamang.
- **deep-research** — keng wedge bo'lganda adversarial tekshiruvli ko'p manbali qamrov uchun.
- **competitor-profiling** / **customer-research** — raqobatchiga o'tish signallari va og'riq tili uchun sharhlarni qazib olish.

## 3-qadam — Manbalar aralashmasi (faqat ommaviy)

Forumlar va ommaviy hamjamiyat thread'lari · ommaviy ijtimoiy postlar va javoblar · mahsulot va ilova marketpleys sharhlari · GitHub issue'lari va funksiya so'rovlari · ommaviy kompaniya sahifalari, ish e'lonlari, changelog'lar, launch e'lonlari · "asbob qidiryapman" postlari va kataloglar.

Yopiq guruhlar, to'siqli hamjamiyatlar, ma'lumot brokerlari, sizib chiqqan datasetlar va shartlari kirishni taqiqlaydigan har qanday manbadan qoching — boshqa barcha yo'nalishlar bilan bir xil compliance himoya chegaralari (SKILL.md ga qarang), jumladan sezgir belgilar qoidasi.

**Faqat biznes/professional kontekst.** Faqat kimdir professional yoki biznes sifatida ish muammosi haqida post qo'ygan joyda malakalang va murojaat qiling (indie-hackers thread'idagi asoschi, GitHub issue'dagi dasturchi, o'z roli subreddit'idagi ops rahbari). Shaxsiy qiyinchilik kontekstlarini butunlay chiqarib tashlang — salomatlik, moliyaviy qiyinchilik, giyohvandlik, qayg'u yoki odamlar shaxsiy muammolaridan shikoyat qilayotgan har qanday iste'molchi qo'llab-quvvatlash forumi, mahsulotingiz bilan ozgina bog'liq bo'lsa ham. Harakat haqiqatan iste'molchiga yo'naltirilgan (B2C) bo'lsa, ommaviy og'riq posti o'z-o'zidan sovuq murojaat uchun qonuniy asos emas — odamlarga kanalning o'z me'yorlari orqali yeting (javob kutiladigan joyda ommaviy javob bering) va shaxsiy postdan boshlab begonaga hech qachon DM yozmang.

Minimal iqtibos keltiring, odatiy ravishda parafraz qiling va har bir muhim og'riq yoki vaqt signaliga havola bering.

## 4-qadam — Demand-fit bo'yicha ballang (ICP-fit emas)

Ro'yxat tuzish yo'nalishlari Hot/Warm/Cold ni ICP moslik bo'yicha ballaydi. Bu yo'nalish **talab mosligi** bo'yicha 0–100 ball beradi — dalil aynan shu prospekt aynan shuni hozir qanchalik kuchli xohlashini qanchalik kuchli ko'rsatadi. Har bir o'lchovni 0–5 ball bilan baholang:

| O'lchov | Vazn | Nimani o'lchaydi |
|---|---|---|
| **Og'riq kuchi** | 25% | Bayon qilingan muammoning to'g'ridan-to'g'riligi, jiddiyligi, takrorlanishi va narxi |
| **Mahsulot mosligi** | 25% | Mahsulotingiz dalillangan vazifani qanchalik to'g'ridan-to'g'ri hal qiladi |
| **Vaqt (timing)** | 20% | Yangilik + joriy trigger mavjudligi |
| **Ommaviy yetib borish** | 15% | Tabiiy, tegishli ommaviy/professional kontakt yo'li mavjud |
| **Dalil sifati** | 15% | Aniqlik, manba ishonchliligi, signal haqiqatan ularniki ekaniga ishonch |

```
score = pain/5*25 + fit/5*25 + timing/5*20 + reachability/5*15 + evidence/5*15
```

| Diapazon | Ma'nosi |
|---|---|
| **80–100** | Kuchli birinchi mijoz nomzodi |
| **65–79** | Istiqbolli — tez tasdiqlang |
| **50–64** | Ishonarli, lekin muhim signal yetishmaydi |
| **50 dan past** | Asosiy qisqa ro'yxatga kiritmang |

Eski aniq so'rov hali ham hisobga olinishi mumkin — lekin vaqt ballini pasaytiring va sanani belgilang. Faqat sohaga mos keladigan, dalillangan triggeri bo'lmagan kompaniya bu yerda malakalangan prospekt *emas*.

### Prospekt bosqichlari

- **High intent** — yechimni ommaviy so'rayapti yoki faol almashtirayapti
- **Problem aware** — og'riq yoki qimmat vaqtinchalik yechimni aniq tasvirlayapti
- **Trigger present** — joriy biznes hodisa mahsulotni tegishli qiladi
- **Potential fit** — ICP mosligi, to'liq bo'lmagan dalil → asosiy qisqa ro'yxatdan *tashqarida* saqlang

### Dalillar daftari (har bir malakalangan prospekt uchun)

Ko'rsatiladigan nom (kompaniya/loyiha/ommaviy mutaxassis) · manba sarlavhasi + URL · ko'rinadigan nashr sanasi yoki "sana mavjud emas" · manba turi · qisqa og'riq/vaqt signali · kuzatilgan dalil va xulosa (qaysi ekanini belgilang) · ball taqsimoti · signal eskirganda yangilik ogohlantirishi.

## 5-qadam — Murojaatni qoralang, hech qachon yubormang

Manba bilan *allaqachon bog'liq* eng tabiiy kanalni tavsiya qiling, va faqat javob shu kanalning odatiy qismi bo'lgan joyda (ommaviy thread'da javob bering, ommaviy professional profil orqali javob bering). Ommaviy postni muallif taklif qilmagan shaxsiy DM'ga aylantirmang va shaxsiy qiyinchilik postidan boshlab hech kimga murojaat qilmang. Quyidagi shaklda ~90 so'zdan kam bitta ochuvchi xabar qoralang:

1. ommaviy kontekstni tabiiy tarzda eslang
2. uni aniq muammoga bog'lang
3. mahsulotni bir gapda tushuntiring
4. bitta past ishqalanishli savol bering

O'zingizda yo'q tanishlikni hech qachon da'vo qilmang, shaxsiy tafsilotlarni to'qimang va hech qachon avtomatik yubormang: foydalanuvchi alohida ruxsat bermaguncha xabarlar, connect'lar, follow'lar, izohlar, forma yuborishlar yoki CRM yozuvlari yo'q. Bu marketing-loops himoya chegaralaridagi qo'lda/darvozali yondashuv.

## 6-qadam — Dalillar hisobotini yetkazing

Eng amaliy dalildan boshlang, quyidagi tartibda:

1. **Xulosa** — mahsulotda yetib borsa bo'ladigan erta mijoz signali bormi yoki hali yo'qmi? (Halol "hali yo'q, mana nega" to'g'ri javob.)
2. **ICP** — xaridor, vazifa, trigger, diskvalifikatorlar.
3. **Top prospekt** — eng kuchli dalilga asoslangan yagona nomzod va nega hozir.
4. **Prospektlar qisqa ro'yxati** — har bir prospekt uchun: manba, og'riq signali, demand-fit balli, bosqich, nega hozir, kanal, ochuvchi xabar.
5. **Takrorlanuvchi naqshlar** — prospektlar bo'ylab qaytariladigan og'riqlar va triggerlar (bular sizning pozitsiyalash va xabar oltini).
6. **Yetti kunlik qo'lda murojaat rejasi** — kam hajmli tasdiqlash ketma-ketligi (masalan, top 3 ga bitta manbaga asoslangan savol bilan murojaat qiling; mockup'ni faqat og'riq tasdiqlangandan keyin ulashing; uchta suhbat va bitta dizayn-hamkorlik majburiyatini maqsad qiling).
7. **Cheklovlar** — qanday dalil yetishmaydi va haqiqiy suhbatlar orqali nima tasdiqlanishi kerak.

Ulashsa bo'ladigan mustaqil HTML versiya uchun ad-creative'ning [creative-review-page.md](../../ad-creative/references/creative-review-page.md) dagi JSON→HTML generator naqshi namuna (har bir qiymatni escape qiling; o'zida mustaqil saqlang).

## Halollik qoidalari (muzokarasiz)

- Har bir asosiy prospekt kamida bitta haqiqiy ommaviy signalga havola qiladi. Signal yo'q — qisqa ro'yxat yo'q.
- Natijani **"ommaviy signallarga asoslangan potentsial mijoz"** deb belgilang — hech qachon "qiziqqan," "sotib oladi" yoki "rozilik bergan" demang.
- Uzun umumiy ro'yxatdan ko'ra o'nta kuchli moslikni afzal ko'ring. Noaniqlik va eskirgan dalilni ko'rinadigan qiling.
- Shaxsiylashtirishni keltirilgan manbadan qiling, to'qilgan taxminlardan emas.
- Qisqa ro'yxatni mijozlar bazasi emas, suhbatlar orqali tasdiqlanadigan tadqiqot gipotezasi deb biling.
