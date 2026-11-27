# Orkestratsiya protokoli (dirijyor referensi)

Marshrutlash uchun yagona haqiqat manbai — `manifests/workflows.json` (`python3 tools/tyrion_workflows.py check` bilan tekshiriladi), uni `tools/skill-search.py route` iste'mol qiladi. Bu fayl faqat dirijyor rejani qanday bajarishini belgilaydi.

## 1. Delegatsiya paketi (native sub-agent chaqiruvi)

Chat transkriptini emas, tuzilgan kontekstni uzating. Paketni ~1.5 KB dan oshirmang, bosqichga kerak yuqori oqim natijalarini qo'shing.

```text
GOAL: <one sentence, the stage output name from the plan, e.g. audience_architecture>
CONTEXT (verified): <facts the user gave; each with label USER_PROVIDED>
CONTEXT (assumptions): <ASSUMPTION items; do not treat as facts>
UPSTREAM: <outputs of stages in `needs`, compact JSON/bullets>
READ FIRST: <stage skills: paths> ; REFERENCES: <1-2 paths>
TOOLS ALLOWED: <from plan; run `--help` before first use>
OUTPUT CONTRACT: <agent charter contract + stage output name>
QUALITY BAR: every number labelled; no invented interests/IDs/stats/testimonials; list execution_evidence {tools_used, files_read, not_used}
BOUNDARY: bounded to this goal; do not call tyrion_universal_router without caller="specialist"; do not spawn agents; do not mutate any ad account
```

## 2. Mutaxassis natija konverti (dirijyor nimani kutadi)

`status` (`completed | needs_input | blocked_mutation_approval`), `output` (bosqich natijasi), `assumptions[]`, `evidence_labels`, `execution_evidence {tools_used, files_read, not_used}`, `open_questions[]`, `contradictions[]`. `needs_input` yaroqli: dirijyor foydalanuvchidan so'rashni yoki belgilangan taxminlar bilan davom etishni hal qiladi.

## 3. Tekshiruv rubrikasi (har bir bosqichga, so'ng butun natijaga qo'llang)

| Tekshiruv | Xato misoli | Harakat |
|---|---|---|
| Kontraktga nisbatan to'liqlik | Exclusion'larsiz auditoriya natijasi | Yetishmayotgan maydon nomi bilan bir marta qaytaring |
| Dalil | Manbasiz "CPA $5 bo'lishi kerak" | Olib tashlang yoki `HEURISTIC_PRIOR_MODEL` deb belgilang; `calculator.py` orqali hisoblang |
| Targeting aniqligi | `meta-targeting-engine.py` qaytarmagan qiziqish yaroqli deb taqdim etilgan | Gipotezaga tushiring; asl nom va ID'ni faqat tasdiqlangan elementlar uchun saqlang |
| To'qima | To'qilgan sharh, "mijozlarning 90% i...", kafolat, narx | Olib tashlang; `[ADD VERIFIED ...]` o'rin egasi bilan almashtiring |
| Policy | Shaxsiy belgilar da'volari, before/after, daromad va'dalari | Belgilang; haqiqiy ko'rib chiqishsiz muvofiqlikni hech qachon da'vo qilmang |
| Izchillik | Kreativ rejadagi byudjet iqtisoddan oshadi | `unit_economics` natijasiga qarshi hal qiling (raqamlar ustun) |
| Ijro halolligi | Natija ishlatilmagan asbob/skillni da'vo qiladi | O'sha da'voni rad eting |
| Asl maqsad | So'rovga javob bermaydigan chiroyli natija | Sintezdan oldin qayta qamrang |

Butun natija tekshiruvi: maqsadga javob berildimi? har bir taxmin qanday tekshirilishi bilan yozilganmi? raqamlar bo'limlar bo'ylab mos keladimi (byudjet = kampaniyalar yig'indisi, CPA maqsadlari iqtisodga mos, voronka hajmlari byudjetga mos)? til va bozor to'g'rimi (standart o'zbek lotin; tabiiy moslashtirish, so'zma-so'z tarjima emas)?

## 4. Parallel va ketma-ket

Rejadagi `parallel_levels` dan foydalaning. Parallel faqat daraja ichidagi hech bir bosqich boshqasining natijasini o'qimasa. Meta strategiyasidagi muhim bog'liqliklar: `positioning` `research` ni kutadi; `audience` va `architecture` `positioning` + `economics` ni talab qiladi; `creative` `positioning` ni talab qiladi; `video` `creative` ni talab qiladi; `validate` hammasini talab qiladi. Foydalanuvchi bergan tadqiqotni takrorlamang (`optional_when`).

## 5. Zaxira matritsasi

| Harness | Sub-agentlar | Xatti-harakat |
|---|---|---|
| Claude Code | `Agent` asbobi (`subagent_type` = agent nomi, `agents/*.md` / `.claude/agents` dan) | Har bir bosqich uchun native. Agent turi yo'q bo'lsa (sessiya o'rnatishdan oldin boshlangan): shu bosqich uchun zaxira. |
| Codex, Cursor, Windsurf, CLI/MCP | yo'q | Yagona dirijyor: charter + skillni o'qing, bosqichni inline bajaring, `executed_by: conductor_as_<agent>` deb belgilang. Kontekst `AGENTS.md`/qoidalar + router MCP asbobidan keladi. |
| Har qanday | Asbob/API mavjud emas | Qaysi ekanini xabar qiling, belgilangan taxminlar yoki oflayn holatlar bilan davom eting. |

Haqiqatan `Agent` chaqiruvi ishlamaguncha hech qachon `subagents_actually_spawned: true` deb xabar qilmang.

## 6. Asbob tanlash eslatmalari (flaglar `--help` bo'yicha tekshirilgan)

- `calculator.py breakeven --price --cogs [--shipping --processing-fee-pct --target-profit-pct --currency] --json`
- `calculator.py funnel-economics --price --cogs [--lead-to-sale-cvr --target-profit-pct --daily-budget --assumed-cpl ...] --json` (hajm prognozlari faqat foydalanuvchi taxminiy CPL bergandagina; natijalar `ASSUMPTION` deb belgilanadi)
- `meta-targeting-engine.py search --product --niche --customer-profile --problem --objective --country --language [--account-id] --json` (`META_ACCESS_TOKEN` kerak; usiz har bir element `API_UNAVAILABLE`, bu xabar qilinadi, hech qachon soxtalashtirilmaydi)
- `meta-audience.py architect|overlap|saturation|lookalike|retargeting|diagnose|launch-blueprint --help`
- `creative-matrix.py video-script --product --problem --format --duration [--price --market --language] --json` (`claim_safety` ni chiqaradi)
- `creative-matrix.py iterate ...` (haqiqiy metrikalardan diagnostika; `skills/video/references/reels-scripting/references/performance-video-system.md` ga qarang)
- `ad-export-analyzer.py analyze --file <csv|json> [--target-cpa --breakeven-roas --primary-conversion] --json`
- `spend-guard.py budget|packet|copy|tracking --help`

## 7. Xotira va o'rganish

Avval `MEMORY.md` ni o'qing (til, bozor, faol garovlar). Faqat quyidagilarni yozing: (a) o'lchangan dalil bilan tasdiqlangan saboq -> `/learn`; (b) gipoteza -> Bet Ledger'ga `PENDING` sifatida. Mijoz nomlari yoki sirlarni `MEMORY.md` ga yozmang (mijoz ma'lumoti `clients/<slug>/` da).

## 8. Ishlangan iz (qisqartirilgan): "Shu biznes uchun Meta Ads strategiya tuz"

1. Marshrut -> `meta_strategy`, asosiy `launch-planner`, darajalar: intake > economics||research||tracking > positioning > architecture||audience||creative > video > validate > synthesize.
2. `ads-plan`, `ads-launch`, `ads-budget` ni to'liq + `meta-strategy-deliverable.md` ni o'qing.
3. Intake: foydalanuvchi faqat mahsulot va shaharni berdi -> narx/marja, maqsad, oylik byudjet va treking holatini bir marta so'rang; javob bo'lmasa, belgilangan taxminlar bilan davom eting.
4. 2-daraja bitta xabarda: `audit-budget` (calculator), `research-worker` (foydalanuvchi raqobatchilarni bergan bo'lsa o'tkaziladi), `tracking-specialist`.
5. 4-daraja: `launch-planner`, `meta-audience-architect` (targeting asbobi, 6 status), `creative-strategist` parallel.
6. `reels-scriptwriter` eng yaxshi 1–2 konseptni yozadi; `source-verifier` da'volarni tekshiradi; dirijyor tekshiradi, byudjetni voronka hajmlari bilan moslashtiradi, `outputs/<client>/<date>-meta-strategy.md` ni yozadi va qaysi bosqichlar native va qaysilari zaxira bo'lganini xabar qiladi.
