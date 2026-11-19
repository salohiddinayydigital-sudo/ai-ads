# Tyrion v8 — golden eval natijalari

**Natija: ishga tushirilmadi (muhitda LLM eval yo'q).** Suite tayyor (28 case); hech qanday ball yoki baseline farqi to'qilmagan.

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
