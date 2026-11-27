---
disable-model-invocation: true
name: video-plan
description: "Video kontent reja (haftalik/oylik matritsa) va batch syomka rejasi (Alias: /video-reja)"
alias_of: video-reja
argument-hint: "<biznes> [1|2|4 hafta]"
---

# `/video-plan` (Alias: `/video-reja`)

Vazifa: **$ARGUMENTS**

`/video-reja` bilan bir xil jarayon (kanonik, o'zbekcha): Video kontent reja (haftalik/oylik matritsa) va batch syomka rejasi. Foydalanuvchi tilida javob bering. Faqat pre-production: montaj/render qatlamiga tegmaydi.

## Bajarish tartibi
1. Foydalanuvchi tilini (uz lotin/kirill, ru, en) va bozorni (`markets/<market>/pack.json`, standart `global`) aniqlang. Faqat yetishmayotganini so'rang: mahsulot/taklif, auditoriya, maqsad, tasdiqlangan dalil (statistika, sharh yoki narxni hech qachon to'qimang — `[ADD VERIFIED ...]` dan foydalaning).
2. `skills/video/SKILL.md` dagi Intent Router'ni yuklang va faqat mos referenceni o'qing.
3. Deterministik skeletni ishga tushiring:
   ```bash
   python3 tools/creative-matrix.py video-script --mode plan --lang <uz|ru|en> --weeks 2 --per-week 5 --niche <niche> --product "<business>" --json
   ```
4. Skeletni foydalanuvchining haqiqiy ma'lumotlari bilan to'ldiring; topshirishdan oldin `skills/video/references/script-quality-rubric.md` bo'yicha o'zingizni baholang (>= 85/100).
