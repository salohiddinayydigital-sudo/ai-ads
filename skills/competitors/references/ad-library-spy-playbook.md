<!-- v8.3 Targetolog Copilot Pack: ad-spy-analyst metodologiyasi. Ref: agents/ad-spy-analyst.md -->

# Ad Library razvedka playbooki — winner signal → Counter-Angle

> Maqsad: raqobatchi reklamalarini nusxalash emas, ularning **ishlayotgan mexanizmini** tushunib, bozordagi bo'shliqqa uradigan farqlovchi burchak (Counter-Angle) topish.

## 1. Manbalar

| Platforma | Manba | Nima ko'rinadi |
|---|---|---|
| Meta | Meta Ad Library (facebook.com/ads/library) yoki `ads_library_search` MCP | faol e'lonlar, boshlanish sanasi, variantlar soni, platformalar |
| TikTok | TikTok Creative Center (Top Ads) | top kreativlar, nisha, CTR darajasi (agregat) |
| Telegram | Telegram Ads kanal postlari, raqobatchi kanallari | matn (160 belgi), kanal, CTA |
| Google | Ads Transparency Center | qidiruv/YouTube e'lonlari |

Har kuzatuv: skrinshot/URL + sana. Manbasiz kuzatuv qabul qilinmaydi.

## 2. Winner signallari (longevity)

| Signal | Talqin (`HEURISTIC_PRIOR_MODEL`) |
|---|---|
| E'lon ≥ 30 kun faol | kuchli winner ehtimoli (to'xtatilmagan = pul keltiryapti) |
| 14–30 kun | o'rta signal |
| < 14 kun | test bosqichi — winner deb atalmaydi |
| Bir kreativning 3+ varianti | masshtablangan, raqobatchi unga ishonadi |
| Bir xil hook turli formatlarda | angle isbotlangan |

Faol kunlar soni noma'lum bo'lsa — `days_active: null`, "winner" deyilmaydi.

## 3. Dekonstruksiya shabloni

`Raqobatchi | Hook (0–3 s) | Offer | Isbot | Format | CTA | Funnel (Direct/Lead Form/sayt/bot) | Faol kun | Manba`

Ajrat: **kuzatuv** (`OBSERVED` — e'londa ko'rinadi) vs **taxmin** (`ASSUMPTION` — byudjet, ROAS, konversiya). Raqobatchi byudjeti/ROAS'i hech qachon fakt sifatida yozilmaydi.

## 4. Counter-Angle freymvorki

1. **Raqobatchi zaifligi:** ular nimani va'da qilmaydi? (kafolat, tezlik, narx shaffofligi, mahalliy servis)
2. **Bozor charchog'i:** hamma bir xil hook ishlatsa ("Chegirma 50%") — kontrast angle.
3. **Segment bo'shlig'i:** raqobatchi qaysi ICP'ni e'tiborsiz qoldirgan (masalan, B2B, viloyatlar, rus tilli auditoriya).
4. **Isbot ustunligi:** bizda bor, ularda yo'q (real keys, sertifikat, yetkazib berish vaqti).
5. **Format bo'shlig'i:** ular statik — biz UGC video; ular uzun — biz 7 soniyalik.

Har Counter-Angle: `angle | qaysi zaiflikka uradi | gipoteza (metrika + qaror qoidasi)`. Kamida 5 ta.

## 5. Taqiqlar

- Raqobatchi matni/vizualini ko'chirish (mualliflik huquqi va Andromeda dublikat kreativ).
- Raqobatchi brendini o'z reklamasida kamsitish yoki nomini ishlatish (policy).
- E'lon necha kun ishlaganini bilmasdan "winner" deyish.
