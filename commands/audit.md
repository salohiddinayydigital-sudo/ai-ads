---
description: Platforma auditi — conductor + worker'lar bilan (Meta, Google, TikTok, ...)
argument-hint: <platforma> <mijoz>
---

# /audit — platforma auditi

Vazifa: **$ARGUMENTS** (platforma + mijoz)

## Oldindan (majburiy)

1. Qoida yukla: `rules/00-manba.md` + `rules/40-xavfsizlik-va-hisob.md` (+ mijoz bo'lsa `rules/30-ozbekiston-konteksti.md`).
2. Kontekst: `MEMORY.md` (operator xotirasi) + `journal/<mijoz>.md` (mijoz holati).
3. Ma'lumot bor/yo'q ro'yxatini tuz — yetishmaganini **so'ra**, taxmin qilma.

## E'lon (fan-out oldidan)

```
Maqsad: <X> · Jamoa: <N bot: nomlari>
```

## Ijro

| Qadam | Kim | Nima |
|-------|-----|------|
| 1 | conductor (shu sessiya) | kontrakt, dalil yig'ish, savol berish |
| 2 | `audit-<platforma>` worker | platforma bo'yicha dalilga asoslangan findings |
| 3 | `audit-tracking` / `audit-budget` | kerak bo'lsa: o'lchov va matematika (2-qadam bilan **parallel**) |
| 4 | conductor | yig'ish, ziddiyatlarni ajratish, tavsiya |
| 5 | `release-verifier` | topshirish oldidan nazorat |

### Dispatch (haqiqiy ijro)

- 2–3-qadamdagi mustaqil worker'larni **bitta xabarda** `Agent` asbobi bilan parallel ishga tushir: `subagent_type: audit-<platforma>` (+ kerak bo'lsa `audit-tracking`, `audit-budget`). Har biriga: mijoz, oyna, valyuta, maqsad va dalil fayllari yo'li. Hisob o'zgartirish ruxsati berilmaydi.
- Worker natijasini charter `output_contract` ga solishtir (`status`, `missing_inputs`, `execution_evidence`). `needs_input` bo'lsa so'rovni foydalanuvchiga ko'tar; `blocked_mutation_approval` bo'lsa tasdiqsiz davom etma.
- Agent turi topilmasa yoki muhitda sub-agent yo'q bo'lsa (Codex/Cursor/CLI yoki yangi `.claude/agents/` hali yuklanmagan): worker ishlarini o'zing ketma-ket bajar va natijada **`execution_mode: single_conductor_fallback`** deb ochiq yoz; sub-agent ishga tushganday ko'rsatma. Muvaffaqiyatli dispatchda: `execution_mode: native_subagent_dispatch`.

## Natija

- Fayl: `outputs/<mijoz>/<sana>-<platforma>-audit.md`
- Har topilma: `control_id` · dalil · severity · confidence · teskari qadam
- Checklist: ROAS · Pixel/CAPI · UTM · Policy ([[50-topshirish-dod]])
- Hisob o'zgarishi kerak bo'lsa — **draft + tasdiq**, o'zing o'zgartirmaysan.

Oxirida: `journal/<mijoz>.md` ga qaror va sababi, `LOG.md` ga 1 qator.
