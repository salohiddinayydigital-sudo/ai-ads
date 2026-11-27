---
disable-model-invocation: true
name: ask
description: "Barcha agent, skill va wiki qaydlari bo'ylab oddiy tildagi universal pullik media va targetologiya marshrutlash so'rovi (Alias: /savol)"
alias_of: savol
---

# `/ask` (Alias: `/savol`)

Barcha agent, skill va wiki qaydlari bo'ylab oddiy tildagi universal pullik media va targetologiya marshrutlash so'rovi (Alias: /savol).

## Bajarish tartibi
1. Foydalanuvchi tilini va faol bozor paketini aniqlang (`markets/<market>/pack.json`, standart `global`).
2. Yagona kanonik tizim bilan marshrutlang (bajarishni `tyrion` skilli boshqaradi; agent yoki skillni qo'lda tanlamang):
   ```bash
   python3 tools/skill-search.py route "$ARGUMENTS" --context-mode manifest --json
   ```
   So'ng `skills/tyrion/references/conductor-v7.md` ga amal qiling (tanlangan skilllarni to'liq o'qing, delegatsiya qiling yoki belgilangan zaxira rejimini ishga tushiring, tekshiring, umumlashtiring).
3. Xulosalarni foydalanuvchi tilida, valyutaga mos metrikalar va manba havolalari bilan umumlashtiring.
