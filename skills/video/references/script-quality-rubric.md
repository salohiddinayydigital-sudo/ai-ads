# Ssenariy sifati rubrikasi — 100 ball, o'tish chegarasi 85

> Har video ssenariy (`sales`, `organic`, `plan` uchun ssenariylar) va motion blueprint (`motion`) yetkazishdan oldin shu rubrika bo'yicha **o'zi tekshiriladi**. Ball < 85 bo'lsa — eng past mezonni tuzatib qayta tekshir (ko'pi bilan 2 aylanish), keyin ham < 85 bo'lsa foydalanuvchiga aniq sabab bilan ayt.
> Bu ichki sifat tekshiruvi: u **kutilayotgan natijaning** (ko'rish, konversiya) bashorati emas. Ball `HEURISTIC_PRIOR_MODEL`; real natija faqat `MEASURED_ACCOUNT_DATA` bilan baholanadi ([[00-manba]]).

## 1. Mezonlar

| Mezon | Maks. | Tekshiruv |
|---|---:|---|
| **Hook kuchi (0–3 s)** | 20 | Vizual + og'zaki + matnli hook uchalasi yozilgan; ≥ 3 variant mexanizmi bo'yicha farqli (sales); salomlashish/tanishtirish ochilishi yo'q; hook mustaqil ma'noli |
| **Retention va ritm** | 15 | Har ~2–4 s da vizual/kadr/matn/SFX o'zgarishi jadvalda ko'rinadi; isbot erta; oxirgi 20% da ham yangi qiymat |
| **Konversiya yoki qiymat mantig'i** | 20 | Sales: Proof + e'tiroz yopish + aniq Offer/CTA (haqiqiy). Organic: aniq foyda + saqlash/ulashish sababi. Plan: funnel balansi, har video uchun 1 metrika, mavzu manbasi |
| **Tabiiy nutq (anti-cliché)** | 15 | Jonli og'zaki til; klişelar yo'q; til versiyalari alohida yozilgan; VO so'z soni vaqtga mos (≤ soniya × 2.6) |
| **Vizual, safe-zone va ijrochanlik** | 20 | 6 ustunli AV-jadval yoki Motion Storyboard to'liq; 720×1200 safe-zone; B-roll/motion cue va SFX aniq; ssenariyni boshqa odam suratga/animatsiya qila oladi |
| **Platforma compliance va halollik** | 10 | Isbotsiz foiz/kafolat/sharh yo'q; `[ADD VERIFIED ...]` ochiq; `claim_safety.needs_verification` hal qilingan; xavf zonalari belgilangan |

## 2. Ball qo'yish qoidasi

- Mezon bo'yicha ball butun son; to'liq → maks., qisman → proporsional, yo'q → 0.
- **Avtomatik bloker (ball qanday bo'lmasin "o'tmadi"):** to'qilgan statistika/sharh/narx; hook'siz video; AV-jadval yoki storyboard yo'q; kafolatlangan tibbiy/moliyaviy natija da'vosi; vaqt yig'indisi davomiylikka teng emas.
- Mezon "qo'llanilmaydi" (masalan, `plan` rejimida kamera ritmi) — qolgan mezonlar maksimumiga qayta shkalalanadi va bu yozib qo'yiladi.

## 3. Rejimga mos tekshiruv ro'yxati

**Sales:** 3–5 hook (uch kanalli) · 2 body · 2 offer+CTA (Direct/Soft) · awareness'ga mos kirish · isbot manbasi · e'tiroz · compliance qatori.
**Organic:** format nomi · 1 foyda · open loop · saqlash sababi · serialda Part N ochiq savoli.
**Plan:** funnel ulushi (+yorlig'i) · ≥ 3 format/hafta · matritsa to'liq · batch plan (lokatsiya, kiyim, yorug'lik, B-roll) · taxminlar ro'yxati.
**Motion:** brief 8 maydon · sahna vaqtlari yig'indisi · VO so'z limiti · motion cue nomlangan · SFX harakatga bog'langan · asset checklist · render kodi yo'q.

## 4. Anti-cliché ro'yxati (qisqartma; to'liq misollar `sales-video-scripting.md` §5)

| Til | Taqiqlangan / shubhali iboralar |
|---|---|
| uz | "Siz ham charchadingizmi?", "Eng sifatli va arzon", "Shoshiling, joylar cheklangan" (haqiqiy cheklovsiz), "Innovatsion yechim", "Hayotingizni o'zgartiring", "Assalomu alaykum, bugun sizlarga …" |
| ru | «Лучшее качество по доступной цене», «Успейте, количество ограничено» (без реального лимита), «Уникальное предложение», «Не упустите шанс», «Всем привет, сегодня …» |
| en | "Game-changer", "Revolutionary", "Stop scrolling", "Hey guys, today …", "Unlock your potential" |

Klişe topilsa: konkret vaziyat yoki aniq ot/fe'l bilan almashtiriladi (umumiy sifatdan voz kech).

## 5. Self-Audit chiqish bloki (ssenariy oxiriga qo'yiladi)

```
Self-Audit: <ball>/100  (hook 18/20 · retention 13/15 · qiymat 17/20 · nutq 13/15 · ijro 17/20 · compliance 9/10)
Blokerlar: yo'q | <ro'yxat>
Ochiq [ADD VERIFIED ...]: <ro'yxat>
Tuzatilgan aylanishlar: <0|1|2>
Yorliq: HEURISTIC_PRIOR_MODEL (ichki tekshiruv, natija prognozi emas)
```

Asbob: `python3 tools/creative-matrix.py video-script --mode <rejim> ... --json` chiqishidagi `self_audit_checklist` avtomatik tekshiriladigan qismlarni (vaqt yig'indisi, VO limit, hook soni, claim_safety) beradi; qolgan mezonlar (nutq tabiiyligi, mantiq) qo'lda baholanadi.
