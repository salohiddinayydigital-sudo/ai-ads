# Apple Ads nazorat referensi

Olingan: 2026-07-11. Control-plane yangilanish sanasidan keyin bu referencedan foydalanishdan oldin
rasmiy mahsulot, API, policy va mavjudlik manbalarini yangilang.

## Kategoriyalar modeli

Bu reference bajariladigan ballash profilini belgilamaydi. Tegishli nazoratlarni qamrab oluvchi va
vaznlari jami 100 bo'lgan versiyalangan profilni bog'lang; aks holda sog'liq balisiz topilmalarni
yarating. Deterministik dvigatel vaznlarni faqat har bir kategoriya ichida tegishli nazoratlarni ballagandan
keyin qo'llaydi.

## Runtime baholash kontrakti

- Har bir qatorni avval qo'llanilishni tekshiradigan dalil savoli deb qarang. Yo'q dalil — `unknown`;
  mavjud bo'lmagan yoki yaroqsiz yuzalar — `not_applicable`.
- Baholashdan oldin ilova, bozor, placement, kampaniya turi, hisobotga kirish, atributsiya yo'li va
  akkaunt muvofiqligini tekshiring.
- Quyidagi ro'yxatdan o'tgan manba faqat developer API yuzasini asoslaydi. Joriy mahsulot, policy,
  atributsiya, maxfiylik chegarasi, hisobot maydoni, bidding va kreativ da'volari qo'shimcha sanalangan
  rasmiy manba ID yoki akkaunt dalilini talab qiladi.
- Bu reference faqat maslahat va eksportni o'qish uchun. U jonli Apple Ads API o'quvchisi yoki o'zgartirish adapterini bermaydi.

## Nazoratlar

| ID | Kategoriya | Dalil savoli |
| --- | --- | --- |
| AP-M01 | Measurement | AdServices, AdAttributionKit, MMP yoki ichki atributsiya manbalari va cheklovlari e'lon qilingan. |
| AP-M02 | Measurement | O'rnatishlar va o'rnatishdan keyingi eventlar Apple Ads va ilova analitikasi manbasi o'rtasida moslashtirilgan. |
| AP-M03 | Measurement | Atributsiya maxfiylik chegaralari va yetishmayotgan tafsilotlar noaniqlik deb qaraladi, nol natija deb emas. |
| AP-M04 | Measurement | Kampaniya, placement, ad-group, kalit so'z, qidiruv iborasi va reklama hisobotlari taqqoslanadigan oynalardan foydalanadi. |
| AP-S01 | Structure | Kampaniyalar muhim bo'lganda brend, kategoriya, raqobatchi, discovery va placement niyatini ajratadi. |
| AP-S02 | Structure | Search Match discovery va qo'lda targetlangan kalit so'zlar nazoratsiz overlap yaratmaydi. |
| AP-K01 | Keywords | Match turi, negativlar, qidiruv iboralari va kalit so'z harakati kuzatilgan so'rov dalillariga amal qiladi. |
| AP-K02 | Keywords | Bid va CPT qarorlari tap-through, konversiya, CPA, qiymat va hajmni birga hisobga oladi. |
| AP-A01 | Audience | Mamlakat, qurilma, mijoz turi, demografiya va auditoriya tanlovlari yaroqli va ongli. |
| AP-C01 | Creative | Standart va maxsus mahsulot sahifalari kalit so'z, placement, auditoriya va app-store va'dasiga mos. |
| AP-C02 | Creative | Mahsulot sahifasi testlari kreativ yoki xabar o'zgarishini ajratadi va yetarli kuzatuv vaqtiga ega. |
| AP-B01 | Budget | Byudjet taqsimoti va pacing isbotlangan niyatni moliyalashtirib, discovery'ni saqlaydi. |
| AP-B02 | Budget | Maqsadga asoslangan bidding yoki avtomatlashtirish faqat yaroqli va dalil bilan qo'llab-quvvatlansa tavsiya etiladi. |
| AP-R01 | Reporting | Valyuta, vaqt mintaqasi, kechiktirilgan atributsiya va API sahifalash/hisobot to'liqligi oshkor qilingan. |
| AP-P01 | Policy | Ilova, bozor, yosh, maxfiylik va mahsulot muvofiqligi talablari tekshirilgan. |
| AP-E01 | Experiment | Testlar gipoteza, placement, asosiy metrika, himoya chegaralari va o'qish oynasini belgilaydi. |

`pass`, `fail`, `unknown` yoki `not_applicable` dan foydalaning. Noma'lum nazoratlar qamrovni kamaytiradi.
Ixtiyoriy, beta, premium, mavjud bo'lmagan, o'zgarmas yoki yaroqsiz funksiyalar ballanmagan imkoniyatlardir.

## Ro'yxatdan o'tgan rasmiy dalil

- `apple-ads-api-official`: [Using Apple Ads API functionality](https://developer.apple.com/documentation/apple_ads/using-apple-search-ads-api-functionality)

Rasmiy manbalar o'zgarganda bu xulosadan ustun turadi. Qo'llab-quvvatlanmagan nazoratlar `unknown`
bo'lib qoladi; vendor keyslari (case study) belgilangan va kontekstual bo'lib qoladi.
