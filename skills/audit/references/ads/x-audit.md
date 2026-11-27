# X Ads nazorat referensi

Olingan: 2026-07-11. Control-plane yangilanish sanasidan keyin bu referencedan foydalanishdan oldin
rasmiy platforma va policy manbalarini yangilang.

## Kategoriyalar modeli

Bu reference bajariladigan ballash profilini belgilamaydi. Tegishli nazoratlarni qamrab oluvchi va
vaznlari jami 100 bo'lgan versiyalangan profilni bog'lang; aks holda sog'liq balisiz topilmalarni
yarating.

## Runtime baholash kontrakti

- Har bir qatorni avval qo'llanilishni tekshiradigan dalil savoli deb qarang. Yo'q dalil — `unknown`;
  mavjud bo'lmagan yoki yaroqsiz yuzalar — `not_applicable`.
- Baholashdan oldin maqsad, placement, geografiya, o'lchov yo'li, hisobot ta'riflari, policy, brend xavfsizligi nazoratlari va akkaunt muvofiqligini tekshiring.
- Quyidagi ro'yxatdan o'tgan manba faqat veb-sayt konversiya trekingini asoslaydi. Joriy CAPI, ilova/oflayn o'lchov, targeting, format, policy, API va mavjudlik da'volari qo'shimcha sanalangan rasmiy manba ID yoki
  akkaunt dalilini talab qiladi.
- Bu reference faqat maslahat va eksportni o'qish uchun. U jonli X API o'quvchisi yoki o'zgartirish adapterini bermaydi.

## Nazoratlar

| ID | Kategoriya | Dalil savoli |
| --- | --- | --- |
| XA-M01 | Measurement | X Pixel, Conversions API, MMP yoki oflayn manba e'lon qilingan va tekshirilgan. |
| XA-M02 | Measurement | Konversiya eventlari sezgir kategoriyalardan qochadi va X ma'lumotdan foydalanish siyosatiga rioya qiladi. |
| XA-M03 | Measurement | Identifikatorlar, event qiymatlari va brauzer/server deduplikatsiyasi hujjatlashtirilgan. |
| XA-M04 | Measurement | Ilova kampaniyalari qo'llab-quvvatlanadigan mobil o'lchov yo'lidan foydalanadi. |
| XA-S01 | Structure | Kampaniya maqsadi va optimallashtirish eventi biznes natijasiga mos. |
| XA-S02 | Structure | Kampaniya, line-item/ad-group, kreativ va akkaunt muvofiqligi yaroqli. |
| XA-A01 | Audience | Kalit so'z, suhbat, qiziqish, follower-lookalike, geografiya va first-party tanlovlari dalilga asoslangan. |
| XA-A02 | Audience | Prospecting, retargeting, exclusion'lar va kengaytirish kutilmagan overlapdan qochadi. |
| XA-C01 | Creative | Matn va media tanlangan format, placement va landing sahifa va'dasiga mos. |
| XA-C02 | Creative | Kreativ xilma-xillik mazmunan farqli hooklar, konseptlar va formatlarni qamrab oladi. |
| XA-C03 | Creative | Placement ko'rsatadigan joyda javoblar va suhbat konteksti hisobga olingan. |
| XA-B01 | Budget | Byudjet, bid, pacing va optimallashtirish holati mavjud dalil uchun yaroqli. |
| XA-R01 | Reporting | Sana oynasi, atributsiya, valyuta va metrika ta'riflari izchil. |
| XA-R02 | Reporting | Organik signallar pullik atributsiya va optimallashtirish da'volaridan alohida qoladi. |
| XA-P01 | Policy | Brend xavfsizligi, qo'shnilik, tartibga solinadigan kategoriya, maxfiylik va akkaunt holati xavflari ko'rib chiqilgan. |
| XA-E01 | Experiment | Testlar e'lon qilingan oyna va muvaffaqiyat o'lchovi bilan bitta qarorni ajratadi. |

`pass`, `fail`, `unknown` yoki `not_applicable` natijalaridan foydalaning. Noma'lum nazoratlar dalil
qamrovini kamaytiradi; mavjud bo'lmagan, beta, premium yoki yaroqsiz funksiyalar ballanmagan imkoniyatlardir.

## Ro'yxatdan o'tgan rasmiy dalil

- `x-conversion-tracking`: [X website conversion tracking](https://business.x.com/en/help/campaign-measurement-and-analytics/conversion-tracking-for-websites/about-conversion-tracking)

Rasmiy manbalar o'zgarganda bu xulosadan ustun turadi. Qo'llab-quvvatlanmagan nazoratlar `unknown`
bo'lib qoladi; amaliyotchi materiallari rasmiy dalilni to'ldirishi mumkin, lekin almashtira olmaydi.
