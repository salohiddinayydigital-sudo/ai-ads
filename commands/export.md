---
name: export
description: "CSV/JSON reklama akkaunt eksporti tahlilchisi — behuda sarfni aniqlash, marginal CPA bo'linmasi va masshtab/o'chirish xulosalari (Alias: /eksport)"
alias_of: eksport
---

# `/export` (Alias: `/eksport`)

CSV/JSON reklama akkaunt eksporti tahlilchisi — behuda sarfni aniqlash, marginal CPA bo'linmasi va masshtab/o'chirish xulosalari (Alias: /eksport).

## Bajarish tartibi
1. Foydalanuvchi tilini va faol bozor paketini aniqlang (`markets/<market>/pack.json`, standart `global`).
2. Deterministik CLI asbobini ishga tushiring:
   ```bash
   python3 tools/ad-export-analyzer.py --help
   ```
3. Natijalarni foydalanuvchi tilida, valyutaga mos metrikalar va manba havolalari bilan umumlashtiring.
