# Tyrion v8 — qarorlar jurnali

## D0. Hujjatdan tekshirilgan Claude Code faktlari (2026-11-19, code.claude.com orqali sub-agent; qayta tekshirish Bosqich 1/2 da)
- `disable-model-invocation: true` — skill/buyruq tavsifi model kontekstiga tushmaydi, faqat foydalanuvchi `/nom` bilan chaqiradi (skills.md). `user-invocable: false` tavsifni kontekstdan olmaydi. Natija: UZ aliaslar `disable-model-invocation: true` bilan belgilanadi.
- Plugin `commands/` fayllari frontmatter'ini qo'llashi hujjatda to'liq tasdiqlanmagan (`unverified`); yechim: aliaslarni `skills/<alias>/SKILL.md` ko'rinishida (kanonik joy) yoki buyruq faylida ikkalasini tekshirib belgilash. Bosqich 1 da `claude plugin validate` bilan sinaladi.
- PreToolUse chiqishi: `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow|deny|ask","permissionDecisionReason":"..."}}`, exit 2 = blok; matcher: faqat harf/raqam/`_`/`-`/`|` bo'lsa aniq nom, aks holda regex (anchorsiz). Plugin MCP nomi: `mcp__plugin_<plugin>_<server>__<tool>`.
- `claude plugin eval`: `evals/<case>/prompt.md` + `graders/*.md` (type: regex|tool_used|tool_order|file_exists|llm|baseline), `--ablation with-without`, `--threshold`. Bosqich 7 uchun asos.
- Meta Ads MCP URL `https://mcp.facebook.com/ads` — ikkilamchi manbadan; `source_status: unverified` (developers.facebook.com bu muhitda yetib bo'lmaydi). Google Ads MCP: github.com/googleads/google-ads-mcp (yozuv asboblari bor: assets_*, labels_*).

## D1. Token o'lchovi
`tools/token-budget.py`: tokenlar = belgilar/4 (`HEURISTIC_PRIOR_MODEL`); faqat `disable-model-invocation` bo'lmagan skill/agent/buyruq tavsifi hisoblanadi. Muqobil (haqiqiy tokenizer) rad etildi: stdlib-only cheklovi.
