---
disable-model-invocation: true
description: Sotuvchi yoki organik video ssenariy — 6 ustunli AV-jadval, modulli hook/body/CTA
argument-hint: <mahsulot/taklif> [sales|organic] [15|30|45|60]
---

# /video-ssenariy — video ssenariy (sotuvchi va umumiy)

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/00-manba.md` (dalilsiz raqam yo'q) + `rules/10-til-va-uslub.md` + `rules/30-ozbekiston-konteksti.md`.
2. Rejimni tanla (`skills/video/SKILL.md`): reklama/lid/sotuv → `sales`; ekspert/brend/case → `organic`. Noaniq bo'lsa — bitta savol.
3. O'qi: `skills/video/references/sales-video-scripting.md` yoki `organic-video-content.md` (faqat kerakligini).

## Ijro

1. **Kirish** (`video-producer`): mahsulot/taklif, avatar, awareness bosqichi, asosiy e'tiroz, **tasdiqlangan** isbot, til, davomiylik. Yetishmasa — so'ra.
2. **Skelet:**
   ```bash
   python3 tools/creative-matrix.py video-script --mode sales --lang uz --duration 30 --hooks 3 --niche <niche> --product "<mahsulot>" --problem "<muammo>" --json
   ```
   (`--mode organic` — organik uchun.)
3. **Yozish:** Creative Brief Header → 6 ustunli AV-jadval (sales: 3–5 hook × 2 body × 2 CTA) → Production Notes.
4. **Tekshiruv:** `skills/video/references/script-quality-rubric.md` ≥ 85/100; `claim_safety.needs_verification` hal qilingan; platforma compliance (compliance-reviewer — tibbiyot/moliya).

## Natija

`outputs/<mijoz>/<sana>-video-ssenariy.md`: brief · AV-jadval(lar) · production notes · Self-Audit · ochiq `[ADD VERIFIED ...]` ro'yxati. Montaj/render — faqat so'ralsa (`/video-ssenariy` doirasida emas).
