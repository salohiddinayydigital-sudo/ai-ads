# Security Policy & Spend-Guard Architecture (`SECURITY.md`)

## 1. Supported Versions & Inventory

| Version | Status | Architecture Inventory |
|---|---|---|
| **7.0.x** | Supported (Current Global Release) | **36 agents**, **63 skills**, **27 slash commands**, **29 CLI tools**, 100 wiki notes |
| **5.0.x** | Maintenance | Single-Root ECC (Uzbekistan default) |

## 2. Reporting a Vulnerability

If you discover a security vulnerability, prompt injection vector, or credential leak risk:
- **GitHub Security Advisories:** [https://github.com/salohiddinayydigital-sudo/ai-ads/security/advisories](https://github.com/salohiddinayydigital-sudo/ai-ads/security/advisories)
- **Repository Maintainer:** [@salohiddinayydigital-sudo](https://github.com/salohiddinayydigital-sudo)
- Do **not** open a public issue containing live tokens, ad account IDs, or exploit payloads.

## 3. Spend-Guard & Ad Account Mutation Safety (6 Mandatory Gates)

Tyrion enforces strict read-only default operation. Any action that mutates a live ad account (budget change, pausing campaigns, bid modification) is blocked by `tools/spend-guard.py` and the Universal Auto-Router until all 6 gates pass:
1. **Preview Diff (`1_preview_diff`)**
2. **Explicit Human Approval (`2_human_approval` / `--approved`)**
3. **Budget Velocity Limit (`3_budget_velocity_le_20pct` — max +20% per 48–72h)**
4. **Hard Daily Ceiling (`4_max_daily_cap`)**
5. **Automated Stop-Loss Rule (`5_stop_loss_rule`)**
6. **Instant Rollback Plan (`6_rollback_plan`)**

## 4. Privacy, Consent Gate & PII Protection

- **CAPI Consent Gate (`tools/capi-utm-builder.py`):** When `--no-consent` (`consent_granted=False`) is passed, Tyrion strips all PII (`ph`, `em`, `fn`, `ct`, `fbp`, `fbc`) before hashing or transmission (`BLOCKED_PII_NO_CONSENT`), enforces Google Consent Mode v2 (`denied`), and enables Meta Limited Data Use (`data_processing_options=['LDU']`).
- **Secret Redaction (`tools/tyrion_core.py` & `tools/tyrion-shield.py`):** Automatically scans and masks Meta (`EAA...`), OpenAI (`sk-...`), Anthropic (`sk-ant-...`), Google (`AIza...`), Telegram, and GitHub tokens.
