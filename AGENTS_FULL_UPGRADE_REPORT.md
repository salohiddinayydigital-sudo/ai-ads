# Agentlarni to'liq yangilash hisoboti — reliz 8.1.0 → 8.3.0 (Tyrion Charter v2 + Targetolog Copilot Pack)

**Branch:** `feat/agents-v8.3-full-upgrade` (`main` @ `1b1e848` dan yaratilgan, avval toza ish daraxti tekshirilgan)
**Qamrov:** A bosqich = `agents-upgrade-plan.md` (12 core agent uchun Charter v2) · B bosqich = `targetolog-agents-plan.md` (7 ta Targetolog Assistant agenti, 7 ta buyruq, 6 ta DAG workflow)

## 1. Commitlar

| # | Commit | Xabar | Versiya |
|---|---|---|---|
| 1 | `f4ab728` | `feat(agents): upgrade 12 core agents to Charter v2` | 8.2.0 |
| 2 | shu hisobotni qo'shgan commit (branch HEAD; `git log -1 feat/agents-v8.3-full-upgrade`) | `feat(agents): add 7 targetolog assistant agents, commands, and workflows` | 8.3.0 |

Commit o'z hash'ini o'z ichiga ola olmaydi, shu sabab 2-commit o'rniga ko'ra aniqlanadi: u branch HEAD va bu faylni qo'shgan yagona commit.

## 2. Tekshiruvlar: boshlang'ich holat, 1-commitdan keyin va yakuniy holat

| Tekshiruv | Boshlang'ich (`main`, 8.1.0) | 1-commitdan keyin (8.2.0) | Yakuniy (8.3.0) |
|---|---|---|---|
| `python3 tools/doctor.py` | exit 0 · 18 ok · 1 ogohlantirish (eskirgan bilim grafi) · 0 xato | exit 0 · 18 ok · 1 ogohlantirish (commit qilinmagan fayllar) · 0 xato | exit 0 · 18 ok · 1 ogohlantirish (commitdan oldin commit qilinmagan fayllar) · 0 xato |
| `python3 tools/tyrion_workflows.py check` | 16 workflow · 0 xato · 0 ogohlantirish | 16 · 0 · 0 | **22** · 0 · 0 |
| `python3 -m pytest -q` | 574 o'tdi · 1 o'tkazib yuborildi | 590 o'tdi · 1 o'tkazib yuborildi | **603 o'tdi · 1 o'tkazib yuborildi** (650 subtest) |
| `python3 tools/catalog.py check` | OK (351 element) | OK (352) | OK (374) |
| `python3 tools/skill-search.py check` | 19 skill · 12 agent · 30 ulanish | 19 · 12 · 30 | 19 · **19** · **37** ulanish, reyestr butun |
| skill-eval (doctor orqali) | 51/51 | 51/51 | 51/51 |
| TyrionShield (doctor orqali) | 6/6 toza | 6/6 | 6/6 |

Yangi test to'plamlari: `tests/test_agents_charter_v2.py` (16 ta test) va `tests/test_targetolog_agents.py` (13 ta test).

## 3. Barcha 19 ta kanonik agent

`main` = `main` dagi qatorlar soni (— = yangi). Darvoza: `>=85` = rubrika bali, `P/F` = Pass/Fail cheklist. Qaysi biri bo'lmasin, o'tmagan darvoza agent natija qaytarishidan oldin bitta ichki qayta yozishni majburlaydi.

| # | Agent | Guruh | Qatorlar (main → hozir) | maxTurns | Darvoza | Handoff paketi |
|---|---|---|---|---|---|---|
| 1 | `strategist` | Core | 85 → 107 | 28 | >=85 | `strategic_brief` |
| 2 | `platform-auditor` | Core | 152 → 181 | 28 | P/F | `audit_findings_packet` |
| 3 | `creative-strategist` | Core | 107 → 126 | 28 | >=85 | `strategic_brief` → video |
| 4 | `video-producer` | Core | 104 → 107 | 24 | >=85 | ssenariy → creative/content |
| 5 | `budget-analyst` | Core | 63 → 81 | 24 | P/F | `budget_guard_packet` |
| 6 | `audience-architect` | Core | 66 → 91 | 24 | P/F | auditoriya arxitekturasi |
| 7 | `data-analyst` | Core | 52 → 75 | 24 | P/F | `analytics_readout_packet` |
| 8 | `tracking-specialist` | Core | 77 → 104 | 24 | P/F | `tracking_spec_packet` |
| 9 | `content-planner` | Core | 95 → 111 | 24 | >=85 | kalendar → video |
| 10 | `compliance-reviewer` | Core | 68 → 89 | 18 | P/F | `compliance_clearance_packet` |
| 11 | `research-verifier` | Core | 67 → 92 | 18 | P/F | `verified_research_packet` |
| 12 | `release-verifier` | Core | 66 → 91 | 18 | P/F | reliz xulosasi |
| 13 | `client-onboarder` | Targetolog | — → 92 | 20 | >=85 | `client_onboarding_packet` |
| 14 | `ad-spy-analyst` | Targetolog | — → 97 | 20 | P/F | `ad_spy_packet` |
| 15 | `campaign-launcher` | Targetolog | — → 101 | 24 | P/F | `launch_blueprint_packet` |
| 16 | `daily-optimizer` | Targetolog | — → 101 | 24 | P/F | `daily_triage_packet` |
| 17 | `funnel-cro-doctor` | Targetolog | — → 93 | 24 | >=85 | `cro_fix_packet` |
| 18 | `account-recovery-specialist` | Targetolog | — → 98 | 18 | P/F | `recovery_action_packet` |
| 19 | `client-comms-lead` | Targetolog | — → 90 | 18 | >=85 | `client_comms_packet` |

**Token / qatorlar ta'siri (12 core charter):** jami taxminan 1 000 → 1 255 qator (+25%). Agent sikli va tartibining ~30 qatorlik nusxasi har bir charterdan olib tashlandi: endi u `rules/70-charter-baseline.md` §2 da bir marta turadi. Bo'shagan joy va o'sish domen mazmuniga ketdi: rejimlar, qaror tartibi, anti-patternlar, rubrika va handoff. Har bir charter matni 140 qatordan oshmaydi (test bilan majburlanadi). Baytlarda `platform-auditor` va `video-producer` kichraydi (9.3 KB → 8.4 KB, 7.7 KB → 6.9 KB). Qolganlari 0–1.6 KB ga o'sdi.

## 4. Marshrutlash test matritsasi (`tools/skill-search.py` `route_task`)

| So'rov (til) | Aniqlangan `primary_agent` | Workflow |
|---|---|---|
| yangi mijoz brif (uz) | `client-onboarder` | `new_client_onboarding` |
| бриф нового клиента онбординг (ru) | `client-onboarder` | `new_client_onboarding` |
| client onboarding checklist for a new client (en) | `client-onboarder` | `new_client_onboarding` |
| raqobatchi ad library tahlil (uz) | `ad-spy-analyst` | `competitor_ad_spy` |
| реклама конкурентов библиотека рекламы (ru) | `ad-spy-analyst` | `competitor_ad_spy` |
| spy competitor ads teardown (en) | `ad-spy-analyst` | `competitor_ad_spy` |
| kampaniya cbo abo launch reja (uz) | `campaign-launcher` | `campaign_build_to_launch` |
| структура кампании cbo или abo (ru) | `campaign-launcher` | `campaign_build_to_launch` |
| campaign structure blueprint naming convention (en) | `campaign-launcher` | `campaign_build_to_launch` |
| ertalabki optimizatsiya kill scale (uz) | `daily-optimizer` | `morning_media_buyer_triage` |
| утренняя оптимизация почему вырос cpl (ru) | `daily-optimizer` | `morning_media_buyer_triage` |
| morning triage kill hold iterate scale (en) | `daily-optimizer` | `morning_media_buyer_triage` |
| direct skript lid sifati (uz) | `funnel-cro-doctor` | `lead_quality_and_dm_fix` |
| скрипт для директа заявки есть продаж нет (ru) | `funnel-cro-doctor` | `lead_quality_and_dm_fix` |
| dm qualification script lead form (en) | `funnel-cro-doctor` | `lead_quality_and_dm_fix` |
| reklama rejected apellyatsiya (uz) | `account-recovery-specialist` | `account_restriction_recovery` |
| аккаунт заблокирован апелляция (ru) | `account-recovery-specialist` | `account_restriction_recovery` |
| ad account restricted request review (en) | `account-recovery-specialist` | `account_restriction_recovery` |
| mijozga telegram hisobot (uz) | `client-comms-lead` | — (skill reytingi) |
| отчет клиенту в телеграм (ru) | `client-comms-lead` | — |
| client objection reply why no sales (en) | `client-comms-lead` | — |
| offer tuzish lead magnet g'oya | `strategist` | — |
| полная маркетинговая стратегия | `strategist` | `marketing_plan_full` |
| meta ads audit qilib ber · google ads pmax search terms | `platform-auditor` | — |
| kreativ charchoq hook rate past · продающий текст для рекламы | `creative-strategist` | `creative_improve` / — |
| reels skript yozib ber | `video-producer` | `video_script` |
| break-even roas hisobla | `budget-analyst` | `budget_math` |
| detailed targeting lookalike overlap | `audience-architect` | `audience_design` |
| capi tekshir pixel sozla | `tracking-specialist` | `tracking_setup` |
| контент-план на месяц | `content-planner` | — |
| special ad category policy violation | `compliance-reviewer` | — |
| raqobatchilarni o'rganish bozor tahlili | `research-verifier` | `competitor_research` |

**To'qnashuv auditi:**
- Hech bir trigger ibora 19 ta agentdan ikkitasida umumiy emas (katta-kichik harfga sezgir emas; test bilan majburlanadi).
- 232 ta core-agent triggeri `main` da va yana shu branch'da marshrutlandi. 228 tasi avvalgidek bir xil agentga yo'naldi. Qolgan 4 tasi (`reklama bloklandi`, `ad rejected`, `модерация отклонила`, `блокировка рекламы`) ataylab `compliance-reviewer` dan `account-recovery-specialist` ga ko'chirildi.
- Yangi agentlarning 105 ta triggeridan birortasi boshqa agentga yo'naltirilmaydi; 75/105 tasi o'z agentiga yo'naladi. Qolgan 30 tasi 2 so'zli parchalar bo'lib, mavjud scope darvozasi ularni agent tanlanishidan oldin `out_of_scope` yoki `needs_clarification` bilan to'xtatadi. Core-agent triggerlariga `main` da ham xuddi shunday munosabat qilinadi.

## 5. Fayllar

**A bosqich (1-commit)**
- Yaratildi: `schemas/agent-handoff.schema.json`, `skills/{strategy,creative,budget,analyze,content}/references/quality-rubric.md`, `skills/analyze/references/data-analyst-playbook.md`, `tests/test_agents_charter_v2.py`.
- Qayta yozildi: barcha 12 ta `agents/*.md` va ularning `.claude/agents/` mirrorlari; `rules/70-charter-baseline.md` (`.cursor/rules/tyrion-70-charter-baseline.mdc` va `.windsurfrules` ga qayta eksport qilingan).
- Yangilandi: `AGENTS.md` §3, `CHANGELOG.md`, `tools/catalog.py` (2 ta yangi claim naqshi `rules/70` dagi agentlar sonini sinxron saqlaydi, shuning uchun eskirgan "36" qaytib kela olmaydi), `manifests/catalog.json`.
- Versiya 8.1.0 → 8.2.0 repozitoriyning `VERSION` + `catalog.py sync-claims` mexanizmi orqali ko'tarildi (manifest va hujjatlardagi versiya satrlari).

**B bosqich (2-commit)**
- Yaratildi:
  - `agents/{client-onboarder,ad-spy-analyst,campaign-launcher,daily-optimizer,funnel-cro-doctor,account-recovery-specialist,client-comms-lead}.md` va ularning mirrorlari
  - `commands/{onboard,ad-spy,launch-plan,morning-triage,cro-dm,appeal,client-update}.md` va ularning mirrorlari
  - `skills/*/references/` ostidagi 6 ta playbook
  - `tests/test_targetolog_agents.py`
  - shu hisobot
- Yangilandi:
  - `manifests/workflows.json`: 6 ta yangi workflow; `client_report` endi Telegram, e'tiroz va upsell xabarlari uchun `none_of` guard'ga ega.
  - `schemas/agent-handoff.schema.json`: 14 ta paket.
  - `skills/{client,competitors,strategy,pulse,funnel,system}/SKILL.md`: bog'lanishlar endi ikki tomonlama, yangi triggerlar qo'shildi.
  - `tools/skill-search.py`: scope darvozasi endi targetolog atamalarini taniydi.
  - `agents/compliance-reviewer.md`: endi faqat pre-flight.
  - Core charterlardagi handoff qatorlari endi yangi agentlarga ishora qiladi.
  - `AGENTS.md` §3.1 and §3a, `CLAUDE.md`, `README*.md`, `INDEX.md`, `rules/README.md`, `commands/shield.md`.
  - Sonlar tekshiruvi 12 → 19 agent va 35 → 42 buyruqqa yangilandi: `tests/test_agent_charters.py`, `tests/test_audit_v5.py` and `tests/test_vault_audit.py`.
  - `CHANGELOG.md`, versiya 8.2.0 → 8.3.0 ga ko'tarildi.

## 6. Rioya qilingan himoya chegaralari

- Faqat Python stdlib; hech qanday bog'liqlik qo'shilmadi.
- **Spend-Guard:**
  - `campaign-launcher` va `daily-optimizer` da yozish asboblari yo'q va ular jonli kampaniyalarni hech qachon yaratmaydi yoki o'zgartirmaydi.
  - +20% dan yuqori har qanday o'zgarish, har qanday pauza va har qanday launch `tyrion_spend_guard` qoralamasi va foydalanuvchi tasdig'ini talab qiladi.
  - Ikkala agentning output kontraktida `spend_guard_required` bor (test bilan tekshiriladi).
- **White-hat:** `account-recovery-specialist` quyidagilarni taqiqlaydi:
  - cloaking
  - soxta hujjatlar
  - fermadagi, o'g'irlangan yoki ijaraga olingan akkauntlar
  - policy'ni aylanib o'tish

  Bu to'rt joyda majburlanadi:
  - uning vakolat chegarasi
  - uning anti-patternlari
  - muhim Self-Audit bandi
  - sxema doimiysi `white_hat_only: true`

  U `rules/40-xavfsizlik-va-hisob.md` ga bog'langan va barchasini test tekshiradi.
- Quyidagilar sinxron saqlanadi: `.claude/agents/`, `.claude/commands/`, `.cursor/rules/`, `.windsurfrules` va `manifests/catalog.json`. Doctor mirror driftini 0 deb xabar qiladi (42 juftlik).

## 7. Keyingi ishlar — 8.3.1 da yopildi

Beshala keyingi ish 8.3.1 da bajarildi (`CHANGELOG.md` ga qarang):

1. `data-analyst` da endi 17 ta UZ/RU/EN trigger bor. Eksperiment, statistik ahamiyat, tanlama hajmi va normallashtirish so'rovlari unga yo'naladi. Eksport natijalarini tahlil qilish ataylab `results_analysis` workflow'da qoldi.
2. `client_report` tekshirildi. Uning `release-verifier` asosiy agenti ataylab shunday: bosqich hisobotni yangi kontekstda tekshirishdir. Mijozga mo'ljallangan Telegram va e'tiroz xabarlari endi `client-comms-lead` ga yo'naladi: `client_report` guard'i 8.3.0 da, mos `weekly_review` guard'i 8.3.1 da qo'shildi. Eval regressiyalari yo'q.
3. 7 ta yangi agent va `data-analyst` uchun eval'lar qo'shildi: 8 ta `universal_route` ssenariy va 7 ta golden `claude plugin eval` case.
4. `skills/tyrion/references/workflow-recipes.md` endi barcha oltita targetolog workflow'ni hujjatlashtiradi (E–J bo'limlari).
5. `docs/v8-baseline.md` — tarixiy snapshot va ataylab o'zgartirilmagan.

Eval'larni yozish paytida topilgan ikkita marshrutlash nuqsoni ham tuzatildi: `meta_strategy` reklama rad etilishi apellyatsiyalarini egallab olardi, `weekly_review` esa Telegram mijoz xabarlarini egallab olardi.
