---
name: funnel
description: "End-to-end conversion funnel architecture & leak diagnostics across E-Commerce, B2B SaaS, WhatsApp/Telegram/LINE & CRM (Alias: /voronka)"
alias_of: voronka
---

# `/funnel` (Alias: `/voronka`)

End-to-end conversion funnel architecture & leak diagnostics across E-Commerce, B2B SaaS, WhatsApp/Telegram/LINE & CRM (Alias: /voronka).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/calculator.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
