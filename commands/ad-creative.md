---
name: ad-creative
description: "Generate high-converting ad creative, S/A-tier 9:16 video ad scripts (UGC, Founder, iMessage/ChatGPT Reveal, Greenscreen, Faceless Motion), Andromeda PDA diversity matrices, and platform-validated copy with zero AI tells (Aliases: /creative, /kreativ)"
argument-hint: "<product/offer> [--platform meta|google_rsa|tiktok|linkedin|telegram] [--format ugc_reaction_demo|founder_authority|imessage_reveal|greenscreen_proof]"
---

# `/ad-creative` — Performance Ad Creative & Video Ad Studio

Task: **$ARGUMENTS**

## Execution Workflow (Practitioner-First, Zero Coding Required)

1. **Check Workspace Context:** Read `.claude/product-marketing.md`, `.agents/product-marketing.md`, or client `BRIEF.md` if present, and detect user language + active market pack (`markets/<market>/pack.json`).
2. **Run the Deterministic Creative & Video Engines (`tools/creative-matrix.py`):**
   ```bash
   # 1. Andromeda Entity-ID & Persona-Desire-Awareness (PDA) Diversity Plan + 3x3 Matrix
   python3 tools/creative-matrix.py pda-matrix --niche <niche> --product "<offer>" --price <price> --market <market> --currency <ISO>

   # 2. Ready-to-Shoot 9:16 Video Ad Script & Storyboard (720x1200 safe zone, 3 hook variants)
   python3 tools/creative-matrix.py video-script --niche <niche> --product "<offer>" --problem "<pain_point>" --format <ugc_reaction_demo|founder_authority|imessage_reveal|chatgpt_reveal|greenscreen_proof|no_yapping_split_screen|faceless_motion_explainer> --language <lang>

   # 3. Platform-Validated Ad Copy Pack + Automatic No-AI-Tells Linter
   python3 tools/creative-matrix.py ad-copy --platform <meta|google_rsa|tiktok|linkedin|telegram> --product "<offer>" --problem "<pain_point>" --proof "<proof>" --language <lang>
   ```
3. **Deliver Structured Creative Package:**
   - **Andromeda Entity ID & PDA Matrix:** 8–12 visually distinct concepts across Personas, Desires, and Awareness Stages (so Meta Andromeda assigns separate retrieval tickets).
   - **9:16 Video Ad Scripts:** 3 opening hook options (`0-3s`) + scene-by-scene time-coded storyboard (`A-Roll`, `B-Roll`, `720x1200` safe-zone text, `Audio/VO`).
   - **Platform-Validated Ad Copy:** Character-counted headlines, primary text, and descriptions with **Zero AI Tells** and a **Falsifiable Test Hypothesis** for every concept.
