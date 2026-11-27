# Konversiya trekingi va o'lchov

**Tekshirilgan:** 2026-07-11
**Yangilash muddati:** platforma hujjatlari uchun 2026-08-10
**Dalil holati:** arxitektura va audit savollari; amalga oshirish akkauntga xos

Treking faqat biznes eventi, rozilik holati, brauzer va server yo'llari, platforma konfiguratsiyasi va keyingi
biznes yozuvi bir-biriga mos kelgandagina maqbul. Teg yoki API ulanishining mavjudligi o'lchov aniqligini isbotlamaydi.

## Kanonik event kontrakti

Har bir optimallashtirish va hisobot eventi uchun yozing:

- Barqaror event nomi va biznes ta'rifi.
- Event vaqti, vaqt mintaqasi, manba va noyob event ID.
- Qonuniy va mos bo'lsa buyurtma, lid yoki opportunity ID.
- Valyuta va qiymat ta'rifi, shu jumladan qaytarishlar va bekor qilishlar.
- Brauzer/server/oflayn kelib chiqish va deduplikatsiya kaliti.
- Rozilik holati va ruxsat etilgan qayta ishlash maqsadi.
- Platforma konversiya harakati, asosiy/ikkilamchi roli, hisoblash xatti-harakati, atributsiya oynasi va biddingga kiritilishi.
- CRM qabul qilish holati va moslashtirish natijasi.

Keraksiz shaxsiy yoki sezgir ma'lumotlarni yubormang. Hashlash rozilik emas va aks holda taqiqlangan yig'ishni qonuniy qilmaydi.

## Platforma dalili

| Platforma | Joriy birlamchi manba | Nimani qo'llab-quvvatlaydi |
| --- | --- | --- |
| Google Ads | `google-consent-modeling-official` — [Consent mode modeling](https://support.google.com/google-ads/answer/10548233) | Modellashtirishning muvofiqlik va amalga oshirish talablari bor; u har bir reklama beruvchi uchun kafolatlanmagan |
| TikTok Ads | `tiktok-events-api-official` — [About Events API](https://ads.tiktok.com/help/article/events-api) | TikTok veb-konversiya mijozlari uchun event deduplikatsiyali Pixel plus Events API'ni tavsiya qiladi |
| LinkedIn Ads | `linkedin-conversions-api-official` — [Conversions API Playbook](https://business.linkedin.com/content/dam/me/business/en-us/marketing-solutions/resources/pdfs/Conversions-API-Playbook.pdf) | Brauzer va server konversiya manbalari ongli hisobot sozlamasini talab qiladi |
| Microsoft Advertising | `microsoft-uet-official` — [UET setup](https://help.ads.microsoft.com/apex/index/3/en/56913) | UET sozlash, sahifa qamrovi, tekshiruv va nosozliklarni bartaraf etish |

Meta, Apple, Amazon, Reddit, Pinterest, Snapchat, X va joriy source-ledger yozuvida aks etmagan har qanday
platforma tafsilotlari uchun ishga tushirish vaqtida joriy rasmiy akkaunt hujjatlari va imkoniyatlar manifestini
ko'rib chiqing. Boshqa platformaning event nomlari yoki talablarini o'xshashlik bo'yicha qayta ishlatmang.

Google'ning joriy consent-mode modellashtirish sahifasi sifat tekshiruvlari orasida to'g'ri consent mode yoki IAB TCF
amalga oshirilishini va mamlakat/domen guruhi uchun yetti kun ichida kuniga 700 reklama klikini keltiradi. Bu o'sha
Google funksiyasi uchun muvofiqlik fakti, minimal akkaunt byudjeti yoki modellashtirilgan konversiyalar kafolati emas.

## Audit ketma-ketligi

1. Bitta haqiqiy test eventini foydalanuvchi harakatidan brauzer so'rovi, server so'rovi, platforma qabul qilishi,
   deduplikatsiya, hisobot va CRM yozuvigacha kuzating.
2. Jami ko'rsatkichlarni event sanasi va qayta ishlash sanasi bo'yicha kechikishi yetilgan oynada solishtiring.
3. Dublikatlar, yetishmayotgan ID'lar, yaroqsiz qiymat/valyutalar, soat siljishi va yaroqli rozilikdan oldin
   kelgan eventlarni tekshiring.
4. Faqat mo'ljallangan biznes natijalari biddingga ta'sir qilishini tasdiqlang.
5. Qo'llanilsa, qaytarishlar, bekor qilishlar, oflayn holat o'zgarishlari, cross-domain oqimlar va to'lov-provayder
   redirectlarini sinang.
6. Platforma diagnostikasini vendor kuzatuvlari sifatida yozing, so'ng kirish imkoni bo'lsa xom payload loglar va
   biznes yozuvlari bilan tekshiring.

## Deduplikatsiya

Bir xil biznes harakatining brauzer va server nusxalari platformaning hujjatlashtirilgan deduplikatsiya maydonlarini
bo'lishishi shart. Universal maydon xaritasini o'ylab topmang. Tekshiring:

- Bir xil harakat bitta qabul qilingan platforma konversiyasini beradi.
- Turli harakatlar ID'da to'qnashmaydi.
- Qayta urinishlar idempotent.
- Kechikkan oflayn yangilanishlar ikkinchi sotuv yoki lid yaratmaydi.
- Deduplikatsiya cross-domain va to'lov oqimlarida saqlanadi.

## Atributsiya va moslashtirish

Quyidagi ko'rinishlarni ajrating:

- Yetkazib berish diagnostikasi uchun platforma-atributsiyali konversiyalar.
- Sayohat tahlili uchun analitika atributsiyasi.
- Qabul qilingan biznes qiymati uchun CRM/buxgalteriya natijalari.
- Inkrementallik uchun eksperiment yoki model baholari.

Platformalararo atributsiyalangan konversiyalarni noyob odamlar yoki inkremental natijalardek hech qachon
qo'shmang. Atributsiya oynalari, view-through munosabati, identifikatsiyani aniqlash, rozilik istisnolari va
konversiya kechikishini oshkor qiling.

## Jiddiylik bo'yicha yo'riqnoma

Kritik topilmalar kuzatilgan ta'sirni talab qiladi, masalan asosiy event yo'qligi, tasdiqlangan ikki marta hisoblash,
ruxsatsiz sezgir-ma'lumot uzatilishi, sezilarli noto'g'ri qiymat/valyuta yoki biznes bo'lmagan eventga qarshi bidding.
Server-side integratsiya yo'qligining o'zi — imkoniyat yoki qamrov bo'shlig'i, agar joriy platforma talabi yoki
kuzatilgan o'lchov yo'qotilishi uni og'irlashtirmasa.

## Yakunlash dalili

Treking ko'rib chiqishi faqat sinalgan eventlar, muhitlar, vaqt oynasi, rozilik holatlari, payload dalili, platforma
diagnostikasi, CRM moslashtirishi, bo'shliqlar, ishonch va tuzatish egasi aniqlansagina to'liq. Sog'liqni faqat
konfiguratsiya skrinshotlaridan hech qachon xulosa qilmang.
