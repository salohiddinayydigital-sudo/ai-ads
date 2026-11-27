# GAQL muvofiqligi va aniqligi bo'yicha eslatmalar

GAQL maydonlari, muvofiqlik qoidalari, sana konstantalari va API versiyalari o'zgaradi. Bu faylni so'rov
dizayni bo'yicha yo'riqnoma deb qarang, joriy maydonlar katalogi deb emas. So'rovni bajarishdan oldin mijoz ID,
API versiyasi, so'rov resursi, tanlangan maydonlar, sana oynasi va joriy Google Ads API maydon/reference manba
ID'sini yozing. Runtime `INVALID_ARGUMENT` yoki `UNRECOGNIZED_FIELD` so'rovni tuzatish uchun `needs_input`
hisoblanadi; uni jimgina bo'sh ma'lumotlar to'plamiga aylantirmang.

## Muvofiqlikni aniqlash

Tanlangan versiya uchun joriy rasmiy Google Ads API hujjatlari va maydon metama'lumotlaridan foydalanib tekshiring:

- har bir tanlangan va filtrlangan maydon asosiy resurs bilan tanlanishi mumkinmi;
- segmentlar qator donadorligini o'zgartiradimi yoki metrikalar bilan to'qnashadimi;
- tanlangan sana konstantasi mavjudmi, aks holda aniq sanalardan foydalaning;
- resurs holati so'rov ichida mavjudmi yoki olingandan keyin birlashtirilishi yoxud filtrlanishi kerakmi;
- sahifalash, qisman muvaffaqiyatsizlik, kvota, valyuta birligi, vaqt mintaqasi va manager-akkaunt xatti-harakati.

So'rovni faqat avvalgi API versiyasida ishlagani uchun keyingisiga ko'chirmang.

## Kalit so'zlarni deduplikatsiya qilish

**Muammo:** `keyword_view + segments.date DURING LAST_30_DAYS` har bir kalit so'z uchun kuniga bitta qator qaytaradi.
5 kun faol kalit so'z = 5 qator. Xuddi shu kalit so'z BROAD + PHRASE bilan = kuniga 2 qator = jami 10.

**Tuzatish:** Olish vaqtida `(ad_group_id + keyword_text + match_type)` bo'yicha deduplikatsiya qiling. Dublikat qatorlar
bo'yicha metrikalarni (impressions, clicks, cost, conversions) jamlang.

**Muqobil:** Sana darajasidagi dublikatni manbada yo'qotish uchun GAQL so'rovlaridan `segments.date` ni butunlay olib tashlang.

Hosil bo'lgan qator donadorligini run manifestida yozing. Keyingi tekshiruvlar normallashtirilgan kalit so'z
donadorligini faqat fixture yoki akkaunt darajasida moslashtirishdan keyin iste'mol qilishi mumkin.

## Filtr qamrovi bo'yicha eng yaxshi amaliyotlar

Holatni javob beriladigan savolga moslang. Joriy xizmat ko'rsatish sog'lig'i ko'rinishi odatda yoqilgan, pauza qilingan
va olib tashlangan obyektlarni ajratadi. Tarixiy o'zgarish, overlap yoki rollback tekshiruvi pauza qilingan obyektlarni
talab qilishi mumkin. So'rov ataylab holatni chiqarib tashlasa, akkauntni hech qachon to'liq deb ta'riflamang va
qat'iy lookback har bir konversiya kechikishi yoki biznes siklga mos deb o'ylamang.

## Xatolarni qayta ishlash

Qaysi ma'lumot olishlari va nega muvaffaqiyatsiz bo'lganini kuzating. G-SYS1 diagnostikasi sifatida xabar bering:
- Barcha muvaffaqiyatsiz ma'lumot manbalarini xato xabarlari bilan sanab chiqing
- Ma'lumot yetishmasligi sababli qaysi tekshiruvlar o'tkazib yuborilganini har bir tekshiruv uchun kontekst bilan bering
- Tekshiruvlarni hech qachon jimgina o'tkazib yubormang; ma'lumot nega mavjud emasligini doim tushuntiring

## Tarixiy match-type talqini

Eski Broad Match Modified xatti-harakatini yoki reklama beruvchi niyatini joriy `BROAD` enum, bidding strategiyasi yoki
`+` prefiksi yo'qligidan taxmin qilmang. Sanalangan o'zgarishlar tarixi, qidiruv iboralari, joriy moslashtirish xatti-harakati,
kampaniya nazoratlari va egasi niyatini tekshiring. Bu dalil mavjud bo'lmasa, tarixiy tasnifni `unknown` deb xabar qiling;
uni muvaffaqiyatsizlikka yoki avtomatik negativ kalit so'z harakatiga aylantirmang.
