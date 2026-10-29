---
name: reels-scripting
description: "Write high-converting, ready-to-shoot 9:16 short-form video scripts for Instagram Reels, TikTok, YouTube Shorts, and Meta Video Ads (UGC, Founder Authority, iMessage/ChatGPT Reveal, Greenscreen, No-Yapping Split-Screen, Problem-Solution, and Reference Reel Adaptation) in Uzbek, Russian, English, or any BCP 47 language. Works out-of-the-box with zero external API keys required."
triggers:
- reels skript
- reels ssenariy
- tiktok skript
- shorts skript
- 3 soniyalik hook
- сценарий рилс
- рилс сценарий
- видео скрипт
- video ssenariy
- ugc skript
- script a reel
- reels scripting
- turn this into a reel
aliases:
- reels-script
- short-form-script
- ugc-script
- video-ad-script
domains:
- creative
- video
- copywriting
platforms:
- instagram
- meta
- tiktok
- youtube
attached_agents: [reels-scriptwriter]
related_skills:
- ad-creative
- ads-creative
- video-editing
- social
references:
- skills/ad-creative/references/video-ad-scripts-and-specs.md
- skills/ad-creative/references/meta-creative-formats.md
risk_level: low
output_contract: Complete Time-Coded 9:16 Video Script (3 Visual/Verbal Hook Options, Scene-by-Scene A-Roll/B-Roll Table, 720x1200 Safe-Zone Text Overlays, Audio/SFX Cues & Falsifiable Test Hypothesis)
---

# 🎬 Reels, TikTok & Meta Video Ad Scripting Engine (`reels-scripting`)

Generate ready-to-shoot, high-retention `9:16` vertical video scripts for **paid Meta/TikTok/YouTube video ads** and **organic Reels/Shorts** — immediately and with **zero mandatory external API keys** (`APIFY_API_TOKEN` is never required).

## 1. Deterministic Video Script Generation (`tools/creative-matrix.py video-script`)

Always run the built-in zero-token video script generator first to scaffold the time-coded storyboard, 3-second hook variants, `720x1200` safe-zone overlays, and BNPL/offer anchors:

```bash
python3 tools/creative-matrix.py video-script \
  --niche <ecom|edu|real-estate|medical|b2b|beauty|auto|local> \
  --product "<product_or_offer>" \
  --problem "<main_customer_pain>" \
  --format <ugc_reaction_demo|founder_authority|imessage_reveal|chatgpt_reveal|greenscreen_proof|no_yapping_split_screen|faceless_motion_explainer> \
  --duration <15|30|45> \
  --price <price> \
  --market <uz|global|eu|us|mena|latam|sea|in> \
  --language <uz_latin|uz_cyrillic|ru|en>
```

## 2. Supported Video Ad & Reels Formats (2026 S/A-Tier)

1. **`ugc_reaction_demo` (S-Tier UGC Reaction + Hard-Cut Demo):**
   - `0–3s`: Visceral problem/reaction hook + bold `720x1200` text overlay.
   - `3–12s`: Immediate hard cut to hands-on product/service demonstration (no intro rambling).
   - `12–22s`: Quantified result + objection crusher (guarantee / installment anchor).
   - `22–30s`: Direct CTA with concrete next step.
2. **`founder_authority` (S-Tier Founder / Doctor / Expert Direct-to-Camera):**
   - `0–3s`: Counter-intuitive industry truth or costly mistake 90% of buyers make.
   - `3–15s`: Transparent mechanism breakdown with B-roll proof overlays every `2s`.
   - `15–25s`: Real client case study + risk-reversal guarantee.
   - `25–30s`: Low-friction consultation/order CTA.
3. **`imessage_reveal` / `chatgpt_reveal` (A-Tier iOS-Native Screen Reveal):**
   - `0–3s`: Notification / screenshot hook (*"Did you see what they quoted me?!"* or typed prompt).
   - `3–15s`: Bubble-by-bubble message thread or streaming answer revealing the hidden gem solution.
   - `15–25s`: Quick cut to real product/clinic/platform proof + offer code/anchor.
4. **`greenscreen_proof` (A-Tier Greenscreen Comment / Price Breakdown):**
   - Creator points to a real customer comment, competitor comparison table, or contract/pricing sheet behind them while walking through the proof.
5. **`no_yapping_split_screen` (S-Tier Split-Screen Fast Demo):**
   - Top 50% of `9:16` frame shows continuous uninterrupted visual demo; bottom 50% shows rapid-fire proof callouts.
6. **`faceless_motion_explainer` (A-Tier Faceless Motion / B-Roll + Voiceover):**
   - Designed for teams who do not want to appear on camera: dynamic B-roll / motion graphics + word-timed captions + energetic TTS/voiceover.

## 3. Mandatory Output Structure for Every Script

For every video request, deliver:
1. **3 Distinct 0–3s Hook Variations** (Curiosity/Truth, Pain/Mistake, Quantified Proof/Filter) — each with **Visual Action**, **On-Screen Safe-Zone Text (`<=7 words`)**, and **Spoken Line**.
2. **Time-Coded Scene-by-Scene Production Table (`00:00` to `00:30`):**
   - `Timecode` | `Visual / Camera / B-Roll` | `On-Screen Text (720x1200 Safe Zone)` | `Spoken Audio / VO (Native Language)`
3. **Production & Editing Notes:** `0.5-1.5s` cut cadence, lighting/props checklist, `-14 LUFS` audio rule, and Falsifiable Test Hypothesis.
