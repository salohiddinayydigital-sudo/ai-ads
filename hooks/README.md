---
name: hooks-readme
description: Tyrion hook qatlami — deterministik nazorat, nima uchun faqat o'lchanadigan dalil ishlatiladi
tags: [hooks, avtomatika, sifat]
source: "ECC delivery-gate naqshi (skills/delivery-gate/SKILL.md) asosida Tyrion uchun (2026-09-16)"
updated: 2026-11-12
---

# 🪝 HOOK QATLAMI

> Hook har sessiyada ishlaydi va **kontekstga matn qo'shadi** — shuning uchun faqat
> o'lchanadigan dalil ishlatiladi: fayl bor/yo'q, sana, regex, exit kod. LLM hukmi yo'q.

## Nima ishlaydi

| Hodisa | Skript | Nima qiladi | Bloklaydimi |
|--------|--------|-------------|-------------|
| `SessionStart` | `tyrion-hook.py brief` | 1 qator holat: qayd/agent soni, graf eskiligi, drift, git | yo'q |
| `PreToolUse` (Edit/Write/MultiEdit) | `tyrion-hook.py guard --warn-only --quiet` | sir fayllari (`.env`, kalit, sertifikat) va generatsiya fayllariga (`catalog.json`, `graph.json`) yozishni tekshiradi | **faqat `strict` profilida** (exit 2); `standard` da ogohlantiradi |
| `PostToolUse` (Edit/Write) | `tyrion-hook.py ingest` | yangi qayd `INDEX.md` da bormi, `LOG.md` bugun yangilanganmi | yo'q (ogohlantiradi) |
| `Stop` | `tyrion-hook.py dod --warn-only` | topshirish darvozasi: `doctor` xatolari + ingest | yo'q (ogohlantiradi) |

## Nimani majburlaydi va nimani MAJBURLAMAYDI

Halol chegara: hook — bu **fayl nomi/yo'li bo'yicha** tekshiruv, xavfsizlik devori emas.

| Himoya | Majburlanadi? | Qanday |
|--------|---------------|--------|
| Sir faylga yozish (`.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa`, `credentials.json`, `secrets.*`, `.netrc` ...) | `strict` — **ha** (exit 2, tool bloklanadi); `standard` — faqat **ogohlantirish** (stderr); `minimal` — hook o'chirilgan | `TYRION_HOOK_PROFILE=strict`. `.env.example/.sample/.template` ruxsat. `hooks.json` dagi `--warn-only` sirlarga ta'sir qilmaydi (strict baribir bloklaydi) |
| Generatsiya fayllariga qo'lda yozish (`manifests/catalog.json`, `graphify-out/graph.json`) | `strict` — ha; `standard` — hooks.json `--warn-only` bilan ogohlantirish | `catalog.py build` ishlating |
| Spend-Guard (byudjet +20%, jonli hisob o'zgarishi) | **YO'Q — faqat siyosat darajasida.** Hech qaysi hook `spend-guard.py` ni chaqirmaydi | `rules/40-xavfsizlik-va-hisob.md`, router `blocked_mutation_approval` holati va `spend-guard.py` CLI/MCP — bularni agent o'zi ishlatishi kerak. Agar agent reklama API/MCP vositasini to'g'ridan-to'g'ri chaqirsa, hech narsa uni to'xtatmaydi |
| Sir **mazmuni** (kod ichiga yopishtirilgan token) | Yo'q | `tools/tyrion-shield.py scan` va `doctor.py` qo'lda/CI da ishlaydi; hook faylni o'qimaydi |
| Bash orqali yozish (`echo X > .env`, `sed -i`) | Yo'q | `pre:guard` faqat `Edit`, `Write`, `MultiEdit` ga ulangan |
| Sessiya oxiri `dod`, `post:ingest` | Yo'q (ogohlantiradi) va faqat maintainer rejimida (`TYRION_DEV=1` yoki ombor ildizi) | — |
| Hook xatosi | Fail-open: muhit xatosida (python topilmadi va h.k.) exit 0; `strict` da exit 2 | `run-hook.cjs` |

`TYRION_DISABLED_HOOKS=pre:guard` yoki `minimal` profili himoyani butunlay o'chiradi — bu foydalanuvchi qarori.
Chiqish kodi siyosati (barcha asboblar): `0` o'tdi · `1` darvoza bloklandi · `2` validatsiya xatosi yoki hook bloki.

Qo'lda **qat'iy** rejim (ishni bloklaydi, exit 1):

```powershell
python3 hooks\tyrion-hook.py dod              # to'siq bo'lsa exit 1
python3 hooks\tyrion-hook.py ingest           # faqat ingest
```

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
