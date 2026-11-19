# MIGRATION — Tyrion 7.x → 8.0

Mashina o'qiydigan xarita: `manifests/migration-v8.json`. Router eski nomlarni alias sifatida taniydi
(`--agent audit-meta`, `agent_hint: "audit-meta"` → `platform-auditor`; eski skill nomlari yangi skillning `aliases:` ida).
Hech narsa o'chirilmadi: eski matnlar yangi skill'ning `references/` papkasiga ko'chirildi.

## Nima o'zgardi

- **Skill: 61 → 19.** Har skill bitta foydalanuvchi vazifasi. Eski `SKILL.md` matni `skills/<yangi>/references/<eski>.md` da.
- **Agent: 36 → 12.** 13 platforma auditi `platform-auditor` ga birlashdi; platforma delegatsiya paketida beriladi (full audit'da parallel nusxalar). Eski charterlar `skills/<skill>/references/legacy-agents/<eski>.md` da.
- **Buyruq.** Model ko'radigan kanonik buyruqlar: `/start /audit /audience /creative /budget /export /report /client /competitors /tracking /pulse /connect`. Qolganlari (`/auditoriya /kreativ /voronka /eksport /hisobot /mijoz /raqobatchi /savol`, `/doctor /learn /shield /sop /scale /utm /ask /funnel /ad-creative`) foydalanuvchi uchun saqlanadi, lekin `disable-model-invocation: true` bilan model kontekstidan chiqarilgan.
- **UZ bozori.** `uzbekistan-market-intel` skill'i `markets/uz/market-intel.md` ga ko'chdi va faqat `market=uz` da yuklanadi.
- **Token.** Doimiy description narxi ~10.4K → ~2K token (`python3 tools/token-budget.py`).
- **Yangi:** skill'lar `connect`, `pulse`, `experiments`, `lead-quality`; `schemas/metrics.v1.json`.

## O'tish bosqichlari

1. `git pull`, so'ng `python3 tools/install-hooks.py --agents-only` (`.claude/agents/` qayta generatsiya).
2. O'z skriptlaringizda `skills/ads/references/...` yo'llarini `skills/audit/references/ads/...` ga o'zgartiring (jadvalga qarang).
3. Maxsus agent chaqiruvlarida eski nom ishlaydi (alias), lekin yangi nomga o'ting.
4. Cursor/Windsurf: `python3 tools/harness-export.py --target all`.

## Skill xaritasi (eski → yangi → eski matn)

| Eski | Yangi | Fayl |
|---|---|---|
| `tyrion-universal` | `tyrion` | `skills/tyrion/references/conductor-v7.md` |
| `ads` | `audit` | `skills/audit/references/ads-conductor.md` |
| `ads-validate` | `system` | `skills/system/references/ads-validate.md` |
| `ads-plan` | `strategy` | `skills/strategy/references/ads-plan.md` |
| `ads-launch` | `strategy` | `skills/strategy/references/ads-launch.md` |
| `launch` | `strategy` | `skills/strategy/references/launch.md` |
| `offers` | `strategy` | `skills/strategy/references/offers.md` |
| `product-marketing` | `strategy` | `skills/strategy/references/product-marketing.md` |
| `ads-audit` | `audit` | `skills/audit/references/audit-process.md` |
| `ads-meta` | `audit` | `skills/audit/references/platforms/meta.md` |
| `ads-google` | `audit` | `skills/audit/references/platforms/google.md` |
| `ads-tiktok` | `audit` | `skills/audit/references/platforms/tiktok.md` |
| `ads-youtube` | `audit` | `skills/audit/references/platforms/youtube.md` |
| `ads-linkedin` | `audit` | `skills/audit/references/platforms/linkedin.md` |
| `ads-x` | `audit` | `skills/audit/references/platforms/x.md` |
| `ads-reddit` | `audit` | `skills/audit/references/platforms/reddit.md` |
| `ads-pinterest` | `audit` | `skills/audit/references/platforms/pinterest.md` |
| `ads-snapchat` | `audit` | `skills/audit/references/platforms/snapchat.md` |
| `ads-microsoft` | `audit` | `skills/audit/references/platforms/microsoft.md` |
| `ads-amazon` | `audit` | `skills/audit/references/platforms/amazon.md` |
| `ads-apple` | `audit` | `skills/audit/references/platforms/apple.md` |
| `ads-telegram` | `audit` | `skills/audit/references/platforms/telegram.md` |
| `ads-vk` | `audit` | `skills/audit/references/platforms/vk.md` |
| `ads-yandex` | `audit` | `skills/audit/references/platforms/yandex.md` |
| `ads-meta-audience` | `audience` | `skills/audience/references/ads-meta-audience.md` |
| `ad-creative` | `creative` | `skills/creative/references/ad-creative.md` |
| `ads-creative` | `creative` | `skills/creative/references/ads-creative.md` |
| `ads-create` | `creative` | `skills/creative/references/ads-create.md` |
| `ads-generate` | `creative` | `skills/creative/references/ads-generate.md` |
| `ads-photoshoot` | `creative` | `skills/creative/references/ads-photoshoot.md` |
| `copywriting` | `creative` | `skills/creative/references/copywriting.md` |
| `copy-editing` | `creative` | `skills/creative/references/copy-editing.md` |
| `writing-guidelines` | `creative` | `skills/creative/references/writing-guidelines.md` |
| `ads-dna` | `creative` | `skills/creative/references/ads-dna.md` |
| `reels-scripting` | `video` | `skills/video/references/reels-scripting.md` |
| `video-editing` | `video` | `skills/video/references/video-editing.md` |
| `video-motion-graphics` | `video` | `skills/video/references/video-motion-graphics.md` |
| `ads-attribution` | `tracking` | `skills/tracking/references/ads-attribution.md` |
| `ads-server-side-tracking` | `tracking` | `skills/tracking/references/ads-server-side-tracking.md` |
| `analytics` | `tracking` | `skills/tracking/references/analytics.md` |
| `ads-math` | `budget` | `skills/budget/references/ads-math.md` |
| `ads-budget` | `budget` | `skills/budget/references/ads-budget.md` |
| `ads-optimize` | `analyze` | `skills/analyze/references/ads-optimize.md` |
| `ads-monitor` | `analyze` | `skills/analyze/references/ads-monitor.md` |
| `ads-competitor` | `competitors` | `skills/competitors/references/ads-competitor.md` |
| `ads-research` | `competitors` | `skills/competitors/references/ads-research.md` |
| `customer-research` | `competitors` | `skills/competitors/references/customer-research.md` |
| `cro` | `funnel` | `skills/funnel/references/cro.md` |
| `ads-landing` | `funnel` | `skills/funnel/references/ads-landing.md` |
| `web-design-guidelines` | `funnel` | `skills/funnel/references/web-design-guidelines.md` |
| `content-strategy` | `content` | `skills/content/references/content-strategy.md` |
| `social` | `content` | `skills/content/references/social.md` |
| `marketing-ideas` | `content` | `skills/content/references/marketing-ideas.md` |
| `longform-direct-response` | `content` | `skills/content/references/longform-direct-response.md` |
| `marketing-psychology` | `content` | `skills/content/references/marketing-psychology.md` |
| `prospecting` | `content` | `skills/content/references/prospecting.md` |
| `seo-audit` | `content` | `skills/content/references/seo-audit.md` |
| `ads-report` | `report` | `skills/report/references/ads-report.md` |
| `ads-setup` | `client` | `skills/client/references/ads-setup.md` |
| `ads-test` | `experiments` | `skills/experiments/references/ads-test.md` |
| `uzbekistan-market-intel` | `market:uz` | `markets/uz/market-intel.md` |

## Agent xaritasi

| Eski | Yangi | Eski charter |
|---|---|---|
| `audit-meta` | `platform-auditor` (platforma: meta) | `skills/audit/references/legacy-agents/audit-meta.md` |
| `audit-google` | `platform-auditor` (platforma: google) | `skills/audit/references/legacy-agents/audit-google.md` |
| `audit-telegram` | `platform-auditor` (platforma: telegram) | `skills/audit/references/legacy-agents/audit-telegram.md` |
| `audit-tiktok` | `platform-auditor` (platforma: tiktok) | `skills/audit/references/legacy-agents/audit-tiktok.md` |
| `audit-youtube` | `platform-auditor` (platforma: youtube) | `skills/audit/references/legacy-agents/audit-youtube.md` |
| `audit-linkedin` | `platform-auditor` (platforma: linkedin) | `skills/audit/references/legacy-agents/audit-linkedin.md` |
| `audit-x` | `platform-auditor` (platforma: x) | `skills/audit/references/legacy-agents/audit-x.md` |
| `audit-reddit` | `platform-auditor` (platforma: reddit) | `skills/audit/references/legacy-agents/audit-reddit.md` |
| `audit-pinterest` | `platform-auditor` (platforma: pinterest) | `skills/audit/references/legacy-agents/audit-pinterest.md` |
| `audit-snapchat` | `platform-auditor` (platforma: snapchat) | `skills/audit/references/legacy-agents/audit-snapchat.md` |
| `audit-microsoft` | `platform-auditor` (platforma: microsoft) | `skills/audit/references/legacy-agents/audit-microsoft.md` |
| `audit-amazon` | `platform-auditor` (platforma: amazon) | `skills/audit/references/legacy-agents/audit-amazon.md` |
| `audit-apple` | `platform-auditor` (platforma: apple) | `skills/audit/references/legacy-agents/audit-apple.md` |
| `audit-tracking` | `tracking-specialist` | `skills/tracking/references/legacy-agents/audit-tracking.md` |
| `tracking-specialist` | `tracking-specialist` | `skills/tracking/references/legacy-agents/tracking-specialist.md` |
| `meta-audience-architect` | `audience-architect` | `skills/audience/references/legacy-agents/meta-audience-architect.md` |
| `audit-creative` | `creative-strategist` | `skills/creative/references/legacy-agents/audit-creative.md` |
| `creative-strategist` | `creative-strategist` | `skills/creative/references/legacy-agents/creative-strategist.md` |
| `copy-writer` | `creative-strategist` | `skills/creative/references/legacy-agents/copy-writer.md` |
| `visual-designer` | `creative-strategist` | `skills/creative/references/legacy-agents/visual-designer.md` |
| `format-adapter` | `creative-strategist` | `skills/creative/references/legacy-agents/format-adapter.md` |
| `reels-scriptwriter` | `video-producer` | `skills/video/references/legacy-agents/reels-scriptwriter.md` |
| `video-editor` | `video-producer` | `skills/video/references/legacy-agents/video-editor.md` |
| `audit-budget` | `budget-analyst` | `skills/budget/references/legacy-agents/audit-budget.md` |
| `positioning-strategist` | `strategist` | `skills/strategy/references/legacy-agents/positioning-strategist.md` |
| `launch-planner` | `strategist` | `skills/strategy/references/legacy-agents/launch-planner.md` |
| `campaign-ideator` | `strategist` | `skills/strategy/references/legacy-agents/campaign-ideator.md` |
| `content-planner` | `content-planner` | `skills/content/references/legacy-agents/content-planner.md` |
| `social-content-writer` | `content-planner` | `skills/content/references/legacy-agents/social-content-writer.md` |
| `seo-auditor` | `content-planner` | `skills/content/references/legacy-agents/seo-auditor.md` |
| `audit-policy-compliance` | `compliance-reviewer` | `skills/audit/references/legacy-agents/audit-policy-compliance.md` |
| `audit-regulatory-compliance` | `compliance-reviewer` | `skills/audit/references/legacy-agents/audit-regulatory-compliance.md` |
| `research-worker` | `research-verifier` | `skills/competitors/references/legacy-agents/research-worker.md` |
| `source-verifier` | `research-verifier` | `skills/competitors/references/legacy-agents/source-verifier.md` |
| `release-verifier` | `release-verifier` | `skills/system/references/legacy-agents/release-verifier.md` |
| `skill-reviewer` | `release-verifier` | `skills/system/references/legacy-agents/skill-reviewer.md` |
