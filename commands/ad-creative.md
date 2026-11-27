---
disable-model-invocation: true
name: ad-creative
description: "Yuqori konversiyali reklama kreativi, S/A darajali 9:16 video reklama ssenariylari (UGC, Founder, iMessage/ChatGPT Reveal, Greenscreen, Faceless Motion), Andromeda PDA xilma-xillik matritsalari va AI belgilarisiz platformada tasdiqlangan matn yaratish (Aliaslar: /creative, /kreativ)"
argument-hint: "<mahsulot/taklif> [--platform meta|google_rsa|tiktok|linkedin|telegram] [--format ugc_reaction_demo|founder_authority|imessage_reveal|greenscreen_proof]"
---

# `/ad-creative` — Samarali reklama kreativi va video reklama studiyasi

Vazifa: **$ARGUMENTS**

## Bajarish tartibi (amaliyotchi birinchi, dasturlash shart emas)

1. **Ish maydoni kontekstini tekshiring:** `.claude/product-marketing.md`, `.agents/product-marketing.md` yoki mijoz `BRIEF.md` mavjud bo'lsa o'qing, foydalanuvchi tilini va faol bozor paketini (`markets/<market>/pack.json`) aniqlang.
2. **Deterministik kreativ va video dvigatellarni ishga tushiring (`tools/creative-matrix.py`):**
   ```bash
   # 1. Andromeda Entity-ID va Persona-Desire-Awareness (PDA) xilma-xillik rejasi + 3x3 matritsa
   python3 tools/creative-matrix.py pda-matrix --niche <niche> --product "<offer>" --price <price> --market <market> --currency <ISO>

   # 2. Syomkaga tayyor 9:16 video reklama ssenariysi va storyboard (720x1200 xavfsiz zona, 3 hook varianti)
   python3 tools/creative-matrix.py video-script --niche <niche> --product "<offer>" --problem "<pain_point>" --format <ugc_reaction_demo|founder_authority|imessage_reveal|chatgpt_reveal|greenscreen_proof|no_yapping_split_screen|faceless_motion_explainer> --language <lang>

   # 3. Platformada tasdiqlangan reklama matni to'plami + AI belgilarini avtomatik tozalovchi linter
   python3 tools/creative-matrix.py ad-copy --platform <meta|google_rsa|tiktok|linkedin|telegram> --product "<offer>" --problem "<pain_point>" --proof "<proof>" --language <lang>
   ```
3. **Tuzilgan kreativ paketni topshiring:**
   - **Andromeda Entity ID va PDA matritsasi:** Persona, Desire va Awareness bosqichlari bo'yicha 8–12 ta vizual jihatdan farqli konsept (Meta Andromeda ularga alohida retrieval chiptalarini berishi uchun).
   - **9:16 video reklama ssenariylari:** 3 ta ochilish hook varianti (`0-3s`) + sahnama-sahna vaqt kodli storyboard (`A-Roll`, `B-Roll`, `720x1200` xavfsiz zona matni, `Audio/VO`).
   - **Platformada tasdiqlangan reklama matni:** Belgilar soni hisoblangan sarlavhalar, asosiy matn va tavsiflar — **AI belgilarisiz** va har bir konsept uchun **inkor qilinadigan test gipotezasi** bilan.
