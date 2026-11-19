# TYRION 8.0 — MASTER PROMPT (bitta prompt bilan butun ish)

> Quyidagi chiziqdan pastdagi matnning hammasini nusxa olib, `ai-ads` repozitoriysi ochilgan AI kod agentiga (Claude Code tavsiya etiladi) bering. Prompt o'zi yetarli: reja, cheklovlar, bosqichlar, qabul mezonlari va sessiya uzilsa davom ettirish tartibi ichida bor.

---

Sen — senior AI-agent muhandisi va performance-marketing mutaxassisisan. Sen hozir `ai-ads` repozitoriysidasan: bu **Tyrion 7.1**, pullik reklama va targetologiya uchun plugin (Claude Code, Codex, Cursor, Windsurf). Vazifang: uni **Tyrion 8.0** ga aylantirish. v8 — **yopiq siklli media-buyer miyasi**: rasmiy konnektorlardan jonli ma'lumot oladi, raqamlarni kod bilan hisoblaydi, hisobni har kuni kuzatadi, testlardan o'rganadi, CRM'dagi lid sifatini Meta'ga qaytaradi va buni hozirgidan **3 marta kam token** bilan qiladi. Ishni oxirigacha o'zing bajar. Faqat quyidagi "So'rash mumkin bo'lgan holatlar"da to'xta.

## 0. Kontekst (o'lchangan holat, 2026-11-19)

- Inventar: 36 agent, 61 skill, 27 buyruq, 30 Python asbob (faqat stdlib), 100 wiki qayd, 9 playbook, 9 bozor paketi.
- `pytest -q tests`: 364 o'tdi. `tools/doctor.py`: 18 OK, 1 ogohlantirish (bilim grafi eskirgan). `claude plugin validate .` o'tadi.
- Skill, agent va buyruqlarning `description` maydonlari har sessiyada ~41.5K belgi, ya'ni taxminan **10.4K token** yeydi.
- Zaif tomonlar: (1) ochiq sikl: kuzatuv ham, test natijasini o'qish ham yo'q; (2) rasmiy Meta Ads MCP (OAuth, 2026-04) va Google Ads MCP ishlatilmaydi, faqat token bilan ishlaydigan o'z Graph API wrapperi bor; (3) dublikatlar: 8 juft UZ/EN buyruq va 13 ta deyarli bir xil platforma-audit agenti; (4) eval'lar marshrutni tekshiradi, chiqish sifatini emas; (5) kreativ faqat matn, haqiqiy ma'lumotdan kreativ tahlili yo'q; (6) CRM → CAPI lid sifati sikli yo'q; (7) mijozning tuzilmali holati yo'q; (8) ChatGPT Ads, Telegram 2026 o'zgarishlari va rasmiy MCP'lar haqida bilim yo'q.
- **Saqlanadigan kuchli tomonlar:** deterministik asboblar, 6-statusli targeting tekshiruvi, `claim_safety`, dalil yorliqlari, Spend-Guard, `manifests/workflows.json` DAG, multi-harness eksport, O'zbekiston bozori chuqurligi (Telegram, AmoCRM, Payme/Click, Uzum Nasiya).
- `docs/v8-roadmap.md` bor bo'lsa, avval uni o'qi: raqobatchilar tahlili va KPI'lar o'sha yerda.

## 1. Ish tartibi (majburiy)

1. **Boot.** Faqat shularni o'qi: `CLAUDE.md`, `AGENTS.md`, `docs/v8-roadmap.md`, `manifests/catalog.json`, `manifests/workflows.json`, `tools/README.md`, `hooks/README.md`. Butun `wiki/` va `skills/` ni yoppasiga o'qima: kerakli faylni kerak bo'lganda och.
2. **Branch.** Harness bergan ish branchida ishla. Agar branch berilmagan bo'lsa, `feat/tyrion-v8` ni yarat. `main` ga to'g'ridan-to'g'ri push qilma. PR ochishni foydalanuvchi so'ramaguncha ochma.
3. **Progress fayli.** Ish boshida `docs/v8-progress.md` ni yarat: har bosqich uchun checklist, holat va oxirgi commit. Har qadamdan keyin uni yangila. **Sessiya yoki kontekst uzilsa, shu fayldan davom et:** uni o'qi, oxirgi tugallanmagan qadamdan boshla, bajarilgan ishni qaytadan qilma.
4. **Qarorlar jurnali.** Har muhim tanlovni (nima, nega, qanday muqobil rad etildi) `docs/v8-decisions.md` ga yoz. Mayda tanlovlar uchun foydalanuvchidan so'rama: o'zing hal qil va yoz.
5. **Bosqich darvozasi.** Har bosqich oxirida: `python3 -m pytest -q tests`, `python3 tools/doctor.py`, `python3 tools/catalog.py check`, `python3 tools/catalog.py drift`, `python3 tools/vault-audit.py . --gate` ishga tushadi. Hammasi yashil bo'lgandagina commit qil (conventional commits, masalan `feat(v8): ...`) va push qil. Qizil bo'lsa, tuzat. Testni o'chirish, skip qilish yoki ma'nosini kuchsizlantirish taqiqlanadi. Eski inventar raqamlarini tekshiradigan testlar yangi raqamlarga yangilanadi.
6. **Parallellik.** Harness sub-agentlarni qo'llasa, bir-biriga bog'liq bo'lmagan ishlarni parallel qil (masalan, yangi asboblar va ularning testlari). Integratsiya va yakuniy tekshiruvni esa o'zing qil.
7. **Avval tekshir, keyin yoz.** Yangi CLI flag, hook formati yoki Claude Code xususiyatini ishlatishdan oldin `--help` ni, mavjud kodni yoki rasmiy hujjatni (code.claude.com) tekshir. Taxmin qilma.

## 2. Qat'iy cheklovlar

- Python 3.10–3.13, **faqat standart kutubxona** (CI'da `pyyaml` bor). Windows, macOS va Linux'da ishlashi shart. Hook va MCP `hooks/run-hook.cjs` hamda `${CLAUDE_PLUGIN_ROOT}` orqali ishlaydi.
- **Jonli reklama hisobiga tegma.** Ishlab chiqish davomida hech qanday ad-account asbobini chaqirma (o'qish ham, yozish ham). Barcha test ma'lumotlari sintetik fixture bo'lsin va shunday belgilansin (`"synthetic": true`). Sir, token yoki haqiqiy PII commit qilinmaydi.
- **To'qilgan fakt yo'q.** Platforma fakti (narx, limit, API maydoni, siyosat) faqat rasmiy manbadan tekshirilgandan keyin yoziladi va `source` URL + sana bilan beriladi. Tekshirib bo'lmasa, `source_status: unverified` qo'yiladi. Benchmark raqamlari o'ylab topilmaydi.
- **Bilim yo'qolmaydi.** Konsolidatsiyada eski skill, agent yoki buyruq matni o'chirilmaydi, yangi joydagi `references/` ga ko'chiriladi.
- Foydalanuvchiga ko'rinadigan matn standart bo'yicha o'zbekcha (lotin), UZ/RU/EN qo'llab-quvvatlanadi. Kod identifikatorlari inglizcha.
- Barcha raqamlar `manifests/catalog.json` dan sinxronlanadi (`tools/catalog.py sync-claims`). Versiya yagona manbadan olinadi (`VERSION`).

## 3. Bosqichlar va qabul mezonlari

### Bosqich 0 — Baseline
- `tools/token-budget.py` ni yarat. U model doim ko'radigan tavsiflar narxini o'lchaydi: skill, agent va model chaqira oladigan buyruqlarning `description` belgilari va taxminiy tokenlari, eng qimmat 10 ta element, `--max-tokens N` darvozasi (oshsa exit 1). Testlarini ham yoz.
- `docs/v8-baseline.md` ga yoz: testlar soni, doctor natijasi, token-budget natijasi, eng katta fayllar va `claude plugin validate .` natijasi.

### Bosqich 1 — Lean Core (P0)
- **Skill'lar: 61 → ~20.** Har biri bitta foydalanuvchi vazifasiga mos keladi. Taklif etilgan xarita (asosli sabab bilan o'zgartirish mumkin, sababini `docs/v8-decisions.md` ga yoz):
  - `tyrion` (dirijyor, yagona kirish nuqtasi)
  - `strategy` (ads-plan, launch, offers, product-marketing, positioning)
  - `audit` (ads-audit va barcha platforma skill'lari: meta, google, tiktok, youtube, linkedin, x, reddit, pinterest, snapchat, microsoft, amazon, apple, telegram, vk, yandex — har biri `references/platforms/<p>.md` bo'ladi)
  - `audience` (ads-meta-audience va targeting)
  - `creative` (ad-creative, ads-creative, ads-generate, ads-photoshoot, copywriting, copy-editing, writing-guidelines, ads-dna)
  - `video` (reels-scripting, video-editing, video-motion-graphics)
  - `tracking` (ads-attribution, ads-server-side-tracking, analytics)
  - `budget` (ads-math, ads-budget, scale)
  - `analyze` (export, ads-optimize, ads-monitor, diagnostika)
  - `competitors` (ads-competitor, ads-research, customer-research)
  - `funnel` (cro, ads-landing, web-design-guidelines, voronka)
  - `content` (content-strategy, social, marketing-ideas, longform-direct-response, marketing-psychology, prospecting, seo-audit)
  - `report`
  - `client`
  - `system` (doctor, shield, learn, sop)
  - yangi: `connect`, `pulse`, `experiments`, `lead-quality`
  - `uzbekistan-market-intel` `markets/uz/` ga ko'chadi va faqat `market=uz` bo'lganda yuklanadi.
- **Agentlar: 36 → ~12.** `platform-auditor` (bitta agent; platforma delegatsiya paketida beriladi, full audit'da parallel bir necha nusxa ishlaydi), `tracking-specialist`, `audience-architect`, `creative-strategist` (copy ham shu yerda), `video-producer`, `budget-analyst`, `data-analyst` (eksport, pulse, eksperimentlar), `strategist` (pozitsiyalash, launch, g'oyalar), `content-planner` (kontent, sotsial, SEO), `compliance-reviewer` (policy va regulatory), `research-verifier` (tadqiqot va manba tekshiruvi), `release-verifier`. `manifests/workflows.json` dagi `platform_agents` va bosqichlarni yangi agentlarga moslashtir. `.claude/agents/` ni `tools/install-hooks.py --agents-only` bilan qayta generatsiya qil.
- **Buyruqlar.** Model ko'radigan kanonik buyruqlar ≤ 12 ta bo'lsin. UZ aliaslar (`/auditoriya`, `/kreativ`, `/voronka`, `/eksport`, `/hisobot`, `/mijoz`, `/raqobatchi`, `/savol`) foydalanuvchi uchun saqlanadi, lekin model kontekstiga tushmaydi: Claude Code'ning joriy hujjatida tekshirib, `disable-model-invocation: true` (yoki hozir amaldagi ekvivalenti) bilan belgila. Agar bu imkonsiz bo'lsa, aliaslarni faqat hujjatda qoldir va qaroringni yoz.
- **Tavsif gigiyenasi.** Har `description` ≤ 300 belgi bo'lsin: nima qiladi va qachon chaqiriladi (UZ/RU/EN trigger so'zlari bilan). `SKILL.md` tanasi ≤ 500 qator, qolgani `references/` ga o'tadi.
- **Migratsiya.** `manifests/migration-v8.json` (eski nom → yangi skill/agent/reference yo'li). Router eski nomlarni alias sifatida taniydi. `MIGRATION.md` (7.x → 8.0). Har bir eski nom yangi mavjud faylga ishora qilishini tekshiradigan test.
- Router (`tools/skill-search.py`), `catalog.py`, `harness-export.py` (Cursor/Windsurf), MCP server (`tools/tyrion-mcp-server.py`) va hook'larni yangi tuzilmaga moslashtir. Router xatti-harakatini testlar bilan saqlagan holda kamida 30% qisqartirishga harakat qil.
- **Qabul:** `token-budget.py --max-tokens 3500` o'tadi. Barcha testlar yashil. `evals/scenarios.json` yangi nomlarga yangilangan va 100% o'tadi. `claude plugin validate .` o'tadi.

### Bosqich 2 — Ma'lumot qatlami va Client Brain (P0)
- `schemas/metrics.v1.json` (JSON Schema). Maydonlar: `date`, `platform`, `account_id`, `level` (campaign/adset/ad), `entity_id`, `entity_name`, `spend`, `currency`, `impressions`, `reach`, `frequency`, `clicks`, `link_clicks`, `video_3s`, `thruplay`, `conversions` (event → count), `conversion_value`, `source` (meta_mcp/meta_graph/google_mcp/csv/screenshot), `evidence_label`, `synthetic`.
- `tools/normalize.py`: `meta_mcp` (rasmiy Meta Ads MCP javoblari JSON fayl ko'rinishida), `meta_graph` (`meta-insights-sync.py` mantiqidan qayta foydalan), `google_ads` (GAQL natijalari), `tiktok_csv`, `telegram_csv`, `generic_csv` (`ad-export-analyzer.py` sarlavha normalizatsiyasidan qayta foydalan) → `metrics.v1`. Xato aniq bo'lsin (exit 2), tushunilmagan ustunlar ro'yxati qaytsin. Rasmiy javob formatini developers.facebook.com va developers.google.com dan tekshir. Normalizator noma'lum maydonlarga chidamli bo'lsin.
- **"MCP → snapshot → kod" naqshi** (dirijyor skill'iga va `rules/` ga yoz): model MCP o'qish asboblarini chaqiradi, xom javobni `clients/<slug>/data/raw/<YYYY-MM-DD>-<source>.json` ga saqlaydi, `normalize.py`, keyin tahlil asboblarini ishga tushiradi. KPI'lar hech qachon "xayolda" hisoblanmaydi.
- `connect` skill + `docs/integrations.md` qayta yoziladi. Unda: manbalar ustuvorligi (rasmiy Meta Ads MCP → Google Ads MCP → token bilan Graph API → CSV/JSON eksport → screenshot); rasmiy Meta Ads MCP sozlamasi (remote URL va OAuth: manbalarda `mcp.facebook.com/ads` deyilgan, rasmiy hujjatdan tasdiqla); Google Ads MCP; sessiyada mavjud asboblarni nomi bo'yicha aniqlash. Ulangan sessiyada kuzatilgan rasmiy Meta MCP asboblari, mosligini tekshir: `ads_get_ad_accounts`, `ads_get_ad_entities`, `ads_insights_performance_trend`, `ads_insights_anomaly_signal`, `ads_insights_industry_benchmark`, `ads_insights_performance_vs_peers`, `ads_get_opportunity_score`, `ads_get_dataset_quality`, `ads_library_search`, `ads_experiment_abtest_create_test`, `ads_experiment_lift_create_test`, `ads_account_get_activity_logs`. Yozish asboblari: `ads_create_*`, `ads_update_entity`, `ads_activate_entity`, `ads_duplicate_entity`, `ads_delete_*`, `ads_creative_*`.
- **Spend-Guard'ni haqiqiy darvozaga aylantir.** `hooks/hooks.json` ga `PreToolUse` matcher qo'sh, u MCP yozish asboblariga mos keladi (masalan `mcp__.*__ads_(create|update|activate|duplicate|delete|creative).*`; matcher sintaksisini hujjatdan tekshir). Hook `clients/<slug>/changes/<id>.json` dagi tasdiqlangan change packet'ni (`spend-guard.py packet` chiqishi, `approved_by_user: true`, entity mos, 24 soatdan yangi) tekshiradi. `strict` profilda packet bo'lmasa `deny`, `standard` profilda `ask` qaytaradi. Hook chiqish formatini (permissionDecision) joriy hujjatdan tekshir. Packet'da rollback rejasi majburiy, chunki rasmiy Meta MCP'da undo yo'q. Testlarini yoz.
- **Client Brain.** `schemas/client-state.v1.json` va `tools/client-workspace.py` v2: `init`, `state get|set|validate`, `baseline` (`metrics.v1` dan oxirgi 28 kun bo'yicha CPA, CTR, CVR, CPM, frequency medianalari), `decision add|list`. Mavjud BRIEF/AUDIENCE-MAP fayllari saqlanadi. Barcha workflow'lar boshida state'ni o'qiydi, oxirida yangilaydi.
- Yangi dalil yorlig'i `PLATFORM_BENCHMARK`: faqat rasmiy benchmark asbobidan (masalan `ads_insights_industry_benchmark`) olinadi. `rules/00-manba.md` ni yangila.
- Mavjud tahlil asboblari (`ad-export-analyzer`, breakdown-effect, `creative-matrix fatigue|iterate`, `calculator`) `--metrics <metrics.v1 fayl>` qabul qiladi.
- **Qabul:** har adapter uchun fixture testlari bor. Sxema validatsiyasi testlangan. Hook testlari `deny`/`ask`/`allow` holatlarini qamraydi.

### Bosqich 3 — Pulse va Experiment Ledger (P1)
- `tools/pulse.py run --client <slug> [--metrics f]` quyidagilarni tekshiradi:
  - pacing (sarf rejaga nisbatan ±%);
  - CPA/ROAS drifti bazaviy qiymatga nisbatan (minimal konversiya soni sharti va oddiy statistik test bilan, kichik namunada "ma'lumot yetarli emas" deydi);
  - frequency o'sishi va CTR pasayishi (charchoq);
  - **tracking uzilishi** (sarf bor, konversiya keskin tushgan yoki click→event nisbati buzilgan);
  - sarf sakrashi, learning-limited va rad etilgan reklamalar (ma'lumot bo'lsa).
- Pulse chiqishi JSON va Markdown: `severity`, dalil, tavsiya etilgan keyingi qadam, `needs_approval`. **Hech narsani o'zi bajarmaydi.** Chegaralar `state.json → pulse_config` da saqlanadi. Standart qiymatlar `HEURISTIC_PRIOR_MODEL` deb yorliqlanadi. Rasmiy `ads_insights_anomaly_signal` mavjud bo'lsa, uning natijasini qo'shimcha dalil sifatida qo'sh.
- `pulse` skill + `/pulse` buyrug'i. Rejalashtirish hujjati: Claude Code scheduled tasks yoki `/loop`, cron, Windows Task Scheduler, CSV bilan GitHub Actions.
- `tools/experiments.py`:
  - `design`: bazaviy ko'rsatkich, MDE, alpha va power'dan namuna hajmini hisoblaydi; `calculator.py` orqali byudjet va kunlarni chiqaradi.
  - `register`: testni `clients/<slug>/ledger.jsonl` ga yozadi.
  - `readout`: ikki proporsiya z-testi va stdlib `random.betavariate` bilan Bayesian "yutish ehtimoli"ni hisoblaydi; hukm `WIN | LOSS | INCONCLUSIVE`, namuna hajmi haqida halol ogohlantirish bilan.
  - `promote`: takrorlangan yoki ishonchli natijani `tools/instincts.py add` ga uzatadi.
  - Meta native A/B va lift test uchun change packet tayyorlaydi (avto-yaratmaydi).
- **Qabul:** sintetik fixture'larda har pulse tekshiruvi kamida bitta "topadi" va bitta "topmaydi" testiga ega. Experiment hisoblari ma'lum qiymatlar bilan testlangan.

### Bosqich 4 — Lead Quality Loop va Creative Intelligence 2.0 (P1)
- `tools/crm-bridge.py`:
  - Kirish: AmoCRM va Bitrix24 eksport/API JSON, Google Sheets CSV, generic CSV.
  - `stage_map` konfiguratsiyasi bosqichlarni hodisalarga moslaydi: Lead → QualifiedLead → Appointment/Shown → Purchase, qiymat bilan.
  - Meta CAPI batch payload yasaydi: SHA-256 normalizatsiya (`capi-utm-builder.py` dan qayta foydalan, +998 telefon formatini ham qo'llab), `event_id`/`lead_id` bo'yicha dedup, consent darvozasi. `action_source` va CRM lead hodisalari maydonlarini rasmiy hujjatdan tekshir.
  - Standart rejim `dry-run`. `send` faqat `--confirm` va env'dagi token bilan ishlaydi. PII hech qachon log qilinmaydi.
  - Hisobot: lead→qualified konversiyasi campaign, adset, ad va forma bo'yicha. Bu natija pulse va creative-analytics'ga beriladi.
- `lead-quality` skill: conversion-leads optimizatsiyasi, Higher Intent forma, saralash savollari, Telegram bot orqali kvalifikatsiya, AmoCRM pipeline namunasi, UZ amaliyoti.
- `tools/creative-analytics.py`:
  - Kirish: `metrics.v1` va `creatives.json` (`ad_id` → teglar: angle, hook_type, format, persona, offer, awareness, visual_first_3s, language). Ad nomlash konvensiyasidan (`ANGLE_HOOK_FORMAT_PERSONA_vN`) teglarni avtomatik taklif qiladi.
  - Metrikalar: hook rate = 3s view / impressions, hold rate = ThruPlay / 3s view, CTR, CPA, ROAS. Ta'riflar hisobotda ochiq yoziladi.
  - Teg bo'yicha agregatsiya minimal namuna sharti va Wilson ishonch oralig'i bilan. Chiqish: "g'olib DNK", "o'chirish ro'yxati", keyingi 3 brief va faol kreativlar to'plamining Andromeda xilma-xillik balli.
- `tools/adlib-mine.py`: raqobatchi reklamalarining JSON/CSV'idan (rasmiy `ads_library_search` natijasi yoki qo'lda eksport) quyidagilarni chiqaradi: faollik kunlari, variantlar soni, kalit so'z bo'yicha angle klasterlari, offer naqshlari va qarshi-angle brieflar. Faollik muddati natijaning isboti emas, faqat proksi; hisobotda shunday yorliqlanadi.
- `creative/references/production-pipeline.md`: brief → skript → shot list → assetlar. Sessiyada rasm, video yoki ovoz konnektori bo'lsa, qoralama yaratish yo'li yoziladi; bo'lmasa, topshirish spetsifikatsiyasi beriladi. Qattiq bog'liqlik yo'q.
- **Qabul:** CAPI payload'lari golden fixture'larga mos keladi, hash'lar to'g'ri, dedup ishlaydi. Creative-analytics minimal namuna qoidasini buzmaydi.

### Bosqich 5 — Bilimni yangilash va Audit v2 (P2)
- Rasmiy manbalardan tekshirib yangila yoki qo'sh. Har faktga manba va sana yoki `unverified` qo'yiladi:
  - **ChatGPT Ads**: yangi platforma reference, audit checklist, tracking (CAPI/pixel), router triggerlari ("chatgpt ads", "openai reklama", "реклама в chatgpt"). Manbalarda: self-serve beta 2026-05-05, CPC va CPM, kengayish bor.
  - **Telegram Ads 2026**: Gram kabineti, 2026-08-28 CPM o'zgarishlari (manbalar zid, `ads.telegram.org` dan tasdiqla), formatlar.
  - Rasmiy Meta Ads MCP va Google Ads MCP.
  - Meta Advantage+ ning 2026 holati.
- Tegishli wiki qaydlarida `updated` va `source_status` ni yangila.
- **Audit balli v2** (`tools/audit_scoring.py`): har tekshiruv `id`, `status` (pass/warn/fail/unknown/n_a), `evidence_label` va `severity` ga ega. Natija ikki raqam: **health** (faqat baholangan tekshiruvlar bo'yicha) va **evidence coverage %**. Platforma audit reference'lari tekshiruv ID'lari bilan ishlaydi.

### Bosqich 6 — Mijozga tayyor natija va onboarding (P2)
- `tools/report-html.py`: client state, metrics, ledger va pulse'dan bitta mustaqil HTML yasaydi (inline CSS/SVG grafiklar, CDN yo'q, light/dark, print CSS, `locales/` orqali UZ/RU/EN). Bo'limlar: maqsadga nisbatan KPI plitkalari, trend, kanal kesimi, eksperimentlar, kreativ reytingi, ogohlantirishlar va egasi hamda metrikasi bor keyingi qadamlar. Markdown versiyasi ham bo'ladi.
- `/start` wizard qayta yoziladi. Ketma-ketlik:
  1. harness va konnektorlarni aniqlaydi;
  2. ko'pi bilan 5 ta savol beradi (biznes, offer va narx, marja yoki target CPA, byudjet, asosiy kanal);
  3. `client-workspace init`;
  4. birinchi tezkor natija: CSV, screenshot, MCP yoki demo'dan audit;
  5. HTML hisobot.
- Demo rejim `examples/demo-brand` va sintetik metrics fixture'ni ishlatadi.
- README qayta yoziladi: qiymat birinchi o'rinda; bir qatorli o'rnatish `/plugin install tyrion --marketplace salohiddinayydigital-sudo/ai-ads`; 3 ta namunaviy so'rov; konnektor sozlash. `README.uz.md` sinxron bo'ladi.

### Bosqich 7 — Sifat isboti va reliz (P2)
- `claude plugin eval --help` dan case formatini aniqla. `evals/` da kamida **25 golden case** yarat:
  - Tillar: ≥12 UZ lotin, ≥6 RU, ≥5 EN, ≥2 UZ kirill.
  - Mavzular: Meta strategiya, CSV fixture'dan diagnostika, lid sifati, Reels skript, auditoriya, byudjet matematikasi, pulse ogohlantirishini tushuntirish, eksperiment natijasi, raqobatchi tahlili, hisobot, out-of-scope, mutatsiya so'rovi (tasdiqsiz bajarmasligi shart).
- Grader rubrikasi:
  - dalil yorliqlari bor;
  - to'qilgan raqam, benchmark yoki testimonial yo'q;
  - matematika asbob chiqishiga mos;
  - til to'g'ri;
  - keyingi qadamlarda egasi va metrikasi ko'rsatilgan;
  - ijro hisoboti halol.
- Eval'ni plaginsiz baseline bilan solishtirib ishga tushir. Natijani `docs/v8-eval-results.md` ga yoz. Muhitda LLM eval'ni ishga tushirib bo'lmasa, suite'ni ishga tayyor qoldir, buyruqni hujjatlashtir va natija to'qima.
- Deterministik `skill-eval` ham yangilanadi. Har yangi asbob uchun testlar yoziladi (jami ≥ 480 test). `tests/coverage_gate.py` minimumi 75% ga ko'tariladi. Yangi asboblar `.github/workflows/tyrion-ci.yml` ga qo'shiladi.
- Doctor bilim grafi ogohlantirishini bersa, tuzat: grafni yangila yoki LLM kaliti talab qiladigan qismni ixtiyoriy qil, shunda doctor 0 ogohlantirish beradi.
- `VERSION` → `8.0.0`, `catalog.py sync-claims`, `CHANGELOG.md`, `MIGRATION.md`. `AGENTS.md`, `CLAUDE.md`, `INDEX.md` va manifest tavsiflari qisqa, haqiqatga mos va reklama ohangisiz yangilanadi.
- Oxirida `release-verifier` agenti (yoki toza kontekstda o'zing) butun diff'ni qabul mezonlari bo'yicha tekshiradi.

## 4. Yakuniy qabul (hammasi bajarilishi shart)

- `token-budget.py --max-tokens 3500` o'tadi (v7.1 da ~10.4K token edi).
- Barcha testlar yashil, jami ≥ 480 ta, coverage ≥ 75%. `doctor` 0 xato va 0 ogohlantirish beradi. `claude plugin validate .` o'tadi.
- `metrics.v1` ni o'qiydigan tahlil asboblari: normalize, pulse, experiments, creative-analytics, crm-bridge hisoboti, report-html va moslashtirilgan eski asboblar.
- MCP yozish asboblari hook bilan himoyalangan (testlangan).
- `examples/demo-brand` bilan `/start demo` oqimi boshidan oxirigacha ishlaydi va HTML hisobot chiqaradi (qo'lda tekshir, buyruqlar va natijani progress fayliga yoz).
- `MIGRATION.md` va `manifests/migration-v8.json` to'liq. Har eski nom testlangan.
- Golden eval suite tayyor, natijasi yoki ishga tushirish buyrug'i hujjatlangan.

## 5. So'rash mumkin bo'lgan holatlar (faqat shular)

- Ishni davom ettirish uchun haqiqiy credential yoki jonli hisobga kirish zarur bo'lsa. Bunday holatda o'sha qismni fixture bilan tugatib, keyinga qoldir va so'ra.
- Qaytarib bo'lmaydigan, foydalanuvchi ma'lumotini o'chiradigan amal kerak bo'lsa.
- Rasmiy hujjat va bu prompt bir-biriga zid bo'lsa va xato tanlov foydalanuvchiga zarar keltirsa.

Qolgan barcha holatda o'zing hal qil, qarorni yoz va davom et.

## 6. Yakuniy hisobot (o'zbekcha, qisqa)

1. Nima qilindi: bosqichlar bo'yicha 1–3 qatordan.
2. KPI jadvali: v7.1 va v8.0 (tokenlar, inventar, testlar, coverage, doctor, eval natijasi).
3. Tekshirilmagan qolgan narsalar va nega.
4. Foydalanuvchi bajarishi kerak bo'lgan qadamlar: rasmiy Meta MCP'ni ulash, CRM eksportini berish, eval'ni ishga tushirish.
5. Commitlar ro'yxati va branch nomi.
