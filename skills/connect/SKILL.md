---
name: connect
description: "Connect data sources: official Meta Ads MCP, Google Ads MCP, Graph API token, CSV or screenshot; detect available tools and snapshot raw data. Use for 'ulash', 'connect', 'mcp', 'meta ads mcp', подключить."
triggers:
- "connect"
- "ulash"
- "mcp"
- "meta ads mcp"
- "google ads mcp"
- "подключить"
- "источник данных"
aliases: []
domains:
- data-source
- mcp
platforms:
- meta
attached_agents:
- data-analyst
related_skills: []
references:
- "skills/connect/references/sources-priority.md"
- "skills/connect/references/meta-ads-mcp.md"
- "skills/connect/references/google-ads-mcp.md"
- "skills/connect/references/snapshot-pattern.md"
risk_level: medium
output_contract: "Structured deliverable with evidence labels and honest execution report"
---

## Ish tartibi

1. Sessiyadagi asboblarni nomi bo'yicha aniqla (`skills/connect/references/sources-priority.md`). Hech biri yo'q bo'lsa, foydalanuvchiga eng yaqin yo'lni ayt (CSV eksport eng tez).
2. Meta MCP uchun: `skills/connect/references/meta-ads-mcp.md`. Google uchun: `skills/connect/references/google-ads-mcp.md`. URL va flag'lar `unverified` ekanini ayt.
3. Faqat o'qish asboblarini chaqir; xom javobni snapshot qilib, `normalize.py` dan o'tkaz (`skills/connect/references/snapshot-pattern.md`).
4. Yozish asboblari (`ads_create_*`, `ads_update_entity`, `ads_activate_entity`, `ads_duplicate_entity`, `ads_delete_*`, `ads_creative_*`) — faqat tasdiqlangan change packet va rollback rejasi bilan.
5. Ulanish holatini `client-workspace.py state set` bilan `connectors` ga yoz.

## Manbalar

| Fayl | Mazmun |
|---|---|
| `skills/connect/references/sources-priority.md` | ustuvorlik va asbob aniqlash |
| `skills/connect/references/meta-ads-mcp.md` | rasmiy Meta Ads MCP, asboblar, yozish himoyasi |
| `skills/connect/references/google-ads-mcp.md` | Google Ads MCP |
| `skills/connect/references/snapshot-pattern.md` | MCP → snapshot → kod |
| `docs/integrations.md` | sozlash namunalari |
