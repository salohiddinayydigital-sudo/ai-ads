# Orchestration Protocol (conductor reference)

Single source of truth for routing is `manifests/workflows.json` (validated by `python3 tools/tyrion_workflows.py check`) consumed by `tools/skill-search.py route`. This file only defines how the conductor executes a plan.

## 1. Delegation packet (native sub-agent call)

Pass structured context, not the chat transcript. Keep it under ~1.5 KB plus the upstream outputs the stage needs.

```text
GOAL: <one sentence, the stage output name from the plan, e.g. audience_architecture>
CONTEXT (verified): <facts the user gave; each with label USER_PROVIDED>
CONTEXT (assumptions): <ASSUMPTION items; do not treat as facts>
UPSTREAM: <outputs of stages in `needs`, compact JSON/bullets>
READ FIRST: <stage skills: paths> ; REFERENCES: <1-2 paths>
TOOLS ALLOWED: <from plan; run `--help` before first use>
OUTPUT CONTRACT: <agent charter contract + stage output name>
QUALITY BAR: every number labelled; no invented interests/IDs/stats/testimonials; list execution_evidence {tools_used, files_read, not_used}
BOUNDARY: bounded to this goal; do not call tyrion_universal_router without caller="specialist"; do not spawn agents; do not mutate any ad account
```

## 2. Specialist result envelope (what the conductor expects back)

`status` (`completed | needs_input | blocked_mutation_approval`), `output` (the stage deliverable), `assumptions[]`, `evidence_labels`, `execution_evidence {tools_used, files_read, not_used}`, `open_questions[]`, `contradictions[]`. `needs_input` is valid: the conductor decides whether to ask the user or proceed with labelled assumptions.

## 3. Validation rubric (apply per stage, then to the whole)

| Check | Fail example | Action |
|---|---|---|
| Completeness vs contract | Audience result without exclusions | Send back once with the missing field named |
| Evidence | "CPA should be $5" with no source | Remove or label `HEURISTIC_PRIOR_MODEL`; compute via `calculator.py` |
| Targeting accuracy | Interest not returned by `meta-targeting-engine.py` presented as valid | Downgrade to hypothesis; keep original name and ID only for verified items |
| Fabrication | Invented testimonial, "90% of clients...", guarantee, price | Strip; replace with `[ADD VERIFIED ...]` placeholder |
| Policy | Personal-attribute claims, before/after, income promises | Flag; never claim compliance without a real review |
| Consistency | Budget in creative plan exceeds economics | Resolve against `unit_economics` output (the numbers win) |
| Honesty of execution | Result claims a tool/skill it did not use | Reject that claim |
| Original objective | Beautiful output that does not answer the request | Re-scope before synthesis |

Whole-deliverable pass: objective answered? every assumption listed with how to verify? numbers reconcile across sections (budget = sum of campaigns, CPA targets match economics, funnel volumes match budget)? language and market correct (Uzbek Latin default; natural adaptation, not literal translation)?

## 4. Parallel vs sequential

Use `parallel_levels` from the plan. Parallel only if no stage in the level reads another's output. Dependencies of note in Meta strategy: `positioning` waits for `research`; `audience` and `architecture` need `positioning` + `economics`; `creative` needs `positioning`; `video` needs `creative`; `validate` needs everything. Do not repeat research the user already supplied (`optional_when`).

## 5. Fallback matrix

| Harness | Sub-agents | Behavior |
|---|---|---|
| Claude Code | `Agent` tool (`subagent_type` = agent name, from `agents/*.md` / `.claude/agents`) | Native per stage. If the agent type is missing (session started before install): fallback for that stage. |
| Codex, Cursor, Windsurf, CLI/MCP | none | Single conductor: read charter + skill, do the stage inline, label `executed_by: conductor_as_<agent>`. Context comes from `AGENTS.md`/rules + router MCP tool. |
| Any | Tool/API unavailable | Report which, continue with labelled assumptions or offline statuses. |

Never report `subagents_actually_spawned: true` unless an `Agent` call really ran.

## 6. Tool selection notes (flags verified against `--help`)

- `calculator.py breakeven --price --cogs [--shipping --processing-fee-pct --target-profit-pct --currency] --json`
- `calculator.py funnel-economics --price --cogs [--lead-to-sale-cvr --target-profit-pct --daily-budget --assumed-cpl ...] --json` (volume forecasts only when the user supplies an assumed CPL; outputs are labelled `ASSUMPTION`)
- `meta-targeting-engine.py search --product --niche --customer-profile --problem --objective --country --language [--account-id] --json` (needs `META_ACCESS_TOKEN`; without it every item is `API_UNAVAILABLE`, which is reported, never faked)
- `meta-audience.py architect|overlap|saturation|lookalike|retargeting|diagnose|launch-blueprint --help`
- `creative-matrix.py video-script --product --problem --format --duration [--price --market --language] --json` (prints `claim_safety`)
- `creative-matrix.py iterate ...` (diagnosis from real metrics; see `skills/video/references/reels-scripting/references/performance-video-system.md`)
- `ad-export-analyzer.py analyze --file <csv|json> [--target-cpa --breakeven-roas --primary-conversion] --json`
- `spend-guard.py budget|packet|copy|tracking --help`

## 7. Memory and learning

Read `MEMORY.md` first (language, market, active bets). Write only: (a) validated lesson with measured evidence -> `/learn`; (b) hypothesis -> Bet Ledger as `PENDING`. Do not write client names or secrets into `MEMORY.md` (client data lives in `clients/<slug>/`).

## 8. Worked trace (abridged): "Shu biznes uchun Meta Ads strategiya tuz"

1. Route -> `meta_strategy`, primary `launch-planner`, levels: intake > economics||research||tracking > positioning > architecture||audience||creative > video > validate > synthesize.
2. Read `ads-plan`, `ads-launch`, `ads-budget` fully + `meta-strategy-deliverable.md`.
3. Intake: user gave product and city only -> ask once for price/margin, goal, monthly budget, tracking state; proceed with labelled assumptions if unanswered.
4. Level 2 in one message: `audit-budget` (calculator), `research-worker` (skipped if user supplied competitors), `tracking-specialist`.
5. Level 4: `launch-planner`, `meta-audience-architect` (targeting tool, 6 statuses), `creative-strategist` in parallel.
6. `reels-scriptwriter` writes the top 1-2 concepts; `source-verifier` checks claims; conductor validates, reconciles budget vs funnel volumes, writes `outputs/<client>/<date>-meta-strategy.md`, reports which stages were native vs fallback.
