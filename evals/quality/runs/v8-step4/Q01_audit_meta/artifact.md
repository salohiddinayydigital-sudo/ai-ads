# Meta Ads Audit — act_88291048201 (30 kunlik hisobot asosida)

- **Sana:** 2026-11-12
- **Agent:** audit-meta (ishchi nusxa) · Charter: `agents/audit-meta.md`
- **Akkaunt:** act_88291048201 · Valyuta: USD · Davr: 30 kun (`window_days: 30`)
- **Manbalar:** `examples/demo-brand/assets/meta_performance.json`, `examples/demo-brand/assets/tracking_health.json`
- **Doira:** faqat yuqoridagi ikki manba fayl. Hisobga hech qanday o'zgartirish kiritilmadi; barcha o'zgarish takliflari DRAFT holatida (Spend-Guard gate + operator tasdig'i shart).
- **Qoida:** `rules/00-manba.md` — manbasiz fakt yo'q; bilinmasa "ma'lumot yo'q"; benchmark ko'chirilmaydi.

## Dalil darajalari

- **MEASURED_ACCOUNT_DATA** — manba faylda bevosita qayd etilgan raqam yoki matn.
- **HISOB** — manba raqamlari ustida arifmetika (yaxlitlash bilan); yangi fakt emas.
- **HEURISTIC_PRIOR_MODEL** — model tajribasiga asoslangan usul/chegara taklifi; fakt emas, alohida belgilangan.

## 1. Mavjud / yetishmayotgan ma'lumot

**Bor (manba fayllarda qayd etilgan):** umumiy sarf 3480.50; 482,900 impressiya; 9,180 klik; CTR 1.90%; 245 xarid; CPA 14.20; daromad 6787.00; ROAS 1.95. Ikkala kampaniya darajasidagi ko'rsatkichlar (ABO va ASC): sarf, xarid, CPA, ROAS, FTIR, frekvensiya, learning holati, fatigue flag. Tracking holati: Pixel (ACTIVE, EMQ 6.2), CAPI (ACTIVE, dedup yo'q), Google Enhanced Conversions (ACTIVE), Telegram bot telemetriyasi (webhook faol, UTM yo'q, kechikish 18s).

**Yo'q (missing_inputs — 6-bo'limga qaraydi):** COGS/marja, attribution window, conversion lag, timezone, kunlik taqsimot, ad-level kreativ ma'lumotlari, auditoriya/placement/avtomatlashtirish, policy eligibility, CAPI hodisa loglari, oldingi davr tarixi. Ushbu yo'nalishlar bo'yicha baho berilmaydi — "ma'lumot yo'q".

## 2. Hisobot ichki konsistensiyasi (HISOB)

Manba: `examples/demo-brand/assets/meta_performance.json` · summary va campaigns · 2026-11-12

- Xaridlar: 178 (cmp_01) + 67 (cmp_02) = 245 — summary bilan mos.
- Sarf: 2610.00 + 870.50 = 3480.50 — summary bilan mos.
- CPA: 3480.50 / 245 = 14.21 ≈ 14.20 (yaxlitlash farqi).
- ROAS: 6787.00 / 3480.50 = 1.95 — mos.
- CTR: 9180 / 482900 = 1.90% — mos.
- Sarf ulushlari: cmp_01 = 74.99%, cmp_02 = 25.01% (HISOB).

**Tashxis:** fayl ichidagi raqamlar konsistent — umumiy ko'rsatkichlarga tayanish mumkin. Faqat P1 dagi double-counting tufayli mutlaq qiymatlar (xarid, CPA, ROAS) bo'rtirilgan bo'lishi ehtimoli alohida saqlanadi.

## 3. Topilmalar (prioritet tartibida)

### P1 [KRITIK] Pixel va CAPI orasida deduplikatsiya yo'q — xaridlar ~15% ikki marta qayd etilmoqda

- **Manba:** `examples/demo-brand/assets/tracking_health.json` · `tracking_audit.meta_capi` · 2026-11-12
- **Kuzatuv (MEASURED_ACCOUNT_DATA):** Pixel (ID 84729103847192, ACTIVE, `browser_event_firing: true`) va CAPI (endpoint `gateway.apexstore.uz`, ACTIVE) ikkalasi ham Purchase hodisasini yubormoqda; `event_id_deduplication: false`. Manba critical_risk matni: "Pixel va CAPI ikkalasi ham xaridni yubormoqda, lekin event_id bir xil emas. Meta hisobotlarida ~15% buyurtmalar ikki marta qayd etilmoqda (double counting)." `hashing_compliance: true`.
- **Tashxis (HISOB, manbadagi ~15% taxminiga tayanadi):** event_id mos emasligi tufayli Meta bir xaridni ikki marta sanaydi. Agar manbadagi ~15% taxmin to'g'ri bo'lsa, hisobotdagi 245 xarid taxminan 208–213 haqiqiy xaridga to'g'ri keladi; haqiqiy CPA ~16.3–16.7 (3480.50 / 213 = 16.34; 3480.50 / 208 = 16.73), haqiqiy ROAS ~1.65–1.70. Bu taxminiy hisob — mutlaq fakt emas; tasdiqlash uchun Events Manager / CAPI loglari kerak (missing_inputs). CPA 14.20 va ROAS 1.95 ga qilingan har qanday baho shu noto'g'ri fondagi ko'rsatkichlarga tayanadi.
- **Tavsiya (mutatsiya taklifi — DRAFT, bajari lmagan):** Pixel va CAPI'da Purchase uchun bir xil `event_id` (masalan, buyurtma identifikatori) yuborilib, deduplikatsiya yoqilsin.
  - **Rollback:** gateway/vebsayt konfiguratsiyasining oldingi ishlayotgan versiyasi saqlab qo'yiladi; muammo bo'lsa dedup o'chirilib, oldingi event_id sxemasiga qaytariladi.
  - **Stop-loss:** dedup yoqilgandan keyin 7 kun ichida Purchase hodisalari kutilgan ~15% pasayishdan ko'proq farq qilsa (masalan, nolga yaqinlashsa yoki hajm noto'g'ri tushsa) — konfiguratsiya darhol qaytariladi va CAPI loglari tekshiriladi.
  - **O'lchov oynasi:** tuzatishdan keyin 7–30 kun davomida hisobotlar qayta solishtiriladi.

### P2 [KRITIK] Telegram bot UTM belgilari yo'q — lid kelib chiqishini aniqlab bo'lmaydi

- **Manba:** `examples/demo-brand/assets/tracking_health.json` · `tracking_audit.telegram_bot_telemetry` · 2026-11-12
- **Kuzatuv (MEASURED_ACCOUNT_DATA):** `crm_webhook_active: true`; `utm_tagging_present: false`.
- **Tashxis:** bot orqali kelgan lidlarning qaysi kampaniya/ad set/kreativdan kelgani aniqlanmaydi. "Meta lidlari sifatsiz" degan da'voni akkaunt dalili bilan tasdiqlash yoki inkor etish imkoni yo'q — lid-sifati tahlilining asosiy to'sig'i. Kampaniya darajasidagi lid sifati solishtiruvi (masalan, cmp_01 va cmp_02) hozirgi manbalar bilan bajarilmaydi.
- **Tavsiya (mutatsiya taklifi — DRAFT, bajarilmagan):** botga olib boruvchi barcha linklar UTM belgilari bilan yuritilsin (kamida source/medium/campaign/adset darajasi) va CRM webhook orqali saqlanib qolsin.
  - **Rollback:** oldingi link generatsiya sxemasi saqlanadi; yangi sxema ishlamasa, UTM'siz oldingi holatga qaytariladi.
  - **Stop-loss:** yangi UTM sxemasi botda ochilish yoki CRM'ga yozilishda uzilish keltirib chiqarsa — darhol oldingi sxemaga qaytariladi.
  - **O'lchov oynasi:** kamida 14 kun; keyin lid sifati kampaniyalar kesimida solishtiriladi.

### P3 [YUQORI] Bot javob kechikishi 18 soniya — 35% mijozlar botni tark etmoqda

- **Manba:** `examples/demo-brand/assets/tracking_health.json` · `tracking_audit.telegram_bot_telemetry` · 2026-11-12
- **Kuzatuv (MEASURED_ACCOUNT_DATA):** `latency_seconds: 18`; manba idealini <5 soniya deb belgilagan; mijozlarning 35% botni tark etmoqda.
- **Tashxis:** javob kechikishi konversiya yo'qotishiga olib keladi — Meta'dan kelgan potensial xaridorlar javob olmay chiqib ketadi. Hisobotdagi CPA 14.20 (245 xarid) ushbu yo'qotishdan keyingi natija; tezlik tuzatilsa xaridlar hajmi oshishi mumkin. Aniq yo'qotilgan xaridlar soni manbada yo'q — hisoblab bo'lmaydi.
- **Tavsiya (jarayon o'zgarishi — DRAFT, bajarilmagan):** javob tezligi manba belgilagan <5 soniya maqsadiga qisqartiriladi. Aniq yechim — HEURISTIC_PRIOR_MODEL (masalan, tez avtojavob/tayyor javob shablonlari); tanlov owner zimmasida.
  - **Rollback:** oldingi bot konfiguratsiyasi saqlanadi; muammo bo'lsa oldingi rejimga qaytariladi.
  - **Stop-loss:** yangi javob oqimi xatolar yoki javob sifati pasayishiga olib kelsa — oldingi rejim qaytariladi; kechikish (soniya) va tark etish ulushi (%) kuzatiladi.

### P4 [YUQORI] cmp_01 "BOF_Prospecting_Interests_Split" — LEARNING_LIMITED, 8 ta ad set

- **Manba:** `examples/demo-brand/assets/meta_performance.json` · `campaigns[cmp_01]` · 2026-11-12
- **Kuzatuv (MEASURED_ACCOUNT_DATA):** ABO, 8 ad set, `learning_status: LEARNING_LIMITED`; sarf 2610.00 (umumiy ulush 74.99% — HISOB), 178 xarid, CPA 14.66, ROAS 1.88. Manba finding matni: "Har bir ad set haftasiga o'rtacha 15 ta xarid olmoqda (50 tadan ancha kam)."
- **Tashxis:** sarf 8 ta ad set bo'ylab bo'lingani uchun har bir ad set learning bosqichi uchun yetarli konversiya to'play olmayapti (manbada qayd etilgan LEARNING_LIMITED va haftasiga ~15 xarid) — samaradorlik pasayishining strukturaviy sababi. "50/hafta" mezoni manba matnidan olingan; tashqi norma ko'chirilmagan.
- **Tavsiya (mutatsiya taklifi — DRAFT, bajarilmagan):** ad setlar kamroq guruhga birlashtirilib (konsolidatsiya), learning holati kuzatiladi. Byudjet miqdoriga tegilmaydi.
  - **Rollback:** konsolidatsiyadan oldingi ad set sozlamalari eksport qilib saqlanadi; kerak bo'lsa struktura qayta tiklanadi.
  - **Stop-loss:** konsolidatsiyadan keyingi 14 kunlik CPA manba baseline'i (14.66, 30 kun) dan sezilarli yomonlashsa (masalan, 20%+ — chegara HEURISTIC_PRIOR_MODEL), struktura qayta tiklanadi.
  - **O'lchov oynasi:** 14 kun — learning_status va CPA haftalik kuzatiladi.

### P5 [YUQORI] cmp_01 — kreativ charchashi (FTIR va frekvensiya manba mezonlaridan chiqib ketgan)

- **Manba:** `examples/demo-brand/assets/meta_performance.json` · `campaigns[cmp_01]` (`fatigue_flag: true`) · 2026-11-12
- **Kuzatuv (MEASURED_ACCOUNT_DATA):** FTIR 54.2%; o'rtacha frekvensiya 3.12. Manba charchash mezonlarini o'zi belgilagan: FTIR < 60%, Freq > 3.0; `fatigue_flag: true`.
- **Tashxis:** manba charchashni bevosita tasdiqlaydi — kreativlar auditoriyaga ko'p marta ko'rsatilmoqda; CTR va CPA buzilish xavfi mavjud (30 kunlik CTR 1.90% bu holatdagi natija). Qaysi kreativlar charchagani noma'lum — ad-level ma'lumot yo'q ("ma'lumot yo'q").
- **Tavsiya (mutatsiya taklifi — DRAFT, bajarilmagan):** yangi kreativ variantlar kiritilib, charchagan kreativlar bosqichma-bosqich almashtiriladi. Kreativ tarkibi bo'yicha takliflar — HEURISTIC_PRIOR_MODEL; o'lchov manba mezonlari (FTIR, Freq) bo'yicha kuzatiladi.
  - **Rollback:** almashtirishdan oldingi kreativlar o'chirilmaydi, arxivlanadi; kerak bo'lsa qayta yoqiladi.
  - **Stop-loss:** yangi kreativlar 14 kun ichida FTIR ni yoki CPA ni (baseline 14.66) yomonlasa — yangi to'plam to'xtatilib, oldingi to'plam qaytariladi.

### P6 [O'RTA] cmp_02 "ASC_Advantage_Shopping" — eng samarali kampaniya, ulushi 25%

- **Manba:** `examples/demo-brand/assets/meta_performance.json` · `campaigns[cmp_02]` · 2026-11-12
- **Kuzatuv (MEASURED_ACCOUNT_DATA):** ASC, 1 ad set, `learning_status: LEARNING`; sarf 870.50 (ulush 25.01% — HISOB), 67 xarid, CPA 12.99 (kampaniyalar orasida eng past), ROAS 2.15 (eng yuqori), FTIR 72.0%, frekvensiya 1.85, `fatigue_flag: false`. Manba finding matni: "Yaxshi ishlayapti, lekin CBO ga qaraganda kam byudjet berilgan (25%)."
- **Tashxis:** manba matni ham kampaniya yaxshi ishlayotganini, biroq kichik ulush berilganini qayd etayapti. Ikki ihtiyot chorasi: (1) ushbu ko'rsatkichlar P1 dagi double-counting ta'sirida bo'lishi mumkin — solishtirish dedup tuzatilgach takrorlanadi; (2) faylda "CBO" kampaniyasi mavjud emas — manba matnidagi solishtirish asosi ushbu eksportda keltirilmagan.
- **Tavsiya:** ushbu auditda hisob o'zgarishi (byudjet ulushini oshirish) QILINGAN YO'Q va to'g'ridan-to'g'ri tavsiya etilmaydi. Bunday qaror alohida DRAFT sifatida tayyorlanadi: >20% byudjet o'zgarishi Spend-Guard gate va operator tasdig'isiz bajarmaydi.
  - **Rollback:** byudjet o'zgarishi kundalik darajada qaytariladigan bo'lishi shart; oldingi qiymat (sarf ulushi 25.01%) qayd etiladi.
  - **Stop-loss:** o'zgartirishdan keyin CPA manba baseline'i (12.99) ga nisbatan yomonlashsa — oldingi byudjetga qaytariladi.
  - **O'lchov oynasi:** o'zgartirishdan keyin 7–14 kun.

### P7 [O'RTA] EMQ 6.2 — manbada baho mezon yo'q

- **Manba:** `examples/demo-brand/assets/tracking_health.json` · `tracking_audit.meta_pixel` · 2026-11-12
- **Kuzatuv (MEASURED_ACCOUNT_DATA):** Pixel ACTIVE; `browser_event_firing: true`; `emq_score: 6.2`.
- **Tashxis:** manba EMQ uchun "yaxshi/yomon" mezoni bermagan — baho berilmaydi ("ma'lumot yo'q"; tashqi norma ko'chirilmaydi — rules/00-manba). Biroq P1 dagi dedup yo'qligi signal sifatiga bevosita ta'sir qiluvchi qayd etilgan muammo; EMQ qiymati dedup tuzatilgach qayta o'lchanishi lozim.
- **Tavsiya (o'lchov, mutatsiya emas):** P1 tuzatilgandan keyin Events Manager diagnostikasi orqali EMQ qayta qayd etiladi va diagnostika ko'rsatgan yo'nalishlar asosida ish rejalashtiriladi.

## 4. Lead quality root causes (output contract)

1. **UTM belgilari yo'q** (`utm_tagging_present: false`) — lid manbai kuzatilmaydi, "lidlar sifatsiz" da'vosi manba bilan tekshirilmaydi. Manba: `examples/demo-brand/assets/tracking_health.json`.
2. **Bot javob kechikishi 18 soniya → 35% tark etish** — konversiya yo'qotilmoqda. Manba: `examples/demo-brand/assets/tracking_health.json`.
3. **Double counting ~15%** (`event_id_deduplication: false`) — lid→xarid konversiyasi va CPA/ROAS noto'g'ri baholanmoqda. Manba: `examples/demo-brand/assets/tracking_health.json` + `examples/demo-brand/assets/meta_performance.json`.

## 5. Ziddiyatlar (contradictions)

1. cmp_02 `type: "ASC"`, ammo manba finding matni "CBO ga qaraganda" deydi — faylda CBO kampaniyasi yo'q; atama va solishtirish asosi nomutanosib. Raqamli qism (25% ulush) HISOB bilan mos. Manba: `examples/demo-brand/assets/meta_performance.json`.
2. Summary CPA 14.20 vs hisob 14.21 — yaxlitlash farqi, jiddiy ziddiyat emas. Manba: `examples/demo-brand/assets/meta_performance.json`.
3. Boshqa ziddiyat aniqlanmadi (hisobot ichki konsistent — 2-bo'lim).

## 6. Yetishmayotgan ma'lumotlar (missing_inputs)

- **Objective va geografiya** manbalarda qayd etilmagan — "ma'lumot yo'q".
- **COGS/marja va break-even ROAS/CPA** yo'q — shuning uchun ROAS 1.95 va CPA 14.20 ga "yaxshi/yomon" baho berilmaydi (tashqi benchmark ko'chirilmaydi, o'z tarixi ham manbada yo'q — rules/00-manba).
- **Attribution window, conversion lag, timezone, namuna hajmi konteksti** — yo'q.
- **Kunlik (daily) taqsimot** — yo'q; tendensiya tahlili qilinmaydi.
- **Ad-level kreativ ma'lumotlari** — yo'q; faqat kampaniya darajasidagi agregatlar bor.
- **Auditoriya, placement, avtomatlashtirish, policy eligibility** — yo'q; ushlu boshqaruvlar baholanmagan (`unknown`).
- **CAPI hodisa loglari / Events Manager eksporti** — yo'q; P1 tashxisini mustahkamlash uchun kerak.
- **Oldingi davr tarixi** — yo'q; o'z tarixi bilan solishtirish (eng yaxshi benchmark) imkoni yo'q.

## 7. Yakuniy xulosa

Ustuvorlik tartibi: (1) P1 dedup tuzatish — hisobotlarga ishonchning asosi; (2) P2 UTM belgilari — lid sifatini o'lchashning asosi; (3) P3 bot tezligi — konversiya yo'qotishini kamaytirish; keyin P4/P5 (cmp_01 struktura va kreativ). P6 byudjet masalasi faqat DRAFT — Spend-Guard (20% gate) va operator tasdig'isiga bog'liq. Hisobga o'zgartirish kiritilmagan; barcha mutatsiya takliflarida rollback va stop-loss yozilgan.

## 8. Output contract (JSON xulosa)

```json
{
  "status": "complete_with_missing_inputs",
  "platform": "meta",
  "account_id": "act_88291048201",
  "window_days": 30,
  "currency": "USD",
  "findings": [
    {"id": "P1", "priority": "critical", "title": "Pixel-CAPI dedup yo'q, ~15% double counting", "source": "examples/demo-brand/assets/tracking_health.json"},
    {"id": "P2", "priority": "critical", "title": "Bot UTM belgilari yo'q, lid manbai aniqlanmaydi", "source": "examples/demo-brand/assets/tracking_health.json"},
    {"id": "P3", "priority": "high", "title": "Bot kechikishi 18s, 35% tark etish", "source": "examples/demo-brand/assets/tracking_health.json"},
    {"id": "P4", "priority": "high", "title": "cmp_01 LEARNING_LIMITED, 8 ad set", "source": "examples/demo-brand/assets/meta_performance.json"},
    {"id": "P5", "priority": "high", "title": "cmp_01 kreativ charchashi (FTIR 54.2%, Freq 3.12)", "source": "examples/demo-brand/assets/meta_performance.json"},
    {"id": "P6", "priority": "medium", "title": "cmp_02 eng samarali (CPA 12.99, ROAS 2.15) lekin ulush 25%", "source": "examples/demo-brand/assets/meta_performance.json"},
    {"id": "P7", "priority": "medium", "title": "EMQ 6.2, mezon yo'q — dedup tuzatilgach qayta o'lchanadi", "source": "examples/demo-brand/assets/tracking_health.json"}
  ],
  "lead_quality_root_causes": [
    "UTM belgilari yo'q (utm_tagging_present: false)",
    "Bot kechikishi 18s, 35% tark etish",
    "Double counting ~15% (event_id_deduplication: false)"
  ],
  "contradictions": [
    "cmp_02 type ASC, ammo manba matni 'CBO ga qaraganda' deydi — CBO faylda yo'q",
    "Summary CPA 14.20 vs hisob 14.21 — yaxlitlash farqi"
  ],
  "missing_inputs": [
    "COGS/marja va break-even", "attribution window, conversion lag, timezone",
    "kunlik taqsimot", "ad-level kreativ ma'lumotlari",
    "auditoriya/placement/avtomatlashtirish/policy", "CAPI hodisa loglari",
    "oldingi davr tarixi", "objective va geografiya"
  ],
  "mutations": "none executed; drafts P1-P6 with rollback + stop-loss; budget changes require Spend-Guard + user approval"
}
```

## 9. Manbalar

- `examples/demo-brand/assets/meta_performance.json` — act_88291048201, USD, 30 kun (o'qilgan: 2026-11-12)
- `examples/demo-brand/assets/tracking_health.json` — tracking audit (o'qilgan: 2026-11-12)
- `rules/00-manba.md` — manba majburiyati qoidasi
- `agents/audit-meta.md` — audit-meta charteri (7-band: manba yo'li, prioritet, rollback/stop-loss)
