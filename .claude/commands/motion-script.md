---
disable-model-invocation: true
name: motion-script
description: "Motion video ssenariysi, sahnama-sahna storyboard va dizayn brifi (montajsiz) (Alias: /motion-ssenariy)"
alias_of: motion-ssenariy
argument-hint: "<mahsulot/g'oya> [kinetic|ui|explainer|data|bumper] [15|30|45|60]"
---

# `/motion-script` (Alias: `/motion-ssenariy`)

Vazifa: **$ARGUMENTS**

`/motion-ssenariy` bilan bir xil jarayon (kanonik, o'zbekcha): Motion video ssenariysi, sahnama-sahna storyboard va dizayn brifi (montajsiz). Foydalanuvchi tilida javob bering. Faqat pre-production: montaj/render qatlamiga tegmaydi.

## Bajarish tartibi
1. Foydalanuvchi tilini (uz lotin/kirill, ru, en) va bozorni (`markets/<market>/pack.json`, standart `global`) aniqlang. Faqat yetishmayotganini so'rang: mahsulot/taklif, auditoriya, maqsad, tasdiqlangan dalil (statistika, sharh yoki narxni hech qachon to'qimang — `[ADD VERIFIED ...]` dan foydalaning).
2. `skills/video/SKILL.md` dagi Intent Router'ni yuklang va faqat mos referenceni o'qing.
3. Deterministik skeletni ishga tushiring:
   ```bash
   python3 tools/creative-matrix.py video-script --mode motion --lang <uz|ru|en> --duration 30 --niche <niche> --product "<product>" --json
   ```
4. Skeletni foydalanuvchining haqiqiy ma'lumotlari bilan to'ldiring; topshirishdan oldin `skills/video/references/script-quality-rubric.md` bo'yicha o'zingizni baholang (>= 85/100).
