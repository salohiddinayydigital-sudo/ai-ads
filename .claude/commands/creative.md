---
name: creative
description: "3x3 Creative Testing Matrix, multilingual 3-second hooks (any BCP 47 language), BNPL price anchors & fatigue diagnostics (Alias: /kreativ)"
alias_of: kreativ
---

# `/creative` (Alias: `/kreativ`)

3x3 Creative Testing Matrix, multilingual 3-second hooks (any BCP 47 language), BNPL price anchors & fatigue diagnostics (Alias: /kreativ).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/creative-matrix.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
