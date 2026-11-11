# Tyrion — Global Paid-Media & Targetology Operating System (`ai-ads`)

<!-- tyrion:catalog agents=36 skills=63 wiki=100 playbooks=9 contexts=6 commands=18 rules=9 tools=29 -->

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/Python-3.10%E2%80%933.13-3776AB.svg)](https://www.python.org/)
[![OS: Windows | macOS | Linux](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-success.svg)](#1-minute-quickstart)

> 🇺🇿 **O'zbek tilidagi hujjat:** [README.uz.md](README.uz.md)

**Tyrion (`ai-ads`)** is an open-source, deterministic paid-media, performance marketing, and targetology plugin for **Claude Code**, **OpenAI Codex CLI**, **Cursor**, and **Windsurf**. It works out-of-the-box on **Windows, macOS, and Linux**, responds automatically in the **user's language**, supports **any ISO 4217 currency**, and ships with modular **Market Packs** (`global`, `us`, `eu`, `uk`, `mena`, `latam`, `sea`, `in`, `uz`).

---

## 1. 1-Minute Quickstart

### Install via Claude Code Plugin Marketplace
```bash
/plugin install tyrion --marketplace salohiddinayydigital-sudo/ai-ads
```
On Claude Code older than 2.1.275, add the marketplace first: `/plugin marketplace add salohiddinayydigital-sudo/ai-ads`, then `/plugin install tyrion`.

Settings (`/plugin configure tyrion`): **Standart bozor** (default market, `uz` out of the box), **Hook qat'iyligi** (`minimal` · `standard` · `strict`), a switch for the hooks, and an optional **Meta access token** (`ads_read`, stored in secure storage and passed only to Tyrion's own MCP server) with a default ad account. The token can also come from `META_ACCESS_TOKEN` in the environment or from a `.env` file in your project; the environment wins, then the plugin setting, then `.env`.

### Requirements & OS Compatibility
- **Python:** `3.10` – `3.13` (`python3`, `python`, or `py -3` on Windows — automatically detected by `hooks/run-hook.cjs`)
- **Node.js:** `18+` (bundled with Claude Code / Codex / Cursor)
- **Supported OS:** Windows 10/11, macOS 13+, Ubuntu/Debian/Fedora Linux
- **Works from any project (`cwd != plugin_root`):** commands, skills and agents call tools as `python3 "${CLAUDE_PLUGIN_ROOT}/tools/<tool>.py"`, which Claude Code resolves to the installed copy. Hooks and the built-in STDIO MCP server resolve their own root and fail open (`exit 0`) on non-strict environment warnings, so Tyrion never blocks file edits in your other projects.
- **State survives updates:** operator memory and instincts live in `~/.tyrion/` (override with `TYRION_HOME`); client workspaces are created in the project you are working in (`clients/<name>/`). `python3 tools/tyrion.py paths` prints the exact locations.
- **Two ways to run it:** installed as a plugin, or by opening this repository directly — `.claude/commands/` and `.mcp.json` carry the project-mode form of the same commands and server.

---

## 2. Core Architecture & Inventory

- **36 specialist agents** (`agents/*.md`) — Meta, Google, TikTok, YouTube, LinkedIn, Telegram, CAPI tracking, creative strategy, unit economics, and regulatory compliance.
- **63 platform & marketing skills** (`skills/*/SKILL.md`) + **6 regional platform skills** (`markets/*/skills/`) covering Yandex Direct, VK Ads, LINE Ads, Naver/Kakao, Baidu/Douyin/WeChat, and Taboola/Outbrain.
- **18 slash commands** (`commands/*.md`) — one command per function: `/start`, `/audit`, `/auditoriya` (audience), `/kreativ` (creative), `/voronka` (funnel), `/eksport` (export analysis), `/hisobot` (report), `/mijoz` (client workspace), `/raqobatchi` (competitors), `/savol` (ask), `/budget`, `/scale`, `/tracking`, `/utm`, `/sop`, `/learn`, `/shield`, `/doctor`. Installed as a plugin they are namespaced, e.g. `/tyrion:audit`.
- **2 workflows** (`workflows/*.js`, plugin mode) — `/tyrion:toliq-audit` (multi-platform audit: evidence inventory, one auditor per platform, every finding checked against its evidence file, delivery gate) and `/tyrion:haftalik-tahlil` (weekly review).
- **29 deterministic 0-token Python CLI tools** (`tools/*.py`) — unit economics, CAPI SHA-256 + Consent Gate, 6-status Meta Detailed Targeting verification, Breakdown Effect detector, 3x3 Creative Matrix, and Spend-Guard.
- **Bilim: atomik qaydlar (100)** (`wiki/*.md`) — interlinked paid-media knowledge base with zero orphan notes.

```text
ai-ads/
├── core/                    # Market-independent canonical English rules, playbooks & wiki index
├── markets/                 # Modular regional Market Packs (global, us, eu, uk, mena, latam, sea, in, uz)
├── locales/                 # UI & CLI locale bundles (en, uz, ru)
├── agents/                  # 36 specialist agent charters
├── skills/                  # 63 canonical paid-media & CRO skills
├── commands/                # one slash command per function (no aliases)
├── hooks/                   # Cross-platform ${CLAUDE_PLUGIN_ROOT} hook launcher & guard
├── tools/                   # 29 ta 0-Token Deterministik CLI Asbob & STDIO MCP server
└── wiki/                    # 100 atomic wikilinked knowledge notes
```

---

## 3. Global Market Packs & Usage Examples

Tyrion defaults to `market=global` and auto-detects the market, currency, regulations, and response language from your prompt or CLI flags (`--market`, `--currency`, `--language`):

### Example A — Germany / EU E-Commerce (`market=eu`, `EUR`, GDPR + Consent Mode v2)
```bash
python3 tools/skill-search.py route "My Shopify store in Germany has low ROAS on Meta" --json
python3 tools/creative-matrix.py matrix --niche ecom --product "Espresso Machine" --price 300 --market eu --currency EUR
python3 tools/capi-utm-builder.py capi-payload --event Purchase --country de --market eu --value 300 --currency EUR --no-consent
```

### Example B — Multilingual & RTL Ad Hooks (`de`, `fr`, `ar`, `en`)
```bash
python3 tools/creative-matrix.py hooks --niche ecom --offer "Free Express Shipping + 30-Day Trial" --languages en,de,fr,ar
```

### Example C — Live Meta Detailed Targeting Verification (6-Status Anti-Hallucination Engine)
```bash
python3 tools/meta-targeting-engine.py search --niche real-estate --query "interyer" --query "новостройки" --account-id act_123456789
```

### Example D — Uzbekistan Market Pack (`market=uz`, `UZS`, Telegram/AmoCRM, Payme/Uzum Nasiya)
```bash
python3 tools/tyrion.py route "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top"
```

---

## 4. Optional Live API & MCP Integrations

Copy `.env.example` to `.env` to configure live read-only API access:
- `META_ACCESS_TOKEN`: Enables live Meta Graph API `targetingsearch`, `targetingvalidation`, and `meta-insights-sync.py`.
- `META_GRAPH_API_VERSION`: Defaults to `v26.0` (dynamically read from `.env`; warns automatically if an outdated version `< v25.0` is configured).
- For external `meta-ads-mcp` (`uvx meta-ads-mcp`) and official `google-ads-mcp` setup, see [docs/integrations.md](docs/integrations.md).

---

## 5. License & Attribution

Released under the [MIT License](LICENSE). Includes third-party open-source attributions in [NOTICE](NOTICE) and [THIRD_PARTY.md](THIRD_PARTY.md) for [AgriciDaniel/claude-ads](https://github.com/AgriciDaniel/claude-ads) and [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code).
