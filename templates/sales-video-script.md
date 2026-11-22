---
name: sales-video-script
description: "Sotuvchi video ssenariy shabloni — Creative Brief Header, modulli 3-5 hook x 2 body x 2 CTA, 6 ustunli AV-jadval, Production Notes va Self-Audit"
tags: [template, video, sotuvchi, ssenariy]
source: "skills/video/references/sales-video-scripting.md"
updated: 2026-11-22
---

# Sotuvchi video ssenariy (`sales`)

> Qoida: statistika, sharh, narx, kafolat to'qilmaydi — `[ADD VERIFIED ...]`. Reference: `skills/video/references/sales-video-scripting.md`. Skelet: `python3 tools/creative-matrix.py video-script --mode sales --lang uz --duration 30 --hooks 3 --product "..." --json`.

## 1. Creative Brief Header

- **Biznes / mahsulot:** `[ADD]`
- **Maqsad:** `Lead | Sale | Reach | Trust`
- **Auditoriya va awareness bosqichi:** `[avatar]` · `unaware | problem_aware | solution_aware | product_aware | most_aware`
- **Format va davomiylik:** `9:16` · `15 | 30 | 45 | 60 s`
- **Til:** `uz lotin | uz kirill | ru | en` (alohida yoziladi, tarjima emas)
- **One Big Idea:** `[1 jumla]`
- **Asosiy e'tiroz:** `[ADD]`
- **Tasdiqlangan isbot (manba bilan):** `[ADD VERIFIED ...]` — yo'q bo'lsa: `yo'q`
- **Test gipotezasi:** o'zgaruvchi `[hook]` · metrika `[3s hook rate]` · qaror qoidasi `[ishga tushirishdan oldin]`

## 2. Modulli to'plam (Lego)

### Hook (0-3 s), 3-5 ta, mexanizmi bo'yicha farqli

| ID | Mexanizm | Vizual hook | Matnli hook (3-5 so'z) | Og'zaki hook (<= 7 so'z) |
|---|---|---|---|---|
| H1 | og'riq lahzasi | | | |
| H2 | kutilmagan fakt | | | |
| H3 | qarshi fikr | | | |

### Body (3 - oxirgi 5-8 s), 2 ta

- **B1 Demo-led:** muammo → yashirin sabab/mexanizm → vizual isbot → e'tirozni yopish
- **B2 Case-led:** kontekst → case → mexanizm → e'tirozni yopish

### Offer + CTA (oxirgi 5-8 s), 2 ta

- **C1 Direct:** taklif `[ADD VERIFIED]` + aniq qadam
- **C2 Soft:** saqlash / profil / savol

Kombinatsiyalar: `H1xB1xC1`, `H2xB1xC1`, ... (bir testda bitta o'zgaruvchi)

## 3. 6 ustunli AV-jadval (tanlangan kombinatsiya)

| Vaqt | Bosqich | Vizual / Kadr (A-Roll & B-Roll) | Spiker nutqi / VO | Ekrandagi matn (Safe-Zone 720x1200) | Kamera, Ritm & SFX |
|---|---|---|---|---|---|
| 0:00-0:03 | Hook | | | | |
| 0:03-0:07 | Muammo | | | | |
| | Mexanizm | | | | |
| | Isbot | | | | |
| | E'tiroz | | | | |
| | Taklif | | | | |
| | CTA | | | | |

Retention: har ~2-4 s da pattern interrupt; isbot 3-10 s ichida; VO <= soniya x 2.6 so'z.

## 4. Production Notes

- **Spiker:** intonatsiya, tempi, kiyim
- **Kadr / yorug'lik / ovoz:** `[ADD]`
- **B-roll ro'yxati:** `[ADD: 5-8 klip]`
- **3-Capture:** A-roll (3 hook + tana + 2 CTA) · mexanizm B-roll · isbot B-roll
- **Compliance qatori:** `[ADD: xavf zonalari va muqobil]`
- **Ochiq `[ADD VERIFIED ...]` ro'yxati:** `[ADD]`

## 5. Self-Audit (`skills/video/references/script-quality-rubric.md`)

```
Self-Audit: __/100  (hook __/20 · retention __/15 · qiymat __/20 · nutq __/15 · ijro __/20 · compliance __/10)
Blokerlar: yo'q | ...
Yorliq: HEURISTIC_PRIOR_MODEL (ichki tekshiruv, natija prognozi emas)
```
