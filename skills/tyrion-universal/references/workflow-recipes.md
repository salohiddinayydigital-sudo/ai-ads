# Workflow Recipes (merged from the former `orch-*` skills)

The stage graphs live in `manifests/workflows.json` (`full_audit`, `weekly_review`, `campaign_launch`, `creative_improve`). This file keeps the *domain rules* those four orchestrator skills used to hold, so nothing is lost when the duplicate orchestrators are retired.

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
