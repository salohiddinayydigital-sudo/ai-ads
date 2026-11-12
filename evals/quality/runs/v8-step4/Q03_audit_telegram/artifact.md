# Q03 — Telegram Ads kanallari va bot voronkasi audit (tg_ads_fragment_8819)

- **Manba:** `examples/demo-brand/assets/telegram_campaigns.json` · `examples/demo-brand/assets/tracking_health.json` · 30 kunlik oyna · USD · audit sanasi: 2026-11-12
- **Holat (status):** ok — faqat tahlil va tavsiyalar. Hisobga hech qanday o'zgartirish kiritilmagan; barcha tavsiyalar draft va mutatsiya darvozasidan o'tmaguncha bajarilmaydi ([[40-xavfsizlik-va-hisob]]).
- **Platform:** telegram · **Qoida:** [[00-manba]] — har raqam manbali; noma'lum joylar "ma'lumot yo'q" deb yozilgan.

## 1. Ma'lumot holati: bor / yo'q

**Bor (MEASURED_ACCOUNT_DATA):**
- Umumiy: sarf $1,200.00; CPM $3.40; 352,940 impressiya; 4,235 klik; CTR 1.20%; 2,750 bot start; bot start rate 64.9%; 825 qualified lid; lid rate 30.0%; CPL $1.45; 99 buyurtma; CAC $12.12; daromad $3,180.00; ROAS 2.65.
- 3 kanal: sarf, CPM, CTR, CPL, status (WINNER_SCALE / VALIDATED / KILL_CANDIDATE) va operator izohi.
- Bot telemetriyasi: CRM webhook faol (`crm_webhook_active: true`); UTM taging yo'q (`utm_tagging_present: false`); javob kechikishi 18 soniya (ideal <5); kutish sababli 35% mijoz botni tark etadi.
- O'lchov holati: Meta Pixel faol (EMQ 6.2), Meta CAPI faol lekin `event_id_deduplication: false` (~15% double counting xavfi), Google Enhanced Conversions faol (GA4 bog'langan, Purchase primary).

**Yo'q (missing_inputs):**
- Aniq sana diapazoni va timezone — ma'lumot yo'q (faqat "30 kunlik oyna").
- Kanal bo'yicha buyurtma, AOV, ROAS — ma'lumot yo'q (faqat CPL bor).
- Kanal bo'yicha bot start va drop-off — ma'lumot yo'q (faqat @kulgu_va_memlar uchun 85% qayd etilgan).
- Maqsafiy CPA/ROAS, marja/COGS, LTV — ma'lumot yo'q.
- Bot kechikishining sana bo'yicha dinamikasi va texnik sababi (navbat, tarmoq, javob zanjiri) — ma'lumot yo'q.

## 2. Umumiy voronka matematikasi (30 kun)

| Bosqich | Qiymat | O'tish | Manba |
|---|---|---|---|
| Impressiya | 352,940 | — | telegram_campaigns.json |
| Klik | 4,235 | CTR 1.20% | telegram_campaigns.json |
| Bot start | 2,750 | 64.9% (klik→bot start) | telegram_campaigns.json |
| Qualified lid | 825 | 30.0% (bot start→lid) | telegram_campaigns.json |
| Buyurtma | 99 | 12.0% (lid→buyurtma; hisoblangan: 99/825) | telegram_campaigns.json |
| Daromad | $3,180 | AOV $32.12 (hisoblangan: 3,180/99) | telegram_campaigns.json |

Ichki tekshiruv (manba raqamlaridan hisoblangan): $1,200/825 = $1.45 CPL ✓; $1,200/99 = $12.12 CAC ✓; $3,180/$1,200 = 2.65 ROAS ✓; $1,200/2750 ≈ $0.44 — bir bot start tannarvi.

**Ziddiyat (00-manba, 5-band — yashirilmaydi):** kanal CPL'laridan orqaga hisoblangan lidlar ($450/1.25 = 360; $550/1.85 ≈ 297; $200/3.40 ≈ 59) jami ≈716 bo'lib, umumiy `qualified_leads` 825 dan ≈109 (13%) kam. Bu CPL qiymatlarining yaxlitlanishi yoki bir qism lidning kanal mansubligi noma'lumligidan bo'lishi mumkin — sababi manbada yo'q. Impressiya (kanallar yig'indisi ≈361k vs 352,940, ~2.3%) va klik (≈4,295 vs 4,235, ~1.4%) farqlari yaxlitlash darajasida. Quyidagi kanal tavsiyalari shu aniqlik chegarasida o'qilishi kerak.

## 3. Kanallar bo'yicha qarorlar (faqat tavsiya, draft)

### 3.1 @toshkent_bozori — SCALE qilinadi
- **MEASURED:** sarf $450 (37.5% ulush), CPM $3.00, CTR 1.45% (uchta kanal ichida eng yuqori), CPL $1.25 (eng past; o'rtacha $1.45 dan ~14% arzon). Manba statusi: `WINNER_SCALE`.
- **Manba izohi:** "Eng arzon va sifatli xaridlar. Haftasiga +15% byudjet oshirish mumkin."
- **Tavsiya (draft):** haftasiga +15% bosqichma-bosqich oshish — bu 20% Spend-Guard chegirasidan past; har oshirishdan keyin 7 kun CPL monitoringi. Kanal bo'yicha buyurtma/AOV ma'lumot yo'q, shuning uchun scale qarori CPL va manbaning o'z statusiga tayanadi. Operator tasdig'isiz bajarilmaydi.

### 3.2 @uzb_biznes_yangiliklari — SAQLANADI, o'lchov kengaytiriladi
- **MEASURED:** eng katta sarf $550 (45.8%), CPM $4.20, CTR 1.10%, CPL $1.85 (o'rtachadan ~28%, g'olib kanaldan ~48% qimmat). Manba statusi: `VALIDATED`.
- **Manba izohi:** B2B va yuqori chekli premium kostyumlar xaridorlari.
- **Tavsiya:** to'xtatilmaydi — manba yuqori chekli segmentni ko'rsatadi, ammo kanal bo'yicha AOV/ROAS ma'lumot yo'q. $1.85 CPL yuqori chekli buyurtmada maqbul bo'lishi mumkin; bu farqni faqat kanal darajasidagi AOV yopadi. Avval AOV o'lchanadi, keyin scale/pauza qarori qabul qilinadi.

### 3.3 @kulgu_va_memlar — TO'XTATILADI (reversibl pauza)
- **MEASURED:** sarf $200 (16.7%), CPM $2.50 (eng arzon), CTR 0.85% (eng past), CPL $3.40 (o'rtachadan +134%, g'olibdan +172%). Manba statusi: `KILL_CANDIDATE`.
- **Manba izohi:** "Auditoriya xaridga tayyor emas, botdan keyingi drop-off 85%. To'xtatish tavsiya etiladi."
- **Tavsiya (draft):** o'chirish emas — reversibl pauza (mutatsiya darvozasi: pauza o'chirishdan ustun). Bo'shagan ~$6.7/kun ($200/30) g'olib kanalga test qilinadi. Ssenariy (HEURISTIC_PRIOR_MODEL): bu $200 g'olib kanal CPL $1.25 bilan ishlasa ≈160 lid vs hozirgi ≈59 lid — +101 lid/oyna; bu CPL oshirilgan hajmda ham saqlanadi degan taxminga tayanadi, prognoz va kafolat emas. Alternativ: CPM eng arzon kanal — 160 belgidan qisqa yangi copy bilan qayta test (charter copy cheklovi).

## 4. Bot voronkasidagi kechikish muammosi (18 soniya) va negadir

- **MEASURED (tracking_health.json):** `latency_seconds: 18` (ideal <5); kutish sababli mijozlarning 35% botni tark etadi; CRM webhook faol; UTM taging yo'q.
- **Nega bu muammo:** klik→bot start allaqachon 64.9% (4,235 klikdan 1,485 klik botga bormaydi), bot ichidagi 30.0% lid rate esa kechikish bilan buzilgan ko'rsatkich. 2,750 bot startning 35% ≈ 963 tasi javob kutib tark etadi (hisoblangan: 2,750×0.35). Sarf jihatidan bot start boshi ≈$0.44 bo'lganda, tark etgan oqimga to'g'ri keladigan sarf ≈$420/oyna (hisoblangan, yuqori chegara — bu foydalanuvchilarning bir qismi kechikish bo'lmasa ham konvert bo'lmasligi mumkin).
- **Ssenariy (HEURISTIC_PRIOR_MODEL):** 963 tark etgan oqim o'lchangan 30% lid rate bilan davom etsa ≈+289 lid; CPL $1.45 dan $1.08 ga tushardi. Bu "bir xil konvert ratesi saqlanadi" taxmini — sensivlik bahosi, prognoz emas.
- **Diagnoz chegarasi:** webhook faol, demak kechikish webhook'ning o'zidan emas, keyingi javob uzatish zanjiridan (navbat, ishlov, tarmoq) kelib chiqadi — aniq texnik sabab manbada yo'q, tekshirilishi shart.
- **Tavsiyalar (faqat draft):** kechikishni 18s dan <5s ga tushirish; birinchi javob zudlik bilan sinxron berilib, og'ir ishlar asinxron ko'chiriladi; tuzatish oldi/keyin drop-off solishtirib o'lchanadi. E'tibor: @kulgu_va_memlar'dagi "botdan keyingi drop-off 85%" boshqa hodisa — bu kechikish emas, auditoriya mosligi muammosi; ikkalasi aralashtirilmaydi.

## 5. O'lchov xavflari (audit ishonchini pasaytiradi)

1. **UTM taging yo'q** (`utm_tagging_present: false`): bot start/lidlarning kanal mansubligi bot darajasida tasdiqlanmaydi; kanal CPL'lari platforma hisobotiga tayanadi. Tavsiya (draft): `start=` deep-link orqali UTM taging joriy etiladi (≤64 bayt cheklovi — charter authority boundary).
2. **Meta CAPI `event_id_deduplication: false`**: Pixel va CAPI ikkalasi ham xarid yuboradi, event_id mos emas — Meta hisobotlarida ~15% buyurtma ikki marta qayd etiladi (manba izohi). Bu Telegram akkaunt raqamlariga to'g'ridan-to'g'ri ta'sir qilmaydi, lekin platformalararo buyurtma summalarini aralashtirish manbadagi xavf sifatida qayd etiladi. Tavsiya (draft): dedup tuzatiladi; EMQ 6.2 o'lchangan qiymat sifatida qayd etilgan.
3. **CPL→lid ziddiyati** (≈716 vs 825): 2-bo'limda keltirildi.

## 6. Ustuvor tavsiyalar (barchasi draft — hisobga mutatsiya yo'q)

| # | Amal | Asos | Label |
|---|---|---|---|
| 1 | @toshkent_bozori: +15%/hafta byudjet oshirish | CPL $1.25 eng past, CTR 1.45% eng yuqori, WINNER_SCALE | MEASURED_ACCOUNT_DATA |
| 2 | @kulgu_va_memlar: reversibl pauza, sarfni qayta yo'naltirish testi | CPL $3.40, CTR 0.85%, drop-off 85%, KILL_CANDIDATE | MEASURED + HEURISTIC ssenariy |
| 3 | @uzb_biznes_yangiliklari: saqlash; kanal AOV o'lchangunga qadar scale yo'q | VALIDATED, B2B yuqori chek; AOV ma'lumot yo'q | MEASURED + missing_inputs |
| 4 | Bot javob kechikishi 18s → <5s; birinchi javobni tezlashtirish | 35% tark etish, ideal <5s | MEASURED_ACCOUNT_DATA |
| 5 | `start=` deep-link UTM taging joriy etish (≤64 bayt) | utm_tagging_present: false | MEASURED_ACCOUNT_DATA |
| 6 | Meta CAPI event_id dedup tuzatish | ~15% double counting | MEASURED_ACCOUNT_DATA |

Muvaffaqiyat o'lchovi: kechikish <5s dan keyin bot→lid rate qayta o'lchanadi (bazaviy 30.0%); scale kanalida CPL o'rtacha $1.45 dan yuqoriga chiqmasligi; pauzadan qayta yo'nalgan sarfning lid miqdori.

## 7. missing_inputs

Aniq sana diapazoni va timezone; kanal bo'yicha buyurtma/AOV/ROAS; kanal bo'yicha bot start va drop-off; maqsafiy CPA/ROAS; marja/COGS va LTV; bot kechikishining texnik sababi va dinamikasi; CPL→lid ziddiyatining (716 vs 825) tushuntirilishi.

## 8. JSON output contract

```json
{
  "status": "ok",
  "platform": "telegram",
  "account_id": "tg_ads_fragment_8819",
  "findings": [
    {"control": "channel_scale", "result": "scale", "object": "@toshkent_bozori", "severity": "opportunity", "confidence": "high", "recommendation": "+15%/hafta byudjet oshirish (draft); CPL $1.25, CTR 1.45%, WINNER_SCALE", "evidence": "telegram_campaigns.json"},
    {"control": "channel_scale", "result": "keep_and_measure", "object": "@uzb_biznes_yangiliklari", "severity": "info", "confidence": "medium", "recommendation": "saqlash; kanal AOV o'lchangunga qadar scale qarori yo'q", "evidence": "telegram_campaigns.json"},
    {"control": "channel_selection", "result": "pause_reversible", "object": "@kulgu_va_memlar", "severity": "high", "confidence": "high", "recommendation": "reversibl pauza, sarfni g'olib kanalga test qilish (draft)", "evidence": "telegram_campaigns.json"},
    {"control": "bot_onboarding_latency", "result": "fail", "object": "telegram_bot_telemetry", "severity": "high", "confidence": "high", "recommendation": "18s → <5s; ~963 start 35% tark etish sababli yo'qoladi (hisoblangan)", "evidence": "tracking_health.json"},
    {"control": "deep_link_tagging", "result": "fail", "object": "utm_tagging", "severity": "medium", "confidence": "high", "recommendation": "start= UTM taging joriy etish (<=64 bayt)", "evidence": "tracking_health.json"},
    {"control": "conversion_deduplication", "result": "fail", "object": "meta_capi", "severity": "high", "confidence": "high", "recommendation": "event_id dedup tuzatish (~15% double counting); Telegram raqamlariga alohida qo'llanilmaydi", "evidence": "tracking_health.json"},
    {"control": "data_reconciliation", "result": "contradiction", "object": "cpl_vs_qualified_leads", "severity": "medium", "confidence": "medium", "recommendation": "kanal lidlar yig'indisi (~716) vs 825 — manba aniqlanishi kerak", "evidence": "telegram_campaigns.json"}
  ],
  "funnel_math": {"impressions": 352940, "clicks": 4235, "ctr_pct": 1.20, "bot_starts": 2750, "bot_start_rate_pct": 64.9, "qualified_leads": 825, "lead_rate_pct": 30.0, "orders": 99, "lead_to_order_pct": 12.0, "spend_usd": 1200.00, "cpl_usd": 1.45, "cac_usd": 12.12, "aov_usd": 32.12, "revenue_usd": 3180.00, "roas": 2.65, "abandoned_bot_starts_est": 963, "abandoned_spend_est_usd": 420, "scenario_extra_leads_if_no_delay_est": 289, "scenario_cpl_if_no_delay_usd": 1.08},
  "missing_inputs": ["aniq sana diapazoni va timezone", "kanal bo'yicha buyurtma/AOV/ROAS", "kanal bo'yicha bot start va drop-off", "maqsafiy CPA/ROAS", "marja/COGS/LTV", "bot kechikishining texnik sababi", "CPL-lid ziddiyati tushuntirilishi"]
}
```

Manba: `examples/demo-brand/assets/telegram_campaigns.json` · `examples/demo-brand/assets/tracking_health.json` · 30 kunlik oyna · 2026-11-12
