---
disable-model-invocation: true
name: ask
description: "Universal natural-language paid media & targetology routing query across all agents, skills & wiki notes (Alias: /savol)"
alias_of: savol
---

# `/ask` (Alias: `/savol`)

Universal natural-language paid media & targetology routing query across all agents, skills & wiki notes (Alias: /savol).

## Execution Workflow
1. Detect user language and active market pack (`markets/<market>/pack.json`, default `global`).
2. Route with the single canonical system (the `tyrion` skill owns execution; do not pick agents or skills manually):
   ```bash
   python3 tools/skill-search.py route "$ARGUMENTS" --context-mode manifest --json
   ```
   Then follow `skills/tyrion/references/conductor-v7.md` (read selected skills in full, delegate or run the labelled fallback, validate, synthesize).
3. Synthesize findings in the user's language with currency-accurate metrics and source citations.
