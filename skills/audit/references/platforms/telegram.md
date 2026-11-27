<!-- v8: eski skill `ads-telegram` (v7.1) matni; tavsif: ads.telegram.org va Fragment bo'yicha Telegram Ads kampaniyalarini audit qilish, rejalash, qoralash va optimallashtirish. Kanal targetingi, 160 belgilik matn formulalari, CPM bidding, bot suhbat voronkalari, server-side webhooklar va policy muvofiqligini qamrab oladi. -->

# Telegram Ads operatsion playbooki

## Tartib

1. **Qabul qilish va tekshiruv**:
   - Sotib olish valyutasini aniqlang (TON, Stars yoki Fragment/vakolatli agentlik orqali EUR).
   - Maqsadli manzilni aniqlang: ommaviy kanal (`t.me/channel`), bot (`t.me/bot`), aniq post yoki tashqi veb-sayt.
   - Biznes maqsadini belgilang: kanal obunachilari, bot lidlari, sayt trafigi yoki to'g'ridan-to'g'ri sotuv.
2. **Kanal tadqiqoti va tanlash**:
   - Nomzod ommaviy kanallarni tekshiring: obunachilar soni $\ge 1,000$, Engagement Rate on Reach (ERR) $\ge 15\%$ va organik ko'rishlar barqarorligini tasdiqlang.
   - Aniq kanal targetlarini keng mavzuviy kategoriyalardan ajrating.
3. **160 belgilik matn yozish**:
   - Qat'iy 160 belgi chegarasida yozing.
   - Farqli variantlarni shakllantiring: muammo/yechim, qiziqish/keys, auditoriyaga to'g'ridan-to'g'ri murojaat.
   - Moderatsiyaga muvofiqlikni ta'minlang: ko'pi bilan 1 ta kontekstli emoji, BARCHA BOSH HARFLI so'zlar yo'q, sensatsion clickbait yo'q, tekshirib bo'lmaydigan daromad va'dalari yo'q.
4. **Suhbatli voronka va bot sozlamasi**:
   - Deep linking'ni tekshiring: `t.me/Bot?start=utm_source_campaign_angle`.
   - Bot javob tezligini sinang: avtomatik salomlashuv va lead magnet yetkazish $<10$ soniyada ishga tushishi kerak.
   - CRM webhook integratsiyasi `/start`, faollashtirish, lid va sotuvni kuzatishini ta'minlang.
5. **Auksion bidding va pacing**:
   - Boshlang'ich CPM bid'ni kanal obro'siga qarab belgilang (auksiondan o'tish uchun benchmark pastki chegarasi + 20–30% dan boshlang).
   - Byudjet tez tugab qolmasligi uchun kunlik sarf chegaralarini joriy qiling.
6. **Yetkazib berish va hisobot**:
   - Topilmalarni tuzilgan audit yoki `rules/50-topshirish-dod.md` ga mos launch Change Packet sifatida taqdim eting.

## Chegaralar va xavfsizlik darvozalari

- Standart bo'yicha faqat o'qish: foydalanuvchining aniq tasdig'isiz reklama kabinetlarida bidlar yoki kampaniyalarni hech qachon o'zgartirmang (`rules/40-xavfsizlik-va-hisob.md`).
- Telegram Ads'ni hech qachon faqat click-through rate (CTR) bo'yicha baholamang; malakali lid narxi (CPQL) va yopilgan daromadni baholang.
- Global benchmarklarni olmang: kampaniyalarni mijozning tarixiy ko'rsatkichlari va mahalliy konversiya dinamikasiga qarshi baholang.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Telegram Ads CPM auksioni dinamik raqobatli biddingda ishlaydi; 24 soat ichida nol ko'rsatuv bid pastki chegaradan pastligi (starvation)ni bildiradi.
- Markaziy Osiyo va MDH bozorlarida aniq kanal targetingi keng kategoriya targetingiga nisbatan 2–4 baravar yuqori konversiya samaradorligini beradi.
- Barcha reklama matni maqsadli yozuvda (o'zbek lotin, o'zbek kirill yoki rus) tabiiy yozilishi shart; mashina tarjimasi yuqori rad etish va past engagementga olib keladi.
- Policy ruxsati: Telegram Ads moderatsiyasi tinish belgilari, formatlash va da'volarda qat'iy. Ohang neytral, professional va axborotli bo'lishi kerak.

### Bog'liq manbalar
- `ads/references/telegram-audit.md`
- `wiki/telegram-voronka-va-email-minimum.md`
- `wiki/telegram-ads-platformasi.md`


## Deterministik CLI va asboblar integratsiyasi (`0 token`)
Tavsiyalar yaratish yoki rejalarni o'zgartirishdan oldin `ads-telegram` uchun tegishli Tyrion v8.3 deterministik tekshiruvlarini ishga tushiring:
- **Unit-iqtisodiyot va break-even:** `python3 tools/calculator.py breakeven --price <AOV> --cogs <COGS>`
- **Meta auditoriya va voronka diagnostikasi:** `python3 tools/meta-audience.py architect --niche <niche> --budget <daily_usd>`
- **CSV/JSON eksport va Breakdown Effect:** `python3 tools/ad-export-analyzer.py analyze --file <export.csv>`
- **CAPI v22 SHA-256 va Telegram Bot UTM:** `python3 tools/capi-utm-builder.py utm --url <url> --platform meta`
- **Spend-Guard darvozasi:** `python3 tools/spend-guard.py budget --current <old> --proposed <new> --max-cap <cap>`

## Anti-patternlar (`NOTO'G'RI` va `TO'G'RI`)
| Holat | ❌ XATO (`NOTO'G'RI`) | ✅ TO'G'RI (`TO'G'RI`) |
|---|---|---|
| **Benchmark da'volari** | Akkaunt tarixi yoki break-even hisobisiz umumiy global CTR/CPA o'rtachalarini keltirish. | Avval `tools/calculator.py` orqali aniq `Break-Even ROAS = 1 / Margin` va `Target CPA` ni hisoblash (`[[00-manba]]`). |
| **Byudjetni masshtablash** | Faol ad set byudjetini bir kechada ikki baravar (+100%) oshirib, Learning Phase'ni nolga tushirish. | Vertikal masshtablashda **har 48–72 soatda ko'pi bilan +20%** (`tools/spend-guard.py`) yoki g'olib angle'larni gorizontal klonlash (`[[learning-phase-qoidalari]]`). |
| **Auditoriya izolyatsiyasi** | Cold prospecting (`TOF`) ni `Purchase 180d`, `Leads 30d` va `Active DM 14d` ni chiqarmasdan yuritish. | 4 qatlamli Exclusion matritsasini `tools/meta-audience.py architect` orqali majburiy qilish (`[[meta-auditoriya-arxitekturasi]]`). |
| **Placement'larni qisqartirish** | Yuqori hajmli placement'larni (masalan Instagram Reels) faqat o'rtacha CPA yuqori bo'lgani uchun pauza qilish (*Breakdown Effect*). | Marginal CPA ta'sirini baholash uchun `tools/ad-export-analyzer.py breakdown-effect` ni ishga tushirish (`[[meta-breakdown-effekti]]`). |
