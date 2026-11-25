---
disable-model-invocation: true
description: Ertalabki 5 daqiqalik media-buyer triage — har ad set/ad uchun KILL/HOLD/ITERATE/SCALE, CPL sakrashi tashxisi (CPM x CTR x CVR), xavfsiz masshtab
argument-hint: <eksport yoki 1/3/7 kunlik raqamlar> [morning_triage|cpl_spike_diagnosis|fatigue_rotation|safe_scale_plan]
---

# /morning-triage — kunlik qaror jadvali (`daily-optimizer`)

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/00-manba.md` (raqam faqat asbobdan) + `rules/40-xavfsizlik-va-hisob.md` (> +20% yoki pauza → Spend-Guard).
2. Agent: `agents/daily-optimizer.md`; o'qi: `skills/budget/references/daily-triage-kill-scale.md`.

## Ijro

1. Raqamlar: `python3 tools/normalize.py` → `python3 tools/pulse.py` (yoki MCP snapshot).
2. Har entity: spend vs minimal chegara (< 1.5 × maqsadli CPA → HOLD), keyin daraxt bo'yicha qaror.
3. Hisob: `python3 tools/calculator.py` / `tyrion_breakdown_effect` (segment kesishdan oldin).
4. Harakat chiptalari: `python3 tools/spend-guard.py` draft; jonli o'zgarish faqat tasdiqdan keyin.

## Natija

`daily_triage_packet` + Self-Audit (Pass/Fail). Yo'naltirish: CTR ↓ → `creative-strategist`; CVR ↓ → `/cro-dm`; mijozga → `/client-update`.
