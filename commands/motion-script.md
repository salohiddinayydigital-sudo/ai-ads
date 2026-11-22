---
disable-model-invocation: true
name: motion-script
description: "Motion video script, scene-by-scene storyboard and design brief (no editing) (Alias: /motion-ssenariy)"
alias_of: motion-ssenariy
argument-hint: "<product/idea> [kinetic|ui|explainer|data|bumper] [15|30|45|60]"
---

# `/motion-script` (Alias: `/motion-ssenariy`)

Task: **$ARGUMENTS**

Same workflow as `/motion-ssenariy` (canonical, Uzbek): Motion video script, scene-by-scene storyboard and design brief (no editing). Reply in the user's language. Pre-production only: no editing/rendering pipeline changes.

## Execution Workflow
1. Detect user language (uz Latin/Cyrillic, ru, en) and market (`markets/<market>/pack.json`, default `global`). Ask only what is missing: product/offer, audience, goal, verified proof (never invent statistics, reviews, prices — use `[ADD VERIFIED ...]`).
2. Load `skills/video/SKILL.md` Intent Router and read only the matching reference.
3. Run the deterministic skeleton:
   ```bash
   python3 tools/creative-matrix.py video-script --mode motion --lang <uz|ru|en> --duration 30 --niche <niche> --product "<product>" --json
   ```
4. Fill the skeleton with the user's real data; self-audit with `skills/video/references/script-quality-rubric.md` (>= 85/100) before delivering.
