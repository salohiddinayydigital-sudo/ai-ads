<!-- v8.3 Targetolog Copilot Pack: client-comms-lead metodologiyasi. Ref: agents/client-comms-lead.md, rules/10-til-va-uslub.md -->

# Mijoz bilan muloqot playbooklari — Telegram hisobot, e'tiroz, upsell, inqiroz

> Qoida: har raqam tasdiqlangan manbadan (`data-analyst`, `budget-analyst`, `daily-optimizer` yoki foydalanuvchi). Raqam to'qilmaydi, natija kafolatlanmaydi. Mijoz tili — biznes tili, jargon emas.

## 1. 30 soniyalik Telegram digest (haftalik/kunlik)

```
📊 [Mijoz] — [sana oralig'i]
✅ Nima qildik: [1–2 qator]
📈 Raqamlar: Lidlar [n] (o'tgan haftaga [±%]) · 1 lid narxi [summa] · Sarf [summa]
🔧 Nimani o'zgartiryapmiz: [1 qator]
🙏 Sizdan kerak: [aniq so'rov + muddat]
```

Ko'pi bilan 4 raqam. Jargon tarjimasi: CPL → "1 lid narxi", CTR → "reklamani bosganlar ulushi", CPM → "ko'rsatish narxi", ROAS → "har 1 so'm reklamadan qaytgan daromad".

## 2. E'tirozlarga javob (UZ/RU) — ayblamasdan, fakt + keyingi qadam

| E'tiroz | Javob tuzilmasi |
|---|---|
| "Nega sotuv yo'q?" | Lidlar soni va sifati (fakt) → lid → sotuv bosqichi qayerda uziladi (SLA, javob) → birgalikdagi qadam (masalan, 5 daqiqalik javob tartibi) |
| "Kecha arzon edi, bugun nega qimmat?" | Kunlik tebranish normal (auksion) → 7 kunlik o'rtacha → qachon xulosa qilamiz (sana) |
| "Raqobatchida arzonroq ekan" | Narx ≠ natija; bizning 1 lid narxi va sifati → taqqoslash uchun nima kerak |
| "Byudjetni kesaylik" | Kesish ta'siri (lidlar soni prognozi, `HEURISTIC_PRIOR_MODEL`) → muqobil: samarasiz qismni kesish, g'olibni saqlash |

**RU namuna:** «Понимаем беспокойство. За неделю пришло [n] заявок по [цена]. Из них [m] — целевые. Сейчас основная потеря — время первого ответа ([x] часа). Предлагаем: [шаг] до [дата].»

**Taqiq:** sotuv bo'limini qo'pol ayblash; yomon natijani yashirish; "keyingi hafta albatta" kabi va'da.

## 3. Byudjet oshirish / upsell asosnomasi

1. **Isbot:** test natijasi (lid narxi maqsaddan past, yetarli hajm) — manba bilan.
2. **Imkoniyat:** qaysi qism masshtablanadi, kutilgan diapazon (`HEURISTIC_PRIOR_MODEL`, kafolat emas).
3. **Xavf nazorati:** bosqichma-bosqich (+20% qadamlar), stop-loss qoidasi.
4. **Taklif:** byudjet, yangi kanal (masalan, Meta + Telegram Ads), kreativ/video/CRO xizmati — narx va muddat.
5. **Qaror so'rovi:** bitta aniq savol.

## 4. Inqiroz xabari (blokirovka, uzilish, kuchsiz hafta)

`Nima bo'ldi (fakt) → Mijozga ta'siri → Biz nima qilyapmiz (qadamlar) → Keyingi yangilanish vaqti`. Shaffoflik ishonchni saqlaydi; aybdor qidirish emas, yechim.
