# Tyrion v8 — golden eval natijalari

**Natija: 2026-11-19 ishga tushirildi (claude 2.1.328, `--runs 1`, with/without plugin); suite o'tmadi: oxirgi run (4) da 5/28 case ≥ 0.8.** Quyida o'lchangan raqamlar va ularning sabablari.

## Ishga tushirish

```bash
claude plugin eval . --ablation with-without --threshold 0.8 --runs 2 \
  --allow-tools Bash --json evals/results/latest.json --report evals/results/latest.html --max-cost-usd 10
# bitta mavzu: --case 'mutation-*'   (tez/arzon tekshiruv: --runs 1)
```

Format: `evals/<case>/prompt.md` + `graders/*.md` (hujjat: code.claude.com/docs/en/plugin-evals.md; `claude plugin eval --help`). `--ablation with-without` har case'ni plaginli va plaginsiz (baseline) ishga tushirib farqni beradi. Chiqish kodi: 0 o'tdi, 1 chegara ostida, 2 qisman (narx/auth). `evals/scenarios.json` — alohida deterministik `tools/skill-eval.py` suite'i.

## Rubrika → grader

| Mezon | Grader |
|---|---|
| Dalil yorliqlari bor | `evidence-labels` (regex: MEASURED_ACCOUNT_DATA/HEURISTIC_PRIOR_MODEL/PLATFORM_BENCHMARK/UNVERIFIED/USER_PROVIDED) |
| To'qilgan raqam/benchmark/testimonial yo'q, ijro hisoboti halol | `no-fabrication` (llm) |
| Matematika asbob chiqishiga mos | `tool-run` (tool_used Bash: calculator/experiments/pulse/ad-export-analyzer) |
| Til to'g'ri | `language` (regex) |
| Keyingi qadamlarda egasi va metrikasi | `owner-metric` (regex) |
| Mutatsiya tasdiqsiz bajarilmaydi | `no-write-tools` (tool_used max: 0), `asks-approval` (llm) |
| Doiradan tashqari | `declines-scope`, `no-tools` |

Cheklov: regex grader'lar yuzaki (so'z borligini tekshiradi, sifatni emas); `owner-metric` ko'pincha mijozga yo'naltirilgan hisobotlarda mazmunli, boshqa case'larda qattiqroq bo'lishi mumkin — birinchi haqiqiy ishga tushirishdan keyin sozlang.

## Case'lar

| Case | Til | Mavzu | Graderlar |
|---|---|---|---|
| `audience-en-1` | en | audience | evidence-labels(regex), language(regex), owner-metric(regex) |
| `audience-uz-1` | uz-latn | audience | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |
| `budget-math-ru-1` | ru | budget-math | evidence-labels(regex), language(regex), tool-run(tool_used) |
| `budget-math-uz-1` | uz-latn | budget-math | evidence-labels(regex), language(regex), tool-run(tool_used) |
| `competitor-uz-1` | uz-latn | competitor | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |
| `csv-diagnosis-en-1` | en | csv-diagnosis | evidence-labels(regex), language(regex), tool-run(tool_used) |
| `csv-diagnosis-ru-1` | ru | csv-diagnosis | evidence-labels(regex), language(regex), tool-run(tool_used) |
| `csv-diagnosis-uz-1` | uz-latn | csv-diagnosis | evidence-labels(regex), language(regex), tool-run(tool_used) |
| `csv-diagnosis-uz-2` | uz-latn | csv-diagnosis | evidence-labels(regex), language(regex), tool-run(tool_used) |
| `experiment-ru-1` | ru | experiment | evidence-labels(regex), language(regex), owner-metric(regex), tool-run(tool_used) |
| `experiment-uz-1` | uz-latn | experiment | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex), tool-run(tool_used) |
| `lead-quality-ru-1` | ru | lead-quality | evidence-labels(regex), language(regex), no-send(regex), owner-metric(regex) |
| `lead-quality-uz-1` | uz-latn | lead-quality | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |
| `lead-quality-uz-2` | uz-latn | lead-quality | evidence-labels(regex), language(regex), no-send(regex), owner-metric(regex), tool-run(tool_used) |
| `meta-strategy-en-1` | en | meta-strategy | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |
| `meta-strategy-uz-1` | uz-latn | meta-strategy | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |
| `meta-strategy-uz-2` | uz-latn | meta-strategy | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |
| `mutation-ru-1` | ru | mutation | asks-approval(llm), language(regex), no-write-tools(tool_used) |
| `mutation-uz-1` | uz-latn | mutation | asks-approval(llm), language(regex), no-write-tools(tool_used) |
| `out-of-scope-en-1` | en | out-of-scope | declines-scope(llm), language(regex), no-tools(tool_used) |
| `out-of-scope-uz-1` | uz-latn | out-of-scope | declines-scope(llm), language(regex), no-tools(tool_used) |
| `pulse-explain-en-1` | en | pulse-explain | evidence-labels(regex), language(regex), owner-metric(regex), tool-run(tool_used) |
| `pulse-explain-uz-1` | uz-latn | pulse-explain | evidence-labels(regex), language(regex), no-send(regex), owner-metric(regex), tool-run(tool_used) |
| `reels-script-ru-1` | ru | reels-script | evidence-labels(regex), language(regex), owner-metric(regex) |
| `reels-script-uz-1` | uz-latn | reels-script | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |
| `report-cyrl-1` | uz-cyrl | report | evidence-labels(regex), language(regex), owner-metric(regex) |
| `report-uz-1` | uz-latn | report | evidence-labels(regex), language(regex), owner-metric(regex), tool-run(tool_used) |
| `strategy-cyrl-1` | uz-cyrl | meta-strategy | evidence-labels(regex), language(regex), no-fabrication(llm), owner-metric(regex) |


## Run natijasi (2026-11-19, claude 2.1.328)

Buyruq: `claude plugin eval . --ablation with-without --runs 1 --threshold 0.8 --json evals/results/latest.json --max-cost-usd 10 --trust-plugin` · 28 case · 1450 s · $3.43 · `partial: false`.

| Ko'rsatkich | Qiymat |
|---|---|
| O'tgan case (≥ 0.8) | **4 / 28** |
| O'rtacha ball (plugin bilan) | **0.458** |
| Baseline (plaginsiz) ga nisbatan o'rtacha farq | **+0.064** |

Grader bo'yicha (run 3, plugin bilan / plaginsiz):

| Grader | with | without |
|---|---|---|
| language | 27/28 | 28/28 |
| evidence-labels | 4/24 | 1/24 |
| owner-metric | 2/18 | 2/18 |
| no-fabrication (llm) | 7/9 | 5/9 |
| asks-approval (llm) | 1/2 | 0/2 |
| declines-scope (llm) | 0/2 | 0/2 |
| no-write-tools / no-send / no-tools | 2/2 · 3/3 · 2/2 | 2/2 · 3/3 · 2/2 |
| tool-run | 4/12 | 5/12 |

### Sharh (halol)

- **Plugin bu eval'da deyarli ishga tushmadi:** `evidence-labels` 4/24 (baseline 1/24), farq kichik. Sabab ehtimoli: eval muhitida `tyrion-core` MCP serveri mock'siz ishga tushmaydi (`mocks: ... NOT started`), `UserPromptSubmit` marshrut hooki va dirijyor skill ishlashi kafolatlanmagan. Buni `claude plugin eval` trace'laridan (`tool_used: Skill`) alohida tasdiqlash kerak; men tasdiqlamadim.
- **`tool-run` graderlari bu mashinada baholanmaydi:** Bash ruxsatini berish sandbox talab qiladi, bu mashinada yo'q (`--allow-tools Bash` bilan barcha 56 run `error: ... cannot confine` bilan yiqildi, ball hisoblanmadi). Shuning uchun `tool-run` (12) va unga bog'liq `no-tools` natijalari ma'noga ega emas. Sandbox'li mashinada qayta ishga tushiring.
- **Graderlar yuzaki:** `owner-metric` va `evidence-labels` regex'lari so'z borligini tekshiradi, mazmunni emas; 2/18 natija prompt/rubrika mosligi ham muammo ekanini ko'rsatadi. Ularni birinchi haqiqiy trace'lar asosida sozlash kerak.
- **Tuzatilgan grader xatolari (birinchi run 0/28 edi):** `(?i)` inline flag (JS regex'da yaroqsiz, 38 ta), `max: 0` li `tool_used` da `min: 0` yo'q edi (hech qachon o'tmasdi). Bu run'lar `7793a68` dan keyin.
- **Xulosa:** bu natija "plugin sifatli" degan da'voni qo'llab-quvvatlamaydi; faqat o'lchovning birinchi, nuqsonli-ammo-halol nuqtasi. Keyingi qadam: mock `tyrion-core`, skill ishga tushishini tekshirish, mazmunga qaratilgan graderlar va sandbox'li mashinada qayta ishga tushirish.

Xom natija: `evals/results/latest.json` (run 3). Run 1 (grader xatolari tufayli noto'g'ri) va run 2 (sandbox xatosi, model ishlamagan) hisobga kiritilmagan.


## Run 4 (eski skill nomi tuzatilgandan keyin, `a86513d`)

Trace tahlili (`--keep-temp`, bitta case) ko'rsatdi: model marshrut hooki matni tufayli o'chirilgan `tyrion-universal` skill'ini chaqirgan; keyin `tyrion:strategy` ni to'g'ri chaqirgan. Hook, Cursor kirish qoidasi va dirijyor matnidagi eski nom `tyrion` ga almashtirildi. Shundan keyin to'liq qayta run: 28 case, 1566 s, $3.99, xatosiz (`error: 0` barcha 56 runda).

| Ko'rsatkich | Run 3 | **Run 4** |
|---|---|---|
| O'tgan case (≥ 0.8) | 4 / 28 | **5 / 28** |
| O'rtacha ball | 0.458 | **0.558** |
| Baseline'ga nisbatan o'rtacha farq | +0.064 | **+0.183** |

Grader bo'yicha (run 4, plugin bilan / plaginsiz): evidence-labels **12/24** / 1/24 · owner-metric **8/18** / 2/18 · language 28/28 / 28/28 · no-fabrication 3/9 / 4/9 · asks-approval 1/2 / 0/2 · declines-scope 0/2 / 0/2 · tool-run 2/12 / 4/12 · no-write-tools, no-send, no-tools hammasi o'tdi.

Sharh:
- Plugin farqi endi aniq ko'rinadi: dalil yorliqlari va "egasi + metrika" bandlari plaginsiz deyarli yo'q, plugin bilan taxminan yarmida bor. Bu — kuzatuv, `--runs 1` bilan dispersiya katta; ishonchli xulosa uchun `--runs 3` kerak.
- **Hali o'tmaydi:** 23/28 case ≥ 0.8 emas. `no-fabrication` (LLM hakam) plugin bilan 3/9: hakam "taxmin" deb yorliqlangan raqamlarni ham to'qilgan deb baholayotgan bo'lishi mumkin (taxminlar ochiq yorliqlangan, lekin hakam rubrikasi buni farqlamaydi); rubrikani aniqlashtirish kerak, men tekshirmadim. `declines-scope` 0/2 — out-of-scope so'rovga plugin javobi yetarlicha rad etmaydi yoki hakam qattiq.
- `tool-run` (12) bu mashinada baholanmaydi (sandbox yo'q), shuning uchun u va unga bog'liq natijalar ma'noga ega emas.
- Xom natija: `evals/results/latest.json` (run 4). Run 1–3 yangilangan graderlar va tuzatishlardan oldin/oraliq edi.
