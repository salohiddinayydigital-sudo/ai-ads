---
name: audience
description: "Meta Ads & multi-platform audience architecture, 6-status live interest verification, overlap & saturation analysis (Alias: /auditoriya)"
alias_of: auditoriya
---

# `/audience` (Alias: `/auditoriya`)

Meta Ads & multi-platform audience architecture, 6-status live interest verification, overlap & saturation analysis (Alias: /auditoriya).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/meta-audience.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
