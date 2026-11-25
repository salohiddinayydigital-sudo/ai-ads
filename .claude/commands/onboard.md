---
disable-model-invocation: true
description: Yangi mijozni qabul qilish — 8 parametrli target brif, Go/Fix-First/No-Go filtri, BM/Pixel/IG/TG ruxsatlar cheklisti va kickoff taklifi
argument-hint: <mijoz xabari yoki transkript> [intake_brief|readiness_filter|access_checklist|kickoff_proposal]
---

# /onboard — yangi mijozni qabul qilish (`client-onboarder`)

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/00-manba.md` + `rules/40-xavfsizlik-va-hisob.md` (parol/SMS kod hech qachon so'ralmaydi) + `rules/60-loyiha-papkasi.md`.
2. Agent: `agents/client-onboarder.md` — rejimni tanla (noaniq bo'lsa `intake_brief`).
3. O'qi: `skills/strategy/references/client-onboarding-framework.md`.

## Ijro

1. 8 biznes parametrini ajrat; yetishmaganlarini mijozga oddiy savollar sifatida yoz.
2. Break-even CPA: `python3 tools/calculator.py breakeven ...` (yoki `tyrion_media_calculator`).
3. Tayyorlik hukmi (Go / Fix-First / No-Go) + ruxsatlar cheklisti (`granted/pending/missing`).
4. Mijoz papkasi kerak bo'lsa: `python3 tools/client-workspace.py`.

## Natija

`client_onboarding_packet` (`schemas/agent-handoff.schema.json`) + Self-Audit (>= 85/100). Keyingi qadam: `strategist`, `tracking-specialist`, `/ad-spy`.
