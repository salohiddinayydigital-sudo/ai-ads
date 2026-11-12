# CAPI Deduplikatsiya Tashxisi — demo-brand

Tashxis `tracking_health.json` eksporti asosida tayyorlandi. Hisobga o'zgartirish kiritilmadi — faqat tashxis va tuzatish rejasi (draft).

## 1. Mavjud holat (eksportdan)

| Element | Holat | Manbadagi qiymat |
|---|---|---|
| Meta Pixel | O'rnatilgan, ACTIVE | pixel_id: 84729103847192, brauzer hodisalari yuborilyapti |
| Meta CAPI | O'rnatilgan, ACTIVE | endpoint: gateway.apexstore.uz |
| event_id deduplikatsiya | Yo'q | `event_id_deduplication: false` |
| Hashing | Muvofiq | `hashing_compliance: true` |
| EMQ | Past-o'rta | 6.2 |

## 2. Aniq sabab

Pixel va CAPI **ikkalasi ham xaridni (Purchase) yubormoqda**, lekin ikki yuborishda **event_id bir xil emas** (`event_id_deduplication: false`). Meta deduplikatsiyani `event_name + event_id` juftligi mosligi orqali qiladi; juftlik mos kelmasa, server va brauzer hodisasi bitta o'rniga **ikki alohida hodisa** sifatida qayd etiladi.

## 3. Hisobotga ta'siri

- Manbada qayd etilganidek: **~15% buyurtmalar ikki marta qayd etilmoqda (double counting)**.
- Natijada Purchase soni va aylanma taxminan 15% ga ko'pirtirilgan; shu raqamlar ustidan hisoblangan ROAS/CPA ham shu og'ish bilan noto'g'ri bo'ladi (aniq qiymat eksportda yo'q — ma'lumot yo'q).
- Hashing muvofiqligi buzilgan emas — muammo faqat deduplikatsiyada.

## 4. Tuzatish ro'yxati (draft — konduktor tasdig'isiz hisobga tegilmaydi)

1. Har bir xarid uchun **yagona event_id** generatsiya qilinsin; eng tabiiy manba — buyurtma ID'si.
2. Bir xil qiymat **ikki tomonda ham** berilsin:
   - brauzer tomonda: pixel qo'ng'irog'ining `eventID` parametrida (masalan, `fbq('track', 'Purchase', data, {eventID: '<order_id>'})`);
   - server tomonda: CAPI payload'ining `event_id` maydonida aynan shu qiymat.
3. `event_name` ham ikki tomonda bir xil bo'lsin ("Purchase") — juftlik to'liq mosligi shart.
4. Gateway (`gateway.apexstore.uz`) kodi shunday tuzatilsinki, CAPI yuborishda pixel tomonidan berilgan event_id ni qabul qilib, o'zgartirmasdan qaytarsin.
5. Tekshirish: Events Manager'da "deduplicated" hodisalar soni ko'rinishi kerak; tuzatish oldi/keyin bir xil davr solishtirilib, ~15% farq yo'qolganini tasdiqlash.
6. Test buyurtma bilan end-to-end tekshiruv: brauzer va server bitta hodisani bir vaqtda yuborib, faqat bitta Purchase hisoblanishini ko'rish.

## 5. Ma'lumot yetishmasligi (eksportda yo'q)

- Pixel va CAPI tomonidan yuborilgan real event_id namunalari — ma'lumot yo'q.
- Davrlar bo'yicha aniq double-counting statistikasi — ma'lumot yo'q (faqat ~15% ko'rsatkichi bor).
- EMQ 6.2 foydalanuvchi aniqligi alohida masala — bu tashxis chegarasidan tashqarida.

---
Manba: examples/demo-brand/assets/tracking_health.json · 2026-11-12
