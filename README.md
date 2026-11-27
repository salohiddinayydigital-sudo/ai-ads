# Tyrion v8.3 — pullik reklama uchun yopiq siklli media-buyer miyasi (`ai-ads`)

<!-- tyrion:catalog agents=19 skills=19 wiki=101 playbooks=9 contexts=6 commands=42 rules=9 tools=40 -->

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/Python-3.10%E2%80%933.13-3776AB.svg)](https://www.python.org/)
[![OS: Windows | macOS | Linux](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-success.svg)](#o-rnatish)

> 🇺🇿 **Qisqa o'zbekcha tanishuv:** [README.uz.md](README.uz.md) · 7.x dan o'tish: [MIGRATION.md](MIGRATION.md)

Tyrion reklama hisobi ma'lumotlarini rasmiy konnektorlar orqali oladi, **har bir raqamni kod bilan hisoblaydi** (hech qachon "modelning xayolida" emas), hisobni har kuni kuzatadi, testlardan o'rganadi va CRM'dagi lid sifatini Meta'ga qaytaradi. Doimiy yuklanadigan tavsif tokenlari v7.1 ga nisbatan taxminan **5 baravar kam** (≈2K va ≈10.4K, `tools/token-budget.py` bilan o'lchangan). Claude Code, Codex, Cursor va Windsurf'da ishlaydi; o'zbek (lotin/kirill), rus yoki ingliz tilida javob beradi.

```text
ulash (MCP / token / CSV) → snapshot → normalize (metrics.v1) → tahlil / pulse → qaror (change packet) → test → saboq → CRM → CAPI
```

## O'rnatish

```bash
/plugin install tyrion --marketplace salohiddinayydigital-sudo/ai-ads
```

Python 3.10–3.13 (faqat stdlib) va Node 18+ (hook ishga tushirgichi) kerak. Sinab ko'rish uchun hisob shart emas:

```bash
python3 tools/tyrion.py demo        # sintetik demo brend → pulse ogohlantirishlari → mustaqil HTML hisobot
```

## Sinab ko'rish uchun uchta so'rov

```text
"Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top"      -> lead-quality + audit + tracking
"Mana CSV eksport. Qaysi reklamani o'chirib, qaysini masshtablay?" -> analyze (kod bilan hisoblangan Kill/Keep/Scale)
"Мне нужен недельный отчёт по рекламе в Telegram и Meta"          -> pulse + report (HTML, RU)
```

Agent yoki asbobni siz tanlamaysiz: `tyrion` skilli yagona dirijyor (`tools/skill-search.py route`, `manifests/workflows.json`). Codex/Cursor/Windsurf'da u aniq belgilangan yagona dirijyor zaxira rejimida ishlaydi.

## Ma'lumotlarni ulash (ustuvorlik tartibida)

1. **Rasmiy Meta Ads MCP** (OAuth) — `https://mcp.facebook.com/ads` *(Meta rasmiy hujjatidan tasdiqlangan, 2026-11-19)*.
2. **Google Ads MCP** — [googleads/google-ads-mcp](https://github.com/googleads/google-ads-mcp).
3. Graph API token (`META_ACCESS_TOKEN`) → 4. CSV/JSON eksport → 5. skrinshot.

Batafsil, asbob nomlari va "MCP → snapshot → kod" naqshi: [docs/integrations.md](docs/integrations.md), `skills/connect/`.

## Xavfsizlik

Hisobga yozish asboblari (`ads_create_*`, `ads_update_entity`, `ads_activate_entity`, …) `PreToolUse` hook bilan himoyalangan: `clients/<slug>/changes/` da tasdiqlangan, yangi (<24 soat) va rollback rejali `change-packet.v1` talab qilinadi — `strict` rejimida `deny`, `standard` rejimida `ask` ([hooks/README.md](hooks/README.md) chegaralarni ochiq aytadi). Dalil yorliqlari (`MEASURED_ACCOUNT_DATA`, `PLATFORM_BENCHMARK`, `HEURISTIC_PRIOR_MODEL`, …) har bir raqamni belgilaydi.

## Tarkib

- **19 ta ixtisoslashgan agent** — `platform-auditor` (platforma delegatsiya paketida beriladi), `tracking-specialist`, `audience-architect`, `creative-strategist`, `video-producer`, `budget-analyst`, `data-analyst`, `strategist`, `content-planner`, `compliance-reviewer`, `research-verifier`, `release-verifier`; shuningdek **Targetolog Copilot Pack** — `client-onboarder`, `ad-spy-analyst`, `campaign-launcher`, `daily-optimizer`, `funnel-cro-doctor`, `account-recovery-specialist` (faqat white-hat), `client-comms-lead`. Har bir charter Charter v2 ga amal qiladi (rejimlar, anti-patternlar, Self-Audit darvozasi, tipli handoff — `schemas/agent-handoff.schema.json`).
- **19 ta platforma va marketing skilli** — `tyrion`, `strategy`, `audit`, `audience`, `creative`, `video`, `tracking`, `budget`, `analyze`, `competitors`, `funnel`, `content`, `report`, `client`, `system`, `connect`, `pulse`, `experiments`, `lead-quality` (O'zbekiston bozori paketi faqat `market=uz` bo'lganda yuklanadi).
- **42 ta slash buyruq** — 12 tasi modelga ko'rinadi (`/start /audit /audience /creative /budget /export /report /client /competitors /tracking /pulse /connect`); o'zbekcha aliaslar (`/auditoriya /kreativ /voronka /eksport /hisobot /mijoz /raqobatchi /savol`) foydalanuvchi chaqira oladi, lekin model kontekstidan yashirilgan. Video pre-production buyruqlari (foydalanuvchi uchun): `/video-ssenariy` (`/video-script`), `/video-reja` (`/video-plan`), `/motion-ssenariy` (`/motion-script`). Targetolog yordamchilari (foydalanuvchi uchun): `/onboard`, `/ad-spy`, `/launch-plan`, `/morning-triage`, `/cro-dm`, `/appeal`, `/client-update`.
- **40 ta 0-token deterministik Python CLI asbob** (faqat stdlib) — `normalize`, `pulse`, `experiments`, `crm-bridge`, `creative-analytics`, `adlib-mine`, `audit_scoring`, `report-html`, `calculator`, `spend-guard`, `meta-targeting-engine`, …; Bilim: atomik qaydlar (101), 9 playbook, bozor paketlari `global us eu uk mena latam sea in uz`.

```text
ai-ads/
├── agents/                  # 19 ta ixtisoslashgan agent charteri (12 core + 7 targetolog yordamchi) (eski charterlar skills/*/references/legacy-agents/ da saqlangan)
├── skills/                  # 19 ta skill; SKILL.md + references/
├── commands/                # 42 ta slash buyruq (12 tasi modelga ko'rinadi)
├── hooks/                   # ${CLAUDE_PLUGIN_ROOT} hook ishga tushirgichi, guard, Spend-Guard darvozasi
├── tools/                   # 40 ta 0-Token Deterministik CLI Asbob & STDIO MCP server
├── schemas/                 # metrics.v1, client-state.v1
├── markets/                 # Bozor paketlari (global, us, eu, uk, mena, latam, sea, in, uz)
└── wiki/                    # atomik, wikilink bilan bog'langan bilim qaydlari
```

## Litsenziya va atribusiya

[MIT](LICENSE). Uchinchi tomon atribusiyalari: [NOTICE](NOTICE), [THIRD_PARTY.md](THIRD_PARTY.md) ([AgriciDaniel/claude-ads](https://github.com/AgriciDaniel/claude-ads), [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)).
