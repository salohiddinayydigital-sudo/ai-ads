# YouTube Ads nazorat referensi

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
- Baholashdan oldin kampaniya kichik turi, inventar, maqsad, geografiya, format, hisobot maydonlari, o'lchov yo'li va akkaunt muvofiqligini tekshiring.
- Quyidagi ro'yxatdan o'tgan manba faqat Google Ads API video kampaniya qo'llab-quvvatlashini asoslaydi. Joriy Demand Gen, migratsiya, engagement-maqsad, kreativ, policy va mavjudlik da'volari qo'shimcha sanalangan rasmiy manba ID yoki
  akkaunt dalilini talab qiladi.
- Bu reference faqat maslahat va eksportni o'qish uchun. U jonli Google/YouTube API o'quvchisi yoki o'zgartirish adapterini bermaydi.

## Nazoratlar

| ID | Kategoriya | Dalil savoli |
| --- | --- | --- |
| YT-M01 | Measurement | Asosiy konversiya yoki engagement maqsadi va uning hisoblash roli aniq. |
| YT-M02 | Measurement | Google Ads, GA4, kanal-havola, view-through va yordamchi o'lchov tanlovlari moslashtirilgan. |
| YT-M03 | Measurement | Kerak bo'lganda hisobotda YouTube va YouTube bo'lmagan Demand Gen inventari ajratilgan. |
| YT-M04 | Measurement | To'g'ridan-to'g'ri javob maqsadga javob bera olmasa, brand-lift yoki inkrementallik usullaridan foydalaniladi. |
| YT-S01 | Structure | Kampaniya kichik turi, kanal nazoratlari, maqsad, bidding va inventar mo'ljallangan natijaga mos. |
| YT-S02 | Structure | Ko'chirilgan yoki eski Video Action Campaign holati va mos kelmaydigan sozlamalar ko'rib chiqilgan. |
| YT-A01 | Audience | Auditoriya signallari yoki segmentlari niyatga mos va first-party exclusion'lar overlapdan qochadi. |
| YT-A02 | Audience | Kontent mosligi, placementlar, mavzular va inventar nazoratlari ongli boshqariladi. |
| YT-C01 | Creative | Ochilish o'tkazib yuborishdan oldin e'tiborni tortadi va taklifni aniq yetkazadi. |
| YT-C02 | Creative | Gorizontal, vertikal, kvadrat, qisqa va uzun formatlar mo'ljallangan inventarni qamrab oladi. |
| YT-C03 | Creative | Mazmunan farqli konseptlar va hooklar mavjud, kosmetik variantlar emas. |
| YT-C04 | Creative | Demand Gen aktivi va mahsulot-feed tanlovlari ongli va yaroqli. |
| YT-B01 | Budget | Bid va byudjet strategiyasi maqsad, dalil hajmi va kampaniya yetukligiga mos. |
| YT-R01 | Reporting | Ko'rish, engagement, klik, konversiya va xarajat metrikalari izchil oyna va ta'rifdan foydalanadi. |
| YT-P01 | Policy | Kontent mosligi, brend xavfsizligi, oshkor qilishlar va tartibga solinadigan kategoriya majburiyatlari tekshirilgan. |
| YT-E01 | Experiment | Kreativ yoki auditoriya eksperimentlari bitta qarorni ajratadi va konversiya kechikishini hisobga oladi. |

`pass`, `fail`, `unknown` yoki `not_applicable` natijalaridan foydalaning. Noma'lum nazoratlar dalil
qamrovini kamaytiradi; mavjud bo'lmagan, beta, premium yoki yaroqsiz funksiyalar ballanmagan imkoniyatlardir.

## Ro'yxatdan o'tgan rasmiy dalil

- `youtube-google-ads-video-official`: [Google Ads API video campaigns](https://developers.google.com/google-ads/api/docs/video/overview)

Rasmiy manbalar o'zgarganda bu xulosadan ustun turadi. Qo'llab-quvvatlanmagan nazoratlar `unknown`
bo'lib qoladi; vendor keyslari (case study) belgilangan va kontekstual bo'lib qoladi.
