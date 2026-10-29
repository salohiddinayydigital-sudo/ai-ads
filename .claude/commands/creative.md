---
name: creative
description: "3x3 Creative Testing Matrix, Andromeda PDA diversity plan, 9:16 video ad scripts, multilingual 3-second hooks, BNPL price anchors & fatigue diagnostics (Aliases: /ad-creative, /kreativ)"
alias_of: kreativ
argument-hint: "<product/offer> [--niche ecom|edu|real-estate|medical|b2b|beauty|auto|local] [--price 100] [--market global|uz|eu|us]"
---

# `/creative` (Aliases: `/ad-creative`, `/kreativ`) — Creative Strategy, Video Scripts & Hook Studio

Task: **$ARGUMENTS**

## Execution Workflow (Never Stop at `--help`!)

1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Execute the deterministic creative, video-script, and hook engines:
   ```bash
   python3 tools/creative-matrix.py pda-matrix --niche <niche> --product "<product>" --price <price> --market <market> --currency <ISO>
   python3 tools/creative-matrix.py video-script --niche <niche> --product "<product>" --format ugc_reaction_demo --language <lang>
   python3 tools/creative-matrix.py hooks --niche <niche> --offer "<product>" --languages <lang>
   ```
3. Synthesize the 3x3 Angle x Format matrix, Andromeda PDA diversity plan, time-coded 9:16 video script, character-validated copy, and falsifiable test hypotheses in the user's language.
