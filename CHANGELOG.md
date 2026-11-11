# Changelog

All notable changes to **Tyrion (`ai-ads`)** are documented in this file following [Semantic Versioning](https://semver.org/).

## [Unreleased] — v7.1 / v7.2 follow-ups (code-level only)

Market facts that could not be confirmed against official sources (Meta API v27.0, 2026 attribution rules, Ads MCP, Uzbek ad-law changes, Telegram/Google reference updates, wiki refresh) are **not** written into rules; they are tracked as unverified (`manifests/api-versions.json`, `doctor` freshness/source checks).

### Fixed
- **B08** Uzbek Latin queries ("TikTok reklamani qanday boshlayman", "kampaniyam … oshib ketdi") are detected as `uz_latin` and therefore resolve to the `uz` market/UZS.
- **B09** `plugin.json` `userConfig` is honoured: `hooks_enabled`, `hook_profile` (`minimal` skips guard/ingest) in `hooks/run-hook.cjs`; `default_market` as fallback in `market_locale.py` (`TYRION_*` env vars win).
- **B10** Removed the unsourced `blended_cpa * 1.38` Breakdown-Effect projection; result is `null` + `HEURISTIC_PRIOR_MODEL` label and a "measure marginal CPA" note.
- **B12** MCP server: `ping`, protocol-version negotiation, tool failures returned as `isError` results (JSON-RPC `-32602` only for unknown tools), input schemas now list every parameter `call_tool` reads; `tyrion_capi_utm` gained `mode: capi-payload`; `tyrion_spend_guard` accepts `target_cpa`/`approve_pause`.
- **B13** Telegram copy check counts ⭐/flag emojis and Uzbek Cyrillic capitals (Ў Қ Ғ Ҳ); Meta banned phrases in RU/EN; wrong `tracking` docstring flags fixed.
- **B15** `doctor` graph staleness uses git commit times (no false warning on fresh clones); stale `gy.cmd` hint removed.
- **B16** Insights requests pin `action_attribution_windows` (`--attribution`, default `7d_click,1d_view`; `account_default` to skip) and the report states the attribution basis; non-USD exports flag legacy `*_usd` keys.
- **B17** Phone normalisation to E.164 using `--country`/`--phone-country-code` (trunk `0` removed); unknown country code is warned, never guessed.
- **B18/B19** `VERSION` is the single version source (`doctor` verifies all manifests; MCP server and `tyrion.py` read it); `CAPI v22`/stale `v5.x` banners removed; `manifests/api-versions.json` is the single Graph API version registry (default stays `v26.0`; `v27.0` listed as unverified candidate).
- **B20** CI runs on pushes to every branch.

### Added
- Spend-Guard 24-hour window: `--entity`, `--ledger`, `--record --approved-by` (JSONL ledger under git-ignored `outputs/`); stacked ≤20% steps that exceed 20% within 24 h are blocked.
- Export analyzer skips "Total" rows (no double counting) and reports the file's period/preamble.
- `doctor`: `Yangilik (refresh_due)`, `Wiki manbalari` and `Versiya` checks.
- Spend-Guard copy check warns on credit/instalment wording in Uzbek ads (labelled `UNVERIFIED_SECONDARY_SOURCE`).

### Tests
- `tests/test_v71_followups.py` (40 tests). Suite: 242 → 282.

### Not done (needs official sources or a decision)
B21 wiki sources (restore or mark), B22 splitting the 3 000-line test file, B01-B06 fixtures for real Google/Telegram files, Meta Ads MCP integration, attribution/Telegram/Google reference rewrites, Detailed Targeting repositioning, Uzbek SMS/call-hours checks.

## [7.0.1] — 2026-11-11 (Ishonch hotfix / Trust hotfix)

Fixes the P0/P1 bugs from `docs/UPDATE-PLAN-v7.1.md` (B01–B07, B11, B14). Version fields in manifests are intentionally left at `7.0.0` until the version-drift cleanup (B18, v7.1).

### Fixed
- **B01 `/eksport` read real exports as zero spend:** `tools/ad-export-analyzer.py` now maps real Meta Ads Manager (EN `Amount spent (USD)`, `Ad set name`, `Link clicks`, `Purchases conversion value`; RU `Сумма затрат (USD)`…), Google Ads (report preamble lines, UTF-16/TSV, `Cost`, `Conv. value`) and Telegram Ads (`Spent, TON`) columns; currency is taken from the header suffix. A missing spend column aborts with an error (exit 2); rows with spend = 0 get `NO_VERDICT_ZERO_SPEND` instead of KEEP/SCALE. Misaligned (unquoted-comma) headers are rejected.
- **B02 decimal separators:** `safe_float` no longer deletes commas (`"499,90"` was 49990). New `tyrion_core.parse_number` / `detect_number_locale` handle `61,230`, `499,90`, `1 234,56`, `1.234,56`; an ambiguous bare `1,234` raises `AmbiguousNumberError` instead of guessing.
- **B03 Spend-Guard budget gate:** `nan`, `inf`, negative budgets are blocked (and never emit JSON `NaN`); `--proposed 0` (pause) is blocked unless `--approve-pause` is given.
- **B04 Change Packet check:** structural validation — Rollback, Stop-loss, Baseline, Risk and Human-approval sections must exist with non-empty, non-placeholder values; unticked `[ ]` approval fails. Keyword-only files no longer pass; the unconditional "6 gates satisfied" message is gone. The launch-packet template gained Baseline/Risk/Approval sections.
- **B05 MCP server:** `.mcp.json` uses `${CLAUDE_PLUGIN_ROOT:-.}` so `tyrion-core` starts when the repo is opened as a plain project. `doctor.py` now launches the configured command without `CLAUDE_PLUGIN_ROOT` and checks the `initialize` and `tools/list` replies (previously it only imported the module).
- **B06 CAPI payload:** no invented values — hard-coded `fbp`/`fbc`, default city/country, `order_id`, `event_source_url`, zero LDU fields and the fake EMQ bonus are gone. New flags `--fbp --fbc --user-agent --ip --action-source --event-id --event-time --event-source-url`; missing required fields are listed in `missing_fields`/`warnings`; `--value` requires `--currency`; EMQ is labelled `HEURISTIC_PRIOR_MODEL`.
- **B07 UTM links:** UTM parameters are inserted before the `#fragment`.
- **B11 `calculator.py`:** loss-making breakeven exits 1; `nan`/`inf` and negative inputs are rejected (exit 2).
- **B14 privacy:** `clients/*` and `outputs/` are git-ignored (demo brand and templates stay tracked); `push.sh`/`push.ps1` push the current branch to the existing `origin` (no `set-url`, no forced `main`) and run the unit tests first.

### Tests
- New `tests/test_v701_trust_hotfix.py` (46 tests) and real-format fixtures in `tests/fixtures/` (Meta EN/RU, Google Ads, Telegram Ads). Suite: 196 → 242 tests.
- `evals/scenarios.json` E07 now supplies `fbp`/`fbc`/city/first name explicitly.

## [7.0.0] — 2026-10-29 (Practitioner Targetology, `/ad-creative` Video Studio & Meta 2026 5-System AI Stack)

### Added
- **`/ad-creative` Skill & Slash Command (`skills/ad-creative/SKILL.md`, `commands/ad-creative.md`):** Full integration of the 4-mode Ad Creative & Video Ad Studio (`Generate from Scratch`, `Iterate from Performance Data`, `Grounded Static & Video Batches`, `Creative Strategy Roadmap & Retro`) with the 2026 S->F Meta Ad Format Tier List (`meta-creative-formats.md`), 9:16 vertical video safe-zone spec (`720x1200` inside `1080x1920`, `video-ad-scripts-and-specs.md`), Falsifiable Test Hypotheses, and strict No-AI-Tells linter (`no-ai-tells-and-hypotheses.md`).
- **Zero-Friction Video Ad Scripting (`tools/creative-matrix.py video-script`, `skills/reels-scripting/SKILL.md`):** Generates ready-to-shoot 9:16 scripts across 7 S/A-tier formats (`ugc_reaction_demo`, `founder_authority`, `no_yapping_split_screen`, `imessage_reveal`, `chatgpt_reveal`, `greenscreen_proof`, `faceless_motion_explainer`) with 3 opening hook variants, time-coded storyboards, and `720x1200` safe-zone overlays — with zero mandatory external API keys (`APIFY_API_TOKEN` removed) and zero coding required.
- **Andromeda Entity-ID & Persona-Desire-Awareness (PDA) Engine (`tools/creative-matrix.py pda-matrix`):** Builds 6–9 visually distinct concepts across Personas x Desires x Schwartz's 5 Awareness Stages so Meta Andromeda's computer-vision clustering assigns independent retrieval tickets.
- **Platform-Validated Ad Copy & AI-Tell Linter (`tools/creative-matrix.py ad-copy`):** Character-counted copy generation for Meta (`125/40/30`), Google RSA (`30/90`), TikTok (`80/100`), LinkedIn (`150/70/100`), and Telegram (`160`) with automatic removal of AI tells (*"It's not X, it's Y"*, *"Stop scrolling"*, em-dashes).
- **Meta 2026 Five-System AI Stack & Practitioner Targetologist Playbook (`tools/meta-targeting-engine.py`, `tools/meta-audience.py`, `skills/ads/references/meta-ai-stack.md`):** Added `GEM` (Teacher Foundation Model), `Andromeda` (Retrieval + Entity ID), `Lattice` (Unified Ranking + Sequence Learning), `UTIS` (User True Interest Survey Calibrator), `Adaptive Ranking Model` (`<100ms`), `Value Rules` (`+200%` to `-90%` bid multipliers), `GUIDED_CREATION` ASC API (`v25.0+`), Meta AI Chat Signal regional GDPR carve-outs, and the 9-section practitioner zero-coding Ads Manager setup guide.
- **Shared Product Marketing Context Template (`templates/product-marketing.md`):** Compatible with `.claude/product-marketing.md` and `.agents/product-marketing.md`.

## [6.0.0] — 2026-10-21 (Breaking: Global Architecture & Cross-Platform Release)

### Breaking Changes
- **Default Market Pack (`default_market`):** Changed default market in `plugin.json` from `"uz"` to `"global"`. `rules/30-ozbekiston-konteksti.md` and `uzbekistan-market-intel` are now loaded **only** when `market=uz` is active or detected.
- **Canonical English Slash Commands:** Added canonical English commands (`/audience`, `/creative`, `/funnel`, `/export`, `/report`, `/client`, `/competitors`, `/ask`) while preserving all Uzbek commands (`/auditoriya`, `/kreativ`, `/voronka`, `/eksport`, `/hisobot`, `/mijoz`, `/raqobatchi`, `/savol`) as aliases.
- **Canonical Hook Configuration:** Consolidated hooks into `hooks/hooks.json` using `${CLAUDE_PLUGIN_ROOT}` and `hooks/run-hook.cjs`; removed duplicate root `hooks.json` and `.claude/settings.json`.

### Added
- **Cross-Platform Node Hook & MCP Launcher (`hooks/run-hook.cjs`):** Automatically resolves `${CLAUDE_PLUGIN_ROOT}`, detects `python3` -> `python` -> `py -3` across Windows, macOS, and Linux, gates `ingest` and `dod` behind `TYRION_DEV=1` (or plugin repo root), caps `Stop` timeout at 5s, and fails open (`exit 0`) unless `TYRION_HOOK_PROFILE=strict`.
- **9 Regional Market Packs (`markets/`):** Added `global`, `uz`, `us`, `eu`, `uk`, `mena`, `latam`, `sea`, and `in` packs with currencies, BNPL providers (`Klarna`, `Afterpay`, `Affirm`, `Tabby`, `Tamara`, `Pix`, `Atome`, `Simpl`, `Uzum Nasiya`), seasonality calendars, privacy regulations, and source-cited `benchmarks.md`.
- **3 UI/CLI Locales (`locales/`):** Added `en`, `uz`, and `ru` message bundles and `core/` market-independent English rules and playbooks.
- **ISO 4217 Multi-Currency & Zero-Decimal Support:** Added `--currency` across CLI tools (`EUR`, `GBP`, `BRL`, `INR`, `JPY`, `KRW`, `UZS`, `USD`) and neutral currency keys alongside legacy `_usd` fields.
- **Global Privacy & CAPI Consent Gate (`tools/capi-utm-builder.py`):** Added `--consent-granted` / `--no-consent` PII gate, Google Consent Mode v2 signals, Meta Limited Data Use (`data_processing_options=['LDU']`), and GDPR/CCPA/LGPD/DPDP checks.
- **6 Regional Platform Audit Skills:** Added Yandex Direct, VK Ads, LINE Ads, Naver/Kakao, Baidu/Douyin/WeChat, and Taboola/Outbrain audit skills under `markets/*/skills/`.
- **Progressive Disclosure Router (`<= 15 KB` Budget):** Default `progressive` context mode keeps single-step query context under 15 KB.
- **Upstream MIT Attributions:** Added `AgriciDaniel/claude-ads` and `affaan-m/everything-claude-code` notices in `LICENSE`, `NOTICE`, and `THIRD_PARTY.md`.

---

# Changelog

All notable changes to **Tyrion** are documented in this file.

## [5.0.0] - 2026-10-20 — Calibrated Recommendation Engine, Live Meta Insights Sync & Single-Source Parity

### Added
- **Universal Auto-Router & Autonomous Agent Orchestrator (`tools/skill-search.py`, `tools/tyrion.py route`, MCP `tyrion_universal_router`)**:
  - Automatic natural-language task routing across Uzbek Latin, Uzbek Cyrillic, Russian, and English without manual `/skill-search` or `/agent` selection.
  - Enriched metadata across all 62 skills and 36 agents (`triggers`, `aliases`, `domains`, `platforms`, `related_skills`, `references`, `risk_level`, `output_contract`, `authority_boundary`).
  - Session-cached disk loading (`SessionContextCache`), dynamic mid-task re-routing (`--reroute-with`), universal conductor fallback, and Spend-Guard mutation gate.
- **Detailed Targeting Pagination, Payload & Cache Hardening (`tools/meta-targeting-engine.py`, `tools/catalog.py`)**:
  - Per-query `pages_fetched`, `is_truncated`, and `results_count` diagnostics; explicit truncation disclosures; separation of `MALFORMED_ITEM_PAYLOAD` from genuine `NOT_FOUND`; context-isolated cache keys (`special_ad_category`, `country`, `objective`, `language`, `locale`, `ad_account_id`, `api_version`, `api_base_url`); and CRLF-resilient SHA-256 in `catalog.py`.
- **Detailed Targeting Accuracy Engine (`tools/meta-targeting-engine.py`, `docs/DETAILED-TARGETING-ACCURACY.md` & MCP `tyrion_meta_detailed_targeting`)**:
  - Zero-hallucination 6-status verification system (`VERIFIED_AVAILABLE`, `FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED`, `RELATED_UNVERIFIED`, `NOT_FOUND`, `API_UNAVAILABLE`).
  - Multi-endpoint Meta Marketing API v26.0 integration (`/search?type=adinterest`, `/{ad-account-id}/targetingsearch`, `/{ad-account-id}/targetingsuggestions`, `/{ad-account-id}/targetingvalidation`) with `paging.next` pagination, `(id, type)` deduplication, multilingual query expansion (`uz_latin`, `uz_cyrillic`, `ru`, `en`), and TTL cache validation.
- **Live Meta Ads Insights Connector (`tools/meta-insights-sync.py` & MCP `tyrion_meta_live_insights`)**: Pulls live campaign, ad set, and ad telemetry from [Meta Graph API v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) (`/act_<id>/insights`) or validates raw Graph API JSON exports (`actions`, `action_values`), normalizes conversions/revenue, and pipes them into `ad-export-analyzer.py`.
- **Confidence Intervals & Model Disclosures (`tools/meta-audience.py`)**:
  - `saturation` now accepts `--active-reach-ratio` and `--measured-freq-7d`, outputs `estimated_fatigue_window_days` (`conservative_early_fatigue_day`, `baseline_fatigue_day`, `optimistic_late_fatigue_day`), and includes `model_disclosure` (`HEURISTIC_PRIOR_MODEL` vs `MEASURED_ACCOUNT_DATA`).
  - `architect` now derives `target_cpa` from unit economics (`--aov`, `--margin-pct`, `--lead-to-sale-cvr`) or user targets, and labels fallback estimates as `PROVISIONAL_HEURISTIC_FALLBACK` inside `evidence_and_assumptions`.
  - `lookalike` now exposes `heuristic_seed_readiness_score_100` with explicit disclosure (`is_meta_internal_score: False`).
- **Python AST & Dead-Code Scanner (`tools/tyrion-shield.py`)**: Added 6th check verifying zero syntax errors and zero unreachable statements across all Python modules, removed `tests/` from `SKIP_DIRS`, and added `scope_and_limitations` disclosure.

### Fixed & Changed
- **Fixed 3 Concrete Bugs in `tools/meta-audience.py`**:
  1. Removed 16 lines of unreachable dead code after `return` in `query_live_graph_api`.
  2. Added `--no-telegram-bot` / `--has-telegram-bot false` CLI flags in `retargeting`.
  3. Removed artificial `100/500/1000/200` minimum pool floors in `calc_retargeting` when source traffic is `0` (now returns `0` pool size and `INSUFFICIENT_RETARGETING_POOL`).
- **Unified 20% Audience Overlap Threshold**: Standardized `calc_overlap` warning threshold to `20.0%` (`<20%` = `HEALTHY_ISOLATION`, `20%–29.9%` = `MODERATE_OVERLAP`, `>=30%` = `CRITICAL_COLLISION`) matching all documentation, and added explicit distinction between `STATIC_AUDIENCE_POOL_INTERSECTION` and live auction delivery overlap.
- **Upgraded Default Meta Graph API Version to `v26.0`**: Updated `.env.example`, `tools/meta-audience.py`, `tools/capi-utm-builder.py`, and `tools/meta-insights-sync.py` to default to `v26.0` and dynamically interpolate `META_GRAPH_API_VERSION`.
- **Single-Source Version & Inventory Parity (`v5.0.0`)**: Synchronized all version strings (`v5.0.0`) and inventory counts (`36` agents, `62` skills, `100` wiki notes, `18` commands, `9` playbooks, `6` contexts, `29` tools) across all manifests, docs, and scripts.

## [4.0.0] - 2026-10-18 — Single-Root ECC Architectural Overhaul

### Added
- **Unified Master CLI (`tools/tyrion.py`)**: Single entrypoint routing across `status`, `doctor`, `shield`, `audience`, `creative`, `client`, `calc`, `guard`, `search`, `skills`, `instincts`, `catalog`, `graph`, and `audit`.
- **Meta Ads Audience Studio (`tools/meta-audience.py`)**: Added deterministic engines (`retargeting`, `lookalike`, and `diagnose`) alongside `architect`, `interests`, `overlap`, and `saturation`.
- **Andromeda 2 Creative Matrix & Hook Studio (`tools/creative-matrix.py`)**: Deterministic 3x3 Angle x Format matrix builder (`matrix`), 3-language Hook generator (`hooks`), and creative fatigue radar (`fatigue`).
- **Client Workspace Scaffolder (`tools/client-workspace.py` & `/mijoz`)**: Instant 1-command client workspace generator.
