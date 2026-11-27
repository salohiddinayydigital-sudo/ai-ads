# Amazon Ads nazorat referensi

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
- Baholashdan oldin marketplace, mintaqa, seller/vendor munosabati, reklama mahsuloti, API kirishi,
  atributsiya, hisobot darajasi va retail egaligini tekshiring.
- Quyidagi ro'yxatdan o'tgan manba faqat API mavjudligini asoslaydi. Joriy mahsulot, policy, metrika,
  atributsiya, katalog va format da'volari qo'shimcha sanalangan rasmiy manba ID yoki akkaunt dalilini talab qiladi.
- Bu reference faqat maslahat va eksportni o'qish uchun. U jonli Amazon API o'quvchisi yoki o'zgartirish adapterini bermaydi.

## Nazoratlar

| ID | Kategoriya | Dalil savoli |
| --- | --- | --- |
| AMZ-M01 | Measurement | Profil, marketplace, mintaqa, valyuta, vaqt mintaqasi va atributsiya oynasi aniq ko'rsatilgan. |
| AMZ-M02 | Measurement | Buyurtmalar, sotuvlar, ACOS, ROAS, TACOS, new-to-brand va retail metrikalari aralashtirilmagan. |
| AMZ-M03 | Measurement | Asinxron hisobot hayot sikli, holat, yuklab olish, sahifalash va yetishmayotgan qatorlar tekshirilgan. |
| AMZ-M04 | Measurement | Amazon Ads atributsiyasi Seller/Vendor va biznes darajasidagi natijalar bilan solishtirilgan. |
| AMZ-S01 | Structure | Portfellar, kampaniya turlari, targeting va nomlash mahsulot hamda maqsad egaligini aks ettiradi. |
| AMZ-S02 | Structure | Sponsored Products, Brands, Display, DSP va video rollari alohida baholanadi. |
| AMZ-T01 | Targeting | Avtomatik, kalit so'z, mahsulot, auditoriya va himoya targetingining aniq maqsadi bor. |
| AMZ-T02 | Targeting | Qidiruv iboralarini yig'ish va negativlar yetarli so'rov va konversiya dalillariga asoslangan. |
| AMZ-R01 | Retail | Buy Box, inventar, narx, sharhlar, detail-page sifati va suppression xavflari tekshirilgan. |
| AMZ-R02 | Retail | Katalog va variatsiya munosabatlari reklama qilingan ASIN va landing tajribasini qo'llab-quvvatlaydi. |
| AMZ-C01 | Creative | Sponsored Brands, video, display va Store aktivlari format va mahsulot va'dasiga mos. |
| AMZ-C02 | Creative | Test uchun mazmunan farqli qiymat takliflari va formatlar mavjud. |
| AMZ-B01 | Budget | Byudjet, bid, placement tuzatishlari va pacing marja, zaxira, maqsad va dalillarni aks ettiradi. |
| AMZ-B02 | Budget | Avtomatlashtirish o'zgarishlari profil/mintaqa qamrovi, o'rganishga ta'siri va akkaunt shiftlariga rioya qiladi. |
| AMZ-P01 | Policy | Mahsulot muvofiqligi, da'volar, kreativ, auditoriya va marketplace policy cheklovlari tekshirilgan. |
| AMZ-E01 | Experiment | Testlar bitta richagni ajratadi va retail, organik, narx va inventar o'zgarishlarini hisobga oladi. |

`pass`, `fail`, `unknown` yoki `not_applicable` dan foydalaning. Noma'lum nazoratlar qamrovni kamaytiradi.
Ixtiyoriy, beta, premium, mavjud bo'lmagan, o'zgarmas yoki yaroqsiz funksiyalar ballanmagan imkoniyatlardir.

## Ro'yxatdan o'tgan rasmiy dalil

- `amazon-ads-api-official`: [Amazon Ads API overview](https://advertising.amazon.com/about-api/)

Rasmiy manbalar o'zgarganda bu xulosadan ustun turadi. Qo'llab-quvvatlanmagan nazoratlar `unknown`
bo'lib qoladi; vendor keyslari (case study) belgilangan va kontekstual bo'lib qoladi.
