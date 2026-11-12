# Q04 — Byudjet qayta taqsimlash rejasi: Apex E-Commerce

> **HOLAT: FAQAT TAKLIF (DRAFT).** Tizim o'qish rejimida ([[40-xavfsizlik-va-hisob]] §1). Quyidagi har bir o'zgarish Mutation Gate'dan o'tmaguncha hisobda hech narsa o'zgartirilmaydi: (1) Preview, (2) foydalanuvchidan aniq "ha", (3) idempotentlik, (4) tekshiruv, (5) audit yozuvi, (6) rollback.
>
> Manbalar: `examples/demo-brand/BRIEF.md`, `examples/demo-brand/assets/meta_performance.json`, `examples/demo-brand/assets/google_search_terms.json`, `examples/demo-brand/assets/telegram_campaigns.json` · 30 kunlik oynacha, USD · 2026-11-12.

---

## 1. Unit ekonomika asosi (MEASURED — BRIEF.md)

| Ko'rsatkich | Qiymat |
|---|---|
| AOV | 350,000 UZS (~$28) |
| Tannarx + yetkazib berish + komissiya (2%) | 120,000 + 25,000 + 7,000 = 152,000 UZS |
| Sof yalpi foyda = **Break-even CPA** | **198,000 UZS ($15.84)** |
| **Break-even ROAS** | **1.77x** (margin 56.6%) |
| Target CPA / Target ROAS | $11.20 (140,000 UZS) / 2.50x+ |

Hisob vositasi bilan tasdiqlandi: `tyrion_media_calculator(price=350,000; cogs=120,000; shipping=25,000)` → gross profit 198,000 UZS, BE ROAS 1.77x (2026-11-12). Qoida: **CPA > $15.84 bo'lgan har sarf bloki — zararli sarf; CPA < $15.84 — foydali; CPA < $11.20 — maqsadli foyda.** Quyidagi barcha qarorlar shu chegaraga bog'langan.

## 2. Joriy holat: kanallar break-even CPA ga nisbatan (MEASURED — 30 kunlik exportlar)

| Kanal | Sarf (30k) | CPA/CAC | ROAS | BE $15.84 / 1.77x ga nisbat |
|---|---|---|---|---|
| Meta Ads (jami) | $3,480.50 | $14.20 | 1.95x | CPA < BE ✓, ROAS > BE ✓; lekin Target CPA $11.20 dan yuqori |
| — cmp_01 ABO (8 ad set) | $2,610.00 (75%) | $14.66 | 1.88x | BE ostida, LEARNING_LIMITED, kreativ charchoqi (FTIR 54.2%, Freq 3.12) |
| — cmp_02 ASC | $870.50 (25%) | $12.99 | 2.15x | BE va Target CPA ostida; manba: "CBO ga qaraganda kam byudjet berilgan (25%)" |
| Google Ads (jami) | $1,980.00 | $17.84 | 1.57x | **CPA > BE ✗, ROAS < BE ✗ — zararda** |
| — High-Intent so'rovlar | $963.00 | $10.94 (hisob: 963/88) | — | BE va Target CPA ostida — eng kuchli blok |
| — Axlat broad so'rovlar | $478.80 | ∞ (0 conv / 266 klik) | — | **BE'dan cheksiz yuqori — to'liq zarar**, sarf ulushi 24.18% |
| Telegram Ads (jami) | $1,200.00 | $12.12 | 2.65x | CPA < BE ✓, ROAS > BE ✓ — eng samarali kanal |
| — @toshkent_bozori | $450.00 | CPL $1.25 | — | WINNER_SCALE ("haftasiga +15% byudjet oshirish mumkin") |
| — @uzb_biznes_yangiliklari | $550.00 | CPL $1.85 | — | VALIDATED |
| — @kulgu_va_memlar | $200.00 | CPL $3.40 | — | KILL_CANDIDATE: botdan keyin 85% drop-off |

Jami o'lchangan sarf: **$6,660.50 / 30 kun** (plan byudjeti $6,700/oy — BRIEF.md §2 jadvali).

**Diagnostika:** Google'ning umumiy zarari broad-match axlatidan keladi — High-Intent blokning o'zi ($10.94 CPA) eng foydali blok. Shuning uchun Google'dan kanal sifatida voz kechilmaydi; zararli qismi ichidan kesiladi (BRIEF.md "PMax organik brendni yutmoqda" shikoyati alohida tekshiruv talab qiladi — bu rejada o'zgartirilmaydi).

## 3. Qayta taqsimlash rejasi — prioritetlar (jami $0 o'zgarish)

### P1 — Google ichki qayta yo'naltirish: axlat broad → High-Intent EXACT (−$478.80 / +$478.80)

| Yo'nalish | Summa/oy | Asos (break-even CPA'ga bog'liq) |
|---|---|---|
| **Olinadi:** 45 ta salbiy kalit so'z account-level ro'yxatiga qo'shiladi, 4 ta o'lchangan axlat so'rovini kesadi | **−$478.80** | Axlat CPA = ∞ (266 klik, 0 conversion — MEASURED) vs BE $15.84 — cheksiz zarar. Tejalgan summa manbada $478.80/oy deb yozilgan. |
| **Beriladi:** High-Intent EXACT/PHRASE guruhlari | **+$478.80** | Bu so'rovlar CPA $9.95 / $10.88 / $12.46 — hammasi BE $15.84 dan past, ikkitasi Target CPA $11.20 dan ham past (MEASURED). Manbadagi tavsiya aynan shuni buyuradi. |

- Natija (hisob, shart: salbiy ro'yxat faqat o'lchangan axlatni kesadi, conv hajmi saqlanadi): Google blended CPA = ($1,980 − $478.80) / 111 = **$13.52 < $15.84** — kanal zarardan foydaga chiqadi.
- **Spend-Guard eslatma:** Google hisob darajasida net o'zgarish 0% — byudjet oshirilmaydi. Lekin qabul qiluvchi guruhlar kampaniya darajasida bir martda +$478.80 = +49.7% oladi (hisob: 478.80/963) → learning reset. **Bosqichli: 3 bosqich × ≈+$159.60.** Bosqich 1 o'lchandi: $32.10 → $37.42/kun = **+16.57% → PASS** (tyrion_spend_guard). Axlat tomoni pasayish (−) bo'lgani uchun up-guard qo'llanmaydi.
- Bu — live mutation (salbiy kalit so'z qo'shish ham hisob o'zgarishi): **Mutation Gate + foydalanuvchi tasdig'i shart.** BRIEF DoD #2 bilan mos.

### P2 — Telegram → Meta: o'lik kanal pauzasi, ASC bosqichli tezlashadi (−$200 / +$200)

| Yo'nalish | Summa/oy | Asos (break-even CPA'ga bog'liq) |
|---|---|---|
| **Olinadi:** @kulgu_va_memlar pauzasi | **−$200** | KILL_CANDIDATE (MEASURED): CPL $3.40, CTR 0.85%, botdan keyin 85% drop-off — sarf samarasiz; per-channel CAC manbada yo'q (missing_inputs), lekin funnel drop-off zararli sarf belgisi. |
| **Beriladi:** Meta cmp_02 ASC | **+$200** | ASC CPA $12.99 < BE $15.84, ROAS 2.15x > 1.77x (MEASURED); manba: "kam byudjet berilgan (25%)". ASC ulushi 25% → ≈29% (hisob: 1,070.50/3,700). |

- **Spend-Guard eslatma (o'lchangan gate natijalari, 2026-11-12):**
  - Meta hisob darajasi: $116.67 → $123.33/kun = **+5.71% → PASS**.
  - Telegram hisob darajasi: $40.00 → $33.33/kun = **−16.68% → PASS** (pasayish).
  - ASC bir martda +$200: $29.02 → $35.68/kun = **+22.95% → FAIL** (vosita: maks ruxsat +20% → ≤ $34.82; "learning phase reset"). Shuning uchun **2 bosqich × +$100**: $29.02 → $32.35 = **+11.47% → PASS**; bosqichlar orasi 3–4 kun (HEURISTIC).
- **Breakdown Effect tuzog'i (o'lchangan, `tyrion_breakdown_effect`):** ASC'ning past CPA'i qisman eng arzon auktsionni terib olishdan — blended CPA $14.21, agar ustuvor hajm bloki (cmp_01 ABO) o'chirilsa CPA ~$19.61 ga yomonlashadi. Shuning uchun **cmp_01 ABO o'chirilmaydi**; ASC faqat bosqichli tezlashadi va CPA $15.84 ustiga chiqsa darhol to'xtatiladi.
- Pauza + budget — live mutation: **Mutation Gate + foydalanuvchi tasdig'i shart.**

### P3 — Shartli monitoring va kelgusi qadamlar (hozircha pul ko'chmaydi)

- **@toshkent_bozori shkalasi:** manba bo'yicha eng arzon sifatli xaridlar shu kanalda, o'sish temposi **haftasiga +15%** bilan cheklangan (MEASURED tavsiya). Ajratilgan $200 shunga ko'ra ASC'ga ketadi (ASC tezkorroq sig'diradi). Kelgusi oylarda TG winner o'z +15%/hafta temposida o'sadi (HEURISTIC shart: 4+ hafta CPA $15.84 dan oshmasa; har o'sishda Spend-Guard tekshiriladi).
- **cmp_01 ABO tuzilishi:** BRIEF DoD #1 (1-5-5 CBO konsolidatsiya, 8 → 2 ad set) — alohida Change Packet mavzusi; bu rejada faqat byudjet ko'chiriladi, struktura o'zgarmaydi.
- **Haftalik nazorat:** har o'zgarishdan keyin CPA > $15.84 (BE) yoki ROAS < 1.77x bo'lsa — rollback bo'limidagi triggerlar ishlaydi.

## 4. Natijadagi oylik taqsimot (jami o'zgarmagan: $6,700)

| Kanal | Oldin (BRIEF) | Keyin | Farq |
|---|---|---|---|
| Meta Ads | $3,500 | **$3,700** | +$200 (ASC, 2 bosqich × +$100) |
| Google Ads | $2,000 | **$2,000** | $0 net (ichki: broad −$478.80 → High-Intent +$478.80) |
| Telegram Ads | $1,200 | **$1,000** | −$200 (@kulgu pauza) |
| **Jami** | **$6,700** | **$6,700** | **$0 — byudjet oshirilmagan ✓** |

Kutilgan ta'sir (HISOB/HEURISTIC — "CPA saqlanadi" shartli model, MEASURED emas): ASC'ga +$200 ≈ +15 xarid ($200/$12.99); Google'ning $478.80 sarfi BE ostidagi High-Intent CPA ($10.94–$11.20) bilan ≈ +43–44 xaridga aylanadi. Jami ≈ +58–59 xarid/oy; blended ROAS exportlardan hisoblangan ~1.96x bazadan maqsad yo'nalishiga o'sadi. Diqqat: BRIEF'da hozirgi blended ROAS 1.8x deyilgan, exportlardan hisobi ~1.96x (6,787+3,108+3,180)/6,660.50 — ziddiyat [[00-manba]] #5 bo'yicha yangi export foydasiga hal qilinadi va belgilanadi.

## 5. Spend-Guard gate holati (yakuniy jadval)

| O'zgarish | Daraja | Kunlik oldin→keyin | % | Gate holati (o'lchangan) |
|---|---|---|---|---|
| 45 salbiy kalit so'z | Google hisob ro'yxati | byudjet o'zgarmaydi | 0% net | PASS — lekin live mutation → Mutation Gate + tasdiq |
| High-Intent +$478.80 (bir martda) | Guruhlar | $32.10 → $48.06 | +49.7% (hisob) | **FAIL bo'ladi** — shuning uchun 3 bosqich |
| High-Intent bosqich 1 | Guruhlar | $32.10 → $37.42 | +16.57% | PASS |
| ASC +$200 (bir martda) | Meta kampaniya | $29.02 → $35.68 | +22.95% | **FAIL** (maks ≤ $34.82) — shuning uchun 2 bosqich |
| ASC bosqich 1 | Meta kampaniya | $29.02 → $32.35 | +11.47% | PASS |
| Meta hisob | Hisob | $116.67 → $123.33 | +5.71% | PASS |
| TG hisob (@kulgu pauza) | Hisob | $40.00 → $33.33 | −16.68% | PASS |

Har bir amal audit yozuvi bilan journal'ga yoziladi (nima, qachon, nega) — [[40-xavfsizlik-va-hisob]] §1.5.

## 6. Rollback (teskari qadam) — har o'zgarish uchun

| O'zgarish | Qaytarish yo'li | Rollback trigger |
|---|---|---|
| Salbiy kalit so'zlar | 45 ta so'zni account-level ro'yxatdan olib tashlash (idempotent ro'yxat — qayta qo'llash ta'sir qilmaydi), broad byudjetlar eski qiymatga qaytariladi | Amaldan keyin 14 kun Google blended CPA > $15.84 YOKI High-Intent conv hajmi 111 bazadan >20% pasaysa (HEURISTIC trigger) |
| High-Intent bosqichlari | Oxirgi bosqichni bekor qilish: byudjet oldingi bosqich qiymatiga qaytariladi | Bosqichdan keyin CPA > $15.84 (BE) 14 kun davom etsa |
| @kulgu pauza | Kanal eski $200/oy byudjet bilan qayta yoqiladi | Ozod $200 qabul qiluvchisi (ASC) CPA $15.84 dan oshsa — $200 qaytariladi; eslatma: @kulgu o'z-o'zidan samarasiz (85% drop-off), qaytarish faqat vaqtinchalik xavf kamaytirish |
| ASC bosqichlari | ASC daily byudjet eski $29.02/kun ($870.50/30) ga qaytariladi | 1-bosqichdan keyin ASC CPA > $15.84 YOKI learning statusi yomonlashsa — 2-bosqich bajarilmaydi |

## 7. Evidence ajratish va missing_inputs

- **MEASURED_ACCOUNT_DATA:** barcha sarf/CPA/ROAS/CPL/conv/FTIR/Freq raqamlari — 30 kunlik JSON exportlar + BRIEF.md unit ekonomikasi; bosqich gate foizlari — `tyrion_spend_guard` natijalari (2026-11-12); breakdown tuzog'i — `tyrion_breakdown_effect`.
- **HISOB-KITOB (manbadagi raqamlardan):** High-Intent CPA $10.94 (963/88); Google post-cut blended CPA $13.52 (1,501.20/111); ASC ulushi ≈29%; +$478.80 = +49.7%.
- **HEURISTIC_PRIOR_MODEL:** bosqichlar orasi 3–4 kun, 14 kunlik rollback oynasi, "CPA saqlanadi" proyeksiyasi (≈ +58–59 xarid/oy), @toshkent_bozori 4 haftalik shkalash sharti.
- **missing_inputs:** TG kanallari bo'yicha order sonlari va per-channel CAC (faqat CPL bor — @kulgu'ning aniq CAC'i "ma'lumot yo'q"); Google kampaniya darajasidagi byudjet taqsimoti (faqat search-term darajasi — qaysi kampaniyaga yozilishi noma'lum); conversion lag; LTV va takroriy xarid (LTV:CAC baholanmadi); Meta CAPI deduplikatsiya holati (BRIEF'da bayon, o'lchov emas); BRIEF'dagi blended ROAS 1.8x vs exportdan hisoblangan ~1.96x ziddiyati (davr farqi tekshirilmagan).

## 8. Manbalar

1. `examples/demo-brand/BRIEF.md` — unit ekonomika, kanal jadvali, DoD · 2026-11-12.
2. `examples/demo-brand/assets/meta_performance.json` — Meta 30k export (act_88291048201) · 2026-11-12.
3. `examples/demo-brand/assets/google_search_terms.json` — Google search terms audit (google_ads_482_910_3301) · 2026-11-12.
4. `examples/demo-brand/assets/telegram_campaigns.json` — Telegram kanallar export (tg_ads_fragment_8819) · 2026-11-12.
5. `tyrion_media_calculator`, `tyrion_spend_guard`, `tyrion_breakdown_effect` — hisob va gate vositalari · 2026-11-12.
6. Qoidalar: `rules/00-manba.md`, `rules/10-til-va-uslub.md`, `rules/40-xavfsizlik-va-hisob.md`, `rules/70-charter-baseline.md`.
