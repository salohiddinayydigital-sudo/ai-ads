---
name: lead-quality-uz-2
description: lead-quality (uz-latn)
tags: [lang:uz-latn, topic:lead-quality]
runs: 2
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Bash]
---
tests/fixtures/crm/leads.csv va stage_map.json bilan crm-bridge dry-run qilib, lead→qualified hisobotini ko'rsat. PII chiqarma.
