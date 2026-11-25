# Workflow Recipes (merged from the former `orch-*` skills)

The stage graphs live in `manifests/workflows.json` (`full_audit`, `weekly_review`, `campaign_launch`, `creative_improve` and the v8.3 Targetolog Copilot flows E–J). This file keeps the *domain rules* behind those flows; agent-level detail is in each `agents/<name>.md` charter and its playbook.

## A. Full multi-platform audit (`full_audit`)

Pre-flight: `rules/00-manba.md` (no unsourced metrics), `rules/40-xavfsizlik-va-hisob.md` (read-only by default), `rules/30-ozbekiston-konteksti.md` for Uzbekistan clients; read `MEMORY.md` and prior `outputs/<client>/`. List missing access/data and ask instead of guessing.

Order: platform audit (`audit-<platform>`: structure, Advantage+/manual, CBO/ABO, learning stability, overlap, frequency) -> tracking (`audit-tracking`: Pixel/CAPI match quality, `event_id` parity, UTM taxonomy) -> creative + economics (`audit-creative`, `audit-budget`: hook/hold, format diversity, blended ROAS, MER, break-even CPA) -> policy (`audit-policy-compliance`: prohibited claims, before/after, restricted verticals; no compliance guarantee) -> synthesis gate (`release-verifier`).

Deliverable `outputs/<client>/<date>-<platform>-audit.md`; every finding has `Finding ID`, evidence and metrics, severity (CRITICAL/HIGH/MEDIUM/LOW), actionable recommendation, rollback/reversal.

## B. Weekly review and bet settlement (`weekly_review`)

Ground truth: blended ROAS = total revenue / total ad spend and net cash after ad spend and COGS (`[[blended-roas-net-cash]]`); in-platform ROAS is directional. Read `MEMORY.md` and `journal/<client>.md`.

Order: attribution reconciliation (CRM/backend revenue vs platform, channel contribution) -> pacing and CPA week-over-week -> creative fatigue (frequency, FTIR, 3-second drop-off; winners to iterate per `[[ad-iteration]]`) -> settle last week's hypotheses as Confirmed/Refuted/Inconclusive, write 1-3 new falsifiable bets -> verified report.

Deliverable `outputs/<client>/<date>-haftalik-hisobot.md`: 3-bullet summary, numbers table (spend, revenue, blended ROAS, CPA, net cash), Kill/Keep/Scale with rationale, next-week plan with owner and deadline. Append to `journal/<client>.md` and one line to `LOG.md`; promote only validated lessons to `MEMORY.md`/`/learn`.

## C. Controlled campaign launch (`campaign_launch`)

Safety contract: the AI never mutates a live account. Every recommendation is a human-executable **Change Packet** with rollback. Define break-even CPA, target ROAS, daily cap and stop-loss first.

Three-phase ladder: Phase 1 Sandbox (audience and hook tests, small share of the test budget) -> Phase 2 Validation (CPA stability, CAPI proof) -> Phase 3 Scale (Advantage+/horizontal scale, vertical steps within Spend-Guard's +20% rule). Budget shares are planning parameters derived from the client's economics via `calculator.py ladder`, not universal constants.

Kill/promote rules are expressed against the client's own target CPA (for example: pause an ad set whose spend exceeds a multiple of target CPA with zero conversions; promote when CPA <= target after enough conversions). State the multiple and the conversion count as assumptions with the reason.

Six safety gates before the packet: (1) budget cap defined, (2) creative approved by the client, (3) targeting verified (geo, age, language, exclusions), (4) policy risk assessed, (5) rollback plan written, (6) explicit human sign-off. Packet file: `outputs/<client>/<date>-launch-packet.md` with setup checklist, exact budgets and bid strategy, asset mapping (headline, primary text, creative ID, UTM URL), emergency rollback. Naming: `[TYRION]_[Client]_[Platform]_[Objective]_[Angle]_[Date]`. Validate with `python3 tools/spend-guard.py packet`.

## D. Creative improvement sprint (`creative_improve`)

Research -> concept -> production brief -> test -> measure -> diagnose -> iterate -> scale. Distinct angles (pain, outcome, us-vs-them, skeptic/mechanism) x distinct formats; resizing or re-captioning the same video is not a new concept. Copy per language is adapted natively (Uzbek Latin, Uzbek Cyrillic, Russian), never literally translated. Visual/edit specs: 9:16 for Reels/Stories/TikTok, 4:5 or 1:1 feed, 16:9 YouTube; restrained color grading, readable type inside safe zones; export specs come from `video-editing` and must be re-verified against the platform's current documentation before delivery.

Deliverable `outputs/<client>/<date>-kreativ.md`: angle matrix, copy by language, storyboards with time codes, production checklist, test plan (what changes, what stays constant, decision rule).

## E. New client onboarding (`new_client_onboarding`)

`client-onboarder` -> (`ad-spy-analyst` || `tracking-specialist`) -> `strategist`. Playbook: `skills/strategy/references/client-onboarding-framework.md`.

Eight business parameters (offer, average check, margin, ICP, geo, monthly budget, target CPL/CPA, past experience) are filled or turned into plain-language client questions; no KPI promise before break-even (`calculator.py breakeven`). Readiness is Go / Fix-First / No-Go: one No-Go factor (no sales responder, budget below ~14 days × 2–3 × target CPA, margin that cannot carry ads) means "not ready". Access only via Business Manager partner roles — never a personal password or SMS code. Deliverable: `client_onboarding_packet` + `clients/<slug>/BRIEF.md`.

## F. Campaign build to launch (`campaign_build_to_launch`)

(`audience-architect` || `creative-strategist` || `tracking-specialist`) -> `campaign-launcher` -> `compliance-reviewer`. Playbook: `skills/budget/references/daily-triage-kill-scale.md` (learning and scaling limits).

Each ad set's daily budget >= target CPA × 1.5–2, otherwise consolidate (Andromeda: few ad sets, many distinct creatives). Naming `YYYY-MM_GEO_OBJ_AUD_OFFER_V1`, lower-case UTM table, exclusions in every prospecting ad set, 20-point pre-launch gate and "do not touch for 72 h" rules. The output is a blueprint; creating campaigns or changing budgets is a Change Packet through `tools/spend-guard.py` plus user approval (see C).

## G. Morning media-buyer triage (`morning_media_buyer_triage`)

`data-analyst` (optional when `metrics.v1` exists) -> `daily-optimizer` -> (`budget-analyst` || `funnel-cro-doctor`) -> `client-comms-lead`. Playbook: `skills/budget/references/daily-triage-kill-scale.md`.

One verdict per ad set/ad: KILL / HOLD / ITERATE / SCALE with spend, result count and whether the minimum-spend threshold was met (spend < 1.5 × target CPA is always HOLD). CPL spikes are split by `CPL = CPM / (1000 × CTR × CVR)`; act on one root cause at a time; check Breakdown Effect before cutting a segment. Scaling: +15–20% per 48–72 h; anything above +20% or any pause is a Spend-Guard packet.

## H. Lead quality and DM fix (`lead_quality_and_dm_fix`)

(`tracking-specialist` || `funnel-cro-doctor`) -> `creative-strategist` -> `client-comms-lead`. Playbook: `skills/funnel/references/direct-dm-and-leadform-cro.md`.

Order: message match (ad promise = first DM reply / landing first screen) -> response SLA (first reply <= 5 min in working hours) -> friction (Lead Form <= 5 fields, Higher Intent, 2–3 filter questions) -> CRM stage leak. Fixes are ICE-ranked; testimonials are never invented.

## I. Competitor ad spy (`competitor_ad_spy`)

`ad-spy-analyst` -> `creative-strategist` -> `video-producer` (optional, static only). Playbook: `skills/competitors/references/ad-library-spy-playbook.md`.

Every observation has a URL/screenshot and date; "winner" only with known longevity (>= 30 days strong, 14–30 medium, < 14 test). Observed vs assumed is explicit; competitor budget/ROAS is never stated as fact. At least five Counter-Angles, each tied to a competitor weakness and a testable hypothesis; no copying of text or visuals.

## J. Account restriction recovery (`account_restriction_recovery`)

`account-recovery-specialist` -> `compliance-reviewer` -> `client-comms-lead`. Playbook: `skills/audit/references/account-recovery-whitehat.md`.

White-hat only (`rules/40-xavfsizlik-va-hisob.md`): no cloaking, fake documents, rented/farmed/stolen accounts or filter tricks — such requests are refused with the legitimate path. Identify the incident type and likely policy (official URL + date or `unverified`), give a safe rewrite (never resubmit an unchanged rejected ad), a calm factual EN/RU appeal, and a recovery sequence (Account Quality, ID/BM verification, payment checks). The client hears a transparent crisis update.

