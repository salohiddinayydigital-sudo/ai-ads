---
disable-model-invocation: true
name: video-script
description: "Sales or organic video script with 6-column AV table and modular hooks (Alias: /video-ssenariy)"
alias_of: video-ssenariy
argument-hint: "<product/offer> [sales|organic] [15|30|45|60]"
---

# `/video-script` (Alias: `/video-ssenariy`)

Task: **$ARGUMENTS**

Same workflow as `/video-ssenariy` (canonical, Uzbek): Sales or organic video script with 6-column AV table and modular hooks. Reply in the user's language. Pre-production only: no editing/rendering pipeline changes.

## Execution Workflow
1. Detect user language (uz Latin/Cyrillic, ru, en) and market (`markets/<market>/pack.json`, default `global`). Ask only what is missing: product/offer, audience, goal, verified proof (never invent statistics, reviews, prices — use `[ADD VERIFIED ...]`).
2. Load `skills/video/SKILL.md` Intent Router and read only the matching reference.
3. Run the deterministic skeleton:
   ```bash
   python3 tools/creative-matrix.py video-script --mode <sales|organic> --lang <uz|ru|en> --duration 30 --hooks 3 --niche <niche> --product "<product>" --json
   ```
4. Fill the skeleton with the user's real data; self-audit with `skills/video/references/script-quality-rubric.md` (>= 85/100) before delivering.
