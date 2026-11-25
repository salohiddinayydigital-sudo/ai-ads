---
disable-model-invocation: true
description: Ads Manager launch blueprint — CBO/ABO, Andromeda konsolidatsiyasi, naming convention, UTM, 20 bandli pre-launch va 72 soatlik learning qoidalari
argument-hint: <platforma, kunlik byudjet, maqsadli CPA, offer> [meta_structure|telegram_tiktok_google_launch|naming_and_utm|prelaunch_gate_72h]
---

# /launch-plan — kampaniya arxitekturasi (`campaign-launcher`)

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/40-xavfsizlik-va-hisob.md` (jonli yaratish yo'q, Spend-Guard) + `rules/00-manba.md`.
2. Agent: `agents/campaign-launcher.md`; o'qi: `skills/strategy/references/ads-launch.md`, `skills/budget/references/daily-triage-kill-scale.md`.

## Ijro

1. Byudjet ↔ ad set soni: har ad set >= maqsadli CPA × 1.5–2 (`python3 tools/calculator.py meta-155 ...`).
2. CBO/ABO, placements, optimizatsiya hodisasi, exclusion'lar; naming `YYYY-MM_GEO_OBJ_AUD_OFFER_V1` + UTM jadvali.
3. 20 bandli pre-launch checklist + 72 soat "tegmaslik" qoidalari.
4. Jonli o'zgarish kerak bo'lsa: `python3 tools/spend-guard.py` draft + foydalanuvchi tasdig'i.

## Natija

`launch_blueprint_packet` + Self-Audit (Pass/Fail). Keyingi qadam: `compliance-reviewer` (policy), `/morning-triage` (launchdan keyin).
