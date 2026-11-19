# Meta's 2026 Five-System AI Ad Stack (GEM, Andromeda, Lattice, UTIS & Adaptive Ranking)

- **Verified Date:** `2026-10-29`
- **Primary Sources:**
  - [How Meta's Ads Algorithm Works in 2026: Lattice, UTIS & Andromeda Explained](https://greghal.no/en/blog/meta-ads-algorithm-2026-complete-guide/)
  - [Meta's Advantage+ Audience: 2026 Guide | Linear Design](https://lineardesign.com/blog/metas-advantage-audience/)
  - [Meta Andromeda: What Changed for Ecommerce Ads | StoreHero](https://storehero.ai/metas-andromeda-update-explained-what-it-means-for-businesses/)

## 1. The Teacher-Student Five-System Hierarchy (`~200–300ms` per impression)

| System | Role in Delivery | Rollout & Compute Milestone | Reported Impact |
|---|---|---|---|
| **1. GEM (Generative Ads Recommendation Model)** | LLM-scale **Teacher Foundation Model** using stackable factorization machines + cross-layer attention across organic and paid content on all surfaces; teaches Lattice and Andromeda via knowledge distillation. | Engineering paper Nov 2025; GPU training allocation doubled in Q4 2025. | ~4x efficiency vs prior ranking models; +5% conversions on Reels, +3.5% clicks on Facebook. |
| **2. Andromeda** | **Early-Stage Retrieval Engine** on NVIDIA Grace Hopper & MTIA; narrows tens of millions of ads to ~1,000–1,500 candidates per impression using computer vision and semantic creative analysis. | Global rollout completed Oct 2025; 3x compute efficiency upgrade Jan 2026. | 10,000x model complexity; +6% recall, +8% ads quality. |
| **3. Lattice** | **Unified Cross-Surface & Cross-Objective Ranking** with **Sequence Learning** (models user's action sequence before/after ads), **Lattice Zipper** (freshness vs attribution), and **Lattice Filter**. | Rolled out through 2025; Q1 2026 landing-page-view upgrade. | +12% ad quality, up to +6% conversions (+6% LPV CVR in Q1 2026). |
| **4. UTIS (User True Interest Survey)** | **Interest-Match Calibrator** trained on daily in-feed Facebook Reels 1–5 satisfaction surveys to fix the 48.3% precision ceiling of raw watch-time/click heuristics. | Published Jan 14, 2026; integrated into Late Stage Ranking & early retrieval. | Demotes clickbait/hook-slop that gets clicks without genuine viewer interest. |
| **5. Adaptive Ranking Model** | **Runtime Infrastructure Layer** using selective FP8 quantization, multi-card GPU sharding, and request-centric user signal computation. | Launched on Instagram Q4 2025; expanding across surfaces in 2026 (published Mar 31, 2026). | Trillion-parameter inference in `<100ms`; +3% conversions and +5% CTR on Instagram. |

## 2. Operational Rules for Media Buyers & Targetologists in 2026

1. **Entity ID Clustering (Why Minor Variations Fail):**
   - Andromeda's computer vision assigns a single **Entity ID** (and **1 retrieval ticket**) to visually similar ads. Launching 20 headline/hook text variations on the same video or resizing `1:1`/`4:5`/`9:16` gives only 1 ticket.
   - To earn independent retrieval tickets, vary the **Persona-Desire-Awareness (PDA)** angle, visual format (`UGC Reaction+Demo`, `Founder Authority`, `iMessage/ChatGPT Reveal`, `Greenscreen`, `Static Us-vs-Them`), or run **Partnership Ads (creator whitelisting)**.
2. **Value Rules (`+200%` to `-90%` Bid Multipliers):**
   - Instead of fragmenting budget across 5 separate geo/age ad sets (which causes `Learning Limited`), use **Value Rules** (up to 10 rules / 2 criteria per campaign, prerequisite $\ge 50$ purchases/7d) to bid higher on high-LTV cohorts inside a consolidated campaign.
3. **Advantage+ Sales Campaigns (`smart_promotion_type=GUIDED_CREATION`):**
   - Legacy `AUTOMATED_SHOPPING_ADS` creation was deprecated in Marketing API `v25.0` (Q1 2026). ASC supports up to 150 creatives (sweet spot: 20–50 distinct concepts).
4. **Meta AI Chat Signal (Dec 16, 2025 Rollout & Regional Carve-Outs):**
   - Interactions with Meta AI across FB, IG, WhatsApp, Messenger, and Ray-Ban glasses feed into Andromeda/Lattice/GEM — **except in the EU/EEA, UK, and South Korea** (exempt under GDPR/PIPA) and excluding sensitive topics (health, religion, politics).
