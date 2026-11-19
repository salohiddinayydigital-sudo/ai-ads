---
name: v8-roadmap
description: "Tyrion 7.1 -> v8.0 yaxshilash rejasi: joriy holat auditi, raqobatchi pluginlar va bozor tahlili, bo'shliqlar, 7 bosqichli reja va o'lchanadigan KPI'lar"
tags: [roadmap, v8, strategiya, raqobat, bozor]
source: "Repo auditi (doctor, pytest, claude plugin validate) + 2026-11-19 dagi veb tadqiqot (manbalar oxirida)"
updated: 2026-11-19
---

# Tyrion 8.0 — Yaxshilash rejasi

> **Bir gapda:** v7.1 — yaxshi *maslahatchi* (reja tuzadi, keyin jim bo'ladi). v8.0 — **yopiq siklli media-buyer miyasi**: rasmiy konnektorlardan jonli ma'lumot oladi, raqamlarni kod bilan hisoblaydi, har kuni hisobni kuzatadi, gipotezalarni test qilib natijadan o'rganadi, CRM'dan lid sifatini Meta'ga qaytaradi. Bularning hammasini **3 marta kam token** bilan qiladi.

Hamroh fayl: [[v8-master-prompt]] (butun ishni bajaradigan yagona prompt).

---

## 1. Joriy holat (o'lchangan, 2026-11-19)

| Ko'rsatkich | Qiymat | Manba |
|---|---|---|
| Inventar | 36 agent · 61 skill · 27 buyruq · 30 asbob · 100 wiki · 9 playbook | `manifests/catalog.json` |
| Testlar | 364 o'tdi, 1 o'tkazildi | `pytest -q tests` |
| Doctor | 18 OK · 1 ogohlantirish (bilim grafi eskirgan) | `tools/doctor.py` |
| Plugin validatsiya | o'tdi; maslahat: README'da bir qatorli `/plugin install` yo'q | `claude plugin validate .` |
| Doimiy yuklanadigan tavsiflar (skill+agent+buyruq `description`) | ~41.5K belgi ≈ **~10.4K token har sessiyada** | `description:` maydonlari yig'indisi |
| Eng katta kod fayllari | `skill-search.py` 2 653 qator, `meta-targeting-engine.py` 2 502 qator | `wc -l` |
| Eval'lar | 47 stsenariy — hammasi marshrut/deterministik; **chiqish sifati baholanmaydi** | `evals/scenarios.json` |
| Jonli ma'lumot | O'z Graph API wrapperi + `META_ACCESS_TOKEN`; rasmiy Meta Ads MCP ishlatilmaydi | `docs/integrations.md` |
| Python | faqat stdlib (CI'da `pyyaml`) — bu kuchli tomon, saqlanadi | importlar |

### Kuchli tomonlar (saqlanadi)
- Deterministik 0-token asboblar: raqamlarni LLM emas, kod hisoblaydi.
- Anti-gallyutsinatsiya: 6-statusli targeting tekshiruvi, `claim_safety`, dalil yorliqlari (`MEASURED_ACCOUNT_DATA` / `HEURISTIC_PRIOR_MODEL`).
- Spend-Guard va "reja tuzadi, inson bajaradi" tamoyili.
- Workflow DAG (`manifests/workflows.json`), multi-harness (Claude Code, Codex, Cursor, Windsurf).
- O'zbekiston bozori chuqurligi: Telegram, AmoCRM, Payme/Click, Uzum Nasiya; 9 bozor paketi.

### Zaif tomonlar (v8 tuzatadi)
1. **Ochiq sikl.** Reja → (inson ishga tushiradi) → *hech narsa*. Kuzatuv, anomaliya ogohlantirishi, test natijasini o'qish yo'q.
2. **Jonli hisobdan uzilgan.** Ko'p foydalanuvchi System User token yarata olmaydi; rasmiy OAuth konnektorlar (Meta, Google) bilan integratsiya yo'q.
3. **Shishgan yadro.** ~10.4K token tavsiflar har sessiyada; 8 juft UZ/EN dublikat buyruq; 13 ta deyarli bir xil platforma-audit agenti.
4. **Sifat o'lchanmaydi.** Eval'lar faqat "to'g'ri skillga yo'naltirdimi?" ni tekshiradi, "javob plaginsiz Claude'dan yaxshiroqmi?" ni emas.
5. **Kreativ faqat matn.** Haqiqiy ma'lumotdan kreativ tahlili (hook rate / hold rate teg bo'yicha), Ad Library pattern-mining, ishlab chiqarish quvuri yo'q.
6. **Lid sifati muammosi hal qilinmagan.** CRM → Meta offline konversiya sikli yo'q (UZ bozorining №1 og'rig'i: "lidlar sifatsiz").
7. **Mijoz holati tarqoq.** `MEMORY.md` + markdown fayllar; tuzilmali `state` (KPI, bazaviy qiymatlar, testlar, qarorlar) yo'q.
8. **2026 yangiliklari yo'q.** ChatGPT Ads, rasmiy Meta Ads MCP, Telegram Gram kabineti va CPM o'zgarishlari.

---

## 2. Raqobatchi pluginlar va vositalar

| Raqib | Nimasi kuchli | Tyrion uchun saboq |
|---|---|---|
| **AgriciDaniel/claude-ads v2** (upstream) | 12 platforma, 250+ audit tekshiruvi; nazorat holati va **dalil qamrovi** alohida (pass/fail/unknown/n/a); o'zgarishlar faqat tasdiq bilan | Audit balliga "evidence coverage" qo'shish; har tekshiruv uchun `unknown` halol holati |
| **coreyhaines31/marketingskills** (~57K yulduz) | Oddiy, keng, o'rnatish oson | Soddalik tarqalishni yutadi: kam, kuchli skill |
| **Rasmiy Meta Ads MCP** (2026-04-29, OAuth, ~29 asbob) | Jonli hisob, benchmark, anomaliya signali, A/B va lift test, Ad Library | Tyrion = shu konnektor ustidagi **miya + xavfsizlik qatlami**. Yozish asboblarida undo/draft yo'q, shuning uchun Spend-Guard majburiy |
| **Google Ads rasmiy MCP** | GAQL o'qish; yozish juda cheklangan | O'qish uchun adapter; o'zgarishlar faqat change packet |
| **Madgicx / Birch / Triple Whale Moby** ($49–749/oy) | Doimiy kuzatuv, avtomatik qoidalar, ogohlantirishlar | `pulse` — kundalik sog'liq + anomaliya (avto-ijrosiz) |
| **Motion / Segwise / Superads** | Kreativ teglash, hook rate, hook score | Haqiqiy ma'lumotdan "g'olib kreativ DNK" hisoboti |
| **AdCreative.ai / Arcads / Pencil** | Kreativ generatsiya | Provayderdan mustaqil ishlab chiqarish quvuri (mavjud konnektor bo'lsa) |
| **Meta Advantage+ o'zi** | Targeting va kreativni avtomatlashtirmoqda | Qiymat **kirishlarga** ko'chdi: kreativ xilma-xilligi, signal sifati (CAPI/CRM), offer, o'lchov |

**Strategik xulosa:** Andromeda/Advantage+ davrida targetologning ishi = **signal + kreativ + offer + o'lchov**. v8 aynan shu to'rttasini avtomatlashtiradi; "qaysi interest?" kabi eski savollar ikkinchi darajaga tushadi.

---

## 3. Bozor signallari (2026)

- **Rasmiy AI konnektorlar standart bo'ldi:** Meta Ads MCP (OAuth, ochiq beta), Google Ads MCP. Raw API wrapperlarini yozish o'rniga ularni ishlatish kerak.
- **ChatGPT Ads:** self-serve Ads Manager beta 2026-05-05 (AQSh), CPC va CPM, Conversions API + pixel; sentabr 2026 da Hindiston, Yevropa, MENA'ga kengaymoqda. Yangi kanal — Tyrion'da yo'q.
- **Meta to'liq avtomatlashtirish yo'nalishida:** qo'lda va Advantage+ oqimlari birlashgan, generativ kreativ vositalar kengaygan.
- **Telegram Ads:** TON kabineti "Gram" deb qayta nomlangan; 2026-08-28 dan CPM pollari o'zgargan (manbalar bir-biriga zid → `ads.telegram.org` dan tekshirish shart).
- **Agentic reklama protokollari (AdCP, IAB AAMP):** hali real byudjet kam oqadi — v8'da faqat kuzatish, implementatsiya emas.
- **Kreativ analitika:** hook rate (3s/impr) va thumbstop ta'riflari vositalar orasida farq qiladi → Tyrion o'z ta'rifini ochiq yozishi kerak.

---

## 4. v8.0 arxitekturasi — 8 ustun

| # | Ustun | Nima beradi | Ustuvorlik |
|---|---|---|---|
| A | **Lean Core** — 61→~20 skill, 36→~12 agent, UZ aliaslar kontekstdan tashqarida | Har sessiyada ~65% kam token, aniqroq marshrut | P0 |
| B | **Connector Layer + Unified Metrics Schema** | Rasmiy Meta/Google MCP → snapshot → kod tahlili; CSV/screenshot fallback | P0 |
| C | **Client Brain** (`clients/<slug>/state.json`) | Sessiyalar orasida uzluksizlik: KPI, bazaviy qiymat, qarorlar | P0 |
| D | **Pulse** — kundalik kuzatuv va anomaliya | "Doimiy media-buyer" tajribasi, avto-ijrosiz | P1 |
| E | **Experiment Ledger 2.0** | Gipoteza → MDE/hajm → natija statistikasi → instinkt | P1 |
| F | **Lead Quality Loop** (AmoCRM/Bitrix24/Sheets → CAPI) | Sifatli lid uchun optimizatsiya — UZ'ning eng katta og'rig'i | P1 |
| G | **Creative Intelligence 2.0** | Teg bo'yicha hook/hold/CPA, Ad Library mining, ishlab chiqarish quvuri | P1 |
| H | **Trust & Delivery** — `claude plugin eval` golden suite, HTML hisobot, 5 daqiqalik onboarding, ChatGPT Ads/Telegram 2026 yangilanishi | Sifat isboti va mijozga tayyor natija | P2 |

---

## 5. Bosqichlar

| Bosqich | Mazmun | Chiqish mezoni |
|---|---|---|
| 0 | Baseline o'lchash, `docs/v8-progress.md`, branch | Baseline raqamlari faylda |
| 1 | Lean Core + migratsiya xaritasi + token byudjet testi | Tavsiflar ≤ 3.5K token; eski nomlarning hammasi yangi joyga ishora qiladi |
| 2 | Unified schema, normalizatorlar, konnektor aniqlash, Client Brain | Barcha tahlil asboblari bitta sxemani o'qiydi |
| 3 | Pulse + Experiment Ledger + o'rganish | Sintetik fixture'larda anomaliya va test o'qilishi to'g'ri |
| 4 | Lead Quality Loop + Creative Intelligence 2.0 | CAPI batch dry-run; teg hisoboti min-namuna qoidasi bilan |
| 5 | Bilim yangilanishi: ChatGPT Ads, Telegram 2026, rasmiy MCP, audit v2 balli | Har yangi fakt manba+sana yoki `unverified` |
| 6 | HTML hisobot/dashboard + `/start` wizard | Demo-brand bilan 5 daqiqada birinchi natija |
| 7 | Golden eval suite (baseline bilan), CI, hujjatlar, `8.0.0` | Plugin baseline'dan ≥80% holatda yaxshiroq; doctor 0 ogohlantirish |

---

## 6. Muvaffaqiyat KPI'lari

| KPI | v7.1 | v8.0 maqsad |
|---|---|---|
| Doimiy tavsif tokenlari | ~10.4K | ≤ 3.5K |
| Skill / agent / model ko'radigan buyruq | 61 / 36 / 27 | ~20 / ~12 / ≤ 12 |
| Jonli ma'lumot manbalari | 1 (token bilan Graph API) | Meta MCP, Google MCP, Graph API, CSV, screenshot |
| Chiqish sifati eval'i | yo'q | ≥ 25 golden case, plaginsiz baseline'dan ≥ 80% yutish, 0 to'qilgan raqam |
| Testlar | 364 | ≥ 480, coverage ≥ 75% |
| Doctor | 1 ogohlantirish | 0 |
| Birinchi natijagacha vaqt (demo) | aniqlanmagan | ≤ 5 daqiqa |

---

## 7. Xavflar va himoya

| Xavf | Himoya |
|---|---|
| Konsolidatsiyada bilim yo'qolishi | Eski matn `references/` ga ko'chiriladi, o'chirilmaydi; `manifests/migration-v8.json` + har eski nom uchun test |
| Rasmiy MCP javob formati o'zgaradi | Normalizator tolerant, fixture'lar `synthetic` deb belgilangan, rasmiy hujjatdan tekshirish |
| Jonli hisobga zarar | Barcha yozish asboblari: Spend-Guard change packet + aniq tasdiq + rollback eslatmasi; avto-ijro yo'q |
| To'qilgan benchmark/fakt | Yangi yorliq `PLATFORM_BENCHMARK` faqat rasmiy asbobdan; qolgani manba yoki `unverified` |
| Breaking o'zgarish foydalanuvchini chalg'itadi | `MIGRATION.md`, UZ aliaslar saqlanadi, `8.0.0` major versiya |

---

## Manbalar (2026-11-19 da tekshirilgan, ko'pi ikkilamchi — implementatsiyada rasmiy hujjat bilan qayta tekshirish kerak)

- [Official Meta Ads MCP for Claude: 29 tools (Apr 2026)](https://pasqualepillitteri.it/en/news/1707/official-meta-ads-mcp-claude-29-tools-2026)
- [Meta Ads MCP and CLI: Inside Meta's Official AI Connectors](https://mcp.directory/blog/meta-ads-cli-mcp)
- [The Meta Ads MCP for Claude: what to lock down](https://elevarus.com/meta-ads-mcp-claude-operator-setup/)
- [Google Ads MCP 2026: official server, read-only limits](https://www.enrichlabs.ai/blog/google-ads-mcp-2026)
- [Google Ads MCP server gains 4 write tools](https://ppc.land/google-ads-mcp-server-gains-4-write-tools-still-cant-change-budgets/)
- [What is claude-ads (v2)](https://adadvisor.ai/blog/what-is-claude-ads) · [claude-ads on Claude Marketplaces](https://claudemarketplaces.com/plugins/agricidaniel-claude-ads)
- [coreyhaines31/marketingskills](https://claudemarketplaces.com/plugins/coreyhaines31-marketingskills)
- [Best AI media buying tools for Meta (2026)](https://superscale.ai/best-ai-media-buying-tools-meta-2026) · [AI agents for paid ads 2026](https://resources.rework.com/de/tools/ai-agents/best-ai-agents-for-paid-ads-2026)
- [OpenAI: new ways to buy ChatGPT ads](https://openai.com/zh-Hans-CN/index/new-ways-to-buy-chatgpt-ads/) · [ChatGPT Ads reach $1B, self-serve expands](https://www.channelinsider.com/ai/news-openai-chatgpt-ads-billion-self-service/)
- [Meta fully automated ads by 2026](https://pixis.ai/blog/metas-fully-automated-ads-by-2026-what-performance-teams-should-prepare-for/) · [Andromeda, Lattice, GEM explained](https://www.moburst.com/blog-meta-advantage-andromeda-lattice-and-gem-explained/)
- [Telegram Ads CPM cut for target channels](https://spilnoagency.com.ua/en/news-en/telegram-ads-cpm-cut-target-channels) · [TON vs EUR Telegram Ads 2026](https://tgads.biz/blog/en-ton-vs-eur-telegram-ads-2026)
- [AdCP adoption debate](https://www.pymnts.com/artificial-intelligence-2/2026/ad-industry-moves-to-set-rules-before-ai-agents-control-media-budgets/)
- [Motion AI tagging](https://motionapp.com/releases) · [Creative analytics guide 2026](https://segwise.ai/blog/creative-analytics-complete-guide-2026)
