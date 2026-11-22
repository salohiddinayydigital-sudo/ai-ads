---
name: video
description: "Video pre-production: sales video scripts, organic/expert video, video content plan + shooting day, motion video storyboard; separate editing/rendering. Use for 'reels skript', 'sotuvchi video', 'video reja', 'motion ssenariy', 'montaj', сценарий рилс, монтаж."
triggers:
- "reels skript"
- "reels ssenariy"
- "tiktok skript"
- "shorts skript"
- "3 soniyalik hook"
- "сценарий рилс"
- "рилс сценарий"
- "видео скрипт"
- "video ssenariy"
- "ugc skript"
- "script a reel"
- "reels scripting"
- "turn this into a reel"
- "montaj"
- "montaj qil"
- "montaj qilib ber"
- "edit qil"
- "video edit"
- "kesib ber"
- "kesish"
- "tahrirla"
- "reels qilib ber"
- "edit this video"
- "montage"
- "cut this video"
- "reframe"
- "subtitr"
- "dead air"
- "EDL"
- "bergan video"
- "videomni"
- "xom material"
- "видео монтаж"
- "смонтировать видео"
- "animatsion"
- "animatsion video"
- "animatsion reels"
- "motion graphics"
- "kinetik"
- "kinetik tipografiya"
- "kinetic typography"
- "after effects"
- "remotion"
- "logo animatsiya"
- "logo reveal"
- "2d animatsiya"
- "infografika video"
- "shape animation"
- "text animation"
- "explainer video"
- "dinamik matn"
- "motion design"
- "noldan video"
- "xom videom yo'q"
- "анимационное видео"
- "моушн графика"
- "sotuvchi video"
- "sotuvchi video ssenariy"
- "video reklama ssenariysi"
- "продающее видео"
- "сценарий продающего видео"
- "sales video script"
- "direct response video"
- "video kontent reja"
- "video reja"
- "video kontent rejasi"
- "syomka kuni rejasi"
- "syomka kuni"
- "batch syomka"
- "видео контент-план"
- "план съёмочного дня"
- "video content plan"
- "batch shooting plan"
- "organik video"
- "ekspert video ssenariy"
- "brend video ssenariy"
- "organic video script"
- "motion ssenariy"
- "motion video ssenariy"
- "motion storyboard"
- "storyboard"
- "motion blueprint"
- "motion video blueprint"
- "motion video script"
- "моушн сценарий"
- "раскадровка"
aliases:
- "reels-script"
- "short-form-script"
- "ugc-script"
- "video-ad-script"
- "reels-scripting"
- "montage"
- "video-cut"
- "subtitles"
- "edl"
- "video-editing"
- "motion-design"
- "kinetic-typography"
- "remotion"
- "after-effects"
- "video-motion-graphics"
- "sales-video-script"
- "organic-video-script"
- "video-content-plan"
- "motion-video-blueprint"
domains:
- "creative"
- "video"
- "copywriting"
- "production"
- "animation"
platforms:
- "instagram"
- "meta"
- "tiktok"
- "youtube"
attached_agents:
- "video-producer"
related_skills: []
references:
- "skills/video/references/sales-video-scripting.md"
- "skills/video/references/organic-video-content.md"
- "skills/video/references/video-content-planning.md"
- "skills/video/references/motion-video-scripting.md"
- "skills/video/references/script-quality-rubric.md"
- "skills/video/references/reels-scripting.md"
- "skills/video/references/video-editing.md"
- "skills/video/references/video-motion-graphics.md"
risk_level: low
output_contract: "Structured deliverable with evidence labels, assumptions, tools actually run and an honest execution report"
---

# video

Video pre-production (g'oya → ssenariy → reja → storyboard) va alohida post-production (montaj/render). Ssenariy qatlami montaj qatlamidan **aniq ajratilgan**.

## Intent Router (4 ustun) — avval rejimni tanla

| Foydalanuvchi so'rovi | Rejim | Yuklanadigan reference | `creative-matrix --mode` | Shablon |
|---|---|---|---|---|
| Reklama/sotuv videosi, UGC, Reels reklama skripti, lid/sotuv uchun video | **Sales Video Script** | `sales-video-scripting.md` | `sales` | `templates/sales-video-script.md` |
| Ekspert/brend/organik video, hikoya, mif, Q&A, serial | **Organic Video** | `organic-video-content.md` | `organic` | `templates/organic-video-script.md` |
| Video kontent reja, oylik/haftalik kalendar, syomka kuni | **Video Content Plan** | `video-content-planning.md` | `plan` | `templates/video-content-plan.md` |
| Motion video ssenariy, storyboard, kinetik tipografiya, explainer, bumper (montajsiz) | **Motion Blueprint** | `motion-video-scripting.md` | `motion` | `templates/motion-video-blueprint.md` |
| Foydalanuvchi videosini montaj qil / render qil / kod bilan animatsiya | **Post-Production** (ssenariy emas) | `video-editing.md` yoki `video-motion-graphics.md` | — | — |

Noaniq bo'lsa (maqsad sotuvmi yoki ishonchmi?) — **bitta** aniqlovchi savol ber; taxmin qilma ([[00-manba]]). Montaj/render fayllari faqat foydalanuvchi montaj yoki render so'raganda ochiladi (token tejash).

## Ish tartibi (pre-production rejimlari)

1. Rejimni tanla → tegishli reference'ni `Read` qil (hammasini emas).
2. Kirish ma'lumotlarini tekshir; yetishmasa `needs_input`. Isbot/raqam/sharh to'qilmaydi — `[ADD VERIFIED ...]`.
3. Skelet: `python3 tools/creative-matrix.py video-script --mode <sales|organic|plan|motion> --lang <uz|ru|en> --duration <15|30|45|60> --hooks 3 ...` (mijoz ma'lumoti bilan to'ldiriladi).
4. Chiqish: Creative Brief Header + 6 ustunli AV-jadval (yoki Motion Storyboard) + Production Notes.
5. **Self-Audit:** `script-quality-rubric.md` bo'yicha ≥ 85/100 (anti-cliché, compliance, vaqt yig'indisi) — oldin yetkazma.

## Qoidalar
Skript 9:16 (boshqa nisbat so'ralsa ko'rsatiladi), birinchi 3 soniyada vizual+og'zaki+matnli hook; salomlashish bilan ochilmaydi; litsenziyasiz stock ishlatilmaydi; da'volar manbali. Safe-zone/caption/3-Capture spetsifikatsiyasining **yagona manbasi** — `sales-video-scripting.md` §8.

## Manbalar

Kerakli faylni `Read` bilan och; hammasini yoppasiga o'qima.

| Fayl | Qachon |
|---|---|
| `skills/video/references/sales-video-scripting.md` | Sotuvchi video: awareness, modulli hook/body/CTA, retention, compliance, texnik spetsifikatsiya |
| `skills/video/references/organic-video-content.md` | Organik/ekspert/brend: 8 format, hook, storytelling, serial |
| `skills/video/references/video-content-planning.md` | Video kontent reja, TOFU/MOFU/BOFU, syomka kuni |
| `skills/video/references/motion-video-scripting.md` | Motion blueprint: brief, storyboard jadvali, asset checklist |
| `skills/video/references/script-quality-rubric.md` | 100 ballik tekshiruv va anti-cliché |
| `skills/video/references/reels-scripting.md` | Eski kirish nuqtasi (orqaga moslik); format kutubxonasi va `reels-scripting/references/performance-video-system.md` (research → test → iterate) |
| `skills/video/references/video-editing.md` | Faqat montaj: ingest, EDL, ritm, subtitr |
| `skills/video/references/video-motion-graphics.md` | Faqat motion kodi/render (`tools/video-run.py`) |

Eski nomlar `manifests/migration-v8.json` da; router ularni alias sifatida taniydi.
