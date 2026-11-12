---
name: ask
description: "Universal natural-language paid media & targetology routing query across all agents, skills & wiki notes (Alias: /savol)"
alias_of: savol
---

# `/ask` (Alias: `/savol`)

Universal natural-language paid media & targetology routing query across all agents, skills & wiki notes (Alias: /savol).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Run the deterministic CLI tool:
   ```bash
   python3 tools/skill-search.py --help
   ```
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
