# Agents Full Upgrade Report — release 8.1.0 → 8.3.0 (Tyrion Charter v2 + Targetolog Copilot Pack)

**Branch:** `feat/agents-v8.3-full-upgrade` (created from `main` @ `1b1e848`, clean working tree verified first)
**Scope:** Phase A = `agents-upgrade-plan.md` (Charter v2 for 12 core agents) · Phase B = `targetolog-agents-plan.md` (7 Targetolog Assistant agents, 7 commands, 6 DAG workflows)

## 1. Commits

| # | Commit | Message | Version |
|---|---|---|---|
| 1 | `f4ab728` | `feat(agents): upgrade 12 core agents to Charter v2` | 8.2.0 |
| 2 | the commit that adds this report (branch HEAD; `git log -1 feat/agents-v8.3-full-upgrade`) | `feat(agents): add 7 targetolog assistant agents, commands, and workflows` | 8.3.0 |

A commit cannot contain its own hash, so Commit 2 is identified by position: it is the branch HEAD and the only commit that adds this file.

## 2. Checks: baseline vs. after Commit 1 vs. final

| Check | Baseline (`main`, 8.1.0) | After Commit 1 (8.2.0) | Final (8.3.0) |
|---|---|---|---|
| `python3 tools/doctor.py` | exit 0 · 18 ok · 1 warn (stale knowledge graph) · 0 errors | exit 0 · 18 ok · 1 warn (uncommitted files) · 0 errors | exit 0 · 18 ok · 1 warn (uncommitted files, before the commit) · 0 errors |
| `python3 tools/tyrion_workflows.py check` | 16 workflows · 0 errors · 0 warnings | 16 · 0 · 0 | **22** · 0 · 0 |
| `python3 -m pytest -q` | 574 passed · 1 skipped | 590 passed · 1 skipped | **603 passed · 1 skipped** (650 subtests) |
| `python3 tools/catalog.py check` | OK (351 items) | OK (352) | OK (374) |
| `python3 tools/skill-search.py check` | 19 skills · 12 agents · 30 links | 19 · 12 · 30 | 19 · **19** · **37** links, registry intact |
| skill-eval (via doctor) | 51/51 | 51/51 | 51/51 |
| TyrionShield (via doctor) | 6/6 clean | 6/6 | 6/6 |

New test suites: `tests/test_agents_charter_v2.py` (16 tests) and `tests/test_targetolog_agents.py` (13 tests).

## 3. All 19 canonical agents

`main` = line count on `main` (— = new). Gate: `>=85` = rubric score, `P/F` = Pass/Fail checklist. Either way a failed gate forces one internal rewrite before the agent returns.

| # | Agent | Group | Lines (main → now) | maxTurns | Gate | Handoff packet |
|---|---|---|---|---|---|---|
| 1 | `strategist` | Core | 85 → 107 | 28 | >=85 | `strategic_brief` |
| 2 | `platform-auditor` | Core | 152 → 181 | 28 | P/F | `audit_findings_packet` |
| 3 | `creative-strategist` | Core | 107 → 126 | 28 | >=85 | `strategic_brief` → video |
| 4 | `video-producer` | Core | 104 → 107 | 24 | >=85 | script → creative/content |
| 5 | `budget-analyst` | Core | 63 → 81 | 24 | P/F | `budget_guard_packet` |
| 6 | `audience-architect` | Core | 66 → 91 | 24 | P/F | audience architecture |
| 7 | `data-analyst` | Core | 52 → 75 | 24 | P/F | `analytics_readout_packet` |
| 8 | `tracking-specialist` | Core | 77 → 104 | 24 | P/F | `tracking_spec_packet` |
| 9 | `content-planner` | Core | 95 → 111 | 24 | >=85 | calendar → video |
| 10 | `compliance-reviewer` | Core | 68 → 89 | 18 | P/F | `compliance_clearance_packet` |
| 11 | `research-verifier` | Core | 67 → 92 | 18 | P/F | `verified_research_packet` |
| 12 | `release-verifier` | Core | 66 → 91 | 18 | P/F | release verdict |
| 13 | `client-onboarder` | Targetolog | — → 92 | 20 | >=85 | `client_onboarding_packet` |
| 14 | `ad-spy-analyst` | Targetolog | — → 97 | 20 | P/F | `ad_spy_packet` |
| 15 | `campaign-launcher` | Targetolog | — → 101 | 24 | P/F | `launch_blueprint_packet` |
| 16 | `daily-optimizer` | Targetolog | — → 101 | 24 | P/F | `daily_triage_packet` |
| 17 | `funnel-cro-doctor` | Targetolog | — → 93 | 24 | >=85 | `cro_fix_packet` |
| 18 | `account-recovery-specialist` | Targetolog | — → 98 | 18 | P/F | `recovery_action_packet` |
| 19 | `client-comms-lead` | Targetolog | — → 90 | 18 | >=85 | `client_comms_packet` |

**Token / line impact (12 core charters):** about 1,000 → 1,255 lines in total (+25%). The ~30-line copy of the agent cycle and procedure is gone from every charter: it now lives once in `rules/70-charter-baseline.md` §2. The freed space and the growth hold domain content: modes, decision order, anti-patterns, rubric and handoff. Every charter body stays at or under 140 lines (enforced by a test). On bytes, `platform-auditor` and `video-producer` got smaller (9.3 KB → 8.4 KB, 7.7 KB → 6.9 KB). The others grew 0–1.6 KB.

## 4. Routing test matrix (`tools/skill-search.py` `route_task`)

| Query (lang) | Resolved `primary_agent` | Workflow |
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
| mijozga telegram hisobot (uz) | `client-comms-lead` | — (skill ranking) |
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

**Collision audit:**
- No trigger phrase is shared by two of the 19 agents (case-insensitive; enforced by a test).
- 232 core-agent triggers were routed on `main` and again on this branch. 228 resolve to the same agent as before. The other 4 (`reklama bloklandi`, `ad rejected`, `модерация отклонила`, `блокировка рекламы`) were moved on purpose from `compliance-reviewer` to `account-recovery-specialist`.
- None of the 105 new-agent triggers routes to a different agent; 75/105 route to their own agent. The other 30 are bare 2-word fragments that the existing scope gate stops with `out_of_scope` or `needs_clarification` before any agent is chosen. Core-agent triggers get the same treatment on `main`.

## 5. Files

**Phase A (Commit 1)**
- Created: `schemas/agent-handoff.schema.json`, `skills/{strategy,creative,budget,analyze,content}/references/quality-rubric.md`, `skills/analyze/references/data-analyst-playbook.md`, `tests/test_agents_charter_v2.py`.
- Rewritten: all 12 `agents/*.md` and their `.claude/agents/` mirrors; `rules/70-charter-baseline.md`, re-exported to `.cursor/rules/tyrion-70-charter-baseline.mdc` and `.windsurfrules`.
- Updated: `AGENTS.md` §3, `CHANGELOG.md`, `tools/catalog.py` (2 new claim patterns keep the agent count in `rules/70` synced, so the stale "36" cannot come back), `manifests/catalog.json`.
- Version bump 8.1.0 → 8.2.0 through the repo's `VERSION` + `catalog.py sync-claims` mechanism (version strings across manifests and docs).

**Phase B (Commit 2)**
- Created:
  - `agents/{client-onboarder,ad-spy-analyst,campaign-launcher,daily-optimizer,funnel-cro-doctor,account-recovery-specialist,client-comms-lead}.md` and their mirrors
  - `commands/{onboard,ad-spy,launch-plan,morning-triage,cro-dm,appeal,client-update}.md` and their mirrors
  - the 6 playbooks under `skills/*/references/`
  - `tests/test_targetolog_agents.py`
  - this report
- Updated:
  - `manifests/workflows.json`: 6 new workflows; `client_report` now has a `none_of` guard for Telegram, objection and upsell messages.
  - `schemas/agent-handoff.schema.json`: 14 packets.
  - `skills/{client,competitors,strategy,pulse,funnel,system}/SKILL.md`: attachments now go both ways, plus new triggers.
  - `tools/skill-search.py`: the scope gate now recognises targetolog terms.
  - `agents/compliance-reviewer.md`: now pre-flight only.
  - Handoff lines in the core charters now point at the new agents.
  - `AGENTS.md` §3.1 and §3a, `CLAUDE.md`, `README*.md`, `INDEX.md`, `rules/README.md`, `commands/shield.md`.
  - Count assertions updated 12 → 19 agents and 35 → 42 commands in `tests/test_agent_charters.py`, `tests/test_audit_v5.py` and `tests/test_vault_audit.py`.
  - `CHANGELOG.md`, version bump 8.2.0 → 8.3.0.

## 6. Guardrails honoured

- Python stdlib only; no dependency added.
- **Spend-Guard:**
  - `campaign-launcher` and `daily-optimizer` have no write tools and never create or change live campaigns.
  - Any change above +20%, any pause and any launch requires a `tyrion_spend_guard` draft and user approval.
  - Both agents have `spend_guard_required` in their output contracts (checked by a test).
- **White-hat:** `account-recovery-specialist` forbids:
  - cloaking
  - fake documents
  - farmed, stolen or rented accounts
  - policy circumvention

  This is enforced in four places:
  - its authority boundary
  - its anti-patterns
  - a critical Self-Audit item
  - the schema constant `white_hat_only: true`

  It links to `rules/40-xavfsizlik-va-hisob.md`, and a test checks all of this.
- These are kept in sync: `.claude/agents/`, `.claude/commands/`, `.cursor/rules/`, `.windsurfrules` and `manifests/catalog.json`. Doctor reports mirror drift as 0 (42 pairs).

## 7. Follow-ups — closed in 8.3.1

All five follow-ups were handled in 8.3.1 (see `CHANGELOG.md`):

1. `data-analyst` now has 17 UZ/RU/EN triggers. Experiment, significance, sample-size and normalisation queries route to it. Export performance analysis stays in the `results_analysis` workflow by design.
2. `client_report` was checked. Its `release-verifier` primary is intentional: the stage is a fresh-context verification of the report. Client-facing Telegram and objection messages now go to `client-comms-lead`: the `client_report` guard was added in 8.3.0 and the matching `weekly_review` guard in 8.3.1. No eval regressions.
3. Evals added for the 7 new agents and `data-analyst`: 8 `universal_route` scenarios and 7 golden `claude plugin eval` cases.
4. `skills/tyrion/references/workflow-recipes.md` now documents all six targetolog workflows (sections E–J).
5. `docs/v8-baseline.md` is a historical snapshot and is intentionally unchanged.

Two routing defects found while writing the evals were also fixed: `meta_strategy` was capturing ad-rejection appeals, and `weekly_review` was capturing Telegram client messages.
