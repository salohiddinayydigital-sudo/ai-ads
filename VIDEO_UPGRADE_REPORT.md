# VIDEO_UPGRADE_REPORT — Video pre-production tizimi (4 ustun)

**Branch:** `feat/video-scripting-pro` (`main` dan; `main`ga to'g'ridan-to'g'ri commit yo'q, force-push yo'q)
**Reja:** `reja.md` (foydalanuvchi yuklagan). **Scope:** faqat pre-production; montaj/render qatlamiga tegilmagan.

## 1. Before / After

| Tekshiruv | Baseline (`main`) | Yakuniy |
|---|---|---|
| `python3 -m unittest discover -s tests` | 547 test, OK (1 skipped) | **575 test, OK** (1 skipped) — +28 (`tests/test_video_scripting.py`) |
| `python3 tools/doctor.py` | 19/19 ok, 0 ogohlantirish | 19 tekshiruv, 0 xato; Eval Suite **51/51**; (commitgacha "Git holati" ogohlantirishi — commitdan keyin toza) |
| `python3 tools/tyrion-shield.py` | 6/6 | **6/6** (91 Python modul, 0 sintaksis xato, 0 o'lik kod) |
| `python3 tools/vault-audit.py` | 0 muammo | **0 muammo** |
| `python3 tools/token-budget.py` | 2003 token (gate 3500) | **2038 token** (+35: yangi `video` description va charter qatorlari) |
| `python3 tools/skill-eval.py` | 47/47 | **51/51** (+4 `skill_route`) |
| `tests/coverage_gate.py --min 75` (CI) | — | **75.99%**, o'tdi |
| `catalog.py check / sync-mirrors` | mos | mos (351 element, 35 juft mirror) |

Eslatma: bu eval'lar (`evals/<case>/`) `claude plugin eval` uchun yozilgan golden case'lar; ularning **LLM bilan haqiqiy run natijasi bu yerda o'lchanmagan** (LLM chaqirilmagan). Faqat tuzilma, graderlar va `skill_route` stsenariylari (deterministik) tekshirildi.

## 2. Nima qilindi

**Bilim qatlami (`skills/video/`)**
- `SKILL.md` — qayta yozildi: 4 ustunli Intent Router (Sales / Organic / Plan / Motion) + alohida Post-Production; eski triggerlar saqlangan, yangilari qo'shilgan; montaj/render fayllari faqat so'ralganda yuklanadi.
- Yangi: `sales-video-scripting.md`, `organic-video-content.md`, `video-content-planning.md`, `motion-video-scripting.md`, `script-quality-rubric.md` (100 ball, o'tish 85).
- `reels-scripting.md` — orqaga moslik: tepaga yo'naltiruvchi blok qo'shildi, mazmun va `performance-video-system.md` havolasi saqlangan.
- Takrorlanish olib tashlandi: safe-zone/3-Capture yagona manbasi `sales-video-scripting.md` §8; `video-ad-scripts-and-specs.md` (20 → ~15 qator, havola) va `short-form-video.md` (pointer + batch bo'limi havolaga) qisqartirildi.
- `wiki/video-kreativ-tizimi.md` §9 va `wiki/video-skript-shablonlari.md` (9 format → yangi tizim moslik jadvali) yangilandi.

**Agentlar va buyruqlar**
- `agents/video-producer.md` (+ `.claude/agents/` mirror, `install-hooks.py --agents-only`): rejimlar jadvali, majburiy AV-jadval, Self-Audit >= 85/100, handoff; `content-planner` va `creative-strategist` ga video handoff bo'limi.
- 6 ta buyruq (UZ kanonik + EN alias, `.claude/commands/` mirror bilan): `/video-ssenariy` (`/video-script`), `/video-reja` (`/video-plan`), `/motion-ssenariy` (`/motion-script`). Hammasi `disable-model-invocation` → model ko'radigan buyruqlar soni 13 ta o'zgarmadi.
- `INDEX.md`, `AGENTS.md`, `README*.md`, `CLAUDE.md`, plugin/marketplace manifestlari: raqamlar `catalog.py sync-claims` bilan avtomatik (commands 29 → 35); AGENTS.md dagi eskirgan "27" ham tuzatildi.

**Asbob, shablon, sxema**
- `tools/creative-matrix.py video-script --mode sales|organic|plan|motion --lang uz|ru|en --duration 15|30|45|60 --hooks 3..5` (+ `--content-format`, `--motion-type`, `--ratio`, `--awareness`, `--weeks`, `--per-week`, `--platforms`, `--start-date`). Stdlib-only (`datetime`, `math` qo'shildi). Rejimsiz eski chaqiruv **o'zgarmagan** (`tyrion.video_ad_script/v7`).
- Generator har skeletni avtomatik tekshiradi (`check_av_table`): vaqt yig'indisi = davomiylik, VO <= soniya x 2.6 so'z, ekran matni limiti, salomlashishsiz ochilish, hook soni; `claim_safety` natijasi bo'sh (skelet o'zida foiz/kafolat yaratmaydi). 648 kombinatsiya (rejim x til x davomiylik x hook x format x tur) tekshirilgan.
- `templates/`: `sales-video-script.md`, `organic-video-script.md`, `video-content-plan.md`, `motion-video-blueprint.md`.
- `schemas/`: `video-script-schema.json`, `motion-blueprint-schema.json` (testda stdlib validator bilan generator chiqishiga qarshi tekshiriladi).

**Evals va testlar**
- `evals/sales-video-uz-1`, `organic-video-uz-1`, `video-plan-uz-1`, `motion-script-uz-1` + `scenarios.json` ga E13–E16.
- `tests/test_video_scripting.py` (28 test); `tests/test_audit_v5.py` da `commands` soni 29 → 35.

## 3. Cheklovlar va halol eslatmalar

- Generator **skelet** beradi (struktura, vaqt, limitlar, placeholderlar); strategiya, isbot, narx va natija mijozdan keladi. `[ADD VERIFIED ...]` placeholder to'qilgan statistikaning o'rnini bosadi.
- Funnel ulushi (~50/30/20), ritm (har ~2–4 s), nutq tezligi (2.2–2.6 so'z/s), BPM — `HEURISTIC_PRIOR_MODEL`; fayllarda shunday yorliqlangan. Rubrika bali natija prognozi emas.
- Platforma siyosati (Meta/TikTok/YouTube) bo'yicha jadval — xavf zonalari ro'yxati; joriy rasmiy siyosat tekshirilmagan (`UNVERIFIED`), fayllarda "tekshir" deb belgilangan.
- Uzbek kirill (`uz_cyrillic`) yangi `--mode` yo'lida hozircha yo'q (`uz|ru|en`); eski rejimsiz yo'l `uz_cyrillic` ni qo'llashda davom etadi.
- `bumper` turi faqat 5/8/10 s; boshqa motion turlari 15–60 s.
- `plan` rejimi `--start-date` bo'lmasa `W1-D1` yorliqlaridan foydalanadi.
- Versiya raqami (`VERSION` 8.0.1) o'zgartirilmagan; relizdagi bump muallifning qarori (CHANGELOG da `[Unreleased]`).
- Git branch: loyiha ko'rsatmasi `feat/video-scripting-pro` ni talab qildi; sessiya ishchi branchi `claude/amazing-edison-a3pt9e` ham xuddi shu commitlarga yangilandi.

## 4. O'zgargan fayllar (xulosa)

`skills/video/` (SKILL.md, 5 yangi reference, reels-scripting.md) · `skills/creative/.../video-ad-scripts-and-specs.md` · `skills/content/.../short-form-video.md` · `wiki/video-*.md` (2) · `agents/` (3) + `.claude/agents/` (3) · `commands/` (6 yangi) + `.claude/commands/` (6) · `templates/` (4) · `schemas/` (2) · `tools/creative-matrix.py` · `evals/` (4 suite + scenarios.json) · `tests/` (yangi test + `test_audit_v5.py`) · `INDEX.md`, `AGENTS.md`, `README.md`, `README.uz.md`, `CLAUDE.md`, `SECURITY.md`, `CHANGELOG.md`, `plugin.json`, `package.json`, `marketplace.json`, `.claude-plugin/*`, `.codex-plugin/*`, `manifests/catalog.json` (avtomatik).

**Tegilmagan (scope):** `tools/video-run.py`, `skills/video/references/video-editing.md` (+ `video-editing/`), `skills/video/references/video-motion-graphics.md`, `.mcp.json`, `.windsurfrules`, `.cursor/rules/` — test (`test_scope_boundary_render_and_edit_pipeline_untouched`) `git diff main` bilan tekshiradi.

## 5. Merge

```bash
git fetch origin
git checkout main && git pull --ff-only
git merge --no-ff feat/video-scripting-pro -m "feat(video): 4-pillar video pre-production system"
git push origin main
```

Yoki PR orqali: `feat/video-scripting-pro` → `main`. Merge'dan oldin: `python3 -m unittest discover -s tests && python3 tools/doctor.py`.
