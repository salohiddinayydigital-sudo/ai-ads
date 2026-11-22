---
name: AGENTS
description: "Tyrion v8.1 — kanonik agent shartnomasi: yagona qatlamlar, 12 agent va orkestratsiya tartibi (Claude Code, Cursor, Codex, Windsurf)"
tags: [router, agents, shartnoma, arxitektura, ecc]
source: "ECC (affaan-m/ECC) naqshi asosida Tyrion uchun qurildi"
updated: 2026-11-19
---

# 🧠 TYRION v8.1 — KANONIK AGENT SHARTNOMASI

> **Bir qator:** Tyrion v8.1 — pullik reklama va targetologiya uchun yopiq siklli tizim: 12 agent, 19 skill, 100+ wiki qayd, 9 playbook, 6 kontekst, 29 slash buyruq (12 tasi model ko'radi) va 40 ta 0-token deterministik Python asbobi. Raqamlar `manifests/catalog.json` dan.

<!-- tyrion:catalog agents=12 skills=19 wiki=101 playbooks=9 contexts=6 commands=35 rules=9 tools=40 -->

## 1. Boot Tartibi (Token Tejamkor)

1. **Shu fayl (`AGENTS.md`)** — qatlamlar, 12 agent, orkestratsiya va xavfsizlik chegaralari.
2. **`MEMORY.md`** — operator xotirasi (`<=90` qator: til qonuni, O'zbekiston bozori asoslari, aktiv Bet Ledger va saboqlar).
3. **Vazifaga mos Kontekst va Qoida:** `contexts/` dan 1 ta ish rejimi (`audit-mode`, `launch-mode`, `scale-mode`, `creative-mode`, `uzbekistan-market`) va `rules/` dan 1–2 qoida.
4. **Universal Skill (`tyrion`) — standart kirish nuqtasi:** oddiy marketing so'rovlari uchun yagona dirijyor. U `skill-search.py route` (va `manifests/workflows.json` — yagona marshrut manbasi) orqali agent/skill/asbob/oqimni o'zi aniqlaydi, tanlangan `SKILL.md` va charterlarni haqiqatan o'qiydi, mutaxassislarga delegatsiya qiladi (yoki ochiq `single_conductor_fallback`), natijalarni tekshiradi va bitta hujjatga sintez qiladi. `UserPromptSubmit` hooki (`prompt:route`) har marketing xabarida marshrut maslahatini beradi, `SessionStart` esa kirish nuqtasini eslatadi. Mutaxassis (sub-agent) uni qayta chaqirmaydi (`caller: specialist`).
5. **Universal Auto-Router va 0-Token Kontekst Yuklash:** Foydalanuvchi oddiy tilda topshiriq berganda (`/skill-search` yoki `/agent` yozishi shart emas!), `python3 tools/skill-search.py route "<vazifa>" --load` avtomatik ravishda `primary_agent`, `supporting_agents`, `required_skills`, `references_to_load`, `rules_to_load` va `tools_to_use` ni aniqlaydi hamda faqat kerakli charter va `SKILL.md` fayllarini yuklaydi ([[20-token-gigiyena]], [[70-charter-baseline]]).

## 2. Yagona Ildizli Qatlamlar (Single-Root Layers)

| Qatlam | Kanonik Manzil | Nima saqlanadi | Holat |
|---|---|---|---|
| **Agentlar** | `agents/` (12) | 12 ta ixtisoslashgan agent charteri (`Prompt Defense Baseline` + `skills:` ulangan) | kanonik |
| **Skilllar** | `skills/` (19) | 19 ta skill: `tyrion`, `strategy`, `audit`, `audience`, `creative`, `video`, `tracking`, `budget`, `analyze`, `competitors`, `funnel`, `content`, `report`, `client`, `system`, `connect`, `pulse`, `experiments`, `lead-quality` | kanonik |
| **Buyruqlar** | `commands/` (35) | 35 ta slash buyruq (`.claude/commands/` ga avtomatik mirror qilinadi) | kanonik |
| **Kontekstlar** | `contexts/` (6) | 5 ta ECC Dynamic Context Mode (`audit`, `launch`, `scale`, `creative`, `uzbekistan`) + `README.md` | kanonik |
| **Playbooklar** | `playbooks/` (9) | 8 ta to'liq nisha va platforma playbooki + `README.md` | kanonik |
| **Bilim (Wiki)** | `wiki/` (100) | 100 ta atomik, wikilink bilan bog'langan bilim qaydi va 16 ta SOP | kanonik |
| **Qoidalar** | `rules/` (9) | 8 ta buzilmas qoida (`00-manba` .. `70-charter-baseline`) + `README.md` | kanonik |
| **Asboblar** | `tools/` (40) | `tyrion.py`, `meta-targeting-engine.py`, `meta-audience.py`, `meta-insights-sync.py`, `ad-export-analyzer.py`, `capi-utm-builder.py`, `creative-matrix.py`, `client-workspace.py`, `calculator.py`, `spend-guard.py`, `doctor.py`, `tyrion-shield.py`, `instincts.py` | faol |
| **Xotira** | `MEMORY.md` · `manifests/instincts.json` | Operator xotirasi (`<=90` qator) va `/learn` instinktlar reestri | faol |
| **Katalog & Graf** | `manifests/catalog.json` · `graphify-out/` | Mashina o'qiydigan yagona reestr va 0-token wikilink grafi (generatsiya) | generatsiya |

## 3. Agentlar Jamoasi (12 Charter)

| Agent | Vazifa | Eski charterlar (matn saqlangan) |
|---|---|---|
| `platform-auditor` | Platforma auditi (Meta, Google, TikTok, YouTube, LinkedIn, X, Reddit, Pinterest, Snapchat, Microsoft, Amazon, Apple, Telegram, VK, Yandex, ChatGPT Ads); platforma delegatsiya paketida beriladi, full audit'da parallel nusxalar | `audit-<platforma>` (13) |
| `tracking-specialist` | Pixel/CAPI, atributsiya, CRM→CAPI lid sifati | `audit-tracking`, `tracking-specialist` |
| `audience-architect` | Meta auditoriya arxitekturasi, 6-statusli interest tekshiruvi | `meta-audience-architect` |
| `creative-strategist` | Angle, hook, matn (UZ/RU/EN), kreativ audit, format | `audit-creative`, `copy-writer`, `visual-designer`, `format-adapter` |
| `video-producer` | Video pre-production (sotuvchi/organik video ssenariy, video kontent reja, motion storyboard; Self-Audit >= 85/100) va alohida montaj spetsifikatsiyasi | `reels-scriptwriter`, `video-editor` |
| `budget-analyst` | Break-even, MER, pacing, scale qarori | `audit-budget` |
| `data-analyst` | Eksport, `metrics.v1`, pulse, eksperiment natijasi, hisobot | (yangi) |
| `strategist` | Pozitsiyalash, launch, offer, g'oyalar | `positioning-strategist`, `launch-planner`, `campaign-ideator` |
| `content-planner` | Kontent, sotsial, SEO | `content-planner`, `social-content-writer`, `seo-auditor` |
| `compliance-reviewer` | Platforma policy va regulyator tekshiruvi | `audit-policy-compliance`, `audit-regulatory-compliance` |
| `research-verifier` | Tadqiqot va manba tekshiruvi | `research-worker`, `source-verifier` |
| `release-verifier` | Toza kontekstda qabul/reliz tekshiruvi, skill sifati | `release-verifier`, `skill-reviewer` |

Eski nomlar router tomonidan alias sifatida taniladi (`manifests/migration-v8.json`, [[MIGRATION.md]]).

## 3a. Workflow qatlami va Universal Conductor

`manifests/workflows.json` (validatsiya: `python3 tools/tyrion_workflows.py check`) — cross-agent oqimlar: `meta_strategy`, `competitor_strategy`, `marketing_plan_full`, `campaign_diagnosis`, `results_analysis`, `creative_improve`, `video_script`, `video_edit`, `competitor_research`, `audience_design`, `budget_math`, `tracking_setup`, `campaign_launch`, `full_audit`, `weekly_review`, `client_report`. Har oqim DAG: bosqichlar `needs` bilan bog'langan, bog'liq bo'lmaganlari parallel (`parallel_levels`), ixtiyoriy bosqichlar `optional_when` bilan o'tkazib yuboriladi, bitta bosqich = bitta agent = bitta output (dublikat ish yo'q). Router faqat birinchi 2 mutaxassis charteri va primary skilllarni yuklaydi, qolgan bosqich skilllari `stage_skills_deferred` ga tushadi va bosqich boshlanganda o'qiladi. Progressive rejimda kesilgan skill `truncated` deb belgilanadi va `applied_skills_verified` ga kirmaydi: dirijyor uni `Read` bilan to'liq o'qigandan keyingina "qo'llandi" deydi. Yagona oqimga tushmagan oddiy (1 mutaxassis) vazifalar eski skill reytingi bilan marshrutlanadi.

## 4. Kanonik 6-Bosqichli Avtonom Marshrutlash va Orkestratsiya Oqimi

Barcha muhitlarda (Claude Code, Codex, Cursor, Windsurf, CLI/MCP) bitta kanonik oqim amal qiladi:

1. **Tabiiy tilda qabul qilish:** Foydalanuvchi oddiy tilda vazifa beradi (`uz_latin`, `uz_cyrillic`, `ru`, `en`). Mavjud 35 ta slash buyruq (`/audit`, `/auditoriya`, `/kreativ`, `/budget`, `/hisobot` va b.) universal routerga raqobatchi emas, balki tezkor yorliqlar (shortcuts) sifatida ishlaydi.
2. **Avtomatik tanlash (`route_task`):** `primary_agent`, `supporting_agents` (faqat haqiqatan mustaqil ko'p bosqichli vazifalarda), `required_skills`, `supporting_skills`, `rules_to_load` va `references_to_load` avtomatik aniqlanadi.
3. **To'liq ko'rsatmalarni yuklash (`full` vs `manifest`):** Standart `full` rejimda tanlangan agent charterlari, `SKILL.md`, qoidalar va reference fayllarning **to'liq matni** (`compiled_context_package`) kontekst byudjeti (`max_context_bytes=180,000`) nazorati ostida yuklanadi. To'liq o'qilmagan skill hech qachon "qo'llanildi" deb ko'rsatilmaydi.
4. **Amaliy ijro (`execute_task`) va Multi-Harness halolligi:**
   - **Claude Code:** `.claude/commands/`, `.claude/settings.json` hooklari, `.mcp.json` va native `Task` sub-agent dispatch'ni qo'llaydi.
     - **Sub-agent sifatida chaqirish:** `agents/*.md` kanonik (plugin rejimi, MCP nomi `mcp__plugin_tyrion_tyrion-core__*`); `.claude/agents/` shundan `python3 tools/install-hooks.py --agents-only` bilan **generatsiya** qilinadi (loyiha rejimi nomi `mcp__tyrion-core__*`, qo'lda tahrirlanmaydi). Claude Code sub-agentlarni sessiya boshida yuklaydi: yangi fayllar uchun sessiyani qayta ishga tushiring yoki `/agents` dan foydalaning. Har charter `Agent sikli`ga bo'ysunadi: `completed` | `needs_input` (`missing_inputs`) | `blocked_mutation_approval`, va `execution_evidence` (haqiqatda chaqirilgan asbob/o'qilgan fayl).
   - **Codex / Cursor / Windsurf / Standalone CLI:** `.codex-plugin/plugin.json`, `.cursor/rules/*.mdc` yoki `.windsurfrules` hamda `.mcp.json` (`tyrion_universal_router`) orqali **`single_conductor_fallback`** rejimida ishlaydi (`subagents_actually_spawned: False` ochiq ko'rsatiladi, Conductor to'liq yuklangan ko'rsatmalar va deterministik CLI asboblar yordamida vazifani o'zi bajaradi).
5. **Dinamik qayta marshrutlash (`reroute_task` / `--reroute-with`):** Ish davomida yangi domen ehtiyoji (masalan, kreativdan keyin CAPI tekshiruvi yoki CRO) paydo bo'lsa, yangi agent va skill to'liq matni bilan dinamik ulanadi.
6. **Tekshirish va yakunlash:** Worker va deterministik asboblar natijalari Conductor tomonidan yig'iladi, ziddiyatlar tekshiriladi va [[50-topshirish-dod]] bo'yicha yakunlanadi.

## 5. Qoidalar (`rules/`)

| Qoida | Qachon yuklanadi |
|---|---|
| [[00-manba]] | Har tahlil, audit, benchmark va hisobot oldidan |
| [[10-til-va-uslub]] | Har javob va reklama matni yozishdan oldin |
| [[20-token-gigiyena]] | Uzoq sessiya va katta vazifalarda |
| [[30-ozbekiston-konteksti]] | O'zbekiston bozori, mijoz voronkasi va kreativda |
| [[40-xavfsizlik-va-hisob]] | Hisob o'zgarishi, Spend-Guard, Pixel/CAPI va mijoz faylida |
| [[50-topshirish-dod]] | Ish yakunida (Definition of Done tekshiruvi) |
| [[60-loyiha-papkasi]] | Yangi mijoz loyihasi (`clients/<slug>/`) ochilganda |
| [[70-charter-baseline]] | Sub-agent (worker) chaqirilganda (Prompt Defense + Zero-Findings) |
