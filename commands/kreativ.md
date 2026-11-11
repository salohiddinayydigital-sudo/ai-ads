---
description: Kreativ ishi — angle/avatar strategiyasi, 3x3 matritsa va Andromeda PDA rejasi, 9:16 video skript, 3 tilli hook va platformaga mos reklama matni
argument-hint: <mijoz yoki offer> [--platform meta|google_rsa|tiktok|linkedin|telegram] [--format ugc_reaction_demo|founder_authority|imessage_reveal|greenscreen_proof]
---

# /kreativ — Kreativ Strategiya, Video Skript va Reklama Matni

Vazifa: **$ARGUMENTS**

## Oldindan

1. Qoidalar: `rules/30-ozbekiston-konteksti.md` + `rules/00-manba.md`.
2. Bilim (graf orqali, kerak bo'lsa): [[content-is-targeting]] · [[kreativ-hit-rate]] ·
   [[unique-mexanizm]] · [[funnel-2-kreativ-format]] · [[taklif-tuzilishi]].
3. Mijoz konteksti: `clients/<mijoz>/BRIEF.md` va `journal/<mijoz>.md` (bo'lsa). Til va bozor (`markets/<bozor>/pack.json`) aniqlanadi.

## Deterministik Dvigatellar (`tools/creative-matrix.py`, 0 token)

```bash
# 1. Andromeda Entity-ID va Persona-Desire-Awareness (PDA) xilma-xillik rejasi + 3x3 Angle×Format matritsa
python3 "${CLAUDE_PLUGIN_ROOT}/tools/creative-matrix.py" pda-matrix --niche <niche> --product "<offer>" --price <narx> --market <bozor> --currency <ISO>

# 2. Suratga olishga tayyor 9:16 video skript va storyboard (720x1200 xavfsiz zona, 3 hook varianti)
python3 "${CLAUDE_PLUGIN_ROOT}/tools/creative-matrix.py" video-script --niche <niche> --product "<offer>" --problem "<og'riq>" --format <ugc_reaction_demo|founder_authority|imessage_reveal|chatgpt_reveal|greenscreen_proof|no_yapping_split_screen|faceless_motion_explainer> --language <til>

# 3. Platformaga mos reklama matni + avtomatik "AI izi yo'q" linteri
python3 "${CLAUDE_PLUGIN_ROOT}/tools/creative-matrix.py" ad-copy --platform <meta|google_rsa|tiktok|linkedin|telegram> --product "<offer>" --problem "<og'riq>" --proof "<dalil>" --language <til>

# 4. 3 soniyalik hooklar (til bo'yicha alohida) va charchoq diagnostikasi
python3 "${CLAUDE_PLUGIN_ROOT}/tools/creative-matrix.py" hooks --niche <niche> --offer "<offer>" --languages <uz_latin,ru,en>
python3 "${CLAUDE_PLUGIN_ROOT}/tools/creative-matrix.py" fatigue --hook-rate <%> --hold-rate <%> --ctr-drop-pct <%> --frequency <f> --ftir <%>
```

## Ijro

1. **Strategiya** (`creative-strategist`): avatar → muammolar → angle → big idea.
   Har angle alohida masshtablanadi (kreativ = targeting).
2. **Matn** (`copy-writer`): hook (3 variant) · body · CTA — til bo'yicha alohida
   (uz/ru/kirill), tarjima emas.
3. **Format** (`reels-scriptwriter` / `format-adapter`): TOF problem-solution va
   BOF objection — faqat shu 2 format.
4. **Tekshiruv**: policy ([[40-xavfsizlik-va-hisob]] §5) + hit rate kutilmasi.

## Natija

`outputs/<mijoz>/<sana>-kreativ.md`:

- **Andromeda Entity ID va PDA matritsasi:** Persona, Desire va Awareness bosqichlari bo'yicha 8–12 ta vizual farqli konsept (Andromeda har biriga alohida retrieval ticket berishi uchun).
- **9:16 video skriptlar:** 3 ta ochilish hooki (`0–3s`) + sahnama-sahna vaqt kodli storyboard (`A-Roll`, `B-Roll`, `720x1200` xavfsiz zona matni, `Audio/VO`).
- **Platformaga mos matn:** belgilar soni tekshirilgan sarlavha, asosiy matn va tavsif — AI izisiz.
- **Sinov rejasi:** har konsept uchun rad etilishi mumkin bo'lgan gipoteza (nima o'lchanadi, qaysi chegarada kill/keep/scale).
