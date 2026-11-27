# Tyrion'ga hissa qo'shish (`ai-ads`)

Tyrion'ga hissa qo'shayotganingiz uchun rahmat! Yangi **bozor paketlari**, **lokallar**, **platforma audit skilllari** va **deterministik CLI yaxshilanishlari** mamnuniyat bilan qabul qilinadi.

---

## 1. Yangi bozor paketini qanday qo'shish (`markets/<market_id>/`)

1. `markets/<market_id>/` papkasini yarating (ISO hudud yoki mamlakat slug'i, masalan `ca`, `au`, `jp`, `kr`).
2. `markets/global/pack.json` dagi sxemaga mos `pack.json` qo'shing:
   - `market_id`, `display_name`, `default_currency` (ISO 4217), `supported_currencies`
   - `payment_methods`, `bnpl_providers`, `price_anchor_template`
   - `primary_funnels`, `messaging_channels`, `platform_share`, `seasonality_calendar`
   - `regulations` (`frameworks`, `consent_required_for_pii`, `special_ad_categories`)
   - `languages` (BCP 47 kodlari), `rtl_languages`
   - `verified_date` (`YYYY-MM-DD`) va `sources` (rasmiy URL'lar — benchmark yoki qonunni hech qachon taxmin qilmang).
3. Manba havolalari, tekshiruv sanalari va **Akkaunt tarixi birinchi** ogohlantirishi bilan `README.md` va `benchmarks.md` qo'shing.
4. `<market_id>` ni `tools/market_locale.py` dagi `SUPPORTED_MARKETS` va `GEO_TO_MARKET` ga qo'shing.

---

## 2. Yangi UI/CLI lokalini qanday qo'shish (`locales/<locale_id>/`)

1. `locales/en/messages.json` ni `locales/<locale_id>/messages.json` ga nusxalang.
2. UI matnlarini tarjima qiling, texnik metrikalarni (`ROAS`, `CPA`, `EMQ`, `CAPI`, `FTIR`) o'zgartirmang.

---

## 3. PR yuborishdan oldin tekshiruvlar

Har bir pull request Windows, macOS va Linux'da barcha deterministik darvozalardan o'tishi shart:

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
