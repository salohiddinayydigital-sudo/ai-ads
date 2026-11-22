---
name: motion-video-blueprint
description: "Motion video blueprint shabloni — Concept & Visual Direction Brief, sahnama-sahna Motion Storyboard jadvali va Asset Checklist (montajsiz pre-production)"
tags: [template, video, motion, storyboard]
source: "skills/video/references/motion-video-scripting.md"
updated: 2026-11-22
---

# Motion video blueprint (`motion`)

> Kod, render va montaj bu shablonga kirmaydi. Reference: `skills/video/references/motion-video-scripting.md`. Skelet: `python3 tools/creative-matrix.py video-script --mode motion --motion-type kinetic --duration 30 --product "..." --json`. BPM, so'z/soniya — `HEURISTIC_PRIOR_MODEL`.

## 1. Concept & Visual Direction Brief

| Maydon | Qiymat |
|---|---|
| Concept (1 jumla) | `[ADD]` |
| Tur | `kinetik tipografiya | UI/SaaS | explainer | offer & data | brand bumper` |
| Format / davomiylik | `9:16 | 16:9 | 1:1` · `[s]` |
| Tempo | `~120-130 BPM tez | ~90 BPM sokin | beat-less, SFX-led` |
| Rang palitrasi | asosiy `[#HEX]` · aksent `[#HEX]` · fon `[#HEX]` · matn `[#HEX]` |
| Shrift iyerarxiyasi | sarlavha `[ ]` · kalit so'z urg'u `[ ]` · ikkilamchi `[ ]` (lotin + kirill glif) |
| Safe-zone | `9:16 uchun 720x1200` |
| Ovoz | diktor uslubi, til, tezlik `[ ]` · musiqa kayfiyati `[ ]` |
| Tonallik | 3 sifat + 1 "bo'lmasin" |

## 2. Motion Storyboard

| Sahna # va Vaqt | Diktor / VO (pauza `/`, urg'u **qalin**; <= soniya x 2.6 so'z) | Ekrandagi matn (3-5 so'z) | Vizual kompozitsiya va assetlar | Harakat va o'tish (Motion Cue) | SFX va musiqa aksenti |
|---|---|---|---|---|---|
| S1 `00:00-00:02.5` | | | | zoom-in punch | whoosh + hit |
| S2 | | | | slide-up reveal | pop |
| S3 | | | | counter roll-up | riser / silence hit |
| S_last | | | End-card: logo + CTA | scale-up end-card | beat drop, music out |

Qoidalar: sahnalar yig'indisi = davomiylik · sahna 1.5-4 s · hook <= 3 s · har ~2-4 s yangi hodisa · raqam faqat tasdiqlangan.

## 3. Asset Checklist

| Asset | Format | Mas'ul | Holat |
|---|---|---|---|
| Logo | SVG + monoxrom | | [ ] |
| Mahsulot / xizmat | PNG shaffof, >= 2x | | [ ] |
| UI skrinshot / ekran yozuvi | PNG / MP4 | | [ ] |
| Brend shriftlar | OTF/TTF + litsenziya | | [ ] |
| Raqamli dalillar | qiymat + manba | | [ ] |
| Musiqa / SFX | litsenziyali | | [ ] |
| Voiceover | skript tasdig'i + yozuv/TTS | | [ ] |

## 4. Self-Audit va handoff

```
Self-Audit: __/100  (motion: "ijro" = storyboard to'liqligi, motion cue, SFX)
Blokerlar: yo'q | ...
```
Render so'ralsa: `skills/video/references/video-motion-graphics.md` + `tools/video-run.py` (blueprint — kirish).
