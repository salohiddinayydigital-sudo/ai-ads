# Tyrion v8 — qarorlar jurnali

## D0. Hujjatdan tekshirilgan Claude Code faktlari (2026-11-19, code.claude.com orqali sub-agent; qayta tekshirish Bosqich 1/2 da)
- `disable-model-invocation: true` — skill/buyruq tavsifi model kontekstiga tushmaydi, faqat foydalanuvchi `/nom` bilan chaqiradi (skills.md). `user-invocable: false` tavsifni kontekstdan olmaydi. Natija: UZ aliaslar `disable-model-invocation: true` bilan belgilanadi.
- Plugin `commands/` fayllari frontmatter'ini qo'llashi hujjatda to'liq tasdiqlanmagan (`unverified`); yechim: aliaslarni `skills/<alias>/SKILL.md` ko'rinishida (kanonik joy) yoki buyruq faylida ikkalasini tekshirib belgilash. Bosqich 1 da `claude plugin validate` bilan sinaladi.
- PreToolUse chiqishi: `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow|deny|ask","permissionDecisionReason":"..."}}`, exit 2 = blok; matcher: faqat harf/raqam/`_`/`-`/`|` bo'lsa aniq nom, aks holda regex (anchorsiz). Plugin MCP nomi: `mcp__plugin_<plugin>_<server>__<tool>`.
- `claude plugin eval`: `evals/<case>/prompt.md` + `graders/*.md` (type: regex|tool_used|tool_order|file_exists|llm|baseline), `--ablation with-without`, `--threshold`. Bosqich 7 uchun asos.
- Meta Ads MCP URL `https://mcp.facebook.com/ads` — ikkilamchi manbadan; `source_status: unverified` (developers.facebook.com bu muhitda yetib bo'lmaydi). Google Ads MCP: github.com/googleads/google-ads-mcp (yozuv asboblari bor: assets_*, labels_*).

## D1. Token o'lchovi
`tools/token-budget.py`: tokenlar = belgilar/4 (`HEURISTIC_PRIOR_MODEL`); faqat `disable-model-invocation` bo'lmagan skill/agent/buyruq tavsifi hisoblanadi. Muqobil (haqiqiy tokenizer) rad etildi: stdlib-only cheklovi.

## D2. Skill xaritasi (61 → 19) — taklif etilgan xaritadan farqlar
- `content` skilliga `funnel` dan `seo-audit` kirmadi: `seo-audit` spec bo'yicha `content` da qoldi; `funnel` = cro + ads-landing + web-design-guidelines.
- `ads` (konduktor, 39 reference) → `audit/references/ads-conductor.md` va `audit/references/ads/*` (referencelarning katta qismi audit bilan bog'liq). `tyrion-universal` → `tyrion` (matni SKILL.md da, eski nusxa `references/conductor-v7.md`).
- `ads-validate` → `system`; `ads-setup` → `client`; `ads-test` → `experiments`; `ads-dna`, `ads-create` → `creative`. Yangi: `connect`, `pulse`, `lead-quality`.
- `uzbekistan-market-intel` → `markets/uz/market-intel.md`; router uni `market=uz` bo'lganda `references_to_load` ga qo'shadi (skill reyestrida yo'q).
- Muqobil rad etildi: har eski skillni `disable-model-invocation` bilan yashirish — bilim yo'qolmasdi, lekin 61 papka qolardi va "~20 skill" talabiga zid.

## D3. Agent xaritasi (36 → 12)
- 13 platforma agenti → `platform-auditor` (platforma delegatsiya paketida; `manifests/workflows.json platform_agents.audit_agent` hammasi shu agentga ishora qiladi, `words` bilan platforma aniqlanadi).
- `audit-creative`, `copy-writer`, `visual-designer`, `format-adapter` → `creative-strategist`; `reels-scriptwriter`, `video-editor` → `video-producer`; `source-verifier`, `research-worker` → `research-verifier`; `skill-reviewer` → `release-verifier`; `campaign-ideator`, `launch-planner`, `positioning-strategist` → `strategist`; `social-content-writer`, `seo-auditor` → `content-planner`. `data-analyst` yangi.
- Eski charter matnlari `skills/<skill>/references/legacy-agents/` da (rol bilimi yo'qolmaydi). Barcha yangi agentlarga `tyrion_spend_guard` qo'shildi (charter matni uni eslatadi; test shuni talab qiladi).

## D4. Buyruqlar
- Model ko'radigan 12 ta: start, audit, audience, creative, budget, export, report, client, competitors, tracking, pulse, connect. Qolgan 17 ta (UZ aliaslar va doctor/learn/shield/sop/scale/utm/ask/funnel/ad-creative) `disable-model-invocation: true`. Plugin `commands/` fayllarida bu maydonning ishlashi hujjatda to'liq tasdiqlanmagan (`unverified`): `claude plugin validate` xato bermadi; agar ishlamasa ham foydalanuvchi uchun ishlaydi, faqat token tejami kamayadi.

## D5. Router
- `tools/skill-search.py` strukturasi o'zgarmadi (generic frontmatter bo'yicha); nomlar `manifests/migration-v8.json` orqali alias qilingan. 30% qisqartirish bu bosqichda bajarilmadi: sabab — xatti-harakat testlari (≈100 ta) router ichki jadvallariga bog'liq, va hajm kamaytirishdan ko'ra doimiy kontekst narxi (10.4K→2K) asosiy maqsad edi. Keyingi bosqichda qayta ko'riladi.
- Eval stsenariylari: bitta `platform-auditor` bo'lgani uchun `forbidden_agents` dan kutilgan agent chiqarildi (noto'g'ri-platforma tekshiruvi endi delegatsiya paketida).
