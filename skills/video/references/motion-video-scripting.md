# Motion video ssenariy va storyboard (Pre-Production Blueprint) — `motion`

> **Rejim:** `motion` · **Chiqish:** motion dizayner, kreativ direktor yoki AI video/motion vositasiga topshiriladigan **blueprint** (`templates/motion-video-blueprint.md`).
> **Chegara:** bu fayl **kod, rendering va montaj yozmaydi.** Remotion/After Effects/ffmpeg ishi — `video-motion-graphics.md` (kod/render) va `video-editing.md`; ularga faqat foydalanuvchi aniq render so'rasa o'tiladi. Blueprint → render handoff §7.
> **Manba qoidasi:** BPM, so'z/soniya, matn uzunligi — `HEURISTIC_PRIOR_MODEL`. Raqamlar, narx, UI skrinshot mazmuni — `USER_PROVIDED`; yo'q bo'lsa `[ADD VERIFIED ...]` ([[00-manba]]).

## 1. Motion video turlari

| Tur | Maqsad | Tipik davomiylik | Asosiy dalil/asset |
|---|---|---|---|
| **Kinetik tipografiya** | Tez ritmli matnga asoslangan hook/reklama | 10–30 s | Matn, brend shrift/rang |
| **UI / SaaS / ilova namoyishi** | Feature walkthrough, mahsulot ko'rsatish | 20–45 s | Haqiqiy UI skrinshot/ekran yozuvi |
| **2D/3D explainer** | Murakkab xizmatni 30–60 s da tushuntirish | 30–60 s | Ikonalar, illustratsiya, jarayon sxemasi |
| **Offer & Data motion** | Raqam, grafik, chegirma, taqqoslash animatsiyasi | 10–25 s | **Tasdiqlangan** raqamlar |
| **Brand / Logo bumper** | Intro/outro, esda qolarli brend lahzasi | 5–10 s (`--duration 5\|8\|10`) | Vektor logo, brend tovush |

## 2. Kirish ma'lumotlari

Maqsad (Lead/Sale/Reach/Trust) · tur · format (`9:16` / `16:9` / `1:1`) · davomiylik · auditoriya va awareness · One Big Idea · brend assetlari (logo SVG, rang, shrift) · haqiqiy raqam/UI materiali · til (uz lotin/kirill/ru/en) · ovoz (diktor/TTS/yo'q) · joylashuv (Reels, YouTube, sayt hero). Yetishmasa so'ra.

## 3. Concept & Visual Direction Brief (blueprintning 1-qismi)

| Maydon | Nima yoziladi |
|---|---|
| **Concept** | Bitta g'oya, 1 jumlada; hook mexanizmi |
| **Format/Davomiylik** | Nisbat, soniya; platforma xavfsiz zonalari |
| **Tempo** | Tez kesimli ~120–130 BPM yoki sokin explainer ~90 BPM (`HEURISTIC_PRIOR_MODEL`); musiqa yo'q bo'lsa "beat-less, SFX-led" |
| **Rang palitrasi** | 1 asosiy + 1 aksent + fon + matn (HEX); kontrast: matn/fon o'qiladigan |
| **Shrift iyerarxiyasi** | Sarlavha / kalit so'z (urg'u) / ikkilamchi; kirill/lotin glif qo'llab-quvvatlanishi tekshiriladi |
| **Safe-zone** | 9:16 uchun 720×1200 (yagona manba: `sales-video-scripting.md` §8); 16:9 da pastki subtitr zonasi |
| **Ovoz** | VO uslubi, til, tezlik; musiqa kayfiyati |
| **Tonallik** | 3 sifat ("tez, ishonchli, sodda") + 1 "bo'lmasin" (masalan, "shov-shuvli") |

## 4. Sahnama-sahna Motion Storyboard jadvali (2-qism)

| Sahna # va Vaqt | Diktor / VO | Ekrandagi matn | Vizual kompozitsiya va assetlar | Harakat va o'tish (Motion Cue) | SFX va musiqa aksenti |
|---|---|---|---|---|---|
| S1 `00:00–00:02.5` | Qisqa, urg'uli gap (pauza: `/`, urg'u: **qalin**) | 3–5 so'z, kalit so'z ajratilgan | Fon, UI karta, ikona, mahsulot, grafik — nima qayerda | zoom-in punch · slide-up reveal · morph · counter roll-up · camera pan | whoosh · pop/click · riser · beat drop · silence hit |

Qoidalar:
- **Vaqt:** sahnalar yig'indisi = davomiylik; sahna 1.5–4 s (`HEURISTIC_PRIOR_MODEL`); hook sahnasi ≤ 3 s.
- **VO:** ~2.2–2.6 so'z/soniya; har sahna VO so'z soni ≤ `sahna_soniyasi × 2.6`; nafas/pauza belgilanadi.
- **Ekrandagi matn:** maks. 3–5 so'z (hook'da ≤ 7); kalit so'z urg'u rangida; VO'ni aynan takrorlamaydi — to'ldiradi.
- **Har ~2–4 soniyada** yangi vizual hodisa (retention).
- **Motion cue** aniq nomlanadi: nima, qayerdan qayerga, qancha tez (ease: tez-kirish/sekin-chiqish; ~0.2–0.4 s oraliq — `HEURISTIC_PRIOR_MODEL`). "Chiroyli animatsiya" kabi mavhum ibora yozilmaydi.
- **SFX** harakatga bog'lanadi (whoosh = slide/zoom; pop/click = UI element; riser = taklif oldidan; silence hit = kutilmagan raqam oldidan).
- Oxirgi sahna: CTA + logo, kamida 1.5–2 s qimirlamas "end-card".
- Raqamli sahnalar faqat tasdiqlangan qiymat bilan: `counter roll-up: 0 → [ADD VERIFIED NATIJA]`.

## 5. Asset Checklist (3-qism)

| Asset | Format | Manba/Mas'ul | Holat |
|---|---|---|---|
| Logo | SVG (vektor) + monoxrom variant | Mijoz | [ ] |
| Mahsulot/xizmat rasmi | PNG shaffof fon, ≥ 2× | Mijoz | [ ] |
| UI skrinshot / ekran yozuvi | PNG / MP4; shaxsiy ma'lumotlar yopilgan | Mijoz | [ ] |
| Brend shriftlar | OTF/TTF + litsenziya (lotin + kirill) | Mijoz | [ ] |
| Raqamli dalillar | Tasdiqlangan qiymat + manba | Mijoz | [ ] |
| Musiqa/SFX | Litsenziyalangan; nomi va havola | Dizayner | [ ] |
| Voiceover | Skript tasdig'i + yozuv/TTS ovozi | Producer | [ ] |

Litsenziyasiz stock/musiqa ishlatilmaydi.

## 6. Chiqish formati

1. **Concept & Visual Direction Brief** (§3).
2. **Motion Storyboard jadvali** (§4) — to'liq, vaqt yig'indisi tekshirilgan.
3. **Asset Checklist** (§5) + ochiq `[ADD VERIFIED ...]` ro'yxati.
4. **Self-Audit Score** (`script-quality-rubric.md`; motion uchun "Vizual/ijrochanlik" mezoni = storyboard to'liqligi, motion cue, SFX).

## 7. Handoff: blueprint → render (faqat foydalanuvchi so'rasa)

Blueprint JSON'ga eksport qilinadi (`--json`; sxema `schemas/motion-blueprint-schema.json`). Render so'ralsa — `skills/video/references/video-motion-graphics.md` va `tools/video-run.py` ishlatiladi: bu fayllar blueprint'ni **kirish** sifatida oladi, uni o'zgartirmaydi. AI video generatsiya vositalari uchun har sahna alohida prompt qilib berilishi mumkin (vizual + harakat + davomiylik).

## 8. Tool

```bash
python3 tools/creative-matrix.py video-script --mode motion --lang uz --duration 30 \
  --niche b2b --product "<mahsulot>" --problem "<muammo>" --json
```
Chiqish — sahna skeleti, vaqt yig'indisi, VO limit (so'z/sahna) va asset checklist; kontent mijoz materialidan to'ldiriladi.
