---
name: hooks-readme
description: Tyrion hook qatlami — deterministik nazorat, nima uchun faqat o'lchanadigan dalil ishlatiladi
tags: [hooks, avtomatika, sifat]
source: "ECC delivery-gate naqshi (skills/delivery-gate/SKILL.md) asosida Tyrion uchun (2026-09-16)"
updated: 2026-11-11
---

# 🪝 HOOK QATLAMI

> Hook har sessiyada ishlaydi va **kontekstga matn qo'shadi** — shuning uchun faqat
> o'lchanadigan dalil ishlatiladi: fayl bor/yo'q, sana, regex, exit kod. LLM hukmi yo'q.

## Nima ishlaydi

| Hodisa | Skript | Nima qiladi | Bloklaydimi |
|--------|--------|-------------|-------------|
| `SessionStart` | `tyrion-hook.py brief` | 1 qator holat: qayd/agent soni, instinktlar, profil, bozor. Plugin boshqa loyihada ishlaganda qo'shimcha: Tyrion ildizi, xotira yo'li va qat'iy qoidalar (u yerda `CLAUDE.md` yuklanmaydi) | yo'q |
| `PostToolUse` (Edit/Write) | `tyrion-hook.py ingest` | yangi qayd `INDEX.md` da bormi, `LOG.md` bugun yangilanganmi | yo'q (ogohlantiradi) |
| `Stop` | `tyrion-hook.py dod --warn-only` | topshirish darvozasi: `doctor` xatolari + ingest | yo'q (ogohlantiradi) |

Qo'lda **qat'iy** rejim (ishni bloklaydi, exit 1):

```powershell
python3 hooks\tyrion-hook.py dod              # to'siq bo'lsa exit 1
python3 hooks\tyrion-hook.py ingest           # faqat ingest
```

## Sozlamalar (plugin `userConfig`)

Claude Code plugin sozlamalarini hook jarayoniga `CLAUDE_PLUGIN_OPTION_<KALIT>` ko'rinishida beradi.
Aniq berilgan `TYRION_*` o'zgaruvchisi har doim ustun turadi.

| Sozlama | O'zgaruvchi | Ta'siri |
|---------|-------------|---------|
| `hooks_enabled` | `CLAUDE_PLUGIN_OPTION_HOOKS_ENABLED` | `false` bo'lsa barcha hooklar jim chiqadi |
| `hook_profile` | `TYRION_HOOK_PROFILE` ← `CLAUDE_PLUGIN_OPTION_HOOK_PROFILE` | `minimal` · `standard` · `strict` |
| `default_market` | `TYRION_DEFAULT_MARKET` ← `CLAUDE_PLUGIN_OPTION_DEFAULT_MARKET` | topshiriqda bozor aniqlanmaganda ishlatiladi (majburlash emas — buning uchun `TYRION_MARKET`) |

`SessionStart` hook standart bozorni `CLAUDE_ENV_FILE` ga ham yozadi, shunda Bash orqali chaqirilgan asboblar ham uni ko'radi.

## O'rnatish

```powershell
python3 tools/install-hooks.py --dry-run      # nima qo'shilishini ko'rsatadi
python3 tools/install-hooks.py                # .claude/settings.json ga qo'shadi (nusxa olib)
python3 tools/install-hooks.py --target "claude-ads-main\.claude\settings.json"
```

`install-hooks.py` mavjud hook'larni **o'chirmaydi** — faqat o'zinikini qo'shadi (takrorlamaydi),
avval `settings.json.bak` nusxasini oladi.

## Nega Stop hook bloklamaydi

Har to'xtashda qat'iy tekshiruv ishni to'xtatib qo'yardi (katalog har tahrirdan keyin eskiradi).
Shuning uchun hook **ogohlantiradi**, qat'iy darvoza esa qo'lda yoki haftalik auditda ishlatiladi.

**Bog'liq:** [[AGENTS.md]] · [[50-topshirish-dod]] · [[tools/README|asboblar]] · [[haftalik-audit]]
