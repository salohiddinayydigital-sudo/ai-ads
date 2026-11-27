# Avtomatlashtirish delegatsiyasi klassifikatori

**Tekshirilgan:** 2026-07-11
**Yangilash:** asosiy ko'rib chiqish 2027-01-07 gacha; platforma modullari ishga tushirish vaqtida
**Qamrov:** nazorat va o'zgartirish xavfi, akkaunt sog'lig'i bali emas

Kampaniyada "avtomatlashtirilgan" mahsulot yorlig'i bor-yo'qligini emas, qanday vakolat delegatsiya
qilinganini tasniflang. Bitta kampaniya bidding'ni delegatsiya qilib, byudjet, targeting, kreativ va
tasdiqlashlarni inson nazoratida qoldirishi mumkin.

## Delegatsiya o'lchamlari

Har bir o'lchamni alohida kuzating:

- Maqsad va konversiyani tanlash.
- Bidding va bid maqsadlari.
- Byudjet taqsimoti va pacing.
- Auditoriya yoki so'rovni kengaytirish va exclusion'lar.
- Placement tanlash.
- Kreativ yaratish, variatsiya va manzilni tanlash.
- Kampaniya yaratish va tuzilmaviy o'zgarishlar.
- Monitoring, pauza va hodisani cheklash.
- Tashqi agent/MCP o'qish va yozish vakolati.

Joriy akkaunt UI/API va imkoniyatlar manifestidan foydalaning. Modul holatini kampaniya nomidan taxmin qilmang.

## Darajalar

| Daraja | Ta'rif | Majburiy nazorat |
| --- | --- | --- |
| T0 Kuzatilgan qo'lda | Hech bir qaror moduli delegatsiya qilinmagan; asboblar faqat hisobot berishi mumkin | Standart QA va o'zgarishlarni boshqarish |
| T1 Yordamchi | Avtomatlashtirish tavsiya qiladi yoki qoralama qiladi, lekin inson tanlaydi va qo'llaydi | Dalil, qo'llanilish va yakuniy diff'ni ko'rib chiqish |
| T2 Cheklangan delegatsiya | Bir yoki bir nechta modul akkaunt belgilagan aniq chegaralarda harakat qiladi | Modul bo'yicha maqsadlar, shiftlar, monitoring va rollback |
| T3 Keng platforma delegatsiyasi | Platforma yetkazib berish modullarining ko'pini boshqaradi, maqsad, aktiv va himoya chegaralari odamlarda | Signal sifati, maqsad, kreativ, exclusion va marginal natijani ko'rib chiqish |
| T4 Tashqi agent yozishi | Tashqi agent akkaunt obyektlarini yaratishi yoki o'zgartirishi mumkin | To'liq o'zgartirish darvozasi, eng kam imtiyoz, idempotentlik, mustaqil tekshiruv va hodisaga javob |

Akkaunt darajasi — eng yuqori faol vakolat, lekin o'lchamlar xaritasini saqlang; faqat umumiy daraja
qaror uchun to'liq emas.

## Tasniflash usuli

1. Faol kampaniyalar va ulangan integratsiyalar inventarini oling.
2. Har bir o'lchamning kuzatilgan holati, egasi, chegaralari va dalil vaqt tamg'asini yozing.
3. Tavsiya, qoralama, qo'llash va avtonom qo'llash vakolatlarini ajrating.
4. To'qnashuvchi boshqaruvchilarni aniqlang, masalan platforma pacing'i va tashqi byudjet agenti.
5. Ishonchni belgilang va noma'lum yoki mavjud bo'lmagan holatlarni sanang.
6. Muhim konfiguratsiya yoki konnektor o'zgarishlaridan keyin qayta tasniflang.

## Daraja bo'yicha ko'rib chiqish

- T0: qo'lda operatsiyalar ataylab va monitoring ostida ekanini tekshiring; qo'lda ishlash avtomatik ravishda xavfsizroq yoki sog'lomroq emas.
- T1: tavsiya sifati va ko'rib chiquvchi javobgarligini tekshiring.
- T2: har bir delegatsiya qilingan modul uchun shiftlar, chekka holatlar, ogohlantirish va tiklashni sinang.
- T3: biznes maqsadiga moslik, konversiya sifati, marginal natija, kreativ/manzil nazorati, exclusion'lar va platforma muvofiqligini tekshiring.
- T4: `mcp-integration.md` ni qo'llang; aniq imkoniyatni tekshirish, tasdiq, audit, masofaviy tekshiruv va rollbacksiz yozish yo'q.

## Topilmalar

Avtomatlashtirishni qabul qilish va yangiligi — ballanmaydigan kontekst. Faqat barqaror nazoratni ballang:
tasdiq yo'qligi, shift yo'qligi, to'qnashuvchi avtomatlashtirish, ruxsatsiz qamrov, buzilgan monitoring yoki
(qo'llanilsa) rollback yo'qligi.

Platforma, kampaniya/obyekt ID'lari, o'lcham, kuzatilgan vakolat, daraja, dalil, ishonch, xavf, egasi va
tuzatishni qaytaring. Diagnostika qilingan akkaunt muammosi va sinaladigan kutilgan natijasiz "ko'proq
avtomatlashtirish" yoki "ko'proq qo'lda nazorat"ni buyurmang.
