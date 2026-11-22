# 9:16 Short-Form Video Ad Scripting & Production Specification

> **Yagona manba (Single Source of Truth):** safe-zone (`1080x1920` → `720x1200`), caption retsepti, 3-Capture syomka tizimi va pacing qoidalari endi `skills/video/references/sales-video-scripting.md` §4 va §8 da yuritiladi. Takrorlanish dublikat va nomuvofiqlik manbai bo'lgani uchun bu yerda faqat qisqa xulosa va havola qoldirildi. Organik videolar: `skills/video/references/organic-video-content.md`; sifat darvozasi: `skills/video/references/script-quality-rubric.md`.

## Qisqa xulosa (batafsil — yagona manbada)

- **Canvas / safe zone:** 1080×1920; matn va asosiy vizual markaziy **720×1200** ichida (yuqori ~250 px, pastki ~470 px, o'ng ~200 px platforma UI uchun bo'sh). Yetkazishdan oldin joriy rasmiy spetsifikatsiyani tekshiring (`UNVERIFIED`).
- **Birinchi 3 soniya:** bir vaqtda vizual hook + 5–7 so'zli matnli hook + og'zaki hook; "Hello guys" yo'q.
- **Tana:** har ~2–4 soniyada pattern interrupt (`HEURISTIC_PRIOR_MODEL`); eski 0.5–1.5 s kesim ritmi montaj uchun yo'riqnoma, ssenariyda o'zgarish nuqtalari AV-jadvalda yoziladi.
- **3-Capture:** A-roll (3 hook + tana + 2 CTA) → mexanizm B-roll → isbot B-roll.
- **Generator:** `python3 tools/creative-matrix.py video-script --mode sales ...` (eski rejimsiz chaqiruv ham ishlaydi).
