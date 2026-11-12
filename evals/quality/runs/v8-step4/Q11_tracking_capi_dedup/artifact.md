# CAPI Deduplikatsiya Tashxisi — Q11

**Agent:** tracking-specialist
**Sana:** 2026-11-12
**Holat:** faqat tashxis va tuzatish rejasi. Hisobga hech qanday o'zgartirish kiritilmagan — bu hujjat draft.

**Manba:** `examples/demo-brand/assets/tracking_health.json` · 2026-11-12 da o'qilgan

---

## 1. Qamrov va ma'lumot holati

**Bor (manba faylidan):**

- Meta Pixel: o'rnatilgan, ID `84729103847192`, holati `ACTIVE`, brauzer eventlari yuborilmoqda, EMQ 6.2
- Meta CAPI: o'rnatilgan, endpoint `gateway.apexstore.uz`, holati `ACTIVE`, `hashing_compliance: true`
- `event_id_deduplication: false`
- Audit xulosasi (`critical_risk`): Pixel va CAPI ikkalasi ham xaridni yubormoqda, lekin `event_id` bir xil emas; Meta hisobotlarida ~15% buyurtmalar ikki marta qayd etilmoqda (double counting)

**Yo'q (`missing_inputs`):**

- Haqiqiy payload loglari va namuna `event_id` qiymatlari — ma'lumot yo'q
- ~15% ko'rsatkich qaysi sana oralig'iga tegishli — ma'lumot yo'q
- Events Manager diagnostikasi va test-event natijalari — ma'lumot yo'q
- Buyurtma hajmi (kunlik/haftalik) — ma'lumot yo'q; shuning uchun absolyut yo'qotish/ortiqcha hisob raqami hisoblanmaydi

Eslatma: `telegram_bot_telemetry` blokidagi muammolar (18 soniya kechikish, UTM yo'qligi) bu tashxis qamrovidan tashqarida — alohida masala.

## 2. Kuzatishlar (MEASURED_ACCOUNT_DATA)

| Dalil | Qiymat | Manba joyi |
| --- | --- | --- |
| event_id_deduplication | `false` | `tracking_audit.meta_capi` |
| critical_risk | Pixel va CAPI purchase yuboradi, `event_id` har xil; ~15% double counting | `tracking_audit.meta_capi.critical_risk` |
| Pixel | `ACTIVE`, brauzer eventlari yuborilmoqda | `tracking_audit.meta_pixel` |
| CAPI | `ACTIVE`, hashing muvofiq | `tracking_audit.meta_capi` |

## 3. Tashxis — muammoning aniq sababi

Bir xil xarid hodisasi ikki kanaldan yuborilmoqda — brauzerdan (Pixel, ID `84729103847192`) va serverdan (CAPI, endpoint `gateway.apexstore.uz`), lekin ikkala nusxa **turli `event_id` bilan yuborilmoqda**, CAPI tomonda esa `event_id_deduplication: false`.

Meta brauzer va server nusxalarini faqat **bir xil `event_id` (+ bir xil `event_name`)** juftligi bo'yicha bitta hodisaga birlashtiradi (HEURISTIC_PRIOR_MODEL — Meta platforma standarti; qarang: `skills/ads/references/conversion-tracking.md`, "Deduplication" bo'limi. Eslatma: ushbu reference'ning refresh muddati 2026-08-10 da tugagan, shuning uchun u provisional deb qabul qilinadi).

ID mos kelmagani uchun Meta har bir nusxani alohida hodisa deb hisoblaydi → bitta buyurtma hisobotda ikki marta ko'rinadi.

## 4. Hisobotga ta'siri (qancha ko'pirtirilmoqda)

- Manba faylidagi o'lchov bo'yicha: **~15% buyurtmalar Meta hisobotlarida ikki marta qayd etilmoqda** (double counting) — MEASURED_ACCOUNT_DATA; qaysi davrga oidligi manbada ko'rsatilmagan (`missing_inputs`).
- Demak, Meta hisobotidagi Purchase soni haqiqiy buyurtma sonidan ~15% ga ko'p ko'rinadi.
- Oqibat (diagnosis — mantiqiy xulosa, manbada bevosita yozilmagan): shishgan konversiya hisobi ROAS/CPA va optimizatsiya signalini buzadi; Meta optimizatsiyasi haqiqiy savdo bilan bog'liq bo'lmagan signalga qarab ishlaydi.
- EMQ 6.2 ga deduplikatsiyaning bevosita ta'siri manba faylida ko'rsatilmagan — bu borada taxmin qilinmaydi ("ma'lumot yo'q").

## 5. Tuzatish ro'yxati — `event_id` qanday berilishi (draft, amalga oshirilmagan)

**Tamoyil:** bitta biznes-hodisa = bitta `event_id`, ikkala kanalda bir xil.

1. **Yagona, barqaror ID generatsiya:** har bir buyurtma uchun `event_id` bir marta generatsiya qilinadi. Eng ishonchli tanlov — buyurtma/transaction ID (CRM/order ID). Tasodifiy ID ishlatilsa ham, xuddi shu qiymat ikkala kanalga yetkazilishi shart.
2. **Ikkala kanalga bir xil ID va nom:**
   - Brauzer (Pixel): `fbq('track', 'Purchase', {value, currency, ...}, {eventID: '<xuddi shu ID>'})`
   - Server (CAPI): payload'da `event_id: '<xuddi shu ID>'` va `event_name: 'Purchase'`
   - `event_name` ikkala kanalda bir xil bo'lishi shart (juftlik bo'yicha dedup).
3. **Idempotentlik:** retry va qayta yuborishlar xuddi shu `event_id` bilan ketadi — qayta yuborishda yangi ID generatsiya qilinmaydi.
4. **Kolliziyasizlik:** har xil buyurtma — har xil `event_id`; ikki xil hodisa bitta ID ustida to'qnashmasligi kerak.
5. **Oqim omonligi:** `event_id` checkout va to'lov provayderi redirectlari, cross-domain oqimlar orqali yo'qolmasligi tekshiriladi (dedup to'lov oqimidan keyin ham ishlashi shart).
6. **Tekshiruv (tuzatishdan keyin):** Events Manager test-events'da bitta test xaridi → bitta qabul qilingan Purchase; Meta Purchase soni CRM/buyurtma yozuvlari bilan lag-mature oynada solishtiriladi. Muvaffaqiyat mezonlari: ~15% double counting nolga yaqinlashadi; brauzer+server nusxalar juftligi Events Manager'da "deduplicated" deb ko'rinadi.
7. Hisobga o'zgartirish kiritish (CAPI konfiguratsiyasini yangilash) alohida mutation-gate tasdig'isiz bajarilmaydi; ushbu hujjat faqat tashxis va rejadir.

---

**Manba:** `examples/demo-brand/assets/tracking_health.json` · 2026-11-12 · Qo'shimcha (provisional — refresh muddati o'tgan): `skills/ads/references/conversion-tracking.md` (2026-07-11)
