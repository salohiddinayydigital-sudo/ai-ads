---
name: report
description: "MER, ROAS, CPA va keyingi sprint harakat rejasi bilan mijoz va operator uchun ijroiya hisobot generatori (Alias: /hisobot)"
alias_of: hisobot
---

# `/report` (Alias: `/hisobot`)

MER, ROAS, CPA va keyingi sprint harakat rejasi bilan mijoz va operator uchun ijroiya hisobot generatori (Alias: /hisobot).

## Bajarish tartibi
1. Foydalanuvchi tilini va faol bozor paketini aniqlang (`markets/<market>/pack.json`, standart `global`).
2. Deterministik CLI asbobini ishga tushiring:
   ```bash
   python3 tools/client-workspace.py --help
   ```
3. Natijalarni foydalanuvchi tilida, valyutaga mos metrikalar va manba havolalari bilan umumlashtiring.
