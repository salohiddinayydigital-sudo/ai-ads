---
name: competitors
description: "Competitor Ad Library teardown, offer positioning matrix & counter-hook generation (Alias: /raqobatchi)"
alias_of: raqobatchi
---

# `/competitors` (Alias: `/raqobatchi`)

Competitor Ad Library teardown, offer positioning matrix & counter-hook generation (Alias: /raqobatchi).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/creative-matrix.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
