---
name: audience
description: "Meta Ads & multi-platform audience architecture, 6-status live interest discovery, verification, 5-factor relevance ranking, overlap & saturation analysis (Alias: /auditoriya)"
alias_of: auditoriya
argument-hint: "<product/service> [--niche ecom|edu|real-estate|medical|b2b|beauty|auto|local] [--account-id act_...]"
---

# `/audience` (Alias: `/auditoriya`) — Live Meta Detailed Targeting & 4-Layer Audience Architect

Task: **$ARGUMENTS**

## Mandatory Live Execution Workflow (Never Stop at `--help` or Static Taxonomy!)

1. **Step 1 — Discover, Verify & Rank Detailed Targeting Interests (`tools/meta-targeting-engine.py`):**
   Always execute the live Detailed Targeting engine first using the business context (product/service, problem solved, customer profile, purchase intent, complementary categories, market country, and campaign objective):
   ```bash
   python3 tools/meta-targeting-engine.py search \
     --product "<product_or_service>" \
     --problem "<main_problem_solved>" \
     --customer-profile "<target_customer_and_needs>" \
     --intent "<purchase_intent>" \
     --complementary "<complementary_products>" \
     --niche <ecom|edu|real-estate|medical|b2b|beauty|auto|local> \
     --objective <SALES|LEADS|ENGAGEMENT|TRAFFIC|AWARENESS> \
     --country <ISO_COUNTRY> \
     --account-id <act_id_if_available> \
     --max-queries 12
   ```
   - When `META_ACCESS_TOKEN` is set, this performs read-only live queries against `GET /{api_version}/act_{id}/targetingsearch` (or global `/search?type=adinterest`) and validates candidates via `GET /{api_version}/act_{id}/targetingvalidation`.
   - When credentials are missing or fail (`API_UNAVAILABLE`), report the exact failure category (`MISSING_TOKEN`, `AUTH_401`, `PERMISSION_403`, `RATE_LIMIT_429`, etc.) and next diagnostic step while keeping `verified_targeting_options` empty (`[]`). Never present `RELATED_UNVERIFIED` ideas as confirmed Meta interests!

2. **Step 2 — Build the 4-Layer Audience Architecture & Exclusion Matrix (`tools/meta-audience.py`):**
   ```bash
   python3 tools/meta-audience.py architect \
     --niche <niche> \
     --daily-budget <daily_budget> \
     --geo <country_or_city> \
     --currency <ISO_CURRENCY> \
     --aov <aov> --margin-pct <margin_pct> \
     --has-pixel --has-crm
   ```

3. **Step 3 — Present the 8-Part Targetologist Report:**
   1. **Business & Audience Understanding** (offer, problem solved, customer intent, market, objective).
   2. **Relevant Verified Interests, Ranked by Relevance** (`VERIFIED_AVAILABLE` first, then `FOUND_NOT_VALIDATED`, sorted by the 5-factor `relevance_score`, clearly labeled as Tyrion's estimate rather than a Meta score).
   3. **Validation Status & Official Meta IDs** (exact Meta `name`, `id`, `type`, `path`, `source_endpoint`, and `matched_queries` preserved verbatim; if only 2 relevant verified interests exist, return 2 — never invent extra interests).
   4. **Why Each Interest Fits the Offer** (`relevance_reason` & 5-factor breakdown).
   5. **Closely Related Alternatives, Clearly Separated by Verification Status** (`FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED` with replacement IDs, `excluded_low_relevance_options`, and `RELATED_UNVERIFIED` offline hypotheses).
   6. **Suggested Test Groups with Reason for Grouping** (`Group A: Core Product & Direct Intent`, `Group B: Problem & Complementary Context`, `Group C: Buyer Behavior / Solventnost Hypothesis` — 2–5 thematic options per group instead of stacking 15+ unrelated interests).
   7. **Broad-Targeting Alternatives Where Appropriate** (when Andromeda Broad `Geo + Age + Creative Hook` beats Detailed Targeting vs when Detailed Targeting test groups are warranted).
   8. **Missing Inputs, API Limitations & Next Steps**.
