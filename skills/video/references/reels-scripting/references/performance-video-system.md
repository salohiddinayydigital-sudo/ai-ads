# Performance Video System: research -> concept -> brief -> test -> diagnose -> iterate

Used by the `video_script`, `creative_improve` and `meta_strategy` workflows. Complements the format library in `skills/creative/references/ad-creative/` and the generator `tools/creative-matrix.py`. The generator is a scaffold: it produces structure and placeholders; strategy, proof and claims must come from real client information.

## 1. Research inputs (label each)

Product/service and offer; target audience and awareness stage (unaware, problem-aware, solution-aware, product-aware, most-aware); main problem; desires; objections; unique mechanism; competitors; existing winners and past performance data; reviews/testimonials actually provided; available visual assets (footage, location, product, people, licenses).

Competitor ads: analyze only ads actually seen (user-pasted, screenshots, Meta Ad Library results from a tool that really ran). For each: hook, offer, angle, structure, visual approach, main message, CTA, audience clues. If not accessible, say "not inspected" and do not infer. Extract the strategic insight (e.g. which objection they ignore); never copy scripts, lines or distinctive visuals.

## 2. Concept diversity

Concepts must differ in at least two of: avatar, problem, desire, awareness stage, angle, offer presentation, storytelling structure, visual approach, proof mechanism, CTA. A different caption, voice or crop of the same video is not a new concept (same Andromeda entity cluster).

Format selection (choose what fits, do not force all):

| Format | Fits when | Needs |
|---|---|---|
| UGC / customer testimonial | trust and relatability matter; real customers available | real customer, consent, real result |
| Founder / expert authority | high consideration, expertise sells | credible person on camera |
| Problem-solution demo | visible transformation, product/service demonstrable | footage of the real thing |
| Comparison | clear differentiators vs known alternatives | verifiable comparison facts |
| Objection handling | specific recurring objection (price, trust, safety) | real objection from sales/comments |
| Storytelling | emotional or process-heavy offers | genuine story |
| Educational | complex service, cold audience | simple teachable insight |
| Social proof | strong reviews/results exist | verified proof |
| Screen recording / comment reply | digital product, DM/Telegram funnel, FAQ | real screens/comments |
| Faceless / motion graphics | no talent available, explainers | script + stock/animation rights |
| Offer-focused | warm audience, time-bound real offer | a real offer and date |

## 3. Script package (what every concept delivers)

**A. Strategic brief**: audience, funnel stage, awareness stage, angle, objective (what action), strategic reasoning, test hypothesis (single variable, success metric, decision rule).

**B. Hooks (>= 3, materially different)**, each with: first visual frame, on-screen text, spoken line, camera direction, psychological purpose. No generic openers ("Stop scrolling"). Vary the mechanism: call-out of a specific person, concrete problem moment, counter-intuitive claim you can prove, objection reversal, result-first (only with verified result), curiosity with a payoff delivered in the body.

**C. Storyboard (time-coded table)** with columns: `time | duration | visual | camera angle | presenter action | A-roll | B-roll | voice-over | on-screen text | sound/SFX | transition | CTA`. Beat structures by length:

| Length | Beats |
|---|---|
| 15 s | 0-3 hook, 3-9 problem to solution/proof in one idea, 9-13 proof or offer, 13-15 CTA |
| 30 s | 0-3 hook, 3-10 problem, 10-20 mechanism/demo, 20-26 proof, 26-30 offer + CTA |
| 45 s | 0-3 hook, 3-12 story/problem, 12-27 mechanism and demo, 27-37 proof and objection, 37-45 offer, CTA, risk reversal (only if real) |

**D. Editing instructions**: pacing (cut rhythm per section), transitions, subtitles (burned-in, readable, inside safe zones), typography and hierarchy, sound design (music level under voice, SFX at key beats), B-roll selection, proof placement (earliest believable moment), CTA presentation (visual + spoken). Technical specs (aspect ratio, resolution, safe zones, length limits, file size/format): verify against Meta's current creative documentation before delivery; the repo default for vertical placements is 9:16 with a central text-safe area (generator uses 1080x1920 canvas and a 720x1200 safe box).

**E. Ad copy package**: primary text variants (short and long), headlines, descriptions, CTA button, campaign objective, and landing page / lead-form message match (the first screen repeats the promise made in the hook). Every claim traces to client-provided information; otherwise `[ADD VERIFIED ...]`.

## 4. Claim safety

`creative-matrix.py` output includes `claim_safety`. It flags percentages, time-frame promises, ratios, guarantees and superlatives that are not marked as placeholders. Treat `needs_verification: true` as a blocker until each flagged item is either backed by a client-provided source or removed. Never ship a hook containing an invented statistic. Testimonials: real, consented, unaltered.

## 5. Test and iterate

Loop: research -> concept -> production brief -> test -> measure -> diagnose -> iterate -> scale.

Measure along the funnel: hook rate (3-second plays / impressions), hold/retention, watch time, engagement quality (saves/shares/comments vs reactions), outbound CTR, landing-page conversion, lead quality (CRM qualified rate), CPA, ROAS, sales feedback. Compare against the account's own baseline; if none exists, collect it first.

```bash
python3 tools/creative-matrix.py iterate --hook-rate 31 --baseline-hook-rate 27 \
  --hold-rate 8 --baseline-hold-rate 14 --outbound-ctr 0.6 --cpa 12 --breakeven-cpa 9 --impressions 5000 --json
```
Output is ordered diagnostic hypotheses (attention, retention, click, landing, lead quality), the single priority fix, what to change next and what to keep constant, plus warnings (small sample, priors used).

| Pattern | Hypothesis to test (not a conclusion) | Next iteration |
|---|---|---|
| Low hook rate | first frame/opening does not stop the right person | new 0-3 s only; keep body, offer, CTA |
| Good hook, weak hold | body pacing/storytelling or promise-delivery gap | restructure body; keep hook |
| Good hold, weak outbound CTR | CTA, offer clarity or proof placement | CTA/offer/proof; keep hook and body |
| Good CTR, weak landing conversion | message mismatch, offer, page speed, form friction | change the page/form, not the creative |
| Cheap leads, poor sales | qualification, audience relevance, sales handling | add qualifiers in creative/form, CRM feedback, check call handling |
| CPA above break-even despite healthy upstream metrics | economics or offer problem | revisit price/offer/margin before more creative |

Rules: one variable per test; define the decision rule before launch; do not call a winner before the minimum sample from the economics step; scale a winner by new variants of the *winning concept* (new creator, new setting, new hook) rather than resizing it; retire fatigued creatives with new concepts, not re-edits.
