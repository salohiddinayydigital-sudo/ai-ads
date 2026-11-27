# Reddit Ads nazorat referensi

Olingan: 2026-07-11. Control-plane yangilanish sanasidan keyin bu referencedan foydalanishdan oldin
rasmiy platforma va policy manbalarini yangilang.

## Kategoriyalar modeli

Bu reference bajariladigan ballash profilini belgilamaydi. Tegishli nazoratlarni qamrab oluvchi va
vaznlari jami 100 bo'lgan versiyalangan profilni bog'lang; aks holda sog'liq balisiz topilmalarni
yarating.

## Runtime baholash kontrakti

- Har bir qatorni avval qo'llanilishni tekshiradigan dalil savoli deb qarang. Yo'q dalil — `unknown`;
  mavjud bo'lmagan yoki yaroqsiz yuzalar — `not_applicable`.
- Baholashdan oldin maqsad, placement, geografiya, identifikatsiya, o'lchov yo'li, katalogdan foydalanish, hisobot ta'riflari, policy va akkaunt muvofiqligini tekshiring.
- Quyidagi ro'yxatdan o'tgan manba faqat qo'llab-quvvatlanadigan konversiya eventlarini asoslaydi. Joriy katalog, DPA, targeting, format, policy va API da'volari qo'shimcha sanalangan rasmiy manba ID yoki
  akkaunt dalilini talab qiladi.
- Bu reference faqat maslahat va eksportni o'qish uchun. U jonli Reddit API o'quvchisi yoki o'zgartirish adapterini bermaydi.

## Nazoratlar

| ID | Kategoriya | Dalil savoli |
| --- | --- | --- |
| RD-M01 | Measurement | Asosiy konversiya manbai va egaligi aniqlangan. |
| RD-M02 | Measurement | Reddit Pixel yoki Conversions API eventlari biznes konversiya taksonomiyasiga mos. |
| RD-M03 | Measurement | Pixel va server bir xil eventni yuborganda deduplikatsiyadan foydalanadi. |
| RD-M04 | Measurement | Events Manager diagnostikasi va vakillik qiluvchi test eventlari ko'rib chiqilgan. |
| RD-S01 | Structure | Kampaniya maqsadi va optimallashtirish eventi biznes natijasiga mos. |
| RD-S02 | Structure | Prospecting va retargeting niyatlari farqlanadi va exclusion'lar oldini olsa bo'ladigan overlapni oldini oladi. |
| RD-A01 | Audience | Hamjamiyat, qiziqish, kalit so'z yoki first-party targeting taklif va dalil bilan qo'llab-quvvatlanadi. |
| RD-A02 | Audience | Auditoriyani kengaytirish foydali deb taxmin qilinmasdan, ongli va o'lchanadigan. |
| RD-C01 | Creative | Kreativ tanlangan Reddit placement va hamjamiyat kontekstida tabiiy o'qiladi. |
| RD-C02 | Creative | Test uchun mazmunan farqli konseptlar, hooklar va formatlar mavjud. |
| RD-C03 | Creative | Reklama va'dasi, izohlar konteksti va landing sahifa tajribasi izchil. |
| RD-R01 | Retail | Commerce formatlari ishlatilganda katalog maydonlari, mavjudlik, narxlar, havolalar va yangilanish sog'lom. |
| RD-R02 | Retail | Dinamik mahsulot reklamasi tegishli katalog va o'lchov manbasini xaritalaydi. |
| RD-B01 | Budget | Byudjet va bid strategiyasi maqsad, ma'lumot hajmi va test dizayni uchun yaroqli. |
| RD-P01 | Policy | Brend xavfsizligi, placement, tartibga solinadigan kategoriya va maxfiylik nazoratlari ko'rib chiqilgan. |
| RD-E01 | Experiment | Testlar qarorni ajratadi, muvaffaqiyat mezonlarini belgilaydi va bir-birini qoplaydigan o'zgarishlardan qochadi. |

`pass`, `fail`, `unknown` yoki `not_applicable` natijalaridan foydalaning. Noma'lum nazoratlar dalil
qamrovini kamaytiradi; mavjud bo'lmagan, beta, premium yoki yaroqsiz funksiyalar ballanmagan imkoniyatlardir.

## Ro'yxatdan o'tgan rasmiy dalil

- `reddit-business-help`: [Reddit supported conversion events](https://business.reddithelp.com/articles/Knowledge/supported-conversion-events)

Rasmiy manbalar o'zgarganda bu xulosadan ustun turadi. Qo'llab-quvvatlanmagan nazoratlar `unknown`
bo'lib qoladi; amaliyotchi materiallari rasmiy dalilni to'ldirishi mumkin, lekin almashtira olmaydi.
