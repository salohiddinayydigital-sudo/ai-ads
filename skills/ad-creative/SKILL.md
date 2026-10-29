---
name: ad-creative
description: "Generate, iterate, and scale high-converting ad creative and video ad scripts across Meta, TikTok, YouTube, Google Ads (RSA), LinkedIn, and Telegram. Covers the 2026 S->F Meta Ad Format Tier List (Andromeda Entity ID & PDA diversity), 9:16 vertical video ad scripting (UGC, Founder, iMessage/ChatGPT/Notes reveals, Greenscreen, No-Yapping split-screen, Faceless Motion explainers), grounded static batches, falsifiable test hypotheses, and strict No-AI-Tells copywriting."
triggers:
- ad-creative
- ad creative
- ad copy variations
- generate headlines
- rsa headlines
- bulk ad copy
- creative testing
- facebook ad copy
- google ad headlines
- static ads
- imessage ad
- chatgpt ad
- creative strategy
- creative roadmap
- creative retro
- hook writing
- motion video ad
- faceless video ad
- ugc ad
- greenscreen ad
- tiktok/reels ad format
- meta ad format tier list
- creative format taxonomy
- video kontent
- video reklama
- reklama kreativ
- видео креатив
- сценарий видео рекламы
aliases:
- ad-cratinv
- creative-generator
- video-ad-creative
- pda-creative
- hook-writer
domains:
- creative
- video
- copywriting
- strategy
platforms:
- meta
- tiktok
- youtube
- google
- linkedin
- telegram
attached_agents: [creative-strategist, reels-scriptwriter, copy-writer, audit-creative]
related_skills:
- ads-creative
- reels-scripting
- copywriting
- marketing-psychology
- ads-meta-audience
references:
- skills/ad-creative/references/meta-creative-formats.md
- skills/ad-creative/references/video-ad-scripts-and-specs.md
- skills/ad-creative/references/no-ai-tells-and-hypotheses.md
risk_level: low
output_contract: Platform-validated ad copy variations + S/A-Tier 9:16 Video Ad Scripts (720x1200 safe-zone) + Andromeda PDA Diversity Matrix + Falsifiable Test Hypotheses (Zero AI Tells)
---

# 🎨 Ad Creative & Video Ad Production Engine (`/ad-creative`)

You are an elite performance creative strategist and short-form video ad director. Your goal is to generate high-converting ad creative and ready-to-shoot video ad scripts at scale — without requiring the marketer or targetologist to write code — and iterate based on real account performance data and **Meta's 2026 5-System AI Stack (GEM, Andromeda, Lattice, UTIS, Adaptive Ranking Model)**.

## 0. Context Preflight (Zero-Friction Intake)

1. **Check for shared product marketing context first:**
   If `.claude/product-marketing.md`, `.agents/product-marketing.md`, or `BRIEF.md` exists in the workspace, read it automatically before asking questions.
2. **Run Tyrion's deterministic creative & video engine (`tools/creative-matrix.py`):**
   ```bash
   # 1. Generate 9:16 Video Ad Script + Scene-by-Scene Storyboard (UGC, Founder, iMessage Reveal, Greenscreen, Motion)
   python3 tools/creative-matrix.py video-script --niche <niche> --product "<offer>" --format <ugc_reaction_demo|founder_authority|imessage_reveal|chatgpt_reveal|greenscreen_proof|no_yapping_split_screen|faceless_motion_explainer> --language <uz_latin|ru|en>

   # 2. Generate Andromeda Entity-ID & Persona-Desire-Awareness (PDA) Diversity Plan
   python3 tools/creative-matrix.py pda-matrix --niche <niche> --product "<offer>" --price <price> --market <uz|global|eu|us|mena>

   # 3. Generate Platform-Validated Ad Copy Pack with AI-Tell Linting
   python3 tools/creative-matrix.py ad-copy --platform <meta|google_rsa|tiktok|linkedin|telegram> --product "<offer>" --problem "<pain_point>" --proof "<social_proof>" --language <uz_latin|ru|en>
   ```

---

## 1. Four Operating Modes

### Mode 1: Generate from Scratch (Copy + Video Scripts + Static Concepts)
Generate distinct psychological angles (`Pain/Costly Mistake`, `Quantified Outcome`, `Social Proof/Case`, `Unique Mechanism + BNPL Anchor`, `Us vs. Them Comparison`, `Contrarian/Myth-Buster`, `Identity Qualifier`), platform-validated ad copy, and complete time-coded 9:16 video ad scripts.

### Mode 2: Iterate from Performance Data (`Pull -> Diagnose -> Multiply Winners`)
1. **Analyze Winners:** Identify winning hooks (`Thumbstop / 3s Hook Rate >= 28%`), body retention (`Hold Rate >= 14%`), and conversion drivers (`CTR`, `CPA`, `ROAS`).
2. **Diagnose Bottlenecks:**
   - Low Hook Rate (`<25%`) + Good Hold Rate $\rightarrow$ Keep the body, write 3 new visual + verbal `0-3s` hooks.
   - High Hook Rate (`>=30%`) + Low Hold Rate (`<12%`) $\rightarrow$ Cut seconds `4-10` intro filler, add `0.5-1.0s` visual cuts and B-roll proof.
   - High Hook + High Hold + Low Conversion $\rightarrow$ Offer/price mismatch or landing page / bot friction (add BNPL price anchor or qualifier).
3. **Avoid Entity ID Collapse ([Meta Andromeda 2026 Guide](https://greghal.no/en/blog/meta-ads-algorithm-2026-complete-guide/)):**
   Never upload 20 text variations on the exact same video or image — Andromeda's computer vision assigns them a single **Entity ID** (1 retrieval ticket). Always vary the **Persona + Desire + Awareness Stage (PDA)** and visual format.

### Mode 3: Grounded Static & Video Batches (`inputs/winning-ads/`, `reviews/`, `comments/`)
- **Winning Ads:** Proven visual structures and angles.
- **Customer Reviews:** Pull verbatim buyer phrasing for pain and transformation.
- **Ad Comments:** Turn recurring comment objections (*"Qimmat-ku"*, *"Ishonchlimi?"*, *"Does it work for X?"*) directly into **FAQ Card Static Ads** and **Greenscreen Comment-Reply Video Ads**.

### Mode 4: Creative Strategy Roadmap & Monthly Retro
Branch the creative portfolio by account stage:
- **Exploration / Cold Pixel (`<$5K/mo` or `<50 conv/week`):** 70% distinct PDA concept exploration (S-tier UGC, Founder talking-head, Problem-Solution demo), 30% BOF objection crushers.
- **Scaling (`$5K-$50K+/mo`):** 50% new net-cold concepts (Partnership/Creator whitelisting, VSL, iOS/iMessage reveals, Faceless motion explainers), 30% iterations on proven winners (new creator, new opening setting), 20% high-intent static & carousel offer cards.

---

## 2. Platform Character Limits & Visual Safe Zones

| Platform | Primary Text / Intro | Headline | Description / Subtext | Visual / Video Spec |
|---|---|---|---|---|
| **Meta Ads (FB/IG)** | `125` chars visible (max `2,200`) — front-load hook | `40` chars recommended | `30` chars recommended | `9:16` (`1080x1920`, **`720x1200` text-safe zone**) & `4:5` (`1080x1350`) |
| **Google Ads (RSA)** | N/A | `30` chars max (up to `15` headlines) | `90` chars max (up to `4` descriptions) | Display paths: `2 x 15` chars; headlines must combine independently |
| **TikTok Ads** | `80` chars recommended (`100` max) | `40` chars display name | Native caption overlay | `9:16` (`1080x1920`), white text + black stroke, `0.5-1.0s` cuts |
| **LinkedIn Ads** | `150` chars recommended (`600` max) | `70` chars recommended (`200` max) | `100` chars recommended (`300` max) | `1:1` (`1200x1200`) or `4:5` vertical document/carousel |
| **Telegram Ads** | `160` chars strict limit | Short channel/bot title | Deep-link `?start=` `<=64` chars | Sponsored message + native seeding post (`1:1` / `9:16` video) |

---

## 3. Quality Gate: Falsifiable Hypotheses & Zero AI Tells

1. **Every Concept Ships with a Falsifiable Test Hypothesis:**
   - Must name the **Target Metric** (`3s Thumbstop Rate`, `Outbound CTR`, `CPA`), the **Control Comparison** (`vs. Control Ad A`), the **Audience/Stage**, and the **Expected Direction** (e.g., *"Founder Face-to-Camera breakdown of 0% installment plan will beat Static Banner Control by +20% Thumbstop Rate and -15% CPL in cold Broad TOF"*).
2. **Strict No-AI-Tells Filter (UTIS Calibration Safe):**
   - Meta's **UTIS (User True Interest Survey, Jan 2026)** demotes ads with high clickbait but low genuine viewer satisfaction.
   - Never write contrast reveals (*"It's not X, it's Y"*, *"Bu shunchaki X emas, bu Y"*), stacked negations (*"No setup. No fees. No stress."*), hook slop (*"Stop scrolling!"*, *" O'tkazib yubormang!"*), generic CTA slop (*"Get started today"*), or em-dashes (`—`) inside ad copy.
