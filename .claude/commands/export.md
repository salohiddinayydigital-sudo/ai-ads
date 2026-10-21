---
name: export
description: "CSV/JSON ad account export analyzer — wasted spend detection, marginal CPA breakdown & scale/kill verdicts (Alias: /eksport)"
alias_of: eksport
---

# `/export` (Alias: `/eksport`)

CSV/JSON ad account export analyzer — wasted spend detection, marginal CPA breakdown & scale/kill verdicts (Alias: /eksport).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/ad-export-analyzer.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
