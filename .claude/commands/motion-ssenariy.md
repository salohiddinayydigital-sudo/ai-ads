---
disable-model-invocation: true
description: Motion video ssenariy, sahnama-sahna storyboard va dizayn brif (montajsiz)
argument-hint: <mahsulot/g'oya> [kinetik|ui|explainer|data|bumper] [15|30|45|60]
---

# /motion-ssenariy — motion video blueprint

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/00-manba.md` (raqam va UI mazmuni to'qilmaydi).
2. O'qi: `skills/video/references/motion-video-scripting.md`.

## Ijro

1. **Kirish** (`video-producer`): tur, format (9:16/16:9/1:1), davomiylik, brend assetlari, tasdiqlangan raqamlar/UI, til.
2. **Skelet:**
   ```bash
   python3 tools/creative-matrix.py video-script --mode motion --lang uz --duration 30 --niche <niche> --product "<mahsulot>" --problem "<muammo>" --json
   ```
3. **Blueprint:** Concept & Visual Direction Brief → Motion Storyboard jadvali (vaqt, VO, ekran matni, vizual, motion cue, SFX) → Asset Checklist.
4. **Tekshiruv:** `script-quality-rubric.md` ≥ 85/100; sahna vaqtlari yig'indisi = davomiylik; VO so'z limiti.

## Natija

`outputs/<mijoz>/<sana>-motion-blueprint.md` (+ ixtiyoriy `--json`, `schemas/motion-blueprint-schema.json`). Render/kod — faqat foydalanuvchi so'rasa (`video-motion-graphics.md`).
