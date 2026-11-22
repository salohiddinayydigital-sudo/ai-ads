---
name: CLAUDE
description: "Tyrion v8.1 — yopiq siklli media-buyer miyasi: skill/agent routeri, ma'lumot qatlami, Spend-Guard"
tags: [router, tyrion, ecc, v8]
source: "affaan-m/ECC arxitekturasi asosida Tyrion uchun"
updated: 2026-11-19
---

# 🧠 TYRION v8.1 — AI PAID MEDIA & TARGETOLOGY OS

> **Kanonik shartnoma:** [[AGENTS.md]] · **Operator xotirasi:** [[MEMORY.md]] · **Bilim xaritasi:** [[INDEX.md]] · **Kirish:** [[README.md]]

Tyrion v8.1 — pullik reklama va targetologiya uchun yopiq siklli tizim: rasmiy konnektorlardan ma'lumot oladi, raqamlarni kod bilan hisoblaydi (`schemas/metrics.v1.json`), hisobni kuzatadi (`pulse`), testlardan o'rganadi (`experiments`), CRM lid sifatini Meta'ga qaytaradi (`lead-quality`). Arxitektura: yagona ildiz, `affaan-m/ECC` naqshi. 7.x dan o'tish: [[MIGRATION.md]].

## 1. Yagona Ildizli Tuzilma (Single-Root Architecture)

| Qatlam / Joy | Nima saqlanadi | Qachon o'qiladi |
|---|---|---|
| `AGENTS.md` | **Kanonik agent shartnomasi** — 12 agent, orkestratsiya, tamoyillar | Sessiya boshida (boot) |
| `MEMORY.md` | **Operator xotirasi va Bet Ledger** (`<=90` qator) — til, bozor, aktiv gipotezalar, saboqlar | Sessiya boshida (boot) |
| `INDEX.md` | **Yagona Bilim Xaritasi (MOC)** — barcha `wiki/` va `playbooks/` jadvali | Bilim qidirish / yozishdan oldin |
| `agents/` | **12 ta kanonik agent charteri** (`platform-auditor` — platforma delegatsiya paketida; eski 36 charter `skills/*/references/legacy-agents/` da) | Worker ishga tushganda |
| `skills/` | **19 ta kanonik skill** (`tyrion` dirijyor, `audit`, `strategy`, `creative`, `analyze`, `connect`, `pulse`, `experiments`, `lead-quality` …; eski matnlar `references/` da) | Vazifa boshida (`skill-search.py`) |
| `commands/` | **35 ta slash buyruq** (model ko'radigan 12 ta: `/start /audit /audience /creative /budget /export /report /client /competitors /tracking /pulse /connect`; UZ aliaslar `/auditoriya /kreativ /voronka /eksport /hisobot /mijoz /raqobatchi /savol` va `/doctor /learn /shield /sop /scale /utm /ask`, hamda video pre-production `/video-ssenariy /video-reja /motion-ssenariy` (EN: `/video-script /video-plan /motion-script`) foydalanuvchi uchun, `disable-model-invocation`) | Foydalanuvchi chaqirganda |
| `contexts/` | **6 ta kontekst fayli** (5 ta ECC Dynamic Context Mode + `contexts/README.md`) | Vazifa rejimiga qarab ([[contexts/README]]) |
| `playbooks/` | **9 ta playbook fayli** (8 ta amaliy nisha/platforma playbooki + `playbooks/README.md`) | Kampaniya / nisha strategiyasida ([[playbooks/README]]) |
| `wiki/` | **101 ta atomik bilim qaydi** (Andromeda 2, Meta Audience, Google Coliseum, Telegram Ads, CJM, 16 SOP) | Faqat kerakli qayd (`brain-search.py`) |
| `rules/` | **9 ta qoida fayli** (`00-manba` .. `70-charter-baseline` + `rules/README.md`) | Vazifaga mos 1–2 qoida ([[rules/README]]) |
| `tools/` | **40 ta 0-token deterministik CLI asbob** (`tyrion.py`, `normalize.py`, `pulse.py`, `experiments.py`, `crm-bridge.py`, `creative-analytics.py`, `report-html.py`, `meta-targeting-engine.py`, `meta-audience.py`, `meta-insights-sync.py`, `ad-export-analyzer.py`, `capi-utm-builder.py`, `creative-matrix.py`, `client-workspace.py`, `calculator.py`, `spend-guard.py`, `doctor.py`, `tyrion-shield.py`, `instincts.py`) | Har tahlil, hisob va tekshiruvda ([[tools/README]]) |
| `hooks/` | **Deterministik lifecycle hooklar** (`SessionStart`, `PreToolUse` — shu jumladan MCP yozish asboblari uchun Spend-Guard darvozasi, `PostToolUse`, `Stop`) | Avtomatik ([[hooks/README]]) |
| `manifests/` | `catalog.json` (generatsiya reestri) va `instincts.json` (`/learn` xotirasi) | `tools/catalog.py` va `tools/instincts.py` |

## 2. Qat'iy Qoidalar

1. **95% Ishonch Qonuni:** Maqsad, byudjet yoki voronka noaniq bo'lsa — taxmin qilma, avval foydalanuvchidan so'ra.
2. **Universal Skill va Token Gigiyenasi:** Oddiy marketing so'rovini `tyrion` skilli bilan boshla (agent/skill/asbobni foydalanuvchi tanlamaydi). Butun omborni yoppasiga O'QIMA; har bir vazifada `python3 tools/skill-search.py execute "<vazifa>"` (yoki `route "<vazifa>" --load`) orqali faqat tanlangan charter, `SKILL.md` va reference to'liq matni (`compiled_context_package`) yuklanadi ([[token-gigiyenasi]], [[skill-router]]).
3. **Manbasiz Fakt Yo'q va Model Shaffofligi:** Har bir tavsiyada ma'lumot manbasi (`MEASURED_ACCOUNT_DATA` vs `HEURISTIC_PRIOR_MODEL`), taxminlar va ishonchlilik darajasi ochiq ko'rsatiladi ([[00-manba]]).
4. **Spend-Guard Himoyasi:** Reklama hisobiga har qanday o'zgartirish (`budget >20%`, yangi kampaniya, pauza) `tools/spend-guard.py` tekshiruvi, tasdiqlangan `change-packet.v1` (rollback bilan) va foydalanuvchi tasdig'isiz bajarilmaydi; MCP yozish asboblarini `PreToolUse` hook ushlaydi ([[40-xavfsizlik-va-hisob]], [[hooks/README]]).
6. **MCP → snapshot → kod:** MCP o'qish javobini `clients/<slug>/data/raw/` ga saqla → `tools/normalize.py` → tahlil asboblari. KPI hech qachon "xayolda" hisoblanmaydi.
5. **Atomiklik va Yagona Manba:** 1 qayd = 1 tushuncha, YAML frontmatter (`name/description/tags/source/updated`, `\` o'rniga `/`), kamida 2 ta wikilink (`[[...]]`). Barcha raqamlar `manifests/catalog.json` dan avtomatik sinxronlanadi (`python3 tools/catalog.py sync-claims`).

## 3. Asosiy CLI Asboblar (`tools/`)

| Buyruq | Vazifasi |
|---|---|
| `python3 tools/tyrion.py status` | **Yagona Master CLI** — tizim holati va barcha buyruqlar menyusi |
| `python3 tools/tyrion.py route "<vazifa>"` | **Universal Auto-Router** — oddiy tildagi topshiriqdan agent, skill, reference va workflow'ni avtomatik tanlash va yuklash |
| `python3 tools/doctor.py` | **Tizim sog'lig'i** — ko'p qatlamli tekshiruv (bilim, katalog, skill, sirlar, testlar) |
| `python3 tools/tyrion-shield.py scan` | **TyrionShield v8.1 (/shield)** — 6 qavatli statik xavfsizlik, AST va governance skaneri |
| `python3 tools/meta-targeting-engine.py search` | **Detailed Targeting Accuracy Engine (/auditoriya)** — 6-statusli rasmiy Graph API v26.0 interest qidiruv va validation dvigateli |
| `python3 tools/meta-audience.py <cmd>` | **Meta Ads Audience Studio (/auditoriya)** — `architect`, `interests`, `overlap` (<20%), `saturation`, `retargeting`, `lookalike`, `diagnose` |
| `python3 tools/meta-insights-sync.py pull` | **Live Meta Ads Insights (/eksport)** — Graph API v26.0 `/act_<id>/insights` sinxronizatsiyasi va auditi |
| `python3 tools/creative-matrix.py <cmd>` | **Andromeda 2 Creative Studio (/kreativ)** — 3x3 Angle×Format matritsa, 3 tilli Hook va charchoq tahlili |
| `python3 tools/client-workspace.py <cmd>` | **Mijoz Ish Maydoni (/mijoz)** — yangi mijoz papkasi (`BRIEF`, `AUDIENCE-MAP`, `CREATIVE-MATRIX`, `journal`) |
| `python3 tools/calculator.py <cmd>` | **Media Matematika (/budget)** — `breakeven`, `meta-155`, `google-sculpt`, `telegram-funnel`, `ladder` |
| `python3 tools/spend-guard.py <cmd>` | **Spend-Guard** — byudjet (+20%), Telegram (160 belgi), Pixel+CAPI (`event_id`) va Change Packet darvozasi |
| `python3 tools/instincts.py <cmd>` | **Uzluksiz O'rganish (/learn)** — kampaniya saboqlarini saqlash va `MEMORY.md` ga ko'tarish |
