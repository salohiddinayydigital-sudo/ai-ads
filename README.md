# Tyrion v7.0 — Global Paid-Media & Targetology Operating System (`ai-ads`)

<!-- tyrion:catalog agents=36 skills=63 wiki=100 playbooks=9 contexts=6 commands=27 rules=9 tools=29 -->

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/Python-3.10%E2%80%933.13-3776AB.svg)](https://www.python.org/)
[![OS: Windows | macOS | Linux](https://img.shields.io/badge/OS-Windows%20%7C%20macOS%20%7C%20Linux-success.svg)](#1-minute-quickstart)

> 🇺🇿 **O'zbek tilidagi hujjat:** [README.uz.md](README.uz.md)

**Tyrion (`ai-ads`)** is an open-source, deterministic paid-media, performance marketing, and targetology plugin for **Claude Code**, **OpenAI Codex CLI**, **Cursor**, and **Windsurf**. It works out-of-the-box on **Windows, macOS, and Linux**, responds automatically in the **user's language**, supports **any ISO 4217 currency**, and ships with modular **Market Packs** (`global`, `us`, `eu`, `uk`, `mena`, `latam`, `sea`, `in`, `uz`).

---

## 1. 1-Minute Quickstart

### Install via Claude Code Plugin Marketplace
```bash
/plugin marketplace add salohiddinayydigital-sudo/ai-ads
/plugin install tyrion
```

### Requirements & OS Compatibility
- **Python:** `3.10` – `3.13` (`python3`, `python`, or `py -3` on Windows — automatically detected by `hooks/run-hook.cjs`)
- **Node.js:** `18+` (bundled with Claude Code / Codex / Cursor)
- **Supported OS:** Windows 10/11, macOS 13+, Ubuntu/Debian/Fedora Linux
- **Installed Plugin Isolation (`cwd != plugin_root`):** All hooks (`hooks/hooks.json`) and the built-in STDIO MCP server (`.mcp.json`) resolve paths via `${CLAUDE_PLUGIN_ROOT}` and fail open (`exit 0`) on non-strict environment warnings, so Tyrion never blocks file edits in your other projects.

---

## 2. Core Architecture & Inventory

- **36 specialist agents** (`agents/*.md`) — Meta, Google, TikTok, YouTube, LinkedIn, Telegram, CAPI tracking, creative strategy, unit economics, and regulatory compliance.
- **63 platform & marketing skills** (`skills/*/SKILL.md`) + **6 regional platform skills** (`markets/*/skills/`) covering Yandex Direct, VK Ads, LINE Ads, Naver/Kakao, Baidu/Douyin/WeChat, and Taboola/Outbrain.
- **27 slash commands** (`commands/*.md`) — canonical English commands (`/audit`, `/audience`, `/creative`, `/funnel`, `/export`, `/report`, `/client`, `/competitors`, `/ask`, `/plan`, `/budget`, `/tracking`, `/learn`, `/shield`, `/doctor`) with full Uzbek aliases (`/auditoriya`, `/kreativ`, `/voronka`, `/eksport`, `/hisobot`, `/mijoz`, `/raqobatchi`, `/savol`).
- **29 deterministic 0-token Python CLI tools** (`tools/*.py`) — unit economics, CAPI SHA-256 + Consent Gate, 6-status Meta Detailed Targeting verification, Breakdown Effect detector, 3x3 Creative Matrix, and Spend-Guard.
- **Bilim: atomik qaydlar (100)** (`wiki/*.md`) — interlinked paid-media knowledge base with zero orphan notes.

```text
ai-ads/
├── core/                    # Market-independent canonical English rules, playbooks & wiki index
├── markets/                 # Modular regional Market Packs (global, us, eu, uk, mena, latam, sea, in, uz)
├── locales/                 # UI & CLI locale bundles (en, uz, ru)
├── agents/                  # 36 specialist agent charters
├── skills/                  # 63 canonical paid-media & CRO skills
├── commands/                # 27 slash commands (English canonical + Uzbek aliases)
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
