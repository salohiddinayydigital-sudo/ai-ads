---
disable-model-invocation: true
name: funnel
description: "E-Commerce, B2B SaaS, WhatsApp/Telegram/LINE va CRM bo'ylab boshidan oxirigacha konversiya voronkasi arxitekturasi va sizib ketish diagnostikasi (Alias: /voronka)"
alias_of: voronka
---

# `/funnel` (Alias: `/voronka`)

E-Commerce, B2B SaaS, WhatsApp/Telegram/LINE va CRM bo'ylab boshidan oxirigacha konversiya voronkasi arxitekturasi va sizib ketish diagnostikasi (Alias: /voronka).

## Bajarish tartibi
1. Foydalanuvchi tilini va faol bozor paketini aniqlang (`markets/<market>/pack.json`, standart `global`).
2. Deterministik CLI asbobini ishga tushiring:
   ```bash
   python3 tools/calculator.py --help
   ```
3. Natijalarni foydalanuvchi tilida, valyutaga mos metrikalar va manba havolalari bilan umumlashtiring.
