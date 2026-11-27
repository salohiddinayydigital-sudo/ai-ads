# Byudjet taqsimoti va masshtablash

**Tekshirilgan:** 2026-07-11
**Yangilash:** asosiy ko'rib chiqish 2027-01-07 gacha; platforma muvofiqligi runtime'da
**Dalil holati:** deterministik moliya matematikasi; taqsimot evristikalari kontekstual

Byudjetni biznes cheklovlari va marginal dalildan taqsimlang. Qat'iy platforma aralashmasi, minimal
oylik sarf yoki universal masshtablash qadamidan boshlamang.

## Majburiy kirishlar

- Maqsad va qabul qilingan biznes natijasi.
- Yalpi marja yoki hissa marjasi va o'zgaruvchan bajarish xarajatlari.
- Naqd pul, kredit, oylik, kunlik, platforma va kampaniya shiftlari.
- Maqsad CPA, bir konversiyaga hissa yoki maqsad foyda; kim tasdiqlaganini ko'rsating.
- Konversiya kechikishi, sotuv sikli kechikishi, qaytarish/bekor qilish oynasi va ma'lumot yetukligi.
- Platforma bo'yicha joriy sarf, qabul qilingan konversiyalar, qiymat va ishonch.
- Shartnoma, geografiya, policy, inventar va kreativ quvvat cheklovlari.

Egasi tasdiqlagan shiftlar yo'qligi akkauntga yozishni to'sadi. Iqtisod yo'qligi rejani muvaqqat qiladi.

## Asosiy matematika

```text
CPA = spend / accepted conversions
ROAS = accepted conversion value / spend
contribution_after_ads = accepted contribution - spend
break_even_CPA = contribution per accepted conversion
break_even_ROAS = 1 / contribution_margin_rate
marginal_CPA = incremental spend / incremental accepted conversions
marginal_ROAS = incremental accepted value / incremental spend
```

Qaytarishlar, firibgarlik, bekor qilishlar, dublikat lidlar yoki sotuv rad etilishi natijaga sezilarli
ta'sir qilsa, sof qabul qilingan qiymatdan foydalaning. Foydani faqat platforma ROAS'idan chiqarmang.

## Taqsimot ketma-ketligi

1. Muzokara qilinmaydigan majburiyatlar va o'lchov xarajatlarini zaxiralang.
2. To'yinish va naqd pul cheklovlari doirasida musbat marginal hissaning sababiy yoki kuchli
   shu-akkaunt dalili bo'lgan kampaniyalarni himoya qiling.
3. E'lon qilingan gipoteza, minimal aniqlanadigan effekt, qaror sanasi va to'xtatish shartlari bilan
   cheklangan eksperimentlarni moliyalashtiring.
4. Zaxirani faqat biznesda uning aniq maqsadi bo'lgandagina ushlab turing.
5. Qayta taqsimlashni eng yomon o'rtacha CPA yoki ROAS'dan emas, eng zaif marginal imkoniyatdan oling.

Har qanday "isbotlangan / o'sish / eksperiment" bo'linishi — operator siyosati, standart emas. Tanlangan
bo'linish va asosini run manifestida yozing.

## Masshtablash qarori

Masshtablash o'zgarishini faqat barcha shartlar bajarilganda qoralang:

- Konversiya va daromad ma'lumotlari tegishli kechikish davomida yetilgan.
- Treking, rozilik, policy, inventar va landing tajribasi natijani talqin qilish uchun yetarlicha sog'lom.
- Marginal natija egasi tasdiqlagan iqtisodiy chegarada.
- Kampaniya taklif etilgan byudjet va bidding o'zgarishiga yaroqli.
- Reklama beruvchi o'rganish, yetkazib berish va naqd pul oqimi tebranishini ko'tara oladi.
- Oldin/keyin o'lchovi, tekshiruv oynasi va rollback trigeri mavjud.

O'zgarish hajmi va vaqti platforma simulyatsiyalari, akkaunt tarixi, konversiya sikllari va ta'sir doirasi
chegaralaridan keladi. Hech bir universal foiz xavfsiz emas.

## Pauza yoki qisqartirish qarori

Faqat sarf maqsad CPA'ning qat'iy karrali qiymatidan oshgani uchun pauza qilmang. Avval konversiya
kechikishi, treking uzilishlari, kichik tanlama, keyingi lid sifati, mavsumiylik va obyekt faol
eksperiment uchun kerak emasligini tekshiring.

Zudlik bilan cheklash egasi belgilagan nazoratsiz sarf shifti, policy yoki huquqiy xavf, buzilgan manzil,
tasdiqlangan treking buzilishi yoki ruxsatsiz yetkazib berish uchun mos. Eng kichik qaytariladigan
harakatni afzal ko'ring va dalilni saqlang.

## Portfel ko'rinishi

Platformalarni bir xil yetuk oynada qabul qilingan biznes natijalari bo'yicha taqqoslang. Kiriting:

- Sarf ulushi, qabul qilingan qiymat ulushi va reklamadan keyingi hissa.
- Faqat o'rtacha emas, marginal samaradorlik.
- Ishonch va dalil qamrovi.
- Mavjud bo'lsa inkrementallik yoki holdout dalili.
- Harakatni to'sadigan cheklovlar: inventar, auditoriya, policy yoki kreativ o'tkazuvchanlik.

Sarf yoki qabul qilingan qiymat mavjud bo'lmasa, mutanosib vaznlarni to'qimang. Ssenariylarni taqdim eting va
yetishmayotgan qaror kirishini ko'rsating.

## O'zgarish paketi

Har bir taklif etilgan qayta taqsimlash joriy va taklif etilgan summalarni, ta'sirlangan obyekt ID'larini,
iqtisodiy asosni, kutilgan effektni, noaniqlikni, o'rganishga ta'sirni, egasini, tasdiqni, tekshiruv sanasini,
rollback chegarasini va idempotentlik kalitini ko'rsatadi. O'zgartirish darvozasi o'tmaguncha tavsiya
qoralama bo'lib qoladi.
