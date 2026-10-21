---
name: report
description: "Executive client & operator performance report generator with MER, ROAS, CPA & next-sprint action plan (Alias: /hisobot)"
alias_of: hisobot
---

# `/report` (Alias: `/hisobot`)

Executive client & operator performance report generator with MER, ROAS, CPA & next-sprint action plan (Alias: /hisobot).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/client-workspace.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
