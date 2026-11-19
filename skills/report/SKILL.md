---
name: report
description: "Client and operator performance reports from tool output: results, decisions, next steps with owner and metric. Use for 'hisobot', 'report', 'natijalar', 'haftalik hisobot', отчет клиенту."
triggers:
- "hisobot"
- "haftalik hisobot"
- "oylik hisobot"
- "client report"
- "executive summary"
- "отчет для клиента"
- "еженедельный отчет"
- "ҳисобот"
aliases:
- "weekly-report"
- "monthly-report"
- "client-report"
- "ads-report"
domains:
- "reporting"
- "analytics"
platforms:
- "multi-platform"
attached_agents: [data-analyst, release-verifier]
related_skills: []
references:
- "skills/report/references/ads-report.md"
risk_level: low
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

# report

Client and operator performance reports from tool output: results, decisions, next steps with owner and metric. Use for 'hisobot', 'report', 'natijalar', 'haftalik hisobot', отчет клиенту.

## Qoidalar
Hisobot raqamlari asbob chiqishidan; keyingi qadamlarda egasi va metrikasi ko'rsatiladi.

## Manbalar (v7.1 dan ko'chirilgan to'liq matnlar)

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Eski skill | Fayl | Qachon |
|---|---|---|
| `ads-report` | `skills/report/references/ads-report.md` | Render Markdown, HTML, or PDF paid-advertising reports from a validated Claude Ads JSON run bundle. Use for ads report, client report, audit PDF, exec… |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
