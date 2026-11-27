# Repozitoriy holati kontrakti

`/ads status` va `/ads next` uchun deterministik yadrodan foydalaning; tayyorlikni
matndan taxmin qilmang va tarmoq chaqiruvlarini bajarmang.

```bash
python -m claude_ads_core status --root . --as-of YYYY-MM-DD
python -m claude_ads_core next --root . --as-of YYYY-MM-DD
```

Aniq reliz-darvoza hisoboti uchun ixtiyoriy ravishda `--release-gate PATH` bering.
`artifact-order-v1` siyosati aynan bitta natijani shu tartibda tanlaydi: tasdiqlanmagan
yuk ko'taruvchi da'vo, eskirgan yuk ko'taruvchi da'vo, e'lon qilingan birinchi
yetuklik to'sig'i, birinchi kanonik muvaffaqiyatsiz reliz tekshiruvi, birinchi o'chirilgan
ballash profili, birinchi o'chirilgan imkoniyat, so'ng qanoatlantirilmagan eng past
yetuklik darajasi. Repozitoriy manifestlari va ixtiyoriy hisobot — yagona dalil.
Majburiy kirishlar yo'q yoki noto'g'ri tuzilgan bo'lsa, tizim yopiq holda (fail closed) to'xtaydi.
