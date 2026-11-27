# Pinterest Ads nazorat referensi

Olingan: 2026-07-11. Control-plane yangilanish sanasidan keyin bu referencedan foydalanishdan oldin
rasmiy platforma va policy manbalarini yangilang.

## Kategoriyalar modeli

Bu reference bajariladigan ballash profilini belgilamaydi. Tegishli nazoratlarni qamrab oluvchi va
vaznlari jami 100 bo'lgan versiyalangan profilni bog'lang; aks holda sog'liq balisiz topilmalarni
yarating.

## Runtime baholash kontrakti

- Har bir qatorni avval qo'llanilishni tekshiradigan dalil savoli deb qarang. Yo'q dalil — `unknown`;
  mavjud bo'lmagan yoki yaroqsiz yuzalar — `not_applicable`.
- Baholashdan oldin maqsad, placement, geografiya, o'lchov yo'li, domen/katalog holati, maxfiylik tanlovlari, policy va akkaunt muvofiqligini tekshiring.
- Quyidagi ro'yxatdan o'tgan manba faqat Conversions API ni asoslaydi. Joriy katalog, Performance+, collections, targeting, format, policy va mavjudlik da'volari qo'shimcha sanalangan rasmiy manba ID yoki
  akkaunt dalilini talab qiladi.
- Bu reference faqat maslahat va eksportni o'qish uchun. U jonli Pinterest API o'quvchisi yoki o'zgartirish adapterini bermaydi.

## Nazoratlar

| ID | Kategoriya | Dalil savoli |
| --- | --- | --- |
| PN-M01 | Measurement | Pinterest Tag, Conversions API, MMP yoki oflayn manba e'lon qilingan va tekshirilgan. |
| PN-M02 | Measurement | Brauzer va server eventlari event ID yoki hujjatlashtirilgan deduplikatsiya mexanizmidan foydalanadi. |
| PN-M03 | Measurement | Event sifati, kechikish, diagnostika va vakillik qiluvchi test eventlari ko'rib chiqilgan. |
| PN-M04 | Measurement | Maxfiylik flaglari va ma'lumotdan foydalanish tanlovlari tegishli geografiya va roziliklarga mos. |
| PN-R01 | Retail | Katalogning majburiy maydonlari, variantlar, narxlar, mavjudlik, havolalar va tasvirlar tekshiruvdan o'tadi. |
| PN-R02 | Retail | Katalog yangilanishlari eskirgan yoki mavjud bo'lmagan mahsulotlarning ko'rsatilishini oldini oladi. |
| PN-R03 | Retail | Tasdiqlangan domen, manzil va treking xatti-harakati izchil. |
| PN-S01 | Structure | Maqsad, optimallashtirish eventi va kampaniya turi biznes natijasiga mos. |
| PN-S02 | Structure | Performance+ kabi avtomatlashtirish ongli sozlangan va yaroqli. |
| PN-A01 | Audience | First-party, qiziqish, kalit so'z va kengaytirish tanlovlari qidiruv va discovery niyatini aks ettiradi. |
| PN-C01 | Creative | Pinlar format talablariga javob beradi va qo'llab-quvvatlanmaydigan taxminlarga tayanmasdan qiymatni yetkazadi. |
| PN-C02 | Creative | Kreativ xilma-xillik mazmunan farqli konseptlar, formatlar va voronka bosqichlarini qamrab oladi. |
| PN-C03 | Creative | Landing sahifalar Pin va'dasi, mahsulot va treking parametrlarini saqlaydi. |
| PN-B01 | Budget | Byudjet va bidding optimallashtirish eventi va dalil hajmi uchun yaroqli. |
| PN-P01 | Policy | Merchant, kreativ, maxfiylik, AI-oshkor qilish va tartibga solinadigan kategoriya majburiyatlari ko'rib chiqilgan. |
| PN-E01 | Experiment | Testlar e'lon qilingan auditoriya, oyna va muvaffaqiyat o'lchovi bilan bitta qarorni ajratadi. |

`pass`, `fail`, `unknown` yoki `not_applicable` natijalaridan foydalaning. Noma'lum nazoratlar dalil
qamrovini kamaytiradi; mavjud bo'lmagan, beta, premium yoki yaroqsiz funksiyalar ballanmagan imkoniyatlardir.

## Ro'yxatdan o'tgan rasmiy dalil

- `pinterest-conversions-api`: [Pinterest API for Conversions](https://help.pinterest.com/en/business/article/the-pinterest-api-for-conversions)

Rasmiy manbalar o'zgarganda bu xulosadan ustun turadi. Qo'llab-quvvatlanmagan nazoratlar `unknown`
bo'lib qoladi; amaliyotchi materiallari rasmiy dalilni to'ldirishi mumkin, lekin almashtira olmaydi.
