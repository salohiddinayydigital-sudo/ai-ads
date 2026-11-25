# Tyrion v8.3 — closed-loop media-buyer brain for paid ads (`ai-ads`)

<!-- tyrion:catalog agents=19 skills=19 wiki=101 playbooks=9 contexts=6 commands=42 rules=9 tools=40 -->

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/Python-3.10%E2%80%933.13-3776AB.svg)](https://www.python.org/)
[![OS: Windows | macOS | Linux](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-success.svg)](#install)

> 🇺🇿 **O'zbek tilidagi hujjat:** [README.uz.md](README.uz.md) · Migrating from 7.x: [MIGRATION.md](MIGRATION.md)

Tyrion pulls ad-account data through official connectors, **computes every number in code** (never "in the model's head"), watches the account daily, learns from tests, sends CRM lead quality back to Meta — and loads about **5× fewer always-on description tokens than v7.1** (≈2K vs ≈10.4K, measured by `tools/token-budget.py`). It runs in Claude Code, Codex, Cursor and Windsurf; answers in Uzbek (Latin/Cyrillic), Russian or English.

```text
connect (MCP / token / CSV) → snapshot → normalize (metrics.v1) → analyze / pulse → decide (change packet) → test → learn → CRM → CAPI
```

## Install

```bash
/plugin install tyrion --marketplace salohiddinayydigital-sudo/ai-ads
```

Requires Python 3.10–3.13 (stdlib only) and Node 18+ (hook launcher). No account needed to try it:

```bash
python3 tools/tyrion.py demo        # synthetic demo brand → pulse alerts → standalone HTML report
```

## Three requests to try

```text
"Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top"      -> lead-quality + audit + tracking
"Mana CSV eksport. Qaysi reklamani o'chirib, qaysini masshtablay?" -> analyze (code-computed Kill/Keep/Scale)
"Мне нужен недельный отчёт по рекламе в Telegram и Meta"          -> pulse + report (HTML, RU)
```

You never pick an agent or tool: the `tyrion` skill is the single conductor (`tools/skill-search.py route`, `manifests/workflows.json`). Codex/Cursor/Windsurf run it in an explicitly labelled single-conductor fallback.

## Connect your data (priority order)

1. **Official Meta Ads MCP** (OAuth) — `https://mcp.facebook.com/ads` *(verified against Meta's official docs, 2026-11-19)*.
2. **Google Ads MCP** — [googleads/google-ads-mcp](https://github.com/googleads/google-ads-mcp).
3. Graph API token (`META_ACCESS_TOKEN`) → 4. CSV/JSON export → 5. screenshot.

Details, tool names and the "MCP → snapshot → code" pattern: [docs/integrations.md](docs/integrations.md), `skills/connect/`.

## Safety

Account writes (`ads_create_*`, `ads_update_entity`, `ads_activate_entity`, …) are gated by a `PreToolUse` hook: an approved, fresh (<24 h) `change-packet.v1` with a rollback plan in `clients/<slug>/changes/` is required — `deny` in `strict`, `ask` in `standard` ([hooks/README.md](hooks/README.md) states the limits honestly). Evidence labels (`MEASURED_ACCOUNT_DATA`, `PLATFORM_BENCHMARK`, `HEURISTIC_PRIOR_MODEL`, …) mark every number.

## What's inside

- **19 specialist agents** — `platform-auditor` (platform passed in the delegation package), `tracking-specialist`, `audience-architect`, `creative-strategist`, `video-producer`, `budget-analyst`, `data-analyst`, `strategist`, `content-planner`, `compliance-reviewer`, `research-verifier`, `release-verifier`; plus the **Targetolog Copilot Pack** — `client-onboarder`, `ad-spy-analyst`, `campaign-launcher`, `daily-optimizer`, `funnel-cro-doctor`, `account-recovery-specialist` (white-hat only), `client-comms-lead`. Every charter follows Charter v2 (modes, anti-patterns, Self-Audit gate, typed handoff — `schemas/agent-handoff.schema.json`).
- **19 platform & marketing skills** — `tyrion`, `strategy`, `audit`, `audience`, `creative`, `video`, `tracking`, `budget`, `analyze`, `competitors`, `funnel`, `content`, `report`, `client`, `system`, `connect`, `pulse`, `experiments`, `lead-quality` (the Uzbekistan market pack loads only when `market=uz`).
- **42 slash commands** — 12 model-visible (`/start /audit /audience /creative /budget /export /report /client /competitors /tracking /pulse /connect`); Uzbek aliases (`/auditoriya /kreativ /voronka /eksport /hisobot /mijoz /raqobatchi /savol`) stay user-invocable but hidden from the model context. Video pre-production commands (user-invocable): `/video-ssenariy` (`/video-script`), `/video-reja` (`/video-plan`), `/motion-ssenariy` (`/motion-script`). Targetolog assistants (user-invocable): `/onboard`, `/ad-spy`, `/launch-plan`, `/morning-triage`, `/cro-dm`, `/appeal`, `/client-update`.
- **40 deterministic 0-token Python CLI tools** (stdlib only) — `normalize`, `pulse`, `experiments`, `crm-bridge`, `creative-analytics`, `adlib-mine`, `audit_scoring`, `report-html`, `calculator`, `spend-guard`, `meta-targeting-engine`, …; Bilim: atomik qaydlar (101), 9 playbooks, market packs `global us eu uk mena latam sea in uz`.

```text
ai-ads/
├── agents/                  # 19 specialist agent charters (12 core + 7 targetolog assistants) (old charters kept in skills/*/references/legacy-agents/)
├── skills/                  # 19 skills; SKILL.md + references/
├── commands/                # 42 slash commands (12 model-visible)
├── hooks/                   # ${CLAUDE_PLUGIN_ROOT} hook launcher, guard, Spend-Guard gate
├── tools/                   # 40 ta 0-Token Deterministik CLI Asbob & STDIO MCP server
├── schemas/                 # metrics.v1, client-state.v1
├── markets/                 # Market Packs (global, us, eu, uk, mena, latam, sea, in, uz)
└── wiki/                    # atomic wikilinked knowledge notes
```

## License & attribution

[MIT](LICENSE). Third-party attributions: [NOTICE](NOTICE), [THIRD_PARTY.md](THIRD_PARTY.md) ([AgriciDaniel/claude-ads](https://github.com/AgriciDaniel/claude-ads), [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)).
