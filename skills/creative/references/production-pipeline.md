# Ishlab chiqarish quvuri: brief → skript → shot list → assetlar

Qattiq bog'liqlik yo'q: sessiyada rasm/video/ovoz konnektori bo'lsa qoralama yaratiladi, bo'lmasa topshirish spetsifikatsiyasi beriladi.

1. **Brief.** Maqsad, auditoriya (persona, ogohlik darajasi), offer, angle, til (UZ/RU/EN, alohida yoziladi), format, joylashuv, CTA, cheklovlar (policy). Nomlash: `ANGLE_HOOK_FORMAT_PERSONA_vN` (`tools/creative-analytics.py` shu bo'yicha teg taklif qiladi).
2. **Skript.** Birinchi 3 soniya hook (2–3 variant), tana, CTA; 9:16 xavfsiz zonalar. Video uchun `skills/video/SKILL.md`; matn qoidalari `skills/creative/references/writing-guidelines.md`.
3. **Shot list.** Kadr raqami, davomiyligi, tasvir, ekran matni, ovoz, B-roll, litsenziya holati.
4. **Assetlar.**
   - *Konnektor bor* (rasm/video/ovoz generatsiyasi sessiyada ko'rinsa, nomi bo'yicha): 1–3 qoralama yarat, "qoralama" deb belgila, inson ko'rigidan o'tmaguncha nashr qilma; generatsiya kredit sarflashi mumkin — avval ayt.
   - *Konnektor yo'q:* topshirish spetsifikatsiyasi — o'lchamlar (1080×1920, 1080×1350, 1080×1080), fayl nomi, ranglar/shrift, matn nusxalari, ovoz skripti, subtitr fayli, litsenziya manbasi.
5. **QA.** Policy tekshiruvi (`compliance-reviewer`), raqam/testimonial to'qilmaganini tekshirish, nomlash va `creatives.json` tegi.
6. **Test.** Yangi kreativlar xilma-xil bo'lsin (angle/format); natija `creative-analytics.py` bilan o'qiladi.
