---
name: client
description: "Client workspace onboarding & 5-file campaign scaffolding (brief, unit economics, audience, creative, tracking) (Alias: /mijoz)"
alias_of: mijoz
---

# `/client` (Alias: `/mijoz`)

Client workspace onboarding & 5-file campaign scaffolding (brief, unit economics, audience, creative, tracking) (Alias: /mijoz).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/client-workspace.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
