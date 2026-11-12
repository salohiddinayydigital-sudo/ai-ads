# Telegram Ads kanallar audit — tg_ads_fragment_8819

Sana: 2026-11-12 · Platforma: telegram · Valyuta: USD · Oyna: 30 kun (`window_days=30`)
Manbalar: `examples/demo-brand/assets/telegram_campaigns.json` (30 kunlik export) · `examples/demo-brand/assets/tracking_health.json` (telegram_bot_telemetry bo'limi). Export sanasi ikkala faylda ko'rsatilmagan — unknown.

## Ma'lumot holati

- Bor: umumiy summary (spend, CPM, CTR, bot starts, leads, orders, ROAS), 3 kanal darajasidagi spend/CPM/CTR/CPL + status; bot telemetriya: webhook holati, UTM borligi, javob kechikishi, drop-off ogohlantirishi.
- Yo'q (unknown — taxmin qilinmagan): kanal darajasidagi orders/revenue/ROAS, kanallar bo'yicha bot start va drop-off (faqat @kulgu uchun 85% va bot umumiy 35% berilgan), AOV per kanal, conversion lag, rasmiy Telegram limitlar (joriy manbadan tekshirilishi shart, qotirilgan raqam ishlatilmagan).

## Umumiy ko'rsatkichlar (manba: telegram_campaigns.json `summary` bloki)

- Spend 1200 USD, 352 940 impression, CPM 3.40, CTR 1.20% (4235 klik).
- Bot starts 2750 — kliklarning 64.9%; qualified leads 825 — bot startlarning 30.0%; CPL 1.45.
- Orders 99, CAC 12.12, revenue 3180 USD, ROAS 2.65 (hisobning o'z tarixi — yagona benchmark bazasi).
- Kanal spend yig'indisi 450+550+200 = 1200 USD — summary bilan mos, ma'lumot tutashgan (hisoblangan).

## Kanallar bo'yicha dalillar

### 1. @toshkent_bozori — SCALE QILINADI
- Dalil (manba raqamlari): spend 450 (37.5%), CPM 3.00, CTR 1.45%, CPL 1.25, status `WINNER_SCALE`.
- Hisoblangan: CTR hisob o'rtachasidan +21% (1.45 vs 1.20), CPL hisob CPLidan 14% past (1.25 vs 1.45).
- Manba izohi: "Eng arzon va sifatli xaridlar. Haftasiga +15% byudjet oshirish mumkin."
- Negadir: eng past CPL va o'rtachadan yuqori CTR birgalikda sifatli trafikni ko'rsatadi; kanal darajasida orders/ROAS berilmagani uchun scale qarori CPL+CTR+manba statusiga tayanadi.

### 2. @uzb_biznes_yangiliklari — SAQLANADI, monitoring ostida
- Dalil: spend 550 (eng katta ulush, 45.8%), CPM 4.20 (eng qimmat), CTR 1.10%, CPL 1.85, status `VALIDATED`.
- Manba izohi: "B2B va yuqori chekli premium kostyumlar xaridorlari."
- Negadir: "yuqori chek" da'vosini tasdiqlovchi kanal darajasidagi AOV/ROAS faylda yo'q (unknown) — kill ham, agressiv scale ham asoslangan emas; CPL 1.85 yuqoriligi monitoring sababi.

### 3. @kulgu_va_memlar — TO'XTATILADI
- Dalil: spend 200 (16.7%), CPM 2.50 (eng arzon), CTR 0.85%, CPL 3.40 (eng qimmat), status `KILL_CANDIDATE`.
- Hisoblangan: CPL hisob CPLidan 2.34x qimmat (3.40 vs 1.45), CTR o'rtachadan 29% past.
- Manba izohi: "Auditoriya xaridga tayyor emas, botdan keyingi drop-off 85%. To'xtatish tavsiya etiladi."
- Negadir: arzon CPM sifatni o'rnitmaydi — klik arzon, lekin botdan keyin 85% tashlab ketish; bu yolga chiqish sig'imi emas, xarid niyati muammosi (manba izohiga ko'ra).

## Bot voronkasi kechikish muammosi (manba: tracking_health.json → telegram_bot_telemetry)

- Bot javob kechikishi 18 soniya (`latency_seconds: 18`); manba ideal sifatida <5 soniyani ko'rsatgan — 3.6x yuqori (hisoblangan).
- Manba `critical_risk` ogohlantirishi: "Kutish sababli mijozlarning 35% botni tark etmoqda" — kechikish bevosita lead yo'qotish manbai sifatida ko'rsatilgan.
- Voronka matematikasi (hisoblangan, summary asosida): 4235 klik → 2750 bot start (64.9%) → 825 lead (30.0%) → 99 buyurtma (lead→order 12%). Bot startdan leaddingacha jami 70% yo'qotish bor; 35% kutish sababli degan ulush manba berilgan, qolgan yo'qotish sabablari taqsimoti faylda yo'q (unknown).
- `utm_tagging_present: false` — bot trafik manbalarini ajratmaydi; `crm_webhook_active: true` — CRM webhook faol.
- Salbiy zanjir (kuzatuv): arzon lekin sifatsiz trafik (@kulgu, 85% drop-off) + 18 soniya kutish bir-birini kuchaytiradi; kechikish tuzatilmasa scale qilinayotgan kanallar ham lead yo'qotadi.
- Doira chegarasi: tracking_health.json'da Meta CAPI `event_id_deduplication: false` (~15% double counting) ham qayd etilgan, lekin bu Telegram doirasidan tashqari — alohida audit mavzusi.

## Tavsiyalar (faqat matn — hisobga hech qanday o'zgartirish kiritilmagan)

1. @toshkent_bozori: manba tavsiyasiga ko'ra bosqichma-bosqich scale (+15%/hafta); har qadamda CPL 1.25 bazasi (o'z tarixi benchmark) bilan solishtiriladi, CPL sezilarli oshsa to'xtatiladi.
2. @uzb_biznes_yangiliklari: saqlanadi; keyingi qadam — kanal darajasida orders/AOV/ROAS o'lchash va "yuqori chek" da'vosini hisobning o'z ma'lumoti bilan tasdiqlash.
3. @kulgu_va_memlar: manba tavsiyasiga ko'ra to'xtatish; bo'shagan ~200 USD hajm @toshkent_bozori kanalida sinov sifatida ishlatilishi tavsiya etiladi (yakuniy qaror konduktor/mutaxassis qarori).
4. Bot kechikishi: 18s → manbadagi ideal <5s darajasiga tushirish ustuvor muammo sifatida ko'rib chiqilsin, chunki 35% drop-off (manba raqami) bevosita lead hajmiga ta'sir qiladi.
5. UTM: `utm_tagging_present=false` bo'lgani uchun bot `start` deep linkiga UTM parametrlari qo'shilishi tavsiya etiladi — aks holda kechikish tuzatilgandan keyingi yaxshilanish kanallar bo'yicha ajratib o'lchanmaydi.

## Ziddiyatlar va cheklovlar

- Ziddiyat aniqlanmadi: kanal spend yig'indisi summary bilan mos.
- Cheklov: kanal darajasidagi konversiya/ROAS va kanallar bo'yicha drop-off faylda yo'q — audit CPL, CTR, manba statuslari va bot umumiy telemetriyasiga tayanadi; bu hisobning o'z ma'lumoti (1-darajali manba), global benchmark ko'chirilmagan.

Manba: examples/demo-brand/assets/telegram_campaigns.json · examples/demo-brand/assets/tracking_health.json · 30 kunlik oyna, export sanasi ko'rsatilmagan (unknown)
