# Xalqaro SEO: dalillar va manbalar

SEO Audit skilidagi Xalqaro SEO va lokalizatsiya bo'limini qo'llab-quvvatlaydigan batafsil dalillar. Mavzu bo'yicha tartiblangan, manba URL'lari va asosiy iqtiboslar bilan. (Iqtiboslar Google va boshqa manbalarning inglizcha matnidan tarjima qilingan.)

---

## Hreflang

### Joylashtirish usullari

Google uchta teng usulni qo'llab-quvvatlaydi: `<head>` ichidagi HTML `<link>`, HTTP `Link` headerlari va XML sitemap `<xhtml:link>` elementlari. Google hech bir usul boshqasidan ustun emasligini tasdiqladi.

Google ham HTML, ham sitemap signallarini birlashtiradi. Agar bir xil til-mintaqa juftligi usullar bo'ylab turli URL'larga ishora qilsa, Google taxmin qilish o'rniga o'sha juftlikni tashlab yuboradi.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SEJ: Google Combines Hreflang Signals](https://www.searchenginejournal.com/google-combines-hreflang-signals-from-html-sitemaps/389219/)

### O'zaro talab

Google hujjatlari: "Agar X sahifa Y sahifaga havola qilsa, Y sahifa X sahifaga qaytishi kerak. Aks holda bu annotatsiyalar e'tiborsiz qoldirilishi yoki noto'g'ri talqin qilinishi mumkin."

Har bir sahifa hreflang to'plamiga o'zini ham kiritishi (o'ziga ishora qilishi) kerak. O'ziga ishora qiluvchi yozuv yo'qligi Semrush auditlarida topilgan №1 xato. 374 756 ta domen bo'yicha tadqiqot hreflang joriy etishlarning 67% da muammolar borligini ko'rsatdi.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Semrush: 9 Common Hreflang Errors](https://www.semrush.com/blog/hreflang-errors/)
- [SE Land: 31% of International Websites Contain Hreflang Errors](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### x-default

2013-yil aprelda kiritilgan. Tili/mintaqasi e'lon qilingan variantlarning hech biriga mos kelmaydigan foydalanuvchilar uchun zaxira sahifani belgilaydi. Tilga xos alternativlardan biri bilan bir xil URL'ga ishora qilishi mumkin. Har bir variant sahifadagi annotatsiyalarning to'liq to'plamiga kiritilishi kerak.

- [Google Blog: x-default hreflang](https://developers.google.com/search/blog/2013/04/x-default-hreflang-for-international-pages)
- [Google Blog: How x-default can help you (2023)](https://developers.google.com/search/blog/2023/05/x-default)

### Til va mintaqa kodlari

Til: ISO 639-1 (2 harfli). Mintaqa: ISO 3166-1 Alpha 2 (2 harfli). Format: `language[-script][-region]`.

Mintaqa kodini yolg'iz ko'rsatib bo'lmaydi. Keng tarqalgan xatolar: `en-UK` (`en-GB` bo'lishi kerak), `es-419` (ISO 3166-1 emas). Tadqiqot hreflang ishlatadigan saytlarning 8,9% yaroqsiz til kodlariga ega ekanini aniqladi.

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [SE Land: 31% Study](https://searchengineland.com/study-31-of-international-websites-contain-hreflang-errors-395161)

### Katta ko'lamdagi hreflang (20+ lokal)

20 lokal bilan HTML `<head>` hreflang foydalanuvchiga hech qanday foyda keltirmasdan har bir sahifaga ~1,5KB qo'shadi. Sitemap asosidagi hreflang ish vaqti unumdorligiga nol ta'sir ko'rsatadi. `<xhtml:link>` bola elementlari 50 000 URL sitemap limitiga KIRMAYDI (faqat `<loc>` elementlari hisoblanadi).

John Mueller hreflang'ni har bir sahifaga emas, noto'g'ri til trafigini olayotgan sahifalarga qaratishni tavsiya qiladi: "Saytning boshqa sahifalari uchun buni qilmagan bo'lardim, chunki bu juda murakkab va boshqarish qiyin."

- [SERoundtable: Child Elements Don't Count](https://www.seroundtable.com/google-child-elements-dont-count-towards-sitemap-url-limit-34377.html)
- [SERoundtable: Where To Focus Hreflang](https://www.seroundtable.com/using-hreflang-34127.html)
- [Yoast: hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

### Google va Bing

Bing hreflang'ni "zaif signal" deb hisoblaydi. Bing `content-language` meta tegi, HTML `lang` atributi, ccTLD'lar va server joylashuviga tayanadi. Yandex hreflang'ni Google kabi qo'llab-quvvatlaydi.

Ikkala qidiruv tizimi uchun: hreflang (Google/Yandex) + `<html lang="...">` + `<meta http-equiv="content-language">` (Bing) ni joriy qiling.

- [Digital Ready Marketing: Bing Doesn't Use Hreflang](https://digitalreadymarketing.com/bing-doesnt-use-hreflang-annotation-what-does-it-use/)
- [Yoast: hreflang Ultimate Guide](https://yoast.com/hreflang-ultimate-guide/)

---

## Kanonizatsiya va i18n

### O'ziga ishora qiluvchi canonical'lar

Har bir lokal sahifa o'ziga canonical bo'lishi kerak. John Mueller: "rel=canonical'ni tillar/mamlakatlar bo'ylab ishlatmang, uni faqat mamlakat/til asosida ishlating."

Google hujjatlari: "Xuddi shu tilda kanonik sahifani belgilang yoki xuddi shu til uchun kanonik mavjud bo'lmasa, mumkin bo'lgan eng yaxshi muqobil tilni belgilang."

- [John Mueller: hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [Google: Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### Canonical hreflang'ni bekor qiladi

Mueller: "Agar canonical'ingiz boshqa joyga ishora qilsa, Google unga ergashadi va hreflang annotatsiyangizni e'tiborsiz qoldiradi." Canonical URL hreflang to'plamidagi URL'lardan biri bo'lishi kerak, aks holda barcha hreflang markup e'tiborsiz qoldiriladi.

Google shuningdek ta'kidlaydi: "Google kanonizatsiya uchun hreflang klasterlariga kiruvchi URL'larni afzal ko'radi" -- signallar mos kelganda hreflang canonical tanlovini kuchaytiradi.

- [John Mueller: hreflang canonical](https://johnmu.com/hreflang-canonical/)
- [SEJ: Hreflang Tags Are Hints](https://www.searchenginejournal.com/google-reminds-that-hreflang-tags-are-hints-not-directives/546428/)
- [Google: Consolidate Duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

### Deyarli bir xil mintaqaviy variantlar

Mueller (2023 Office Hours): "Agar kontent butunlay bir xil bo'lsa va biz hech qanday farqni ayta olmasak, soddalik va foydalanuvchi tajribasi uchun biz shunchaki bitta versiyani ko'rsatishimiz mumkin -- hreflang mavjud bo'lsa ham."

Google'ning dublikatni aniqlashi hreflang baholashdan OLDIN ishlaydi. Ikkala versiyani ham indekslangan holda saqlash uchun valyuta belgilaridan tashqari sezilarli kontent farqlari kerak.

- [International Web Mastery: Same-Language Duplicate Pages](https://internationalwebmastery.com/blog/how-google-handles-canonicalization-of-same-language-duplicate-near-duplicate-pages/)
- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Lokallar bo'ylab sahifalash

Google: "Sahifalangan ketma-ketlikning birinchi sahifasini kanonik sahifa sifatida ishlatmang. Buning o'rniga har bir sahifaga o'z canonical URL'ini bering." Har bir lokaldagi har bir sahifalangan sahifa o'ziga ishora qiluvchi canonical oladi. `rel="next/prev"` 2019-yil martida eskirgan.

- [Google: Pagination Best Practices](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)

---

## Xalqaro sitemap'lar

### Tuzilma

Har bir `<url>` yozuvi har bir lokal uchun `<xhtml:link>` alternativlarini o'z ichiga oladi. `xmlns:xhtml="http://www.w3.org/1999/xhtml"` namespace talab qilinadi.

Sitemap'larni lokal bo'yicha emas, kontent turi bo'yicha bo'ling. Lokal bo'yicha bo'lish texnik xizmat ko'rsatish muammolarini yaratadi, chunki har bir lokal sitemap boshqa har bir lokalga havola qilishi kerak (o'zaro talab).

- [Google Search Central: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Lumar: How Google Handles Hreflang](https://www.lumar.io/office-hours/hreflang/)

### Hajm limitlari

Har bir sitemap uchun 50 000 URL / siqilmagan 50MB. 50K limitga faqat `<loc>` elementlari hisoblanadi. Lekin har bir yozuvda 20 ta hreflang alternativi bilan 50MB fayl hajmi limiti to'siqqa aylanadi. To'liq hreflang ishlatilganda har bir sitemap uchun 2 000–5 000 URL rejalashtiring.

- [Google: Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [SERoundtable: Sitemap 50,000 Limit](https://www.seroundtable.com/google-sitemap-50-000-limit-based-on-location-urls-not-alternative-urls-33843.html)

### Yuborish

Sitemap indeksini Search Console'ga yuboring VA robots.txt'da havola qiling. Har bir sitemap bo'yicha hisobot uchun alohida bola sitemap'larni ham yuborish mumkin.

- [Google: Build and Submit a Sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)

### Next.js ogohlantirishi

Next.js `alternates.languages` `<loc>` URL uchun o'ziga ishora qiluvchi `<xhtml:link>` ni avtomatik KIRITMAYDI. `<loc>` URL'ning o'z tilini `languages` obyektiga aniq kiritishingiz kerak.

- [Next.js Docs: sitemap.xml](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap)

---

## URL tuzilmasi

### Strategiyalar taqqoslanishi

Google subdirektoriyalar va subdomenlarni teng deb hisoblaydi. Mueller: "Bizning nuqtai nazarimizdan... ular subdomenlar va subdirektoriyalar mohiyatan teng deb aytishadi."

URL parametrlari (`?lang=en`) Google hujjatlariga ko'ra aniq "Tavsiya etilmaydi".

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Standart til

Mueller tavsiya qiladi: `/` ni x-default qilib belgilang, har bir tilni o'z prefiksiga joylashtiring. `/` x-default deb belgilanmasa, "Google uchun '/' boshqalardan alohida sahifa bo'lib ko'rinishi mumkin."

- [Google Blog: x-default](https://developers.google.com/search/blog/2023/05/x-default)
- [Google Blog: Creating the Right Homepage](https://developers.google.com/search/blog/2014/05/creating-right-homepage-for-your)

### Kontent kelishuvi / IP redirect'lar

Google lokalga moslashuvchan sahifalarga qat'iy qarshi tavsiya beradi. Googlebot AQSh IP'laridan crawl qiladi va Accept-Language header'larini yubormaydi. Alohida URL'lar + hreflang talab qilinadi.

- [Google: Locale-Adaptive Pages](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)

### Trailing slash izchilligi

Mueller: trailing slash "URL'ning muhim qismi va u mavjud bo'lishi yoki bo'lmasligi URL'ni o'zgartiradi." Barcha lokal yo'llar, ichki havolalar, canonical'lar, hreflang va sitemap'lar uchun bitta formatni tanlang.

Mueller (2025): "Izchillik — eng katta texnik SEO omili."

- [SERoundtable: Consistency Is The Biggest Technical SEO Factor](https://www.seroundtable.com/google-consistency-seo-40427.html)

### Search Console geotargeting

International Targeting hisoboti eskirgan. Google endi butunlay hreflang, kontent tilini tahlil qilish va bog'lanish naqshlariga tayanadi. Har bir lokal bo'yicha hisobot uchun subdirektoriya xususiyatlarini qo'shishingiz mumkin.

- [Google Support: International Targeting Deprecated](https://support.google.com/webmasters/answer/12474899?hl=en)

### Freymvork lokal rejimlari

`localePrefix: 'always'` (next-intl) yoki ekvivalentidan foydalaning. Lokalni URL'lardan hech qachon yashirmang -- Google har bir til uchun noyob URL'larni talab qiladi. `'never'` rejimidan foydalanish alternativ havolalarni butunlay o'chiradi.

- [next-intl: Routing Configuration](https://next-intl.dev/docs/routing/configuration)
- [Next.js Discussion #18419](https://github.com/vercel/next.js/discussions/18419)

---

## Lokallar bo'ylab kontent sifati

### Avtomatik tarjima qilingan kontent (2025-yil pozitsiyasi)

Google 2025-yil o'rtasida avtomatik tarjima qilingan kontentga qarshi uzoq yillik tavsiyani olib tashladi. Joriy pozitsiya: "Bizning siyosatlarimiz AI tomonidan tarjima qilingan kontentni qat'iy spam deb ta'riflamaydi." Scaled content abuse siyosati tarjimani mumkin bo'lgan vektor sifatida eslatadi, lekin uni taqiqlamaydi.

Reddit Google'ning xabardorligi bilan AI tarjimalarni 35+ tilga masshtabladi. Asosiy farq — usul emas, niyat va sifat.

- [Google Spam Policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Glenn Gabe: Auto-Translating Content](https://www.gsqi.com/marketing-blog/auto-translating-content-google-scaled-content-abuse/)
- [SE Land: Reddit AI Translations](https://searchengineland.com/google-comments-on-reddits-use-of-ai-to-translate-its-pages-456908)

### Yupqa lokal sahifalar

Google: "Sahifaning lokallashtirilgan versiyalari faqat sahifaning asosiy kontenti tarjima qilinmagan bo'lsa dublikat deb hisoblanadi." Faqat tarjima qilingan shablon matni bor sahifalar dublikat sifatida klasterlanadi.

Keraksiz lokal sahifalar uchun noindex ISHLATMANG (crawl budget isrof bo'ladi). Lokallar-aro canonical QILMANG (hreflang bilan ziddiyatga kiradi). Eng yaxshi yondashuv: haqiqatan foydali qila olmaydigan lokal sahifalarni yaratmang.

- [Google: Localized Versions](https://developers.google.com/search/docs/specialty/international/localized-versions)
- [Google: Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)

### Foydali kontent tizimining ta'siri

2024-yil martida asosiy reytingga qo'shildi. Sayt bo'ylab signal: "umuman nisbatan ko'p foydasiz kontentga ega deb baholangan saytlardagi har qanday kontent -- faqat foydasiz kontent emas -- Qidiruvda yaxshi ishlash ehtimoli kamroq."

Past sifatli tarjima qilingan sahifalar butun saytni pasaytirishi mumkin. Bu haqiqatan foydali bo'lmagan lokal sahifalarni yaratmaslikning eng kuchli dalili.

- [Google Blog: Helpful Content Update](https://developers.google.com/search/blog/2022/08/helpful-content-update)
- [Amsive: What Changed in 2024](https://www.amsive.com/insights/seo/googles-helpful-content-update-ranking-system-what-happened-and-what-changed-in-2024/)

### Qisman tarjima

Google: "Sahifalaringizning faqat shablon matnini tarjima qilib, kontentning asosiy qismini bitta tilda qoldirish... yomon foydalanuvchi tajribasini yaratishi mumkin." Google sahifa tilini aniqlash uchun ko'rinadigan kontentdan (lang atributidan emas) foydalanadi.

Lokal versiya yaratsangiz, sahifadagi BARCHA kontentni tarjima qiling. Noto'g'ri tildagi tarjima qilinmagan metama'lumotlar (title, description) CTR'ni pasaytiradi.

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)

### Crawl budget

Faqat 1M+ sahifa yoki kuniga 10K+ sahifa o'zgaradigan holatlarda muammo. Lekin alternativ URL'lar (hreflang nishonlari) crawl budget'ni sarflaydi. Buzilgan hreflang havolalari budget'ni isrof qiladi VA signallarni bekor qiladi.

- [Google: Crawl Budget Management](https://developers.google.com/search/docs/crawling-indexing/large-site-managing-crawl-budget)
- [Google Blog: Crawl Budget](https://developers.google.com/search/blog/2017/01/what-crawl-budget-means-for-googlebot)

### Lokalga xos signallar

Google auditoriyani quyidagilar orqali aniqlaydi: "sahifalardagi mahalliy manzillar va telefon raqamlari, mahalliy til va valyutadan foydalanish, boshqa mahalliy saytlardan havolalar yoki Business Profile signallari."

- [Google: Managing Multi-Regional Sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites)
