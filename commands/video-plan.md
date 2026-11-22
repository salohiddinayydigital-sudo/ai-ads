---
disable-model-invocation: true
name: video-plan
description: "Video content plan (weekly/monthly matrix) and batch shooting plan (Alias: /video-reja)"
alias_of: video-reja
argument-hint: "<business> [1|2|4 weeks]"
---

# `/video-plan` (Alias: `/video-reja`)

Task: **$ARGUMENTS**

Same workflow as `/video-reja` (canonical, Uzbek): Video content plan (weekly/monthly matrix) and batch shooting plan. Reply in the user's language. Pre-production only: no editing/rendering pipeline changes.

## Execution Workflow
1. Detect user language (uz Latin/Cyrillic, ru, en) and market (`markets/<market>/pack.json`, default `global`). Ask only what is missing: product/offer, audience, goal, verified proof (never invent statistics, reviews, prices — use `[ADD VERIFIED ...]`).
2. Load `skills/video/SKILL.md` Intent Router and read only the matching reference.
3. Run the deterministic skeleton:
   ```bash
   python3 tools/creative-matrix.py video-script --mode plan --lang <uz|ru|en> --weeks 2 --per-week 5 --niche <niche> --product "<business>" --json
   ```
4. Fill the skeleton with the user's real data; self-audit with `skills/video/references/script-quality-rubric.md` (>= 85/100) before delivering.
