---
disable-model-invocation: true
name: video-script
description: "6 ustunli AV jadvali va modulli hooklar bilan sotuv yoki organik video ssenariysi (Alias: /video-ssenariy)"
alias_of: video-ssenariy
argument-hint: "<mahsulot/taklif> [sales|organic] [15|30|45|60]"
---

# `/video-script` (Alias: `/video-ssenariy`)

Vazifa: **$ARGUMENTS**

`/video-ssenariy` bilan bir xil jarayon (kanonik, o'zbekcha): 6 ustunli AV jadvali va modulli hooklar bilan sotuv yoki organik video ssenariysi. Foydalanuvchi tilida javob bering. Faqat pre-production: montaj/render qatlamiga tegmaydi.

## Bajarish tartibi
1. Foydalanuvchi tilini (uz lotin/kirill, ru, en) va bozorni (`markets/<market>/pack.json`, standart `global`) aniqlang. Faqat yetishmayotganini so'rang: mahsulot/taklif, auditoriya, maqsad, tasdiqlangan dalil (statistika, sharh yoki narxni hech qachon to'qimang — `[ADD VERIFIED ...]` dan foydalaning).
2. `skills/video/SKILL.md` dagi Intent Router'ni yuklang va faqat mos referenceni o'qing.
3. Deterministik skeletni ishga tushiring:
   ```bash
   python3 tools/creative-matrix.py video-script --mode <sales|organic> --lang <uz|ru|en> --duration 30 --hooks 3 --niche <niche> --product "<product>" --json
   ```
4. Skeletni foydalanuvchining haqiqiy ma'lumotlari bilan to'ldiring; topshirishdan oldin `skills/video/references/script-quality-rubric.md` bo'yicha o'zingizni baholang (>= 85/100).
