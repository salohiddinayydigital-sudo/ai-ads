---
name: audience
description: "Meta Ads va ko'p platformali auditoriya arxitekturasi, 6 statusli jonli qiziqish qidiruvi, tekshiruv, 5 omilli relevantlik reytingi, overlap va to'yinish tahlili (Alias: /auditoriya)"
alias_of: auditoriya
argument-hint: "<mahsulot/xizmat> [--niche ecom|edu|real-estate|medical|b2b|beauty|auto|local] [--account-id act_...]"
---

# `/audience` (Alias: `/auditoriya`) — Jonli Meta Detailed Targeting va 4 qatlamli auditoriya arxitektori

Vazifa: **$ARGUMENTS**

## Majburiy jonli bajarish tartibi (hech qachon `--help` yoki statik taksonomiyada to'xtamang!)

1. **1-qadam — Detailed Targeting qiziqishlarini topish, tekshirish va reytinglash (`tools/meta-targeting-engine.py`):**
   Avval doim jonli Detailed Targeting dvigatelini biznes konteksti bilan ishga tushiring (mahsulot/xizmat, hal qilinadigan muammo, mijoz profili, xarid niyati, qo'shimcha kategoriyalar, bozor mamlakati va kampaniya maqsadi):
   ```bash
   python3 tools/meta-targeting-engine.py search \
     --product "<product_or_service>" \
     --problem "<main_problem_solved>" \
     --customer-profile "<target_customer_and_needs>" \
     --intent "<purchase_intent>" \
     --complementary "<complementary_products>" \
     --niche <ecom|edu|real-estate|medical|b2b|beauty|auto|local> \
     --objective <SALES|LEADS|ENGAGEMENT|TRAFFIC|AWARENESS> \
     --country <ISO_COUNTRY> \
     --account-id <act_id_if_available> \
     --max-queries 12
   ```
   - `META_ACCESS_TOKEN` o'rnatilgan bo'lsa, u `GET /{api_version}/act_{id}/targetingsearch` (yoki global `/search?type=adinterest`) bo'yicha faqat o'qish uchun jonli so'rovlar bajaradi va nomzodlarni `GET /{api_version}/act_{id}/targetingvalidation` orqali tekshiradi.
   - Kirish ma'lumotlari yo'q yoki xato bo'lsa (`API_UNAVAILABLE`), aniq xato toifasini (`MISSING_TOKEN`, `AUTH_401`, `PERMISSION_403`, `RATE_LIMIT_429` va h.k.) hamda keyingi diagnostika qadamini ko'rsating, `verified_targeting_options` bo'sh qoladi (`[]`). `RELATED_UNVERIFIED` g'oyalarini hech qachon tasdiqlangan Meta qiziqishi sifatida ko'rsatmang!

2. **2-qadam — 4 qatlamli auditoriya arxitekturasi va exclusion matritsasini qurish (`tools/meta-audience.py`):**
   ```bash
   python3 tools/meta-audience.py architect \
     --niche <niche> \
     --daily-budget <daily_budget> \
     --geo <country_or_city> \
     --currency <ISO_CURRENCY> \
     --aov <aov> --margin-pct <margin_pct> \
     --has-pixel --has-crm
   ```

3. **3-qadam — 8 qismli targetolog hisobotini taqdim eting:**
   1. **Biznes va auditoriyani tushunish** (taklif, hal qilinadigan muammo, mijoz niyati, bozor, maqsad).
   2. **Relevantlik bo'yicha reytinglangan tasdiqlangan qiziqishlar** (avval `VERIFIED_AVAILABLE`, so'ng `FOUND_NOT_VALIDATED`, 5 omilli `relevance_score` bo'yicha saralangan, Meta balli emas, Tyrion baholashi ekani aniq belgilangan).
   3. **Tekshiruv holati va rasmiy Meta ID'lar** (Meta'ning aniq `name`, `id`, `type`, `path`, `source_endpoint` va `matched_queries` qiymatlari o'zgarishsiz saqlanadi; agar faqat 2 ta tegishli tasdiqlangan qiziqish bo'lsa, 2 tasini qaytaring — qo'shimcha qiziqishlarni hech qachon to'qimang).
   4. **Har bir qiziqish taklifga nega mos** (`relevance_reason` va 5 omilli taqsimot).
   5. **Yaqin muqobillar, tekshiruv holati bo'yicha aniq ajratilgan** (`FOUND_NOT_VALIDATED`, almashtiruvchi ID'lar bilan `UNAVAILABLE_OR_CONSOLIDATED`, `excluded_low_relevance_options` va oflayn gipoteza bo'lgan `RELATED_UNVERIFIED`).
   6. **Taklif etilgan test guruhlari va guruhlash sababi** (`Group A: Core Product & Direct Intent`, `Group B: Problem & Complementary Context`, `Group C: Buyer Behavior / Solventnost Hypothesis` — 15+ bir-biriga aloqasiz qiziqishni yig'ish o'rniga har guruhda 2–5 ta mavzuviy variant).
   7. **Mos joyda Broad-targeting muqobillari** (Andromeda Broad `Geo + Age + Creative Hook` qachon Detailed Targeting'dan ustun, qachon Detailed Targeting test guruhlari o'rinli).
   8. **Yetishmayotgan ma'lumotlar, API cheklovlari va keyingi qadamlar**.
