# Bidding strategiyasi qarorlari

**Tekshirilgan:** 2026-07-11
**Yangilash muddati:** 2026-08-10
**Asosiy manba:** `google-smart-bidding-official` — [Google Ads Help: About Smart Bidding](https://support.google.com/google-ads/answer/7065882)
**Qo'shimcha manba:** `google-target-roas-official` — [Google Ads Help: About Target ROAS](https://support.google.com/google-ads/answer/6268637)

Bidding — universal konversiyalar soni ochadigan zina emas, boshqaruv tizimi. Joriy akkaunt UI'da
ko'rinadigan kampaniya maqsadi, qiymat signali, yetkazib berish cheklovi va o'lchov sifatidan kelib chiqib,
yaroqli strategiyani tanlang.

Google Target CPA, Target ROAS, Maximize conversions va Maximize conversion value'ni auksion vaqtida
optimallashtiradigan Smart Bidding strategiyalari deb ta'riflaydi. Mavjudlik va yorliqlar kampaniya
turiga qarab o'zgarishi mumkin; ularni runtime'da tekshiring.

## Qaror kirishlari

- Asosiy biznes maqsadi: ko'rinish, trafik, qabul qilingan konversiyalar, qiymat, foyda proksisi yoki boshqa aniq natija.
- Konversiya harakati, hisoblash usuli, qiymat manbai, atributsiya va kechikish.
- To'liq konversiya sikllari davomidagi tarixiy hajm va dispersiya.
- Byudjet cheklovi, inventar cheklovi, mavsumiylik va auksion qamrovi.
- Egasi tasdiqlagan CPA, ROAS, hissa, naqd pul va policy chegaralari.
- Kampaniya turi muvofiqligi va har qanday beta, mintaqaviy yoki akkaunt cheklovlari.

Optimallashtirish ma'lumotlari to'liq bo'lmasa yoki buzilgan bo'lsa, cheklash zarur bo'lmasa, bidder'ni
o'zgartirishdan oldin o'lchovni tuzating.

## Strategiya mantig'i

| Maqsad | Nomzod strategiya | Tekshiriladigan dalil |
| --- | --- | --- |
| Byudjet doirasida qabul qilingan konversiyalar hajmini maksimallashtirish | Konversiyani maksimallashtiruvchi strategiya | Asosiy konversiya yaroqli; byudjet va kechikish tushunilgan |
| O'rtacha jalb qilish xarajati maqsadini ushlab turish | Maqsadli-xarajat strategiyasi | Maqsad yetuk akkaunt iqtisodini aks ettiradi va yaroqli |
| Byudjet doirasida qabul qilingan qiymatni maksimallashtirish | Qiymatni maksimallashtiruvchi strategiya | Qiymatlar to'liq, taqqoslanadigan va o'z vaqtida |
| O'rtacha daromad maqsadini ushlab turish | Maqsadli-daromad strategiyasi | Qiymat treki va maqsad iqtisodi sog'lom |
| Ko'rinish yoki qamrov | Ko'rsatuv/qamrov strategiyasi | Natija haqiqatan ko'rinish; placement va chastota cheklovlari aniq |
| Izlanish yoki o'lchovni tuzatish | Mavjud bo'lsa qo'lda/trafik strategiyasi | Vaqt bilan cheklangan maqsad, to'xtatish sharti va keyingi xavf hujjatlashtirilgan |

Aniq platforma yorlig'i — kuzatilgan imkoniyat, platformalararo tarjima emas. O'xshash nomli
strategiyalar bir xil auksion xatti-harakatiga ega deb o'ylamang.

## Maqsadni belgilash

Maqsadlarni qabul qilingan iqtisod va yetuk akkaunt tarixidan chiqaring. Google Target ROAS uchun rasmiy
yo'riqnoma biznes maqsadlari va tarixiy ROAS'dan foydalanishni hamda konversiya sikllari bo'yicha
baholashni tavsiya qiladi; o'sha sahifa haddan tashqari yuqori maqsad trafikni cheklashi mumkinligidan
ogohlantiradi. Bu platforma yo'riqnomasi, kafolatlangan natija emas.

Akkauntlar bo'ylab qat'iy maqsad ko'paytirgichlari, qat'iy minimal konversiyalar soni yoki qat'iy
tuzatish kadansini qo'llamang. Manba oynasi, kechikish yetukligi, ishonch intervali yoki dispersiya va
kutilgan hajm savdosini yozing.

## O'zgartirish intizomi

Bid o'zgartirishdan oldin:

1. Bir vaqtdagi byudjet, konversiya, targeting, kreativ yoki policy o'zgarishi talqinni chalkashtirmasligini tasdiqlang.
2. Mos bo'lsa, platformaning joriy simulyatori yoki eksperiment funksiyasidan foydalaning.
3. Baholash oynasini o'zboshimcha kalendar kunlarida emas, konversiya sikllarida belgilang.
4. Egasi tasdiqlagan chegaralar bilan qaytariladigan o'zgarishni qoralang.
5. Qo'llagandan keyin yetkazib berish, sarf, qabul qilingan natijalar va masofaviy holatni tekshiring.

Google maqsad tuzatishlari uchun rasmiy yo'riqnoma bidder maqsad o'zgarishlariga reaksiya qilishini, ammo
maqsadga yetish uchun bir-ikki konversiya sikli kerak bo'lishi mumkinligini aytadi. Bu muddatni Google'ga
xos yo'riqnoma deb qarang va uni universal muzlatish davri sifatida emas, faol kampaniya bo'yicha tekshiring.

## Diagnostik savollar

- Past yetkazib berishga maqsad qattiqligi, byudjet, muvofiqlik, inventar, kreativ, auditoriya, policy yoki treking sababchimi?
- Ko'rinadigan samaradorlik inkremental qiymat emas, atributsiya yoki aralashma siljishimi?
- Qiymatlar bekor qilishlar, sifatsiz lidlar va takroriy mijoz qoidalarini chiqarib tashlagan holda sof qiymatmi?
- Portfel strategiyasi chindan mos maqsadli kampaniyalarni guruhlayaptimi?
- Bid o'zgarishi o'rganish, eksperiment yoki shartnoma cheklovini buzadimi?

## Xavfli tavsiyalar

- Platforma/akkaunt dalilisiz "N konversiyadan kam bo'lsa qo'lda bidding ishlating".
- Universal qoida sifatida "maqsadni har N kunda N% ga o'zgartiring".
- Faqat bid strategiyasi nomidan kelib chiqib buyurilgan broad match, negativ kalit so'zlar, placement kengaytirish yoki avtomatlashtirishni qabul qilish.
- Prognoz sifatida ishlatilgan vendor ma'lum qilgan lift.
- Aniq akkaunt/obyekt ID'lari, tasdiq, tekshiruv va rollbacksiz bid o'zgartirish.
