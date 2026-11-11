# Tyrion — Update rejasi (v7.0.1 → v7.1 → v7.2)

**Sana:** 2026-11-11 · **Tekshirilgan holat:** `96b43e9` (v7.0.0) · **Holat:** tasdiqlash kutilmoqda, kodga hali tegilmagan

## 1. Xulosa

`doctor.py` 16/17 yashil, 196 test o'tadi — lekin bu testlar tizimning o'zini-o'zi tekshiradi, haqiqiy foydalanish ssenariylarini emas. Qo'lda tekshirganda uchta turdagi muammo chiqdi:

1. **Noto'g'ri tavsiya beradigan baglar.** `/eksport` haqiqiy Meta Ads Manager CSV faylini o'qiy olmaydi va sarf $0 deb, ad setga "SCALE +20%" hukmini chiqaradi. Spend-Guard `nan` va manfiy byudjetni o'tkazib yuboradi.
2. **Ishlamaydigan qism.** `tyrion-core` MCP serveri repo oddiy loyiha sifatida ochilganda ishga tushmaydi (shu sessiyada ham ulanmadi), `doctor` esa uni "faol" deb ko'rsatadi.
3. **Bozordan orqada qolish.** Meta Marketing API v27.0 chiqdi, atributsiya qoidalari o'zgardi, Detailed Targeting "maslahat" darajasiga tushdi, Meta rasmiy Ads MCP serverini chiqardi, O'zbekistonda reklama qonuniga yangi talablar kirdi. Bularning hech biri tizimda aks etmagan.

Tavsiya etilgan tartib: avval **v7.0.1** (ishonchni buzadigan baglar, 1–2 kun), keyin **v7.1** (bozor bilan sinxronlash), keyin **v7.2** (mahsulotni kuchaytirish).

## 2. Qanday tekshirildi va cheklovlar

- Ishga tushirildi: `doctor.py`, MCP serverga qo'lda JSON-RPC handshake, har bir asosiy CLI ga chekka holatli kirishlar, routerga 5 ta tabiiy so'rov, Meta Ads Manager formatidagi (EN va RU interfeys) sinov CSV fayllari.
- Bozor ma'lumoti veb-qidiruvdan olindi. Bu sessiyada `developers.facebook.com` va boshqa saytlarni to'g'ridan-to'g'ri ochib bo'lmadi (tarmoq ruxsati yo'q), shuning uchun **5-bo'limdagi faktlarning ko'pi ikkilamchi manbalardan** — qoidaga aylantirishdan oldin rasmiy sahifada tasdiqlash kerak (`00-manba` talabi).
- Tekshirilmagan: jonli Meta akkaunt bilan ishlash (token yo'q), Windows/macOS, `video-run.py`, `harness-export.py`.

## 3. Tasdiqlangan baglar

Har biri qayta ishlab chiqarilgan. **P0** — noto'g'ri pul qarori yoki buzilgan xavfsizlik darvozasi; **P1** — noto'g'ri natija, lekin oqibati cheklangan; **P2** — drift va tartib.

### P0

| ID | Joy | Nima bo'ladi | Tuzatish |
|---|---|---|---|
| B01 | `tools/ad-export-analyzer.py:95-108` | Haqiqiy Meta eksport ustunlari (`Amount spent (USD)`, `Ad set name`, `Link clicks`, `Purchases conversion value`) tanilmaydi: sarf=0, nom=`Row_N`. 62 konversiyali qator CPA=0 bo'lib **`SCALE (+20% / 48h)`** oladi; $310 sarflab 0 konversiya bergan qator `KEEP`. Ogohlantirish yo'q, exit 0. RU interfeys eksportida hammasi nol. | Ustun xaritasi (EN/RU/UZ, registrga befarq, `(USD)` qo'shimchasini kesib valyutani undan olish). Sarf ustuni topilmasa — xato bilan to'xtash. Sarf=0 va konversiya>0 bo'lsa hukm chiqarmaslik. |
| B02 | `tools/tyrion_core.py:51` | `safe_float` vergulni so'zsiz o'chiradi: `"499,90"` → 49990 (100 barobar), `"1 234,56"` → 123456, `"1.234,56"` → 1.23456. RU/EU formatidagi har qanday eksport buziladi. | O'nlik ajratgichni aniqlash (oxirgi ajratgichdan keyin 1–2 raqam = o'nlik). Noaniq bo'lsa xato, jim taxmin emas. |
| B03 | `tools/spend-guard.py:38-60` | `--proposed nan` → `PASSED`, exit 0 (ustiga noto'g'ri JSON `NaN`). `--proposed -50` → `PASSED`. `--proposed 0` (pauza) → `PASSED`, holbuki CLAUDE.md pauzani ham darvozadan o'tkazishni talab qiladi. | `math.isfinite` va `>0` tekshiruvi; 0 = pauza sifatida alohida tasdiq talab qilsin. |
| B04 | `tools/spend-guard.py:99-146` | Change Packet tekshiruvi kalit so'z qidiradi: ichida faqat `qaytarish chegara` yozilgan fayl o'tadi. Odam tasdig'i tekshiriladi, lekin yo'q bo'lsa xato ham, ogohlantirish ham chiqmaydi. "6 darvoza" yozuvi har qanday buyruqda chiqadi. | Majburiy bo'limlar (sarlavha + bo'sh bo'lmagan qiymat) bo'yicha tuzilmaviy tekshiruv; tasdiq bo'limi majburiy. |
| B05 | `.mcp.json`, `tools/doctor.py:228-241` | `.mcp.json` `${CLAUDE_PLUGIN_ROOT}` ga tayanadi; plagin sifatida o'rnatilmagan bo'lsa u bo'sh va `Cannot find module '.../${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cjs'` bilan yiqiladi. `doctor` faqat modulni import qilib "faol (10 MCP tool)" deydi. | `.mcp.json` da `${CLAUDE_PLUGIN_ROOT:-.}`; `doctor` sozlangan buyruqni haqiqatda ishga tushirib `initialize` + `tools/list` javobini tekshirsin. |
| B06 | `tools/capi-utm-builder.py:110-111, 160-166` | Har bir CAPI payload'ga qattiq yozilgan soxta `fbp`/`fbc` qo'shiladi va shular uchun EMQ ga +2.1 ball beriladi (CLI da ularni berish imkoni ham yo'q). Website hodisasi uchun majburiy `client_user_agent` yo'q. `action_source` doim `website` — Telegram bot/CRM oqimi uchun noto'g'ri. "EMQ 9.4" — o'ylab topilgan formula, evristika deb belgilanmagan. | Soxta standartlarni olib tashlash, `--fbp/--fbc/--user-agent/--ip/--action-source` qo'shish, yo'q maydonlarni ogohlantirish bilan ko'rsatish, EMQ ni `HEURISTIC_PRIOR_MODEL` deb belgilash. |

### P1

| ID | Joy | Nima bo'ladi | Tuzatish |
|---|---|---|---|
| B07 | `tools/capi-utm-builder.py:79` | URL da `#fragment` bo'lsa UTM undan keyin yopishadi (`/page#section?utm_source=...`) va serverga yetib bormaydi. | `urllib.parse` bilan so'rov qismiga qo'shish. |
| B08 | `tools/skill-search.py` (til aniqlash) | Aniq o'zbekcha so'rovlar `lang=en, market=global` bo'lib chiqadi: "TikTok reklamani qanday boshlayman", "Google Ads PMax kampaniyam CPA oshib ketdi". Natijada USD, GDPR/CCPA qoidalari va global benchmark yuklanadi. | O'zbek qo'shimchalari bo'yicha aniqlash (`-ni`, `-man`, `-yapti`, `qanday`, `uchun`...), noaniqlikda `MEMORY.md` dagi standart til/bozor. Evalga 10+ o'zbekcha ssenariy. |
| B09 | `plugin.json` `userConfig` | `hooks_enabled`, `hook_profile`, `default_market` e'lon qilingan, lekin kodda hech qayerda o'qilmaydi — sozlamalar ta'sir qilmaydi. | `run-hook.cjs` va `market_locale.py` da `CLAUDE_PLUGIN_OPTION_*` ni o'qish. |
| B10 | `tools/ad-export-analyzer.py:274` | Breakdown Effect "prognozi" = `blended_cpa * 1.38`. 1.38 — manbasiz konstanta, foydalanuvchiga aniq raqam sifatida ko'rsatiladi. | Raqamni olib tashlash yoki evristika deb belgilab, diapazon bilan berish. |
| B11 | `tools/calculator.py` | Zarar holatida ham exit 0; `--price nan` → `$nan`, exit 0. | Kirishni tekshirish, zarar holatida nolga teng bo'lmagan exit. |
| B12 | `tools/tyrion-mcp-server.py:372-417` | `ping` yo'q (`-32601`); `protocolVersion` `2024-11-05` ga qotirilgan; tool xatolari `isError` natija emas, JSON-RPC xato; `inputSchema` da `call_tool` qabul qiladigan parametrlar yo'q (`creative_matrix`: mode/market/language; targeting: locale/max_queries). | Protokol versiyasini kelishish, `ping`, sxemalarni haqiqiy parametrlar bilan tenglashtirish. |
| B13 | `tools/spend-guard.py:150-210` | Telegram tekshiruvida ⭐ va bayroq emojilari sanalmaydi (5 ta emoji o'tadi); o'zbek kirill bosh harflari (Ў, Қ, Ғ, Ҳ) ALL CAPS deb tanilmaydi; Meta taqiqlangan iboralari faqat o'zbekcha; docstring'dagi `--event-id --has-pixel --has-capi` bayroqlari mavjud emas. | Emoji diapazonini to'ldirish, kirill sinfini kengaytirish, RU/EN iboralar, docstring'ni to'g'rilash. |
| B14 | `.gitignore`, `push.sh` | `clients/` va `outputs/` ignore qilinmagan — mijoz briflari va hisobotlari `push.sh` bilan ochiq repoga ketadi. `push.sh` `origin` manzilini majburan almashtiradi, doim `main` ga push qiladi, unit testlarni ishga tushirmaydi. | `clients/*` (shablondan tashqari) va `outputs/` ni ignore qilish; `push.sh` joriy branch va mavjud remote bilan ishlasin. |
| B15 | `tools/doctor.py:259-273` | Graf eskirganini fayl `mtime` bo'yicha aniqlaydi — yangi klonda hamisha yolg'on ogohlantirish. Maslahatdagi `gy.cmd` fayli repoda yo'q. | Kontent xeshi yoki `updated:` sanasi bo'yicha solishtirish. |
| B16 | `tools/meta-insights-sync.py:240-250` | Insights so'rovida atributsiya oynasi ko'rsatilmaydi — natija akkaunt standartiga bog'liq va 2026 atributsiya o'zgarishlaridan keyin davrlararo solishtirib bo'lmaydi. `*_usd` kalitlari valyuta UZS bo'lsa ham shunday nomlanadi. | Atributsiya sozlamasini aniq so'rash va hisobotda ko'rsatish; `_usd` kalitlarini valyutaga neytral qilish. |
| B17 | `tools/capi-utm-builder.py:45-49` | Telefon normalizatsiyasi faqat O'zbekiston uchun; boshqa 8 bozorda mamlakat kodi qo'shilmaydi, boshidagi 0 olinmaydi — xesh mos kelmaydi. | Bozor paketidan mamlakat kodi; E.164 ga keltirish. |

### P2 — drift

| ID | Nima |
|---|---|
| B18 | Versiya: mahsulot 7.0.0, lekin "v5.0" 130 joyda (`CLAUDE.md`, `AGENTS.md`, `install.*`, `push.*`, `.env.example`, kontekstlar, playbooklar). ~20 ta `SKILL.md` da "CAPI v22", payload'da `capi_v22_payload` kaliti. `catalog.py sync-claims` sonlarni sinxronlaydi, versiyani emas. |
| B19 | Graph API versiyasi 5 faylda alohida konstanta (`DEFAULT_GRAPH_API_VERSION`) — bitta manba yo'q. |
| B20 | CI faqat `main/master/feat/**/sync/**` push'larida ishlaydi; boshqa branchlar PR ochilmaguncha tekshirilmaydi. |
| B21 | Bilim manbasi: 100 wiki qayddan 77 tasining `source:` maydoni repoda yo'q yo'llarga ishora qiladi (`claude-ads-main/...`, `raw/...`, `vedio bilimlar/...`); URL faqat 23 tasida. `mcp-integration.md`: "Refresh due 2026-08-10" — 3 oy o'tib ketgan. |
| B22 | Testlar: 196 test bitta 3 196 qatorli faylda, haqiqiy eksport fixture'lari yo'q; 24 eval faqat routingni tekshiradi, asbob natijasining to'g'riligini emas. |

## 4. Tuzilmaviy kamchiliklar

- **Yashil ko'rsatkichlar haqiqatni aks ettirmaydi.** B01 va B05 ikkalasi ham `doctor`, testlar va CI dan o'tgan. Tekshiruvlar "fayl bormi, son mosmi" darajasida; "asbob to'g'ri javob beradimi" darajasida emas.
- **Evristikalar fakt kabi beriladi.** 20% qoidasi, 50 konversiya, 1.5×/1.35×/0.85× chegaralar, frequency 2.8, EMQ formulasi, Telegram voronka standartlari (CTR 1.2%, bot-start 65%) — hech biri natijada `HEURISTIC_PRIOR_MODEL` deb belgilanmagan. Bu loyihaning o'z 3-qoidasiga zid.
- **Spend-Guard holatsiz.** "24 soatda ≤20%" deyiladi, lekin o'zgarishlar jurnali yo'q — kuniga besh marta +20% o'tadi.
- **Asosiy ustunlik eskirmoqda.** Detailed Targeting Accuracy Engine eng katta modul (2 502 qator), Meta esa interest'larni maslahat darajasiga tushirdi (5-bo'lim).

## 5. Bozor o'zgarishlari va Tyrionga ta'siri

| Soha | Nima o'zgardi | Tyrionda holat | Kerakli ish |
|---|---|---|---|
| Meta API | Marketing API **v27.0** (2026-noyabr boshi): `lookalike_spec` da country/location rad etiladi, katalog `/batch` o'chirildi, yangi Sales ad setlarda product showcase va device expansion standart yoqiq. v26.0 (27-oktabr): Delivery Estimate maydonlari va Instagram Explore placement olib tashlandi. v21 — 2027-01-21, v22 — 2027-05-20 da o'chadi. | Hamma joyda v26.0; eskirish chegarasi `<v25`. | Versiya reyestri (bitta manba + sunset sanalari), v27 ga o'tish, LAL va placement tavsiyalarini ko'rib chiqish. |
| Meta kampaniya | Advantage+ Shopping/App eski kampaniyalarini API orqali yaratib/o'zgartirib bo'lmaydi (2026-05-19 dan barcha versiyalarda). | "ASC" 28 faylda 37 marta. | Atamalar va tuzilma tavsiyalarini Advantage+ Sales modeliga keltirish. |
| Meta atributsiya | 7 va 28 kunlik view oynalari 2026-01-12 da olib tashlandi; 2026-martdan click-through faqat link click; engaged-view chegarasi 10 → 5 soniya. | Hech qayerda yo'q. | `ads-attribution` va `conversion-tracking` ni yangilash; hisobotlarda "2025 bilan to'g'ridan-to'g'ri solishtirmang" ogohlantirishi. |
| Meta targeting | Detailed targeting ko'p konversiya kampaniyalarida maslahat signali; exclusion'lar olib tashlangan; interest'lar birlashtirilgan. | Engine interest'ni qattiq cheklov kabi taqdim etadi. | Natijada "tekshirilgan ≠ kafolatlangan yetkazish" deb yozish; og'irlikni kreativ xilma-xilligi, 1P auditoriya va CAPI ga ko'chirish. |
| Meta AI Connectors | 2026-04-29: rasmiy hosted **Ads MCP** va Ads CLI — 29 tool, kampaniya yaratish/tahrirlash bilan; biznes portfolio darajasida agent qoidalari. | Wiki uchinchi tomon `pipeboard` serverini tavsiya qiladi; `mcp-integration.md` da Meta qatori yo'q. | Rasmiy serverni hujjatlash; Spend-Guard ni yozuvchi tool'lar oldidagi tasdiq darvozasi sifatida joylash. |
| Meta signal sifati | Dataset Quality API ga event spend, event delay va yangi EMQ diagnostikalari qo'shildi. | EMQ taxminiy formula bilan. | Token bo'lsa haqiqiy EMQ ni API dan olish. |
| Google | AI Max aprelda betadan chiqdi; 1-sentabrda ACA/broad kampaniyalar AI Max ga ko'chirildi; DSA 2027-fevralda yopiladi; Display → Demand Gen (2027 gacha); Ads API v26 (14-oktabr), v22 o'chirilgan. | AI Max/Demand Gen qamrab olingan, DSA faqat bitta tekshiruv. | Migratsiya tekshiruvlarini qo'shish, sanalarni yangilash. |
| Telegram Ads | 160 belgi va 1 tugma o'zgarmagan; yangilari: Target Users, siyosiy kanallarni o'chirish, qidiruvdagi reklama, botlardagi reklama, **piksel**, Stars/TON kabinetida bannerlar. | Reference'da piksel va yangi formatlar yo'q. | `telegram-audit.md` ni yangilash; kalkulyator standartlarini evristika deb belgilash. |
| O'zbekiston qonunchiligi | 2026-11-10 dagi qonun: kredit reklamasida moliyaviy xatar ogohlantirishi maydon/davomiylikning ≥10%. 2026-11-01 dan: SMS reklama faqat oldindan rozilik bilan, reklama qo'ng'iroqlari 18:00–09:00 taqiqlangan. Raqobat qo'mitasi 2026 I yarmida 13 500 tekshiruv, ~6 000 buzilish. | Kreativ modul har bir matnga "Oyiga atigi … (Nasiya orqali)" langarini avtomat qo'shadi; UZ voronkasida SMS va 15 daqiqalik call-center SLA. | `markets/uz` ga compliance tekshiruvi: nasiya eslatilsa ogohlantirish talabi, SMS roziligi, qo'ng'iroq vaqti. Yurist/lex.uz bilan tasdiqlash. |
| Raqobat | Google (read-only), Meta, Amazon, TikTok, Microsoft rasmiy MCP serverlari; ochiq "Claude Ads" skill to'plami (12 platforma); 48–98 skilli marketing to'plamlari. | — | Farqlovchi jihat API o'rami emas: boshqaruv qatlami (Spend-Guard), O'zbekiston/MDH lokalizatsiyasi, dalil belgilari. |

## 6. Reja

### v7.0.1 — Ishonch hotfix (1–2 kun)
Tarkib: B01–B07, B11, B14.

Qabul mezoni:
- Haqiqiy formatdagi 4 ta fixture (`Meta EN`, `Meta RU`, `Google Ads`, `Telegram Ads`) testlarda; hech biri sarf=0 bilan hukm chiqarmaydi.
- Spend-Guard: `nan`, `inf`, manfiy, 0 — barchasi bloklanadi (test bilan).
- `doctor` MCP serverni haqiqatda ishga tushiradi; repo plaginsiz ochilganda `tyrion-core` ulanadi.
- CAPI payload'da kiritilmagan qiymat yo'q.
- `clients/` va `outputs/` git'ga tushmaydi.

### v7.1 — Bozor sinxroni (3–5 kun)
1. Graph API versiya reyestri va v27.0 ga o'tish (B19).
2. Atributsiya 2026 qoidalari: skill/reference + insights so'rovi (B16).
3. Detailed Targeting'ni "maslahat signali" sifatida qayta joylash.
4. Meta rasmiy Ads MCP integratsiyasi + Spend-Guard darvozasi; `mcp-integration.md` ni yangilash.
5. O'zbekiston compliance tekshiruvi (kredit ogohlantirishi, SMS, qo'ng'iroq vaqti).
6. Telegram va Google reference'larini yangilash.
7. Yangilik tizimi: har bir bozor faktida `verified` va `refresh_due`; `doctor` muddati o'tganini ko'rsatsin.
8. Versiya driftini tozalash va `sync-claims` ni versiyaga kengaytirish (B18).

Qabul mezoni: har bir yangi fakt rasmiy manba URL va tekshirilgan sana bilan; `doctor` da muddati o'tgan reference 0 ta.

### v7.2 — Mahsulot (1–2 hafta)
1. Eksport tahlili v2: sana oralig'ini hisobga olish, jami qatorni ajratish, kichik tanlamada hukmdan tiyilish.
2. Spend-Guard jurnali: 24 soatlik oyna, o'zgarishlar tarixi, tasdiq yozuvi.
3. CAPI: Telegram bot/CRM hodisalari (`action_source`, `lead_id`), haqiqiy EMQ.
4. Router: o'zbek tilini aniqlash, plagin sozlamalari (B08, B09).
5. MCP protokoli (B12).
6. Barcha evristikalarga `HEURISTIC_PRIOR_MODEL` belgisi va sozlanadigan chegaralar.
7. Testlarni modullarga bo'lish, asbob natijasi uchun evallar, CI barcha branchlarda (B20, B22).
8. Wiki manbalarini tiklash yoki "tasdiqlanmagan" deb belgilash (B21).

## 7. Sizdan kerak bo'lgan qarorlar

1. **Asosiy auditoriya:** O'zbekiston operatori (standart `uz`, o'zbek tili) yoki global mahsulot (standart `global`)? B08 ning yechimi shunga bog'liq.
2. **Yozish huquqi:** Tyrion Meta rasmiy MCP orqali akkauntga o'zgarish kirita olsinmi (Spend-Guard tasdig'i bilan) yoki faqat o'qish va tavsiya rejimida qolsinmi?
3. **20% qoidasi:** qattiq blok bo'lib qolsinmi yoki sozlanadigan ogohlantirishga aylansinmi?
4. **Wiki manbalari (B21):** asl `raw/` materiallar sizda bormi? Bo'lsa qaytarish, bo'lmasa 77 qaydni "tasdiqlanmagan" deb belgilash kerak.

## 8. Manbalar

Bozor faktlari quyidagilardan; rasmiy tasdiq talab qilinadi.

- Meta API: [ppc.land — v27](https://ppc.land/metas-api-v27-may-add-catalog-products-to-new-ads-by-default/), [relevantaudience.com — v27](https://www.relevantaudience.com/meta/meta-marketing-api-v27-product-showcase-device-expansion-defaults/), [Meta — v26.0 changelog](https://developers.facebook.com/docs/graph-api/changelog/version26.0/), [Meta — v25.0](https://developers.facebook.com/blog/post/2026/02/18/introducing-graph-api-v25-and-marketing-api-v25/), [ppc.land — legacy Advantage+ API](https://ppc.land/meta-deprecates-legacy-campaign-apis-for-advantage-structure/)
- Meta reklama: [commonthreadco.com — 2026 o'zgarishlar](https://commonthreadco.com/blogs/coachs-corner/meta-ads-changes-2026), [nowoka.com](https://nowoka.com/blog/meta-ads-andromeda-advantage-plus-guide-2026/), [marketlube.in](https://marketlube.in/blog/meta-ads-updates), [denote.net](https://denote.net/blog/meta-andromeda-update-2026), [growthspreeofficial.com — CAPI](https://www.growthspreeofficial.com/blogs/meta-conversions-api-b2b-saas-2026), [Meta — Dataset Quality API](https://developers.facebook.com/documentation/ads-commerce/conversions-api/dataset-quality-api)
- Meta AI Connectors: [Meta e'loni](https://www.facebook.com/business/news/meta-ads-ai-connectors), [Ads MCP Server hujjati](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-overview)
- Google: [bytown.co](https://bytown.co/guide/google-ads-changes-2026), [hawky.ai](https://hawky.ai/blog/google-ads-updates-2026), [lgg.media](https://www.lgg.media/blog/google-ads-updates-september-2026/), [onemetrik.com — API v26](https://onemetrik.com/market-insights/google-ads-api-v26/)
- Telegram: [adsgram.ai](https://adsgram.ai/blog/adsgram/telegram-ads-the-complete-guide-to-formats-costs-and-launching-your-first-campaign), [adsplatform.net](https://adsplatform.net/en/telegram-ads-new-update/), [propellerads.com](https://propellerads.com/blog/adv-telegram-ads/)
- TikTok: [TikTok Q3 2026 preview](https://ads.tiktok.com/business/en-CA/blog/tiktok-product-preview)
- O'zbekiston: [yuz.uz — kredit reklamasi](https://yuz.uz/en/news/kredit-bilan-bogliq-reklamalarda-moliyaviy-xatarlar-haqida-ogohlantirish-bolishi-kerak), [uzdaily.uz — 1-noyabrdan o'zgarishlar](https://www.uzdaily.uz/en/what-changes-in-uzbekistans-legislation-from-1-november-2026/), [uzdaily.uz — 6 000 buzilish](https://www.uzdaily.uz/en/uzbek-competition-body-finds-6000-ad-violations/), [Dentons — raqamli platformalar](https://www.dentons.com/en/insights/articles/2025/may/14/uzbekistan-digital-platforms-regulation)
- Raqobat: [googleads/google-ads-mcp](https://github.com/googleads/google-ads-mcp), [adadvisor.ai — Claude Ads](https://adadvisor.ai/blog/what-is-claude-ads)
