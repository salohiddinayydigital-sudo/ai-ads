# Video kontent reja va syomka kuni rejasi — `plan`

> **Rejim:** `plan` · **Chiqish:** haftalik/oylik video kontent matritsasi + Batch Shooting Plan (`templates/video-content-plan.md`).
> **Chegara:** reja va syomka tayyorgarligi. Ssenariyning o'zi — `organic-video-content.md` / `sales-video-scripting.md`; montaj — alohida.
> **Manba qoidasi:** funnel nisbati va chastota `HEURISTIC_PRIOR_MODEL` — boshlang'ich taxmin, 4 haftalik o'z natijangiz (`MEASURED_ACCOUNT_DATA`) bilan sozlanadi. Mavzular `USER_PROVIDED` (haqiqiy savollar/mahsulotlar) yoki `ASSUMPTION` deb belgilanadi ([[00-manba]]).

## 1. Kirish (yetishmasa — so'ra)

Biznes va mahsulot/xizmatlar · maqsad (lid/ishonch/qamrov) · platformalar · haftasiga nechta video tushiriladi (real imkoniyat) · kim kameraga chiqadi · mavjud lokatsiya/jihoz · haqiqiy mijoz savollari (komment, DM, sotuv suhbati) · reja davri (1 / 2 / 4 hafta) · mavjud case/natijalar (ruxsat bilan).

## 2. Funnel balansi (boshlang'ich)

| Bosqich | Ulush | Mazmun | Format | CTA |
|---|---|---|---|---|
| **TOFU** | ~50% | Muammo, qamrov, qiziqish | Listicle, mif-buzar, serial, BTS | Soft: saqla, ulash, follow |
| **MOFU** | ~30% | Ishonch, ekspertiza, case | Ekspert, case, taqqoslash, Q&A | Soft→Direct: DM'ga kalit so'z |
| **BOFU** | ~20% | To'g'ridan-to'g'ri taklif | Sotuvchi video (`sales-video-scripting.md`) | Direct: aniq qadam |

Ulush: `HEURISTIC_PRIOR_MODEL`. Sotuv kam-mijozli yoki yuqori o'rtacha chekli bo'lsa BOFU oshiriladi; yangi akkauntda TOFU. Aniq raqamli reja uchun hisobni kod bilan bajaring (video soni × ulush → butun son; yaxlitlash qoidasi: BOFU kamida 1).

## 3. Kontent ustunlari (pillar)

3–4 ta ustun (masalan: Ta'lim · Isbot/Case · Jarayon/BTS · Savol-javob). Har ustun bitta funnel bosqichiga asosan xizmat qiladi. Ustunlar mijoz biznesidan keladi — universal ro'yxat emas.

## 4. Kontent matritsasi (haftalik/oylik)

Har qator = bitta video:

| Sana | Platforma | Funnel | Format | Ustun | Mavzu / Hook (≥ 1 variant) | Maqsadli metrika | CTA | Syomka bloki |
|---|---|---|---|---|---|---|---|---|
| D1 | IG Reels + TikTok | TOFU | Listicle | Ta'lim | "…" | Saves | Soft | A |

Qoidalar: bir kunda bir xil format ketma-ket emas · har 7 kunda ≥ 3 xil format · har videoda **1 ta asosiy metrika** (Watch time / Saves / Shares / DM-Lead) · mavzu manbasi ustunida `USER_PROVIDED` yoki `ASSUMPTION` · 4-haftalikda "sinov slotlari": 2 ta yangi format/hook tajribasi · repurposing: 1 video → Reels + Shorts + TikTok (alohida hook/matn, tarjima emas).

## 5. Batch Shooting Plan (bir kunda 8–12 video)

| Blok | Tarkib |
|---|---|
| **Tayyorgarlik (oldingi kun)** | Ssenariylar chop etilgan/telefonda; mavzu bo'yicha guruhlangan; rekvizit va jihoz ro'yxati; ruxsatlar (mijoz, litsenziya, joy) |
| **Lokatsiyalar** | 2–3 ta fon (ofis, ishlab chiqarish, tashqi) — har lokatsiyada 3–4 video |
| **Kiyim almashinuvi** | 2–3 ta kiyim = 2–3 "kun" ko'rinishi; kiyim bloki bo'yicha tartiblangan |
| **Yorug'lik** | Tabiiy yorug'lik oynadan yoki doimiy yorug'lik; har lokatsiyada bir marta sozlanadi; ovoz: lavalier yoki telefonga yaqin mikrofon |
| **3-Capture** | A-roll (talking head, hook variantlari) → mexanizm B-roll → isbot B-roll (`sales-video-scripting.md` §8) |
| **Umumiy B-roll** | 20–30 klip: qo'llar, jarayon, ekran yozuvi, mijoz bilan muloqot, detal — turli videolarda qayta ishlatiladi |
| **Tartib** | Lokatsiya → kiyim → format; eng murakkab (ko'p matn) videolar energiya baland paytda (boshida); 45–60 daqiqada bir blok |
| **Chiqish** | Fayl nomlash: `YYYYMMDD_<id>_<hookN>` · zaxira: har videoga +1 hook variant ("bepul" test) |

Vaqt prior'lari (blok davomiyligi, 8–12 video/kun) `HEURISTIC_PRIOR_MODEL`: jamoa tezligiga qarab sozlanadi.

## 6. Ko'rsatkichlar va iteratsiya

Haftalik tekshiruv: format bo'yicha hold, saves, shares, DM; eng yaxshi 2 va eng yomon 2 videoning hook'i taqqoslanadi. Qaror: g'olib format ulushi oshadi, yo'qotgan o'rniga yangi sinov. Hisob-kitoblar (CPA, ROAS) — faqat `tools/calculator.py`; reja hisob o'zgartirmaydi.

## 7. Chiqish formati

1. **Brief:** maqsad, davr, platforma, imkoniyat (video/hafta), pillar'lar, funnel nisbati (+ yorlig'i).
2. **Kontent matritsasi** (§4) — oylik reja uchun 4 haftaga bo'lingan.
3. **Batch Shooting Plan** (§5) + tushiriladigan ssenariylar ro'yxati (mavzu → rejim: organic/sales).
4. **Ochiq savollar va taxminlar** (nima `ASSUMPTION`).

## 8. Tool

```bash
python3 tools/creative-matrix.py video-script --mode plan --lang uz --duration 30 \
  --niche local --product "<biznes>" --json
```
(`--duration` — tavsiya etilgan video uzunligi; `--weeks 1|2|4` — reja davri, standart 2; `--per-week` — haftasiga videolar soni, standart 5.)

Handoff: strategiya/ustunlar — `content-planner`; angle/hook — `creative-strategist`; ssenariylar — `video-producer`.
