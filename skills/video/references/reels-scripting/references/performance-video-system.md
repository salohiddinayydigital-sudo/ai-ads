# Performance video tizimi: tadqiqot -> konsept -> brif -> test -> diagnostika -> iteratsiya

`video_script`, `creative_improve` va `meta_strategy` workflow'larida ishlatiladi. `skills/creative/references/ad-creative/` dagi format kutubxonasi va `tools/creative-matrix.py` generatorini to'ldiradi. Generator — skelet: u tuzilma va o'rin egalarini yaratadi; strategiya, isbot va da'volar haqiqiy mijoz ma'lumotidan kelishi shart.

## 1. Tadqiqot kirishlari (har birini belgilang)

Mahsulot/xizmat va taklif; maqsadli auditoriya va xabardorlik bosqichi (unaware, problem-aware, solution-aware, product-aware, most-aware); asosiy muammo; istaklar; e'tirozlar; noyob mexanizm; raqobatchilar; mavjud g'oliblar va o'tgan natija ma'lumotlari; haqiqatan berilgan sharhlar/testimonial'lar; mavjud vizual aktivlar (footage, joy, mahsulot, odamlar, litsenziyalar).

Raqobatchi reklamalari: faqat haqiqatan ko'rilgan reklamalarni tahlil qiling (foydalanuvchi qo'ygan, skrinshotlar, haqiqatan ishlagan asbobdan olingan Meta Ad Library natijalari). Har biri uchun: hook, taklif, angle, tuzilma, vizual yondashuv, asosiy xabar, CTA, auditoriya ishoralari. Kirish imkoni bo'lmasa, "ko'rib chiqilmadi" deb ayting va xulosa qilmang. Strategik insaytni ajratib oling (masalan, ular qaysi e'tirozni e'tiborsiz qoldiradi); ssenariylar, jumlalar yoki o'ziga xos vizualni hech qachon nusxalamang.

## 2. Konsept xilma-xilligi

Konseptlar kamida ikkita jihat bo'yicha farqlanishi kerak: avatar, muammo, istak, xabardorlik bosqichi, angle, taklifni taqdim etish, hikoya tuzilmasi, vizual yondashuv, isbot mexanizmi, CTA. Bir xil videoning boshqa caption'i, ovozi yoki crop'i yangi konsept emas (bir xil Andromeda entity klasteri).

Format tanlash (mosini tanlang, hammasini majburlamang):

| Format | Qachon mos | Nima kerak |
|---|---|---|
| UGC / mijoz sharhi | ishonch va yaqinlik muhim; haqiqiy mijozlar mavjud | haqiqiy mijoz, rozilik, haqiqiy natija |
| Asoschi / ekspert obro'si | yuqori o'ylash, ekspertiza sotadi | kamerada ishonchli shaxs |
| Muammo-yechim demosi | ko'rinadigan o'zgarish, mahsulot/xizmatni ko'rsatish mumkin | haqiqiy narsaning footage'i |
| Taqqoslash | ma'lum muqobillarga nisbatan aniq farqlar | tekshiriladigan taqqoslash faktlari |
| E'tirozlar bilan ishlash | aniq takroriy e'tiroz (narx, ishonch, xavfsizlik) | sotuv/izohlardan haqiqiy e'tiroz |
| Hikoya | hissiy yoki jarayonga boy takliflar | haqiqiy hikoya |
| Ta'limiy | murakkab xizmat, sovuq auditoriya | oddiy o'rgatiladigan insayt |
| Ijtimoiy isbot | kuchli sharhlar/natijalar mavjud | tasdiqlangan isbot |
| Ekran yozuvi / izohga javob | raqamli mahsulot, DM/Telegram voronkasi, FAQ | haqiqiy ekranlar/izohlar |
| Faceless / motion graphics | iste'dod yo'q, tushuntiruvchi videolar | ssenariy + stok/animatsiya huquqlari |
| Taklifga qaratilgan | iliq auditoriya, vaqt bilan cheklangan haqiqiy taklif | haqiqiy taklif va sana |

## 3. Ssenariy paketi (har bir konsept nima beradi)

**A. Strategik brif**: auditoriya, voronka bosqichi, xabardorlik bosqichi, angle, maqsad (qaysi harakat), strategik asos, test gipotezasi (bitta o'zgaruvchi, muvaffaqiyat metrikasi, qaror qoidasi).

**B. Hooklar (>= 3, mazmunan farqli)**, har biri uchun: birinchi vizual kadr, ekrandagi matn, aytiladigan jumla, kamera yo'nalishi, psixologik maqsad. Umumiy ochilishlar yo'q ("Stop scrolling"). Mexanizmni o'zgartiring: aniq odamga murojaat, aniq muammo lahzasi, isbotlay oladigan qarama-qarshi da'vo, e'tirozni teskari qilish, natijadan boshlash (faqat tasdiqlangan natija bilan), asosiy qismda to'lanadigan qiziqish.

**C. Storyboard (vaqt kodli jadval)** ustunlari: `time | duration | visual | camera angle | presenter action | A-roll | B-roll | voice-over | on-screen text | sound/SFX | transition | CTA`. Uzunlik bo'yicha beat tuzilmalari:

| Uzunlik | Beatlar |
|---|---|
| 15 s | 0–3 hook, 3–9 muammodan yechim/isbotgacha bitta g'oyada, 9–13 isbot yoki taklif, 13–15 CTA |
| 30 s | 0–3 hook, 3–10 muammo, 10–20 mexanizm/demo, 20–26 isbot, 26–30 taklif + CTA |
| 45 s | 0–3 hook, 3–12 hikoya/muammo, 12–27 mexanizm va demo, 27–37 isbot va e'tiroz, 37–45 taklif, CTA, xavfni qaytarish (faqat haqiqiy bo'lsa) |

**D. Montaj ko'rsatmalari**: tempo (har bir bo'lim uchun kesish ritmi), o'tishlar, subtitrlar (yoqilgan, o'qiladigan, xavfsiz zonalar ichida), tipografiya va ierarxiya, tovush dizayni (musiqa ovoz ostida, asosiy beatlarda SFX), B-roll tanlash, isbot joylashuvi (eng erta ishonchli lahza), CTA taqdimoti (vizual + og'zaki). Texnik spetsifikatsiyalar (nisbat, o'lcham, xavfsiz zonalar, uzunlik chegaralari, fayl hajmi/formati): topshirishdan oldin Meta'ning joriy kreativ hujjatlariga qarshi tekshiring; vertikal placementlar uchun repozitoriy standarti — markaziy matn-xavfsiz maydonli 9:16 (generator 1080x1920 canvas va 720x1200 xavfsiz quti ishlatadi).

**E. Reklama matni paketi**: asosiy matn variantlari (qisqa va uzun), sarlavhalar, tavsiflar, CTA tugmasi, kampaniya maqsadi va landing sahifa / lead-forma xabar mosligi (birinchi ekran hookdagi va'dani takrorlaydi). Har bir da'vo mijoz bergan ma'lumotga izlanishi kerak; aks holda `[ADD VERIFIED ...]`.

## 4. Da'vo xavfsizligi

`creative-matrix.py` chiqishi `claim_safety` ni o'z ichiga oladi. U o'rin egasi sifatida belgilanmagan foizlar, muddat va'dalari, nisbatlar, kafolatlar va superlativlarni belgilaydi. `needs_verification: true` ni har bir belgilangan element mijoz bergan manba bilan tasdiqlanmaguncha yoki olib tashlanmaguncha to'siq deb qarang. To'qilgan statistikali hookni hech qachon yetkazmang. Sharhlar: haqiqiy, rozilik berilgan, o'zgartirilmagan.

## 5. Test va iteratsiya

Sikl: tadqiqot -> konsept -> ishlab chiqarish brifi -> test -> o'lchov -> diagnostika -> iteratsiya -> masshtab.

Voronka bo'ylab o'lchang: hook rate (3 soniyalik o'ynatishlar / ko'rsatuvlar), hold/retention, ko'rish vaqti, engagement sifati (saves/shares/comments va reaksiyalar), outbound CTR, landing sahifa konversiyasi, lid sifati (CRM malakali daraja), CPA, ROAS, sotuv fikr-mulohazasi. Akkauntning o'z bazasi bilan solishtiring; yo'q bo'lsa, avval uni yig'ing.

```bash
python3 tools/creative-matrix.py iterate --hook-rate 31 --baseline-hook-rate 27 \
  --hold-rate 8 --baseline-hold-rate 14 --outbound-ctr 0.6 --cpa 12 --breakeven-cpa 9 --impressions 5000 --json
```
Chiqish — tartiblangan diagnostik gipotezalar (e'tibor, ushlab turish, klik, landing, lid sifati), yagona ustuvor tuzatish, keyin nimani o'zgartirish va nimani doimiy saqlash, shuningdek ogohlantirishlar (kichik tanlama, ishlatilgan priorlar).

| Naqsh | Sinaladigan gipoteza (xulosa emas) | Keyingi iteratsiya |
|---|---|---|
| Past hook rate | birinchi kadr/ochilish to'g'ri odamni to'xtatmayapti | faqat yangi 0–3 s; asosiy qism, taklif, CTA ni saqlang |
| Yaxshi hook, zaif hold | asosiy qism tempi/hikoyasi yoki va'da-yetkazish bo'shlig'i | asosiy qismni qayta tuzing; hookni saqlang |
| Yaxshi hold, zaif outbound CTR | CTA, taklif aniqligi yoki isbot joylashuvi | CTA/taklif/isbot; hook va asosiy qismni saqlang |
| Yaxshi CTR, zaif landing konversiyasi | xabar nomuvofiqligi, taklif, sahifa tezligi, forma ishqalanishi | kreativni emas, sahifa/formani o'zgartiring |
| Arzon lidlar, yomon sotuv | saralash, auditoriya relevantligi, sotuv ishlov berishi | kreativ/formaga saralovchilar qo'shing, CRM fikr-mulohazasi, qo'ng'iroqlarni tekshiring |
| Sog'lom yuqori oqim metrikalariga qaramay CPA break-even'dan yuqori | iqtisod yoki taklif muammosi | ko'proq kreativdan oldin narx/taklif/marjani qayta ko'ring |

Qoidalar: har bir testda bitta o'zgaruvchi; qaror qoidasini ishga tushirishdan oldin belgilang; iqtisod bosqichidan olingan minimal tanlamagacha g'olibni e'lon qilmang; g'olibni o'lchamini o'zgartirish bilan emas, *g'olib konseptning* yangi variantlari (yangi kreator, yangi sharoit, yangi hook) bilan masshtablang; charchagan kreativlarni qayta montaj bilan emas, yangi konseptlar bilan almashtiring.
