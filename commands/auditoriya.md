---
description: Meta Ads auditoriya arxitekturasi — jonli Detailed Targeting qidiruvi va 6-statusli tekshiruv, 4-qatlamli voronka, Exclusion matritsasi, Overlap (<20%) va Saturation hisobi
argument-hint: <mahsulot yoki nisha> [kunlik_byudjet] [mijoz] [--account-id act_...]
---

# /auditoriya — Meta Ads Auditoriya & Detailed Targeting Arxitektori (Andromeda 2 + UZ Standarti)

Vazifa: **$ARGUMENTS**

## 1. Majburiy Ijro Tartibi (`--help` yoki statik lug'atda to'xtab qolmang)

Ishni deterministik dvigatellardan boshlang. Biznes konteksti (mahsulot, yechiladigan muammo, mijoz profili, xarid niyati, yondosh mahsulotlar, mamlakat, kampaniya maqsadi) yetishmasa — avval so'rang.

```bash
# 1. Detailed Targeting (Interest/Behavior) variantlarini rasmiy Meta API orqali qidirish, tekshirish va saralash
python3 "${CLAUDE_PLUGIN_ROOT}/tools/meta-targeting-engine.py" search --product "<mahsulot>" --problem "<muammo>" --customer-profile "<mijoz>" --intent "<xarid_niyati>" --complementary "<yondosh_mahsulotlar>" --niche <ecom|edu|real-estate|medical|b2b|beauty|auto|local> --objective <SALES|LEADS|ENGAGEMENT|TRAFFIC|AWARENESS> --country <ISO_MAMLAKAT> --account-id <act_id> --max-queries 12

# 2. 4-qatlamli auditoriya rejasi va Exclusion matritsasi (unit-ekonomika bilan)
python3 "${CLAUDE_PLUGIN_ROOT}/tools/meta-audience.py" architect --niche <niche> --daily-budget <byudjet> --aov <chek> --margin-pct <marja> --geo <tashkent|regions|uzbekistan> --currency <ISO_VALYUTA> --has-pixel --has-crm

# 3. Ustma-ust tushish (Static Pool Overlap < 20%) va Charchash oynasi (Saturation Sensitivity Window)
python3 "${CLAUDE_PLUGIN_ROOT}/tools/meta-audience.py" overlap --size-a <A> --size-b <B> --shared <S>
python3 "${CLAUDE_PLUGIN_ROOT}/tools/meta-audience.py" saturation --audience-size <hajm> --daily-budget <byudjet> --cpm 3.2
```

- `META_ACCESS_TOKEN` berilgan bo'lsa, 1-qadam faqat o'qish rejimida jonli so'rov yuboradi: `GET /{api_version}/act_{id}/targetingsearch` (yoki global `/search?type=adinterest`) va nomzodlarni `GET /{api_version}/act_{id}/targetingvalidation` orqali tekshiradi.
- Token uch joydan olinadi: muhit o'zgaruvchisi, plugin sozlamasi (`/plugin configure tyrion`) yoki loyiha papkasidagi `.env`. Plugin sozlamasidagi token faqat Tyrion MCP serveriga beriladi — u holda jonli tekshiruvni `tyrion_meta_detailed_targeting` MCP asbobi orqali bajaring.
- Token yo'q yoki so'rov muvaffaqiyatsiz bo'lsa (`API_UNAVAILABLE`), aniq sababni (`MISSING_TOKEN`, `AUTH_401`, `PERMISSION_403`, `RATE_LIMIT_429` va h.k.) va keyingi diagnostika qadamini ayting; `verified_targeting_options` bo'sh (`[]`) qoladi.

## 2. Qat'iy Qoidalar ([[meta-auditoriya-arxitekturasi]] · [[meta-ads-interest-api]])

1. **Uydirma Interest Taqiqlanadi:** Hech qachon tasdiqlanmagan AI taxminini yoki statik lug'atni (`RELATED_UNVERIFIED`) Meta Ads Manager'da mavjud (`VERIFIED_AVAILABLE`) deb ko'rsatmang. Atigi 2 ta mos tasdiqlangan interest topilsa — 2 tasini bering, qo'shimchasini o'ylab topmang.
2. **Solventnost Gipotezasi:** `iPhone`, `Frequent International Travelers`, `Page Admin` kabi signallar daromad kafolati emas, balki sinovdan o'tkaziladigan marketing gipotezasidir (`MARKETING_HYPOTHESIS`).
3. **Geo-Split va Til Izolyatsiyasi:** Toshkent shahri va Viloyatlar bitta CBO kampaniyada aralashtirilmaydi; O'zbek (lotin/kirill) va Rus tilidagi kreativlar alohida ad setlarga bo'linadi.
4. **Exclusion Matritsasi:** Barcha sovuq (TOF) ad setlardan `Purchase_180d`, `CRM_Active_Clients` va `LeadForm_Submitted_90d` istisno qilinadi; ASC da `Existing Customer Cap = 25%`.

## 3. Natija Formati (8 Qismli Targetolog Hisoboti)

1. **Biznes va Auditoriya Tushunchasi** — offer, yechiladigan muammo, mijoz niyati, bozor, maqsad.
2. **Mos Tasdiqlangan Interestlar, Moslik Bo'yicha Saralangan** — avval `VERIFIED_AVAILABLE`, keyin `FOUND_NOT_VALIDATED`; 5 omilli `relevance_score` bo'yicha. Bu ball Tyrion bahosi, Meta balli emas — shunday deb yozing.
3. **Tekshiruv Holati va Rasmiy Meta ID'lar** — `live_check_status`; Meta bergan `name`, `id`, `type`, `path`, `source_endpoint` va `matched_queries` so'zma-so'z saqlanadi.
4. **Har Interest Nega Offerga Mos** — `relevance_reason` va 5 omil bo'yicha tafsilot.
5. **Yaqin Muqobillar, Holati Bo'yicha Ajratilgan** — `FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED` (o'rnini bosuvchi ID bilan), `excluded_low_relevance_options`, `NOT_FOUND` so'rovlar va `RELATED_UNVERIFIED` oflayn gipotezalar.
6. **Tavsiya Etilgan Test Guruhlari va Sababi** — `A: Asosiy mahsulot va to'g'ridan-to'g'ri niyat`, `B: Muammo va yondosh kontekst`, `C: Xaridor xulqi / Solventnost gipotezasi`; har guruhda 2–5 mavzuga oid variant (15+ aloqasiz interestni bir joyga uymang).
7. **Broad Targeting Muqobili** — qachon Andromeda Broad (`Geo + Yosh + Kreativ Hook`) Detailed Targeting'dan yaxshi, qachon test guruhlari o'zini oqlaydi.
8. **Yetishmayotgan Ma'lumot, API Cheklovlari va Keyingi Qadam** — auditoriya kombinatsiyasi, Exclusion va Overlap/Saturation xulosalari bilan.
