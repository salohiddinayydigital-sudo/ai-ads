# Tyrion sifat evallari (`claude plugin eval`)

Bu papkada ikki xil tekshiruv turadi:

| Fayl | Nima tekshiradi | Narxi |
|---|---|---|
| `scenarios.json` | Router to'g'ri skill va agentni tanlaydimi (`python3 tools/skill-eval.py`) | 0 token, CI'da har push'da |
| `<holat>/prompt.md` + `graders/` | Model javobi pluginning qat'iy qoidalariga amal qiladimi | token sarflaydi, reliz oldidan |

## Ishga tushirish

```bash
# Barcha holatlar, pluginsiz javob bilan solishtirib (har holat 3 marta, ikki tomonda)
claude plugin eval . --allow-real-servers --allow-tools "mcp__plugin_tyrion_tyrion-core__*" "Bash(python3 *)"

# Arzon sinov: bitta holat, 1 marta, solishtirishsiz
claude plugin eval . --case breakeven-hisob --runs 1 --ablation none \
  --allow-real-servers --allow-tools "mcp__plugin_tyrion_tyrion-core__*"
```

- `--allow-real-servers` — Tyrion'ning lokal MCP serverini (kalkulyator, spend-guard, targeting) ishga tushiradi; busiz MCP asboblari modelga berilmaydi.
- `Bash(python3 *)` granti OS sandbox'ini talab qiladi (Linux: `bubblewrap` va `socat`; Windows'da WSL2). Sandbox bo'lmasa bu grantni olib tashlang.
- Natija: `evals/results/<vaqt>/report.html` va `aggregate-result.json` (git'ga kirmaydi).

## Holatlar

| Holat | Tekshiriladigan qoida |
|---|---|
| `uydirma-interest-yoq` | Token yo'q paytda tasdiqlanmagan interest "tasdiqlangan" deb ko'rsatilmaydi |
| `noaniq-brif-savol` | Maqsad/byudjet/voronka noaniq bo'lsa taxmin qilmaydi, so'raydi |
| `breakeven-hisob` | Break-even CPA/ROAS kalkulyator natijasiga teng (67.60$ · 1.78) |
| `manba-belgisi` | O'lchanmagan raqam `HEURISTIC_PRIOR_MODEL` deb belgilanadi |
| `byudjet-20-foiz` | Byudjetni birdan 3 baravar oshirishga rozi bo'lmaydi (+20% qoidasi) |
| `breakdown-effekti` | Placement o'chirishdan oldin marginal CPA tekshiriladi |
| `kill-keep-scale` | Uchta ad set bo'yicha qaror to'g'ri |
| `aloqasiz-sorov` | Marketingga aloqasiz so'rovda skill ishga tushmaydi |

## `asbob-ishlatildi` ko'rsatkichi

Uch holatda (`uydirma-interest-yoq`, `byudjet-20-foiz`, `breakdown-effekti`) model javobni yoddan emas, Tyrion'ning
deterministik MCP asbobi orqali olganmi — shu tekshiriladi. Bu ko'rsatkich ballga kirmaydi (`arm: with-only`):
pluginsiz tomonda u hech qachon o'tmaydi. `--allow-real-servers` berilmasa yoki model asbobni Bash orqali chaqirsa,
ko'rsatkich ✗ bo'ladi, javobning o'zi esa to'g'ri bo'lishi mumkin.

## Birinchi o'lchov (2026-11-11, v8.0.0)

Har holat har tomonda **1 martadan** o'tkazilgan — bu yo'nalishni ko'rsatadi, aniq ball emas (ishonchli son uchun standart 3 marta).
Xarajat: 1.13$. Sandbox yo'q muhitda, faqat MCP granti bilan.

| Holat | Plugin bilan | Pluginsiz | Δ |
|---|---|---|---|
| `aloqasiz-sorov` | 1.00 | 1.00 | 0.00 |
| `breakdown-effekti` | 1.00 | 0.67 | +0.33 |
| `breakeven-hisob` | 1.00 | 1.00 | 0.00 |
| `byudjet-20-foiz` | 1.00 | 0.67 | +0.33 |
| `kill-keep-scale` | 1.00 | 1.00 | 0.00 |
| `manba-belgisi` | 1.00 | 0.67 | +0.33 |
| `noaniq-brif-savol` | 1.00 | 0.33 | +0.67 |
| `uydirma-interest-yoq` | 1.00 | 0.67 | +0.33 |
| **O'rtacha** | **1.00** | **0.75** | **+0.25** |

Ikki narsa ko'rindi. Birinchisi, plugin eng ko'p qiymatni qoidalarda qo'shadi (noaniq brifda so'rash, manba belgisi, +20%),
oddiy arifmetika va aniq jadvalli qarorda esa model pluginsiz ham to'g'ri javob beradi. Ikkinchisi, model savolga skillni
yuklamasdan, to'g'ridan-to'g'ri MCP asbobini chaqirib javob berdi — ya'ni bu oqimlarda asosiy yuk MCP server va sessiya
boshidagi qoidalarda.

## To'liq o'lchov (2026-11-12, v8.0.0)

Har holat har tomonda 3 martadan (6 ta run), pluginsiz tomon bilan solishtirilgan. MCP granti bor, sandbox yo'q.
Jami xarajat: 3.36$ (birinchi urinish 2.71$ + yetishmagan holat 0.65$). Birinchi urinishni o'zimning `timeout 595` buyrug'im to'xtatdi:
7 holat tugadi, `uydirma-interest-yoq` alohida, to'liq 3 martadan qayta o'tkazildi. `noaniq-brif-savol` ning pluginsiz tomonida
3-run uzilgan (0.00, "interrupted"), shuning uchun u holatda 5 ta to'liq run bor, pluginsiz ball 0.22 shu uzilgan runni ham o'z ichiga oladi
(uzilmasa ~0.33).

| Holat | Plugin bilan | Pluginsiz | Δ |
|---|---|---|---|
| `aloqasiz-sorov` | 1.00 | 1.00 | 0.00 |
| `breakdown-effekti` | 1.00 | 0.44 | +0.56 |
| `breakeven-hisob` | 1.00 | 1.00 | 0.00 |
| `byudjet-20-foiz` | 1.00 | 1.00 | 0.00 |
| `kill-keep-scale` | 1.00 | 1.00 | 0.00 |
| `manba-belgisi` | 1.00 | 0.67 | +0.33 |
| `noaniq-brif-savol` | 1.00 | 0.22 | +0.78 |
| `uydirma-interest-yoq` | 1.00 | 0.67 | +0.33 |
| **O'rtacha** | **1.00** | **0.75** | **+0.25** |

Birinchi (1 martalik) o'lchovdan farqlar: `byudjet-20-foiz` da pluginsiz tomon bu safar 3 martaning hammasida o'tdi (0.67 → 1.00), ya'ni
u holatda plugin qiymati o'lchanmadi. `breakdown-effekti` da farq kattalashdi (+0.33 → +0.56). O'rtacha Δ o'zgarmadi (+0.25).

`asbob-ishlatildi` (ballga kirmaydi): `breakdown-effekti` da `tyrion_breakdown_effect` va `byudjet-20-foiz` da `tyrion_spend_guard`
**0 marta** chaqirilgan, model javobni yoddan berdi (javob to'g'ri, asbob esa ishlatilmadi). Bu skill/buyruq ko'rsatmasi modelni
asbobga yo'naltirmayotganini bildiradi: keyingi ish.

## Natijani o'qish

`WITH` — plugin bilan ball, `W/OUT` — pluginsiz, `Δ` — farq. `Δ` musbat bo'lsa plugin qiymat qo'shyapti.
`Δ ≤ 0` chiqqan holatda avval graderni tekshiring (`--judge-model sonnet`), keyin tegishli skill yoki buyruq matnini.
Yangi holat qo'shish: papka oching, `prompt.md` ga foydalanuvchi yozadigandek so'rov, `graders/` ga kamida bitta tekshiruv.
