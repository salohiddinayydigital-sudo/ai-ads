# Claude Ads ballash kontrakti

Production ballash dvigateli sog'liq ballari uchun yagona vakolat hisoblanadi. Promptlar, agentlar, hisobotlar
va testlar bu hujjatni qayta amalga oshirmasdan, uni chaqirishi kerak.

## Chiqishlar

To'rtta chiqishni ajratib saqlang:

1. `health_score`: kuzatilgan natija va amalga oshirish sog'lig'i, 0–100.
2. `evidence_coverage`: tegishli nazorat vaznining natijasi ma'lum bo'lgan ulushi.
3. `regulatory_exposure`: ballni to'ldirmaydigan mustaqil P0/P1 xavf xulosasi.
4. `opportunities`: ballanmaydigan ixtiyoriy, beta, premium yoki yaroqsiz imkoniyatlar.

Harfli baho e'lon qilmang. Har bir ballni qamrov holati va ma'lumot oynasi bilan birga bering.

## Nazorat holatlari

- `pass`: dalil nazoratni qondiradi.
- `fail`: dalil nazoratni qondirmaydi.
- `unknown`: qo'llaniladi, lekin dalil yo'q yoki aniq emas.
- `not_applicable`: nazorat bu akkaunt yoki kampaniyaga tegishli emas.

`not_applicable` sog'liq va qamrov maxrajlaridan olib tashlanadi. `unknown` sog'liq hisobidan olib tashlanadi,
lekin qamrov maxrajida qoladi.

## Jiddiylik vaznlari

| Jiddiylik | Vazn | Ma'nosi |
| --- | ---: | --- |
| critical | 5 | Zudlik bilan sezilarli daromad, ma'lumot, akkaunt, maxfiylik yoki policy xavfi |
| high | 3 | Sezilarli natija yoki operatsion xavf |
| medium | 1 | Past shoshilinchlikdagi ma'noli yaxshilanish |
| informational | 0 | Kontekst yoki ballanmaydigan imkoniyat |

Jiddiylik nazorat muvaffaqiyatsiz bo'lgandagi ta'sirni ifodalaydi. Funksiya yangi yoki strategik qiziqarli bo'lgani uchun
uni oshirib yubormaslik kerak.

## Kategoriya hisobi

Har bir kategoriya uchun faqat ma'lum tegishli nazoratlardan foydalanib:

```text
category_health = 100 * sum(pass_weight) / sum(known_control_weight)
```

bu yerda `control_weight` — jiddiylik vazni. Muvaffaqiyatsiz nazorat nol oladi. Kategoriya o'zining e'lon qilingan
kategoriya vaznini har bir nazoratga ko'paytirmasligi kerak.

Kategoriya qamrovi:

```text
category_coverage = 100 * sum(known_control_weight) / sum(applicable_control_weight)
```

Platforma sog'lig'i kategoriya hisobidan keyin normallashtirilgan kategoriya vaznlarini qo'llaydi:

```text
platform_health = sum(category_health * category_weight)
```

Chaqiruvchi kategoriya vaznlari yig'indisi aniq 100 bo'lgan versiyalangan ballash profilini berishi shart; production
dvigatel bu invariantni tekshiradi. Imkoniyatlar manifesti bajariladigan platforma yuzalarini tasvirlaydi va o'z-o'zidan
ballash profili emas. Tegishli nazoratlari bo'lmagan kategoriya olib tashlanadi va qolgan kategoriya vaznlari shu run
uchun qayta normallashtiriladi.

## Qamrov holati

| Qamrov | Holat | Hisobot qoidasi |
| ---: | --- | --- |
| 80-100% | graded | Sog'liqni qamrov bilan e'lon qiling |
| 60-79.99% | provisional | Sog'liqni provisional deb belgilab e'lon qiling |
| 60% dan past | insufficient_evidence | Sog'liqni akkaunt bahosi sifatida taqdim etmang |

Umumiy qamrov 80% dan yuqori bo'lib qolsa ham, noma'lum kritik nazoratlar ustuvorlik chiqishida ko'rinishi kerak.

## Platforma kategoriyalari

Quyidagilar — dastlabki mahsulot reference profillari. Ular platforma xatti-harakatidan xulosa qilinmagan va shu faylda
paydo bo'lgani uchungina bajariladigan bo'lib qolmaydi:

- Google: measurement 25, waste 20, structure 15, keywords 15, creative 15, settings 10.
- Meta: measurement 25, creative 25, structure 20, audiences 15, delivery 10, policy 5.
- YouTube: measurement 25, creative 25, structure 20, audiences 15, delivery 10, policy 5.
- LinkedIn: measurement 25, audiences 20, creative 20, structure 15, delivery 15, policy 5.
- TikTok: measurement 25, creative 25, delivery 15, structure 15, audiences 15, policy 5.
- Microsoft: measurement 25, structure 20, delivery 15, creative 15, audiences 15, policy 10.
- Apple: measurement 25, structure 20, keywords 20, creative 15, delivery 15, policy 5.
- Amazon: measurement 20, retail 20, targeting 20, structure 15, creative 10, delivery 10, policy 5.
- Reddit: measurement 25, structure 20, creative 20, audiences 15, delivery 10, policy 10.
- Pinterest: measurement 25, retail 20, creative 20, structure 15, audiences 10, policy 10.
- Snapchat: measurement 25, creative 20, structure 20, audiences 15, delivery 10, policy 10.
- X: measurement 25, structure 20, creative 20, audiences 15, delivery 10, policy 10.

Operatsion foydalanishdan oldin tanlangan profilni run manifestiga bog'lang va uning kategoriya nomlari tegishli nazoratlarga
mos kelishini tekshiring. Profillarni faqat versiyalangan mahsulot qarori va regressiya tahlili orqali o'zgartiring.

Bajariladigan holat `control-plane/manifests/control-registry.json` va `control-plane/manifests/scoring-profiles.json`
da yashaydi. Joriy v1 profillar aniq o'chirilgan: katalog qatorlari tipli axborot kuzatuv ro'yxatlari yoki
manba-yangilash aniqlash elementlari bo'lib qoladi. O'chirilgan profil akkaunt sog'lig'ini bermaydi va tasdiqlangan
dalil qamrovi nolga teng. Yuqoridagi reference vaznlarini runga ko'chirmang va promptda jiddiylik belgilamang.

## Portfel sog'lig'i

Bir xil vaqt oynasidagi platforma sarfidan foydalaning:

```text
portfolio_health = sum(platform_health * platform_spend_share)
```

Sarf mavjud bo'lmasa, platformalarni teng vaznli qiling va natijani provisional deb belgilang. Dalili yetarli bo'lmagan
platformani raqamli jamlamaga qo'shmang; uning yetishmayotgan vazni va natijaviy portfel qamrovini aniq ko'rsating.

## Deduplikatsiya va qo'llanilish

- Bitta kanonik xavfni bir nechta kuzatuvli bitta ballanadigan nazorat sifatida modellang.
- Asosiy treking nosozligini ham, uning har bir alomatini ham alohida jarima sifatida ballamang.
- Nazoratni qo'llaniladigan deb e'lon qilishdan oldin funksiya mavjudligi, akkaunt muvofiqligi, geografiya, kampaniya turi va yetuklikni yozing.
- Kuzatuv ro'yxati va kelgusi o'zgarish elementlarini akkauntga ta'sir qilmaguncha ballanmagan holda saqlang.
- Yangi e'lon qilingan funksiyani qabul qilishni sog'liq sifatida ballamang.

## Tavsiyalar

Ballar tekshiruvni ustuvorlashtiradi; ular o'zgartirishlarga ruxsat bermaydi. Har bir tavsiya tegishli topilmani keltirishi,
ishonchni e'lon qilishi, tanlama hajmi va konversiya kechikishini hisobga olishi hamda har qanday akkaunt yozishidan oldin
o'zgartirish darvozasidan o'tishi kerak.
