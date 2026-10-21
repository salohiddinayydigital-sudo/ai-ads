# Contributing to Tyrion (`ai-ads`)

Thank you for contributing to Tyrion! We welcome new **Market Packs**, **Locales**, **Platform Audit Skills**, and **Deterministic CLI Improvements**.

---

## 1. How to Add a New Market Pack (`markets/<market_id>/`)

1. Create a folder `markets/<market_id>/` (ISO region or country slug, e.g. `ca`, `au`, `jp`, `kr`).
2. Add `pack.json` following the schema in `markets/global/pack.json`:
   - `market_id`, `display_name`, `default_currency` (ISO 4217), `supported_currencies`
   - `payment_methods`, `bnpl_providers`, `price_anchor_template`
   - `primary_funnels`, `messaging_channels`, `platform_share`, `seasonality_calendar`
   - `regulations` (`frameworks`, `consent_required_for_pii`, `special_ad_categories`)
   - `languages` (BCP 47 codes), `rtl_languages`
   - `verified_date` (`YYYY-MM-DD`) and `sources` (official URLs — never guess benchmarks or laws).
3. Add `README.md` and `benchmarks.md` with source citations, verification dates, and the **Account History First** (`Akkaunt tarixi birinchi`) disclaimer.
4. Register `<market_id>` in `SUPPORTED_MARKETS` and `GEO_TO_MARKET` in `tools/market_locale.py`.

---

## 2. How to Add a New UI/CLI Locale (`locales/<locale_id>/`)

1. Copy `locales/en/messages.json` to `locales/<locale_id>/messages.json`.
2. Translate UI strings while keeping technical metrics (`ROAS`, `CPA`, `EMQ`, `CAPI`, `FTIR`) intact.

---

## 3. Running Verification Before Submitting a PR

Every pull request must pass all deterministic gates on Windows, macOS, and Linux:

```bash
python3 tools/catalog.py sync-mirrors
python3 tools/catalog.py build
python3 tools/catalog.py check
python3 tools/vault-audit.py . --gate
python3 tools/tyrion-shield.py scan
python3 tools/skill-eval.py
python3 -m unittest discover -s tests -t . -v
python3 tools/doctor.py --quick
```
