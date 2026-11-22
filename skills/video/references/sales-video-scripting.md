# Sotuvchi video ssenariy (Direct-Response / Performance Video) — `sales`

> **Rejim:** `sales` · **Chiqish:** Creative Brief + modulli (Lego) test to'plami + 6 ustunli AV-jadval + Production Notes (shablon: `templates/sales-video-script.md`, §7).
> **Chegara:** faqat pre-production. Montaj/render — `video-editing.md` va `tools/video-run.py` (bu fayl ularga tegmaydi).
> **Manba qoidasi:** raqamli chegaralar (2–4 s pattern interrupt, 3–5 hook, so'z/soniya) — `HEURISTIC_PRIOR_MODEL`; o'z hisobingizdagi hook/hold rate bilan almashtiring. Statistika, sharh, narx, kafolat to'qilmaydi: `[ADD VERIFIED ...]` placeholder ([[00-manba]]).

Yuklash tartibi: bu fayl → kerak bo'lsa `reels-scripting/references/performance-video-system.md` (research → test → iterate sikli) → yakunda `script-quality-rubric.md` (85/100 darvoza).

## 1. Kirish ma'lumotlari (yetishmasa — so'ra, taxmin qilma)

Mahsulot/xizmat va **haqiqiy** taklif · avatar va asosiy muammo · awareness bosqichi · tasdiqlangan isbot (natija, sharh, litsenziya, ruxsat) · asosiy e'tiroz · til (uz lotin/kirill, ru, en) · maqsad (lid / sotuv / qamrov) · mavjud material (kadr, lokatsiya, odam). Yo'q narsa `[ADD VERIFIED ...]` bo'ladi, to'qilmaydi.

## 2. Awareness bosqichi → ssenariy kirishi va dalil chuqurligi

| Bosqich | Hook nimani ochadi | Tana nimaga urg'u beradi | Dalil chuqurligi | CTA turi |
|---|---|---|---|---|
| **Unaware** | Odam bilmagan muammo/xarajat lahzasi, hikoya | Muammoni "ko'rsatish", mahsulotni kechroq (≥ 40% vaqtdan keyin) kiritish | Yengil: vizual ko'rsatish, kuzatuv | Soft (saqlash, profilni ko'rish) |
| **Problem-aware** | Aniq og'riq momenti, "shu menga tegishli" | Yashirin sabab/mexanizm | O'rta: mexanizm demosi | Soft → Direct |
| **Solution-aware** | Hal etish usullari taqqosi, qarshi fikr | Nega aynan bu yo'l (farq) | Yuqori: taqqoslash, case | Direct |
| **Product-aware** | E'tiroz/shubha ("qimmat", "ishonmayman") | E'tirozni yopish + isbot | Eng yuqori: haqiqiy sharh/natija | Direct + risk reversal (faqat haqiqiy) |
| **Most-aware** | Taklif va muddat (haqiqiy) | Offer + keyingi qadam | Minimal: taklif tafsiloti | Direct, aniq qadam |

## 3. Modulli (Lego) test tuzilmasi

Har sotuvchi video bitta qattiq matn emas — **kombinatsiya to'plami**: `H × B × C`.

| Modul | Soni | Vaqt | Tarkib |
|---|---|---|---|
| **Hook** | 3–5 (kamida 3, mexanizmi bo'yicha farqli) | 0–3 s | Vizual hook + Matnli hook + Og'zaki hook — uchalasi ham yoziladi |
| **Body** | 2 | 3–25 s | Muammo → yashirin sabab/mexanizm → vizual isbot (demo/case) → asosiy e'tirozni yopish |
| **Offer + CTA** | 2 | oxirgi 5–8 s | Aniq taklif (narx/bo'lib to'lash/bonus/kafolat — faqat haqiqiy) + xavfsiz keyingi qadam; biri Direct, biri Soft |

Hook mexanizmlari (har biri boshqasidan farqli bo'lsin): **og'riq lahzasi** · **kutilmagan fakt** (isbotlanadigan) · **qarshi fikr** · **natija namoyishi** (faqat tasdiqlangan) · **to'g'ridan-to'g'ri chaqiriq** (aniq odamga). Umumiy ochilishlar ("Assalomu alaykum, bugun…", "Stop scrolling") taqiqlanadi.

Test qoidasi: bir testda bitta o'zgaruvchi (odatda faqat hook); qaror qoidasi ishga tushirishdan oldin yoziladi; g'olibni minimal namunagacha e'lon qilma (`tools/calculator.py`/economics); g'olib konsept yangi variantlar bilan masshtablanadi ([[funnel-2-kreativ-format]], [[kreativ-hit-rate]]).

## 4. Retention mexanikasi (AV-jadvalga majburiy kiritiladi)

- Har ~2–4 soniyada kamida bitta **pattern interrupt**: rakurs/crop almashishi, B-roll, ekrandagi matn/grafika, SFX, intonatsiya o'zgarishi (`HEURISTIC_PRIOR_MODEL`).
- Birinchi 3 soniya: harakat birinchi kadrda; matn 3–5 so'z (≤ 7); og'zaki gap o'zini o'zi tushuntiradi (ovozsiz ham ma'no bor).
- Isbot **eng erta ishonarli** momentda (3–10 s ichida), oxirida emas.
- Nutq tezligi: ~2.2–2.6 so'z/soniya (`HEURISTIC_PRIOR_MODEL`); 3 soniyali hook ≈ 7–8 so'zdan oshmasin. 30 s videoda og'zaki matn ≈ 65–78 so'z.
- Dead air > 0.25 s kesiladi (montaj bosqichida; ssenariyda pauza faqat ataylab "silence hit" sifatida yoziladi).

## 5. Jonli til va anti-cliché filtri (UZ / RU / EN)

- Mijozning haqiqiy og'zaki nutqiga yaqin, qisqa, urg'uli gaplar. Gap boshiga fe'l yoki aniq ot; bitta gapda bitta fikr.
- **Tarjima emas — alohida yozilgan versiya.** uz lotin ≠ uz kirill ≠ ru: kirillcha versiya lotindan translit emas ([[10-til-va-uslub]]).
- Taqiqlangan klişelar (misollar): *"Siz ham charchadingizmi?"*, *"Eng sifatli va arzon"*, *"Shoshiling, joylar cheklangan"* (haqiqiy cheklov bo'lmasa), *"Innovatsion yechim"*, ru: *«Лучшее качество по доступной цене»*, *«Успейте, количество ограничено»*; en: *"game-changer"*, *"revolutionary"*, *"Stop scrolling"*.
- `tools/creative-matrix.py` chiqishidagi `ai_tells_check` va `claim_safety` natijasini o'qing; `needs_verification: true` — bloker.

## 6. Platforma compliance darvozasi (Meta / TikTok / YouTube)

Reklama siyosati o'zgaradi — joriy rasmiy hujjatni tekshirmasdan "ruxsat/taqiq" deb **qat'iy aytilmaydi** (`UNVERIFIED` → tekshiruv shart). Ssenariyda quyidagi xavf zonalari belgilab o'tiladi:

| Xavf | Nima qilinadi | Xavfsiz muqobil |
|---|---|---|
| Kafolatlangan tibbiy/moliyaviy natija | Yozilmaydi | "Natija individual; maslahat uchun yoziling" (haqiqiy shart bilan) |
| "Before/after" (ayniqsa tana, salomatlik) | Platforma siyosatini tekshir; xavfli bo'lsa ishlatma | Jarayon namoyishi, mijoz roziligi bilan ish natijasi (soha ruxsat bersa) |
| Shaxsiy atributga murojaat ("sizning kasalligingiz…", qarz, vazn) | Yozilmaydi | Vaziyatga murojaat: "Agar … bo'lsa" |
| Isbotsiz superlativ/foiz/muddat | `[ADD VERIFIED ...]` | Tasdiqlangan raqam yoki raqamsiz formula |
| Soxta shoshilinchlik / sharh | Taqiq | Haqiqiy muddat/haqiqiy sharh |

Regulyatsiyalangan soha (tibbiyot, moliya, ta'lim kafolati) → `compliance-reviewer` agentiga yo'naltir; [[40-xavfsizlik-va-hisob]].

## 7. Chiqish formati (majburiy 3 qism)

1. **Creative Brief Header:** biznes/mahsulot · maqsad (Lead/Sale/Reach/Trust) · auditoriya va awareness · format va davomiylik · **One Big Idea** · test gipotezasi (bitta o'zgaruvchi, metrika, qaror qoidasi).
2. **6 ustunli AV-jadval** (har modul uchun):

| Vaqt | Bosqich | Vizual / Kadr (A-Roll & B-Roll) | Spiker nutqi / VO | Ekrandagi matn (Safe-Zone) | Kamera, Ritm & SFX |
|---|---|---|---|---|---|
| 0:00–0:03 | Hook | Yaqin plan + keskin harakat | Qisqa, urg'uli gap | 3–5 so'z | Punch-in + hit |

3. **Production Notes:** spiker intonatsiyasi/tempi, yorug'lik/kadr, qo'shimcha B-roll ro'yxati, 3-Capture syomka ro'yxati, **Self-Audit Score** (`script-quality-rubric.md`), claim_safety natijasi, ochiq `[ADD VERIFIED ...]` ro'yxati.

## 8. Texnik spetsifikatsiya — yagona manba (9:16)

Boshqa fayllar (`skills/creative/references/ad-creative/references/video-ad-scripts-and-specs.md`) shu bo'limga havola qiladi; takrorlanmaydi.

- **Canvas:** 1080×1920 (9:16). **Text/key-visual safe zone:** markaziy **720×1200**: yuqori ~250 px, pastki ~470 px (handle, matn, CTA tugma, progress), o'ng ~200 px (Like/Comment/Share/Save) bo'sh. Joriy rasmiy spetsifikatsiyani yetkazishdan oldin tekshir (`UNVERIFIED` → Meta creative docs).
- **Sarlavha retsepti:** oq to'ldirish + qora kontur 3–4 px, pastki-o'rta uchlikda (Y ≈ 1150–1350), qatorda 3–5 so'z, nutq bilan sinxron.
- **3-Capture syomka:** (1) A-roll: 3 hook + to'liq tana + 2 CTA; (2) mexanizm B-roll (5–8 klip: yaqin plan, ekran yozuvi, jarayon); (3) isbot B-roll (haqiqiy mijoz natijasi, sharh ekrani, yetkazib berish, ofis).
- **Audio:** −14 LUFS integrated, −1 dBTP (montaj bosqichi maqsadi).

## 9. Tool

```bash
python3 tools/creative-matrix.py video-script --mode sales --lang uz --duration 30 --hooks 3 \
  --niche medical --product "<mahsulot>" --problem "<muammo>" [--price <narx>] --json
```
Chiqish — skelet va placeholderlar; strategiya, isbot va da'volar mijoz ma'lumotidan keladi. Eski `video-script` (rejimsiz) o'zgarmagan.

Handoff: kontent reja → `content-planner`; reklama matni (primary text/headline) → `creative-strategist`; montaj — `video-editing.md` (faqat foydalanuvchi so'rasa).
