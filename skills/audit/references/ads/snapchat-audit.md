# Snapchat Ads nazorat referensi

Olingan: 2026-07-11. Control-plane yangilanish sanasidan keyin bu referencedan foydalanishdan oldin
rasmiy platforma va policy manbalarini yangilang.

## Kategoriyalar modeli

Bu reference bajariladigan ballash profilini belgilamaydi. Tegishli nazoratlarni qamrab oluvchi va
vaznlari jami 100 bo'lgan versiyalangan profilni bog'lang; aks holda sog'liq balisiz topilmalarni
yarating.

## Runtime baholash kontrakti

- Har bir qatorni avval qo'llanilishni tekshiradigan dalil savoli deb qarang. Yo'q dalil — `unknown`;
  mavjud bo'lmagan yoki yaroqsiz yuzalar — `not_applicable`.
- Baholashdan oldin maqsad, placement, geografiya, o'lchov yo'li, hisobot hayot sikli, katalogdan foydalanish, policy va akkaunt muvofiqligini tekshiring.
- Quyidagi ro'yxatdan o'tgan manba faqat Marketing API yuzasini asoslaydi. Joriy Pixel, CAPI, o'lchov, hisobot maydoni, format, policy va mavjudlik da'volari qo'shimcha sanalangan rasmiy manba ID yoki
  akkaunt dalilini talab qiladi.
- Bu reference faqat maslahat va eksportni o'qish uchun. U jonli Snap API o'quvchisi yoki o'zgartirish adapterini bermaydi.

## Nazoratlar

| ID | Kategoriya | Dalil savoli |
| --- | --- | --- |
| SC-M01 | Measurement | Snap Pixel, Conversions API, MMP yoki oflayn manba e'lon qilingan va tekshirilgan. |
| SC-M02 | Measurement | Eventlar va qiymatlar maqsadga mos va kerak bo'lganda hujjatlashtirilgan deduplikatsiyadan foydalanadi. |
| SC-M03 | Measurement | Ilova kampaniyalari kerakli ilova o'lchov konfiguratsiyasini o'z ichiga oladi. |
| SC-M04 | Measurement | Atributsiya oynalari va hisobot maydonlari aniq va taqqoslanadigan. |
| SC-R01 | Reporting | Sana chegaralari reklama akkaunti vaqt mintaqasidan foydalanadi va ma'lumotni yakunlash oynasi oshkor qilingan. |
| SC-R02 | Reporting | Katta yoki mahsulot darajasidagi hisobotlar qo'llab-quvvatlanadigan asinxron hayot siklidan foydalanadi. |
| SC-S01 | Structure | Kampaniya, ad-squad, reklama, kreativ va maqsad munosabatlari yaroqli. |
| SC-S02 | Structure | Optimallashtirish, placementlar va yetkazib berish tanlovlari e'lon qilingan natijaga mos. |
| SC-A01 | Audience | Auditoriya, geografiya, qurilma va first-party targeting ongli va yaroqli. |
| SC-C01 | Creative | Kreativ mobile-first va tanlangan Snap placement uchun tabiiy. |
| SC-C02 | Creative | Test uchun mazmunan farqli hooklar, formatlar va konseptlar mavjud. |
| SC-C03 | Creative | AR, Lens, Story, collection yoki lead formatlari o'zlarining majburiy aktivlari va manzillaridan foydalanadi. |
| SC-D01 | Retail | DPA ishlatilganda katalog xaritalari, mahsulot mavjudligi va mahsulot darajasidagi hisobotlar tekshiruvdan o'tadi. |
| SC-B01 | Budget | Byudjet, bid, pacing va kampaniya shiftlari yaroqli va to'g'ri valyuta birliklaridan foydalanadi. |
| SC-P01 | Policy | Brend xavfsizligi, yosh, maxfiylik, tartibga solinadigan kategoriya va ko'rib chiqish holati cheklovlari tekshirilgan. |
| SC-E01 | Experiment | Testlar bitta qarorni ajratadi va hisobot kechikishini hisobga oladi. |

`pass`, `fail`, `unknown` yoki `not_applicable` natijalaridan foydalaning. Noma'lum nazoratlar dalil
qamrovini kamaytiradi; mavjud bo'lmagan, beta, premium yoki yaroqsiz funksiyalar ballanmagan imkoniyatlardir.

## Ro'yxatdan o'tgan rasmiy dalil

- `snap-marketing-api`: [Snap Marketing API](https://developers.snap.com/marketing-api/home)

Rasmiy manbalar o'zgarganda bu xulosadan ustun turadi. Qo'llab-quvvatlanmagan nazoratlar `unknown`
bo'lib qoladi; amaliyotchi materiallari rasmiy dalilni to'ldirishi mumkin, lekin almashtira olmaydi.
