---
name: pulse
description: "Daily account watch from metrics.v1: pacing, CPA/ROAS drift, fatigue, tracking breaks, spend spikes. Report only, never acts. Use for 'pulse', 'kunlik tekshiruv', 'monitoring', 'ogohlantirish', мониторинг."
triggers:
- "pulse"
- "kunlik tekshiruv"
- "monitoring"
- "ogohlantirish"
- "мониторинг"
- "anomaly"
aliases: []
domains:
- monitoring
platforms:
- meta
attached_agents:
- data-analyst
related_skills: []
references: []
risk_level: medium
output_contract: "Structured deliverable with evidence labels and honest execution report"
---

# pulse

Daily account watch from metrics.v1: pacing, CPA/ROAS drift, fatigue, tracking breaks, spend spikes. Report only, never acts. Use for 'pulse', 'kunlik tekshiruv', 'monitoring', 'ogohlantirish', мониторинг.

## Qoidalar
Pulse hech narsani bajarmaydi; har topilma `needs_approval` bilan keladi. Standart chegaralar HEURISTIC_PRIOR_MODEL.
