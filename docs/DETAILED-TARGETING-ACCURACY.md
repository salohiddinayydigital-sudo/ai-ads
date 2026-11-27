---
name: detailed-targeting-accuracy
description: "Tyrion v8.3 Detailed Targeting aniqlik dvigateli — arxitektura, rasmiy Meta Marketing API v26.0 endpointlari, 6 ta tekshiruv statusi, keshlash va test qo'llanmasi"
tags: [meta-ads, targeting, api, accuracy, validation]
source: "tools/meta-targeting-engine.py + Meta Marketing API v26.0"
updated: 2026-10-20
---

# 🎯 Tyrion v8.3 — Detailed Targeting aniqlik dvigateli (`tools/meta-targeting-engine.py`)

## 1. Umumiy ko'rinish va asosiy dizayn tamoyili

Meta Ads kampaniyalarini rejalashtirishda AI tizimlari mahsulot tavsifidan Meta Ads Manager'da **mavjud bo'lmagan**, yoki Meta bekor qilgan yoxud birlashtirgan, ishonarli ko'rinadigan qiziqish yoki xatti-harakat nomlarini tez-tez to'qiydi.

Tyrion'ning **Detailed Targeting aniqlik dvigateli** (`tools/meta-targeting-engine.py`, `tools/meta-audience.py`, `tools/tyrion-mcp-server.py` va `tools/tyrion.py` ga integratsiya qilingan) **rasmiy Meta API dalili** bilan **tasdiqlanmagan AI/evristik qidiruv g'oyalari** o'rtasida qat'iy chegara o'rnatadi:

- **Nol to'qima qiziqish:** AI kengaytirgan sinonimlar (o'zbek lotin, o'zbek kirill, rus va ingliz tillarida), statik nisha lug'atlari (`NICHE_TAXONOMY`) va xarid qobiliyati (*Solventnost*) g'oyalari faqat **qidiruv so'rovlari** yoki **tasdiqlanmagan gipotezalar (`RELATED_UNVERIFIED`)** sifatida qaraladi — hech qachon tasdiqlangan Meta targeting variantlari sifatida emas.
- **Aniq nom va ID'ni saqlash:** Rasmiy API natijalari Meta qaytargan aniq `name` va `id` ni mashina tarjimasisiz va o'zgartirishsiz saqlaydi.
- **ID + Type bo'yicha dublikatlarni olib tashlash:** Natijalar `name` bo'yicha emas, qat'iy `(id, type.lower())` bo'yicha deduplikatsiya qilinadi; shu tariqa o'xshash yoki bir xil ko'rinadigan nomli turli Meta targeting obyektlari saqlanadi.
- **To'qilgan reach chegaralari yo'q:** `audience_size_lower_bound` va `audience_size_upper_bound` **faqat** Meta API aniq qaytargandagina to'ldiriladi (aks holda `None`).

## 2. Ishlatiladigan rasmiy Meta Marketing API endpointlari

Dvigatel sozlangan `META_GRAPH_API_VERSION` ni (`.env` / muhitdan standart `v26.0`) ishlatadi va [Meta Marketing API Reference](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/reference/detailed-targeting) da hujjatlashtirilgan to'rtta rasmiy faqat o'qish endpointini qo'llab-quvvatlaydi:

| Endpoint | HTTP yo'li | Vazifasi va qamrovi | Majburiy parametrlar va ruxsatlar |
|---|---|---|---|
| **Global Targeting Search** | `GET /{api-version}/search?type=adinterest` | `ad_account_id` (`act_...`) berilmaganda global reklama qiziqishlari katalogidan qidiradi ([Targeting Search Reference](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/reference/targeting-search)). | `q`, `type=adinterest`, `limit`, `locale`. Haqiqiy `META_ACCESS_TOKEN` kerak. |
| **Account Targeting Search** | `GET /{api-version}/act_{ad_account_id}/targetingsearch` | Akkauntga bog'langan detailed targeting variantlarini (qiziqish, xatti-harakat, demografiya) qidiradi va `audience_size_lower_bound` hamda `audience_size_upper_bound` qaytaradi ([Ad Account Targetingsearch](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/targetingsearch)). | `q`, `limit`, `locale`. `act_{ad_account_id}` uchun `ads_read` yoki `ads_management` kerak. |
| **Targeting Suggestions** | `GET /{api-version}/act_{ad_account_id}/targetingsuggestions` | Boshlang'ich targeting ID'lariga asoslanib, Meta tavsiya qilgan qo'shni targeting variantlarini qaytaradi ([Ad Account Targetingsuggestions](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/targetingsuggestions)). | `targeting_list` (`{"id", "type"}` JSON massivi), `limit`. Ixtiyoriy (`--suggestions`). |
| **Targeting Validation** | `GET /{api-version}/act_{ad_account_id}/targetingvalidation` | Muayyan targeting ID'lari akkaunt uchun hozir faol va yetkazib berilishi mumkinligini tekshiradi, bekor qilingan yoki birlashtirilgan qiziqishlarni belgilaydi ([Ad Account Targetingvalidation](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/targetingvalidation)). | `targeting_list` (JSON massivi). `act_{ad_account_id}` uchun `ads_read` kerak. |

## 3. 6 ta tekshiruv statusining ma'nosi (`validation_status`)

Hisobotdagi har bir targeting elementi yoki so'rovi quyidagi oltita statusdan aynan bittasini oladi:

1. **`VERIFIED_AVAILABLE`**: Rasmiy Meta Graph API qidiruv endpointida (`/search`, `targetingsearch` yoki `targetingsuggestions`) topilgan **va** `/{ad-account-id}/targetingvalidation` tomonidan `valid: true` deb tasdiqlangan.
2. **`FOUND_NOT_VALIDATED`**: Rasmiy Meta Graph API qidiruv endpointida topilgan (`id` va `name` haqiqiy), lekin akkaunt darajasidagi `/{ad-account-id}/targetingvalidation` bajarilmagan (masalan, `--account-id` berilmagan yoki `--no-validate` o'rnatilgan).
3. **`UNAVAILABLE_OR_CONSOLIDATED`**: Rasmiy Meta API javobi (`targetingvalidation` yoki bekor qilish metama'lumotlari) variant yaroqsiz (`valid: false`), bekor qilingan yoki boshqasiga birlashtirilganini ko'rsatadi. Meta almashtirish metama'lumotini bersa, `validation_details.consolidated_into` eski variantni yangi `{id, name, type}` ga bog'laydi.
4. **`RELATED_UNVERIFIED`**: Meta rasmiy API'sida **tasdiqlanmagan** semantik taklif, ko'p tilli sinonim, statik `NICHE_TAXONOMY` urug'i yoki `SOLVENTNOST_HYPOTHESES` elementi. Doim `is_verified_meta_option: False` bilan keladi.
5. **`NOT_FOUND`**: Qidiruv so'rovi jonli Meta Graph API'ga yuborilgan va `0` ta mos element qaytgan. *Muhim:* `NOT_FOUND` — bajarilgan so'rov satri bo'yicha natija qaytmaganini bildiradi; bu Meta'da boshqa taksonomiya nomi ostida tegishli tushuncha yo'qligining mutlaq isboti emas.
6. **`API_UNAVAILABLE`**: Jonli Graph API tekshiruvi `META_ACCESS_TOKEN` yo'qligi, HTTP `401` (ruxsatsiz), HTTP `403` (ruxsat yetarli emas), HTTP `400` (noto'g'ri so'rov), HTTP `429` (backoff'dan keyin rate limit tugagan), HTTP `5xx` (server xatosi), tarmoq timeout'i yoki noto'g'ri JSON sababli yakunlanmagan. **`API_UNAVAILABLE` bo'lganda hech bir statik yoki AI taklif qilgan variant hech qachon `VERIFIED_AVAILABLE` yoki `FOUND_NOT_VALIDATED` deb belgilanmaydi.**

## 4. Qidiruv natijasi va akkauntga yetkazib berish farqi hamda relevantlik bali

- **Qidiruv natijasi (`FOUND_NOT_VALIDATED`) va yetkazib beriladigan variant (`VERIFIED_AVAILABLE`):** Global `/search?type=adinterest` da ko'ringan qiziqish muayyan reklama akkaunti, hudud yoki Special Ad Category (`HOUSING`, `EMPLOYMENT`, `CREDIT`, `ISSUES_ELECTIONS_POLITICS`) uchun baribir cheklangan bo'lishi mumkin. Kampaniyalarni ishga tushirishdan oldin `targetingvalidation` ni bajarish uchun doim `--account-id act_...` bering.
- **`relevance_reason` — AI fikri, Meta isboti emas:** Har bir topilgan variant `relevance_reason` bilan birga `"relevance_is_ai_opinion_not_meta_proof": True` ni o'z ichiga oladi. Semantik relevantlik hech qachon `validation_status` o'rnini bosmaydi.
- **Xarid qobiliyati (*Solventnost*) gipotezalari:** `Engaged Shoppers`, `Frequent International Travelers`, `Facebook Page Admins` yoki flagman qurilma modellari kabi signallar `MARKETING_HYPOTHESIS` deb belgilanadi (API orqali tasdiqlanmaguncha `RELATED_UNVERIFIED`), hech qachon kafolatlangan daromad filtri sifatida emas.

## 5. Zaxira va keshlash xatti-harakati

- **Xavfsiz oflayn zaxira:** `META_ACCESS_TOKEN` yo'q yoki API ishlamasa, `live_check_status.status` = `API_UNAVAILABLE`, `verified_targeting_options` bo'sh (`[]`), `recommended_audience_combinations.status` = `NO_VERIFIED_OPTIONS_AVAILABLE` bo'ladi va nomzod qidiruv urug'lari `related_unverified_ideas` ostida alohida ro'yxatlanadi.
- **TTL kesh kelib chiqishi:** `--cache-file <path>` ishlatilganda har bir yozuv `api_version`, `fetched_at_utc`, `fetched_epoch`, `ttl_seconds` va `query_params` ni saqlaydi. Keshdagi yozuvning `api_version` qiymati joriy `META_GRAPH_API_VERSION` dan farq qilsa yoki yoshi `ttl_seconds` dan oshsa, kesh rad etiladi va hech qachon joriy tekshiruv sifatida berilmaydi.

## 6. CLI va MCP'dan foydalanish

```bash
# 1. Ad Account ID bilan qidirish va tekshirish (targetingsearch + targetingvalidation ishlaydi)
python3 tools/meta-targeting-engine.py search \
  --product "Klassik erkaklar kostyumi" \
  --niche ecom \
  --customer-profile "Toshkentdagi 25-45 yoshli tadbirkorlar" \
  --account-id act_123456789 \
  --suggestions --json

# 2. meta-audience.py yoki Master CLI orqali
python3 tools/meta-audience.py detailed-targeting --product "Стоматология имплантация" --niche medical --language ru --json
python3 tools/tyrion.py targeting search --product "Ko'chmas mulk novostroyka" --niche real-estate --special-ad-category HOUSING
```

## 7. Avtomatik testlarni ishga tushirish

```bash
# To'liq oflayn unit va lokal-HTTP test to'plamini ishga tushirish (136+ test, jonli Meta akkauntiga bog'liq emas)
python3 -m unittest discover tests -v

# Ixtiyoriy jonli integratsiya smoke testi (faqat META_ACCESS_TOKEN va TYRION_RUN_LIVE_META_SMOKE=1 o'rnatilganda ishlaydi)
TYRION_RUN_LIVE_META_SMOKE=1 python3 -m unittest tests/test_tyrion_tools.py -k LiveMetaSmoke -v
```

## 8. Ma'lum cheklovlar

- **Jonli akkaunt tekshiruvi `ads_read` ni talab qiladi:** Jonli `META_ACCESS_TOKEN` va `ads_read` ruxsati berilgan `act_<AD_ACCOUNT_ID>` bo'lmasa, `/{ad-account-id}/targetingsearch`, `targetingsuggestions` va `targetingvalidation` haqiqiy Meta reklama akkaunti bilan tekshirilmaydi; unit testlar protokol va chekka holatlarni lokal `ThreadingHTTPServer` ga qarshi tekshiradi.
- **Mintaqaviy reach chegaralari:** `targetingsearch` qaytargan `audience_size_lower_bound` va `audience_size_upper_bound` to'liq geo-targeting spetsifikatsiyali `reachestimate` / `delivery_estimate` orqali toraytirilmasa, global yoki standart locale chegaralarini aks ettiradi.

**Bog'liq:** [[meta-ads-interest-api]] · [[meta-auditoriya-arxitekturasi]] · [[40-xavfsizlik-va-hisob]] · [[00-manba]]


## 4. Biznes kontekstidan so'rov yaratish va 5 omilli relevantlik reytingi (yangilanish)

### 4.1 Ustuvorlik bo'yicha biznes konteksti so'rovlarini kengaytirish (`expand_search_queries`)
Qidiruv so'rovlari haqiqiy biznes kontekstidan qat'iy ustuvorlik tartibida yaratiladi, shunda foydalanuvchining aniq so'rovlari sinonimlar yoki umumiy nisha urug'lari tomonidan **hech qachon** siqib chiqarilmaydi:
1. **`P1_EXPLICIT_USER_QUERY`**: Foydalanuvchi bergan barcha `--query` argumentlari (kiritilishi kafolatlangan; aniq so'rovlar `--max-queries` dan oshsa, `effective_max` kengayadi).
2. **`P2_EXPLICIT_QUERY_EXPANSION`**: Aniq so'rovlar uchun tanlab tuzilgan o'zbek lotin, o'zbek kirill, rus va ingliz tilidagi domen tushunchalari.
3. **`P3_BUSINESS_CONTEXT_SYNONYM` va `P3_DIRECT_PRODUCT`**: `--product`, `--problem` (`problem_solved`), `--needs` (`customer_needs`), `--intent` (`purchase_intent`), `--customer-profile` va `--complementary` (`complementary_products`) dan ajratilgan tushunchalar.
4. **`P4_PROBLEM_AND_INTENT` va `P5_NICHE_INTENT`**: Muammo/niyat iboralari va kampaniya maqsadi signallari (`SALES`, `LEADS`, `ENGAGEMENT`, `TRAFFIC`, `AWARENESS`).
5. **`P6_NICHE_SEED_FALLBACK`**: Zaxira nisha urug'lari (faqat `--max-queries` ostida o'rin qolsa ishlatiladi).

### 4.2 Shaffof 5 omilli relevantlik reytingi (`score_and_rank_candidate`)
API natijalarining dastlabki 5 tasini kelish tartibida tavsiya qilish o'rniga, har bir nomzod 5 ta shaffof omil bo'yicha ballanadi (`0..100`, `SYSTEM_RELEVANCE_ESTIMATE_NOT_META_SCORE_OR_PERFORMANCE_GUARANTEE` deb belgilangan):
- **Mahsulot/xizmatga bevosita mos kelish (`0..35` ball)**
- **Mijoz muammosi va xarid niyatiga mosligi (`0..25` ball)**
- **Semantik va qo'shimcha taklif aloqasi (`0..20` ball)**
- **Meta kategoriya yo'li, mavzu va tavsifga mosligi (`0..10` ball)**
- **Aniqlik, kenglik va shovqin tuzatishi (`-45..+10` ball)** — ko'ngilochar omonimlarni (guruhlar, filmlar, o'yinlar, tekinlar) va haddan tashqari keng umumiy atamalarni jarimaga tortadi, `relevance_score < --min-relevance` (`35.0`) bo'lgan natijalarni `excluded_low_relevance_options` ga o'tkazadi.
