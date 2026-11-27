# Kreativ spetsifikatsiyani aniqlash

**Tekshirilgan:** 2026-07-11
**Yangilash muddati:** 2026-08-10
**Dalil holati:** manba indeksi va tekshiruv jarayoni, universal spetsifikatsiya jadvali emas

Kreativ talablar format, placement, maqsad, geografiya, akkaunt muvofiqligi va mahsulot relizlariga qarab farqlanadi.
Aktivni tekshirishdan oldin aniq formatni aniqlang. Yagona "platforma spetsifikatsiyasi" jadvali xavfli, chunki u
bir placementga tegishli bo'lmagan talablarni jimgina aralashtiradi.

## Aniqlash tartibi

1. Platforma, maqsad, format, placement, manzil, geografiya va joriy akkaunt UI tanlovini yozing.
2. Mos platformaga xos kreativ referenceni oching.
3. O'zgaruvchan chegaralarni joriy rasmiy yordam sahifasi yoki API sxemasi bilan tekshiring.
4. Aktiv bir necha placementga xizmat qilishi kerak bo'lsa, qattiqroq talabni afzal ko'ring.
5. Akkaunt UI'da oldindan ko'ring va render qilingan crop, overlaylar, matn, subtitrlar, audio, CTA, oshkor qilish va manzilni tekshiring.
6. Manba ID, olingan sana, kuzatilgan UI/API versiyasi va istisnolarni yozing.

Manbalar bir-biriga zid bo'lsa, taxmin qilmang. Tekshiruvni `unknown` deb belgilang, ikkala qiymatni saqlang va joriy
preview yoki API validatsiyasini so'rang.

## Joriy manba kirish nuqtalari

| Platforma | Birlamchi manba | Qamrov |
| --- | --- | --- |
| Google / YouTube | `google-rsa-official` — [Responsive search ads](https://support.google.com/google-ads/answer/7684791) va [Google Ads asset requirements](https://support.google.com/adspolicy/answer/6368661) | Search matni va umumiy aktiv siyosati |
| Meta | `meta-video-ads-official` — [Meta video ads](https://www.facebook.com/business/ads/video-ad-format) | Video placementlar va Ads Guide'ga havola |
| LinkedIn | `linkedin-ads-guide-official` — [LinkedIn Ads Guide](https://business.linkedin.com/marketing-solutions/success/ads-guide) | Joriy format kirish nuqtalari |
| TikTok | `tiktok-ad-format-policy-official` — [Ad format and functionality](https://ads.tiktok.com/help/article/tiktok-ads-policy-ad-format-and-functionality) | Kreativ va tahririy talablar |
| Microsoft | `microsoft-ad-types-official` — [Ad types](https://help.ads.microsoft.com/apex/index/3/en-us/50879) | Joriy reklama turi xatti-harakati |
| Apple | `apple-ads-creative-official` — [Apple Ads creative help](https://ads.apple.com/app-store/help/ad-creative) | Apple Ads kreativ kirish nuqtasi |
| Amazon | `amazon-creative-acceptance-official` — [Creative acceptance policies](https://advertising.amazon.com/resources/ad-policy/creative-acceptance) | Amazon Ads kreativ siyosati |
| Reddit | `reddit-ads-help-official` — [Reddit Ads Help](https://business.reddithelp.com/s/) | Joriy Reddit yordami va policy'ni aniqlash |
| Pinterest | `pinterest-ad-specs-official` — [Pinterest ad specs](https://help.pinterest.com/en/business/article/pinterest-product-specs) | Pinterest formatlari va aktivlari |
| Snapchat | `snap-creative-specs-official` — [Snap creative specifications](https://forbusiness.snapchat.com/advertising/ad-formats) | Snap reklama-formati kirish nuqtasi |
| X | `x-creative-specs-official` — [X Ads creative specs](https://business.x.com/en/help/campaign-setup/creative-ad-specifications) | X formatlari va aktivlari |

Bu sahifalar — aniqlash nuqtalari, har bir format muayyan akkauntda mavjudligining isboti emas. Pass yoki o'zgartirish
chiqarishdan oldin faol UI/API ni qayta tekshiring.

## Aniq saqlangan faktlar

Google'ning joriy responsive-search-ad hujjatida RSA 15 tagacha sarlavha va to'rtta tavsifni qabul qilishi, sarlavha
maydonlari esa 30 belgigacha qo'llab-quvvatlashi aytilgan. Microsoft'ning joriy ad-type sahifasida ham uning RSA'si
15 tagacha sarlavha va to'rtta tavsifni qabul qilishi aytilgan. Bu faktlar faqat shu nomlangan formatlarga tegishli;
ular platformalararo matn standartini belgilamaydi.

## Tekshiruv natijasi

Har bir aktiv uchun qaytaring:

- `platform`, `format`, `placement`, `objective` va `geography`.
- Kuzatilgan o'lchamlar, davomiylik, fayl turi, fayl hajmi, matn maydonlari, audio, subtitrlar, manzil, CTA va oshkor qilish.
- Har bir tegishli talab uchun `pass`, `fail`, `unknown` yoki `not_applicable`.
- Har bir aniq chegara uchun rasmiy manba ID va olingan sana.
- Preview dalili va har qanday crop yoki overlay xavfi.
- Kreativ konseptni saqlaydigan tuzatish.

## Universal bo'lmagan qoidalar

- Universal vertikal-video xavfsiz zonasi yo'q. Joriy placement previewi va platforma overlay yo'riqnomasiga qarshi tekshiring.
- Tavsiya etilgan o'lchamlar har doim minimal qabul qilish talabi emas; ularni belgilang.
- Platformaga muvaffaqiyatli yuklash policy tasdig'i yoki yaxshi render isboti emas.
- Belgilar soni platformaga xos normallashtirishdan foydalanishi mumkin; aniq qabul qilish muhim bo'lsa, platforma API/UI orqali tekshiring.
- "Best practice" aktivlar soni yoki davomiyliklarini muvofiqlik nosozliklariga aylantirmang.
