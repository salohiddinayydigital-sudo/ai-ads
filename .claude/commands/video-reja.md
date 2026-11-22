---
disable-model-invocation: true
description: Video kontent reja (haftalik/oylik matritsa) va syomka kuni rejasi
argument-hint: <biznes> [1|2|4 hafta]
---

# /video-reja — video kontent reja va syomka kuni

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/00-manba.md` + `rules/30-ozbekiston-konteksti.md`.
2. O'qi: `skills/video/references/video-content-planning.md`.
3. Mijoz konteksti: `journal/<mijoz>.md` (bo'lsa).

## Ijro

1. **Kirish** (`content-planner`): maqsad, platformalar, haftasiga nechta video tushiriladi, kim kameraga chiqadi, haqiqiy mijoz savollari. Mavzu to'qilmaydi — `USER_PROVIDED` yoki `ASSUMPTION`.
2. **Skelet:**
   ```bash
   python3 tools/creative-matrix.py video-script --mode plan --lang uz --weeks 2 --per-week 5 --niche <niche> --product "<biznes>" --json
   ```
3. **Reja:** pillar'lar → funnel balansi (~50/30/20, `HEURISTIC_PRIOR_MODEL`) → kontent matritsasi → Batch Shooting Plan (lokatsiya, kiyim, yorug'lik, B-roll).
4. **Handoff:** tanlangan mavzular → `video-producer` (`/video-ssenariy`).

## Natija

`outputs/<mijoz>/<sana>-video-reja.md`: matritsa · syomka kuni rejasi · tushiriladigan ssenariylar ro'yxati · taxminlar.
