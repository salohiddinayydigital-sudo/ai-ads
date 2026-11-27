# O'zgarishlar jurnali (Changelog)

**Tyrion (`ai-ads`)** dagi barcha muhim o'zgarishlar shu faylda [Semantic Versioning](https://semver.org/) bo'yicha hujjatlashtirilgan.


## [8.3.1] — 2026-11-25

Ishlatishga tayyorlik: v8.3 hisobotidagi barcha follow-up'lar yopildi.

### Qo'shildi
- Golden eval'lar (`claude plugin eval`): `onboard-uz-1`, `ad-spy-ru-1`, `launch-plan-en-1`, `morning-triage-uz-1`, `cro-dm-ru-1`, `appeal-cyrl-1`, `client-update-uz-1` (32 → 39 case).
- `evals/scenarios.json`: 8 ta `universal_route` ssenariy (7 targetolog agent + `data-analyst`), 51 → 59, 100% pass.
- `skills/tyrion/references/workflow-recipes.md`: E–J bo'limlari — 6 ta targetolog oqimining domen qoidalari.

### O'zgardi
- `data-analyst`: 17 ta UZ/RU/EN trigger (eksperiment natijasi, statistik ahamiyat, tanlama hajmi, metrics.v1); eksport tahlili ataylab `results_analysis` oqimida qoldi.
- Marshrut tuzatishlari: `meta_strategy` endi rad etilish/apellyatsiya so'rovlarini, `weekly_review` esa Telegram/e'tiroz xabarlarini egallamaydi ("Meta reklama rejected bo'ldi, apellyatsiya matnini tayyorla" → `account-recovery-specialist`; "Mijozga telegram hisobot ... bu hafta" → `client-comms-lead`). 232+105 trigger regressiya tekshiruvida boshqa o'zgarish yo'q.
- `README.md` / `README.uz.md`: 7 targetolog agent va buyruqlari ro'yxatda.

## [8.3.0] — 2026-11-25

Targetolog Copilot Pack: yadro 12 agentni takrorlamasdan amaliyotchi targetologning kunlik operatsion ishlarini yopadigan 7 yordamchi agent (jami 19 kanonik agent: 12 core + 7 targetolog).

### Qo'shildi
- Agentlar (Charter v2): `client-onboarder`, `ad-spy-analyst`, `campaign-launcher`, `daily-optimizer`, `funnel-cro-doctor`, `account-recovery-specialist` (faqat white-hat), `client-comms-lead` + `.claude/agents/` mirror.
- Buyruqlar (`disable-model-invocation`): `/onboard`, `/ad-spy`, `/launch-plan`, `/morning-triage`, `/cro-dm`, `/appeal`, `/client-update` (commands 35 → 42).
- Workflow'lar (`manifests/workflows.json`, 16 → 22): `new_client_onboarding`, `campaign_build_to_launch`, `morning_media_buyer_triage`, `lead_quality_and_dm_fix`, `competitor_ad_spy`, `account_restriction_recovery`.
- Playbooklar: `skills/strategy/references/client-onboarding-framework.md`, `skills/competitors/references/ad-library-spy-playbook.md`, `skills/budget/references/daily-triage-kill-scale.md`, `skills/funnel/references/direct-dm-and-leadform-cro.md`, `skills/audit/references/account-recovery-whitehat.md`, `skills/report/references/client-comms-playbooks.md`.
- `schemas/agent-handoff.schema.json`: +7 paket (`client_onboarding_packet`, `ad_spy_packet`, `launch_blueprint_packet`, `daily_triage_packet`, `cro_fix_packet`, `recovery_action_packet` (`white_hat_only: true`), `client_comms_packet`).
- `tests/test_targetolog_agents.py` — 7 agent, 7 buyruq, 6 DAG, 21 so'rovli UZ/RU/EN routing matritsasi, trigger to'qnashuvi, white-hat va Spend-Guard chegaralari.

### O'zgardi
- `compliance-reviewer` — pre-flight policy/regulyator; reaktiv "reklama bloklandi / ad rejected / модерация отклонила / блокировка рекламы" triggerlari `account-recovery-specialist` ga ko'chirildi (to'qnashuv yo'q).
- Skill ulanishlari (ikki tomonlama): `client`, `competitors`, `strategy`, `pulse`, `funnel`, `system`; yangi targetolog triggerlari `client`, `competitors`, `pulse`, `funnel`, `system` skilllarida.
- Router: scope-darvoza lug'atiga targetolog atamalari (`cpl`, `akkaunt`, `apellyatsiya`, `brif`, `onboarding`, `direct`, `triage`, `optimizatsiya`); `client_report` Telegram/e'tiroz xabarlarini `client-comms-lead` ga qoldiradi.
- Yadro charterlar handoff'lari yangi agentlarga ulandi; `AGENTS.md` §3.1 va §3a, `CLAUDE.md`, `rules/70-charter-baseline.md` (19 agent) yangilandi.

## [8.2.0] — 2026-11-25

Charter v2: barcha 12 kanonik agent "yupqa qobiq"dan rejimli, o'zini ballaydigan va typed handoff'li mutaxassislarga ko'tarildi.

### Qo'shildi
- `schemas/agent-handoff.schema.json` — `tyrion.agent_handoff/v1` konverti va 7 typed paket (`strategic_brief`, `audit_findings_packet`, `analytics_readout_packet`, `budget_guard_packet`, `tracking_spec_packet`, `compliance_clearance_packet`, `verified_research_packet`).
- Sifat rubrikalari: `skills/{strategy,creative,budget,analyze,content}/references/quality-rubric.md`; `skills/analyze/references/data-analyst-playbook.md` (metrics.v1 validatsiya, tanlama hajmi, atributsiya oynasi, anomaliya triage).
- `tests/test_agents_charter_v2.py` — 6 majburiy blok, rolga xos output_contract, buzilgan yo'llar, maxTurns tabaqalari, "36 agent" drifti, schema va routing regressiyasi.

### O'zgardi
- `agents/*.md` (12) + `.claude/agents/` mirror: `## Rejimlar`, `## Qaror tartibi`, `## Anti-Patternlar va Qat'iy Taqiqlar`, rolga xos `## Output contract`, `## Self-Audit Sifat Darvozasi` (>= 85/100 yoki Pass/Fail, 1 majburiy qayta yozish), `## Handoff Kontrakti`; takroriy boilerplate `rules/70-charter-baseline.md` ga ko'chirildi.
- `maxTurns` yuklama bo'yicha tabaqalandi: 28 (strategist, platform-auditor, creative-strategist) · 24 (6 agent) · 18 (compliance/research/release-verifier).
- `rules/70-charter-baseline.md`: "36 agent" drifti tuzatildi (son `catalog.py sync-claims` bilan avtomatik), umumiy Agent sikli va Charter v2 standarti qo'shildi; `.cursor/rules` va `.windsurfrules` qayta eksport qilindi.
- `AGENTS.md` §3: rejimlar, darvozalar, maxTurns va handoff paketlari jadvali.

## [8.1.0] — 2026-11-22

Video pre-production tizimi (4 ustun): sotuvchi video, organik/ekspert video, video kontent reja + syomka kuni, motion video blueprint. Montaj/render qatlami (`video-editing.md`, `tools/video-run.py`) o'zgarmagan.

### Qo'shildi
- `skills/video/SKILL.md` — 4 ustunli Intent Router (Sales / Organic / Plan / Motion + alohida Post-Production); yangi referencelar: `sales-video-scripting.md`, `organic-video-content.md`, `video-content-planning.md`, `motion-video-scripting.md`, `script-quality-rubric.md` (100 ball, o'tish 85).
- `tools/creative-matrix.py video-script --mode sales|organic|plan|motion --lang uz|ru|en --duration 15|30|45|60 --hooks 3..5` (stdlib-only; rejimsiz eski chaqiruv o'zgarmagan).
- Buyruqlar: `/video-ssenariy`, `/video-reja`, `/motion-ssenariy` + EN aliaslar `/video-script`, `/video-plan`, `/motion-script` (commands 29 → 35).
- `templates/`: `sales-video-script.md`, `organic-video-script.md`, `video-content-plan.md`, `motion-video-blueprint.md`; `schemas/`: `video-script-schema.json`, `motion-blueprint-schema.json`.
- Evals: `sales-video-uz-1`, `organic-video-uz-1`, `video-plan-uz-1`, `motion-script-uz-1` + 4 ta `skill_route` stsenariy; `tests/test_video_scripting.py`.

### O'zgardi
- `agents/video-producer.md` (+ `.claude/` mirror): rejimlar, majburiy AV-jadval, Self-Audit >= 85/100, handoff; `content-planner` va `creative-strategist` ga video handoff.
- Takrorlanish olib tashlandi: safe-zone/3-Capture yagona manbasi `sales-video-scripting.md` §8; `video-ad-scripts-and-specs.md` va `short-form-video.md` qisqartirilib havolaga o'tkazildi; `reels-scripting.md` orqaga moslik bilan saqlandi.
- `wiki/video-kreativ-tizimi.md`, `wiki/video-skript-shablonlari.md` yangi tizimga moslandi.

## [8.0.1] — 2026-11-19

Birinchi haqiqiy `claude plugin eval` run'idan keyingi tuzatishlar.

### Tuzatildi
- Eval graderlari: JS regex'da yaroqsiz `(?i)` (38 ta), `max: 0` li `tool_used` graderlarda `min: 0` yo'q edi; case'lar `Read` va `Bash` oladi.
- Marshrutlash: route hooki, Cursor kirish qoidasi va dirijyor matni o'chirilgan `tyrion-universal` nomiga ishora qilardi; endi `tyrion`.
- Windows: `crm-bridge` va boshqa yangi asboblarning `--help` chiqishi cp1252 konsolida yiqilardi (UTF-8 stdout); CI smoke qadami bash'da ishlaydi.

### Hujjat
- `docs/v8-eval-results.md`: o'lchangan natija — 5/28 case ≥ 0.8, o'rtacha ball 0.558, plaginsiz baseline'dan farq +0.183 (`--runs 1`, bitta run). Suite o'tmaydi; `tool-run` graderlari sandbox'siz mashinada baholanmaydi.

## [8.0.0] — 2026-11-19

Yopiq siklli media-buyer miyasi. 7.x dan o'tish: [MIGRATION.md](MIGRATION.md).

### Qo'shildi
- **Lean Core:** skill 61 → 19, agent 36 → 12, model ko'radigan buyruq 12 (UZ aliaslar `disable-model-invocation`). Doimiy description narxi ≈10.4K → ≈2.0K token (`tools/token-budget.py`, CI darvozasi 3500). Eski matnlar `references/` va `legacy-agents/` ga ko'chirildi; `manifests/migration-v8.json` + router alias.
- **Ma'lumot qatlami:** `schemas/metrics.v1.json`, `tools/normalize.py` (meta_mcp, meta_graph, google_ads, tiktok_csv, telegram_csv, generic_csv), "MCP → snapshot → kod" naqshi, `connect` skilli va `docs/integrations.md`, dalil yorlig'i `PLATFORM_BENCHMARK`.
- **Spend-Guard hook:** MCP yozish asboblari uchun `PreToolUse` darvozasi (`tools/spend_gate.py`): tasdiqlangan, yangi, rollback'li `change-packet.v1`; `strict` — deny, `standard` — ask.
- **Client Brain:** `schemas/client-state.v1.json`, `client-workspace.py` v2 (`state`, `baseline`, `decision`).
- **Pulse va eksperimentlar:** `tools/pulse.py`, `tools/experiments.py` (design/register/readout/promote/packet), `ledger.jsonl`.
- **Lid sifati va kreativ:** `tools/crm-bridge.py` (AmoCRM/Bitrix24/CSV → Meta CAPI, dry-run), `tools/creative-analytics.py`, `tools/adlib-mine.py`, `lead-quality` skilli, `production-pipeline.md`.
- **Audit v2:** `tools/audit_scoring.py` (health + evidence coverage), ChatGPT Ads reference (CG01–CG09), Telegram 2026 / rasmiy MCP / Advantage+ qaydlari (`url_cited` yoki `unverified`).
- **Hisobot va onboarding:** `tools/report-html.py`, `tyrion.py demo`, `/start` wizard, README qayta yozildi.
- **Sifat:** 29 golden eval case (`evals/`), `docs/v8-eval-results.md` (LLM eval bu muhitda ishga tushirilmagan), coverage darvozasi 75%.

### O'zgardi
- Eski ad-export/creative-matrix/calculator asboblari `--metrics` / `--from-metrics` qabul qiladi.
- Workflow'lar yangi agentlarga moslandi; `uzbekistan-market-intel` `markets/uz/` ga ko'chdi (faqat `market=uz`).

### Ma'lum cheklovlar
- Spend-Guard hook fayl belgisiga tayanadi (`approved_by_user` ni model ham yozishi mumkin) va Bash/curl orqali to'g'ridan-to'g'ri API chaqirig'ini ushlamaydi.
- Rasmiy Meta/Google/OpenAI/Telegram sahifalari bu muhitdan ochilmadi: bog'liq faktlar `unverified`/`url_cited`.
- Router (`skill-search.py`) hajmi qisqartirilmadi (docs/v8-decisions.md D5).

## [Unreleased] — Plagin tayyorligi tuzatishlari

### Tuzatildi
- Uchala plagin manifestidagi `agents: "./agents/"` maydoni `claude plugin validate` ni yiqitardi ("must end with .md"), shu sabab agentlar o'rnatishda yuklanmasdi; maydon olib tashlandi (`agents/` papkasi avtomatik topiladi). Haqiqiy `claude --plugin-dir` sessiyasida tekshirildi: plagin yuklandi, `tyrion-core` MCP ulandi, 36 ta `tyrion:*` agent va `tyrion:tyrion-universal` ro'yxatdan o'tdi.
- `prompt:route` maslahati tavsiyaviy edi va model dirijyorsiz javob berardi; endi u aniq majburiy birinchi qadam. Haqiqiy sessiyada tekshirildi: `Skill` asbobi `tyrion-universal` ni chaqirdi, router va `creative-matrix.py` ishladi, nisha playbooki o'qildi.
- Cursor va Windsurf eksportlarida faqat qoidalar bor edi; endi ularda generatsiya qilingan kirish qoidasi bor (`tyrion-00-entry.mdc`, `.windsurfrules` tepasida: `tyrion_universal_router` orqali marshrutlash, da'vodan oldin o'qish, yagona dirijyor zaxirasi). Generatsiya qilingan fayllar commit qilingan, eskirsa test yiqiladi.

### Qo'shildi
- `.claude-plugin/icon.png` (plagin katalogi ikonkasi talabi).

## [Unreleased-2] — Universal dirijyor, Meta strategiyasi va kreativ razvedka
- **Nol-ishqalanishli video reklama ssenariylari (`tools/creative-matrix.py video-script`, `skills/reels-scripting/SKILL.md`):** 7 ta S/A darajali formatda (`ugc_reaction_demo`, `founder_authority`, `no_yapping_split_screen`, `imessage_reveal`, `chatgpt_reveal`, `greenscreen_proof`, `faceless_motion_explainer`) syomkaga tayyor 9:16 ssenariylar yaratadi: 3 ta ochilish hook varianti, vaqt kodli storyboard va `720x1200` xavfsiz zona overlaylari — majburiy tashqi API kalitlarsiz (`APIFY_API_TOKEN` olib tashlandi) va dasturlashsiz.
- **Andromeda Entity-ID va Persona-Desire-Awareness (PDA) dvigateli (`tools/creative-matrix.py pda-matrix`):** Persona x Desire x Schwartzning 5 ta xabardorlik bosqichi bo'yicha 6–9 ta vizual jihatdan farqli konsept quradi, shunda Meta Andromeda'ning computer-vision klasterlashi har biriga mustaqil retrieval chiptasi beradi.
- **Platformada tasdiqlangan reklama matni va AI-belgi linteri (`tools/creative-matrix.py ad-copy`):** Meta (`125/40/30`), Google RSA (`30/90`), TikTok (`80/100`), LinkedIn (`150/70/100`) va Telegram (`160`) uchun belgilar soni hisoblangan matn yaratadi va AI belgilarini (*"It's not X, it's Y"*, *"Stop scrolling"*, em-dash) avtomatik olib tashlaydi.
- **Meta 2026 besh tizimli AI stek va amaliyotchi targetolog playbooki (`tools/meta-targeting-engine.py`, `tools/meta-audience.py`, `skills/ads/references/meta-ai-stack.md`):** `GEM` (Teacher Foundation Model), `Andromeda` (Retrieval + Entity ID), `Lattice` (Unified Ranking + Sequence Learning), `UTIS` (User True Interest Survey Calibrator), `Adaptive Ranking Model` (`<100ms`), `Value Rules` (`+200%` dan `-90%` gacha bid multiplikatorlari), `GUIDED_CREATION` ASC API (`v25.0+`), Meta AI Chat Signal bo'yicha mintaqaviy GDPR istisnolari va Ads Manager'ni dasturlashsiz sozlash bo'yicha 9 bo'limli amaliyotchi qo'llanma qo'shildi.
- **Umumiy mahsulot marketing konteksti shabloni (`templates/product-marketing.md`):** `.claude/product-marketing.md` va `.agents/product-marketing.md` bilan mos.

## [6.0.0] — 2026-10-21 (Buzuvchi o'zgarish: global arxitektura va kross-platforma relizi)

### Buzuvchi o'zgarishlar
- **Standart bozor paketi (`default_market`):** `plugin.json` dagi standart bozor `"uz"` dan `"global"` ga o'zgartirildi. `rules/30-ozbekiston-konteksti.md` va `uzbekistan-market-intel` endi **faqat** `market=uz` yoqilgan yoki aniqlangan bo'lsa yuklanadi.
- **Kanonik inglizcha slash buyruqlar:** Kanonik inglizcha buyruqlar (`/audience`, `/creative`, `/funnel`, `/export`, `/report`, `/client`, `/competitors`, `/ask`) qo'shildi, barcha o'zbekcha buyruqlar (`/auditoriya`, `/kreativ`, `/voronka`, `/eksport`, `/hisobot`, `/mijoz`, `/raqobatchi`, `/savol`) alias sifatida saqlandi.
- **Kanonik hook konfiguratsiyasi:** Hooklar `${CLAUDE_PLUGIN_ROOT}` va `hooks/run-hook.cjs` ishlatadigan `hooks/hooks.json` ga birlashtirildi; takroriy ildiz `hooks.json` va `.claude/settings.json` olib tashlandi.

### Qo'shildi
- **Kross-platforma Node hook va MCP ishga tushirgichi (`hooks/run-hook.cjs`):** `${CLAUDE_PLUGIN_ROOT}` ni avtomatik aniqlaydi, Windows, macOS va Linux'da `python3` -> `python` -> `py -3` ni topadi, `ingest` va `dod` ni `TYRION_DEV=1` (yoki plagin ildizi) ortida yopadi, `Stop` timeout'ini 5 soniya bilan cheklaydi va `TYRION_HOOK_PROFILE=strict` bo'lmasa xatoda ochiq qoladi (`exit 0`).
- **9 ta mintaqaviy bozor paketi (`markets/`):** `global`, `uz`, `us`, `eu`, `uk`, `mena`, `latam`, `sea` va `in` paketlari valyutalar, BNPL provayderlari (`Klarna`, `Afterpay`, `Affirm`, `Tabby`, `Tamara`, `Pix`, `Atome`, `Simpl`, `Uzum Nasiya`), mavsumiylik kalendarlari, maxfiylik qoidalari va manbalari ko'rsatilgan `benchmarks.md` bilan qo'shildi.
- **3 ta UI/CLI lokali (`locales/`):** `en`, `uz` va `ru` xabar to'plamlari hamda bozorga bog'liq bo'lmagan `core/` qoidalari va playbooklari qo'shildi.
- **ISO 4217 ko'p valyuta va nol-o'nlik qo'llab-quvvatlash:** CLI asboblarida `--currency` (`EUR`, `GBP`, `BRL`, `INR`, `JPY`, `KRW`, `UZS`, `USD`) va eski `_usd` maydonlari yonida neytral valyuta kalitlari qo'shildi.
- **Global maxfiylik va CAPI rozilik darvozasi (`tools/capi-utm-builder.py`):** `--consent-granted` / `--no-consent` PII darvozasi, Google Consent Mode v2 signallari, Meta Limited Data Use (`data_processing_options=['LDU']`) va GDPR/CCPA/LGPD/DPDP tekshiruvlari qo'shildi.
- **6 ta mintaqaviy platforma audit skilli:** `markets/*/skills/` ostida Yandex Direct, VK Ads, LINE Ads, Naver/Kakao, Baidu/Douyin/WeChat va Taboola/Outbrain audit skilllari qo'shildi.
- **Bosqichma-bosqich ochuvchi router (`<= 15 KB` byudjet):** Standart `progressive` kontekst rejimi bir qadamli so'rov kontekstini 15 KB dan past ushlaydi.
- **Yuqori oqimdagi MIT atribusiyalari:** `LICENSE`, `NOTICE` va `THIRD_PARTY.md` ga `AgriciDaniel/claude-ads` va `affaan-m/everything-claude-code` e'lonlari qo'shildi.

---

# O'zgarishlar jurnali

**Tyrion** dagi barcha muhim o'zgarishlar shu faylda hujjatlashtirilgan.

## [5.0.0] - 2026-10-20 — Kalibrlangan tavsiya dvigateli, jonli Meta Insights sinxronizatsiyasi va yagona manba pariteti

### Qo'shildi
- **Universal Auto-Router va avtonom agent orkestratori (`tools/skill-search.py`, `tools/tyrion.py route`, MCP `tyrion_universal_router`)**:
  - Qo'lda `/skill-search` yoki `/agent` tanlamasdan, o'zbek lotin, o'zbek kirill, rus va ingliz tilidagi topshiriqlarni avtomatik marshrutlash.
  - Barcha 62 skill va 36 agent metadatasi boyitildi (`triggers`, `aliases`, `domains`, `platforms`, `related_skills`, `references`, `risk_level`, `output_contract`, `authority_boundary`).
  - Sessiya keshli diskdan yuklash (`SessionContextCache`), vazifa o'rtasida dinamik qayta marshrutlash (`--reroute-with`), universal dirijyor zaxirasi va Spend-Guard o'zgartirish darvozasi.
- **Detailed Targeting sahifalash, payload va kesh mustahkamlash (`tools/meta-targeting-engine.py`, `tools/catalog.py`)**:
  - So'rov bo'yicha `pages_fetched`, `is_truncated` va `results_count` diagnostikasi; kesilganlik haqida aniq ogohlantirish; `MALFORMED_ITEM_PAYLOAD` ni haqiqiy `NOT_FOUND` dan ajratish; kontekst izolyatsiyalangan kesh kalitlari (`special_ad_category`, `country`, `objective`, `language`, `locale`, `ad_account_id`, `api_version`, `api_base_url`); `catalog.py` da CRLF'ga chidamli SHA-256.
- **Detailed Targeting aniqlik dvigateli (`tools/meta-targeting-engine.py`, `docs/DETAILED-TARGETING-ACCURACY.md` va MCP `tyrion_meta_detailed_targeting`)**:
  - Gallyutsinatsiyasiz 6 statusli tekshiruv tizimi (`VERIFIED_AVAILABLE`, `FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED`, `RELATED_UNVERIFIED`, `NOT_FOUND`, `API_UNAVAILABLE`).
  - Meta Marketing API v26.0 ning ko'p endpointli integratsiyasi (`/search?type=adinterest`, `/{ad-account-id}/targetingsearch`, `/{ad-account-id}/targetingsuggestions`, `/{ad-account-id}/targetingvalidation`): `paging.next` sahifalash, `(id, type)` bo'yicha dublikatlarni olib tashlash, ko'p tilli so'rov kengaytirish (`uz_latin`, `uz_cyrillic`, `ru`, `en`) va TTL kesh tekshiruvi.
- **Jonli Meta Ads Insights ulagichi (`tools/meta-insights-sync.py` va MCP `tyrion_meta_live_insights`)**: [Meta Graph API v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) (`/act_<id>/insights`) dan jonli kampaniya, ad set va reklama telemetriyasini oladi yoki xom Graph API JSON eksportlarini (`actions`, `action_values`) tekshiradi, konversiya/daromadni normallashtiradi va `ad-export-analyzer.py` ga uzatadi.
- **Ishonch intervallari va model shaffofligi (`tools/meta-audience.py`)**:
  - `saturation` endi `--active-reach-ratio` va `--measured-freq-7d` ni qabul qiladi, `estimated_fatigue_window_days` (`conservative_early_fatigue_day`, `baseline_fatigue_day`, `optimistic_late_fatigue_day`) chiqaradi va `model_disclosure` ni (`HEURISTIC_PRIOR_MODEL` va `MEASURED_ACCOUNT_DATA`) o'z ichiga oladi.
  - `architect` endi `target_cpa` ni unit-iqtisodiyotdan (`--aov`, `--margin-pct`, `--lead-to-sale-cvr`) yoki foydalanuvchi maqsadlaridan chiqaradi va zaxira baholarni `evidence_and_assumptions` ichida `PROVISIONAL_HEURISTIC_FALLBACK` deb belgilaydi.
  - `lookalike` endi `heuristic_seed_readiness_score_100` ni aniq ogohlantirish bilan beradi (`is_meta_internal_score: False`).
- **Python AST va o'lik kod skaneri (`tools/tyrion-shield.py`)**: Barcha Python modullarida sintaksis xatosi va yetib bo'lmaydigan operatorlar yo'qligini tekshiradigan 6-tekshiruv qo'shildi, `tests/` `SKIP_DIRS` dan chiqarildi va `scope_and_limitations` ogohlantirishi qo'shildi.

### Tuzatildi va o'zgardi
- **`tools/meta-audience.py` dagi 3 ta aniq xato tuzatildi**:
  1. `query_live_graph_api` dagi `return` dan keyingi 16 qator yetib bo'lmaydigan kod olib tashlandi.
  2. `retargeting` ga `--no-telegram-bot` / `--has-telegram-bot false` CLI flaglari qo'shildi.
  3. Manba trafigi `0` bo'lganda `calc_retargeting` dagi sun'iy `100/500/1000/200` minimal pool pollari olib tashlandi (endi `0` pool o'lchami va `INSUFFICIENT_RETARGETING_POOL` qaytaradi).
- **Auditoriya overlap chegarasi 20% ga yagonalashtirildi**: `calc_overlap` ogohlantirish chegarasi `20.0%` ga standartlashtirildi (`<20%` = `HEALTHY_ISOLATION`, `20%–29.9%` = `MODERATE_OVERLAP`, `>=30%` = `CRITICAL_COLLISION`), barcha hujjatlarga mos keltirildi va `STATIC_AUDIENCE_POOL_INTERSECTION` bilan jonli auksion yetkazib berish overlapi o'rtasidagi aniq farq qo'shildi.
- **Standart Meta Graph API versiyasi `v26.0` ga ko'tarildi**: `.env.example`, `tools/meta-audience.py`, `tools/capi-utm-builder.py` va `tools/meta-insights-sync.py` standart `v26.0` ni ishlatadigan va `META_GRAPH_API_VERSION` ni dinamik o'rnatadigan qilib yangilandi.
- **Versiya va inventar pariteti — yagona manba (`v5.0.0`)**: Barcha versiya satrlari (`v5.0.0`) va inventar sonlari (`36` agent, `62` skill, `100` wiki qayd, `18` buyruq, `9` playbook, `6` kontekst, `29` asbob) barcha manifest, hujjat va skriptlarda sinxronlandi.

## [4.0.0] - 2026-10-18 — Yagona ildizli ECC arxitekturasini to'liq qayta qurish

### Qo'shildi
- **Yagona Master CLI (`tools/tyrion.py`)**: `status`, `doctor`, `shield`, `audience`, `creative`, `client`, `calc`, `guard`, `search`, `skills`, `instincts`, `catalog`, `graph` va `audit` bo'yicha yagona kirish nuqtasi.
- **Meta Ads Audience Studio (`tools/meta-audience.py`)**: `architect`, `interests`, `overlap` va `saturation` yoniga deterministik `retargeting`, `lookalike` va `diagnose` dvigatellari qo'shildi.
- **Andromeda 2 Creative Matrix va Hook Studio (`tools/creative-matrix.py`)**: Deterministik 3x3 Angle x Format matritsa quruvchi (`matrix`), 3 tilli Hook generatori (`hooks`) va kreativ charchoq radari (`fatigue`).
- **Mijoz ish maydoni yaratuvchisi (`tools/client-workspace.py` va `/mijoz`)**: Bir buyruqli mijoz ish maydoni generatori.
