"""normalize.py: adapterlar, xatolar, validator (sintetik fixture'lar)."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

import normalize as nz  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
RAW = FIX / "raw"
MET = FIX / "metrics"


def _run(*args: str):
    return run_tool_inproc("normalize.py", *args)


class AdapterTests(unittest.TestCase):
    def assertValid(self, doc):
        self.assertEqual(nz.validate_metrics(doc), [])

    def test_meta_graph(self) -> None:
        doc = nz.normalize("meta_graph", RAW / "meta_graph_insights.json")
        self.assertValid(doc)
        self.assertTrue(doc["synthetic"])
        self.assertEqual(doc["unmapped_columns"], ["quality_ranking"])
        r = doc["rows"][0]
        self.assertEqual((r["level"], r["entity_id"], r["source"], r["platform"]), ("ad", "a1", "meta_graph", "meta"))
        self.assertEqual((r["spend"], r["video_3s"], r["thruplay"], r["link_clicks"]), (20.5, 900, 300, 60))
        self.assertEqual(r["conversions"], {"lead": 6})
        self.assertEqual(r["evidence_label"], "UNVERIFIED")
        self.assertTrue(r["synthetic"])
        # frequency reach/impressions'dan hisoblangan
        self.assertAlmostEqual(doc["rows"][1]["frequency"], round(2100 / 1650, 4))
        shop = doc["rows"][2]
        self.assertEqual(shop["conversions"], {"purchase": 5})
        self.assertEqual(shop["conversion_value"], 400)

    def test_meta_graph_level_override_and_non_synthetic(self) -> None:
        raw = json.loads((RAW / "meta_graph_insights.json").read_text())
        raw.pop("synthetic")
        doc = nz.normalize_meta(raw, source="meta_graph", level="campaign")
        self.assertEqual({r["level"] for r in doc["rows"]}, {"campaign"})
        self.assertEqual(doc["rows"][0]["entity_id"], "c1")
        self.assertEqual(doc["rows"][0]["evidence_label"], "MEASURED_ACCOUNT_DATA")
        self.assertFalse(doc["rows"][0]["synthetic"])
        self.assertNotIn("synthetic", doc)

    def test_meta_mcp_nested_insights_and_flat(self) -> None:
        doc = nz.normalize("meta_mcp", RAW / "meta_mcp_insights.json")
        self.assertValid(doc)
        self.assertEqual(len(doc["rows"]), 3)
        self.assertEqual(doc["rows"][0]["source"], "meta_mcp")
        self.assertEqual(doc["rows"][0]["currency"], "UZS")
        self.assertEqual(doc["rows"][0]["conversions"], {"conversion": 9})
        self.assertNotIn("conversions", doc["rows"][1])  # 0 konversiya yozilmaydi
        self.assertEqual(doc["rows"][2]["entity_id"], "c11")
        self.assertEqual(doc["unmapped_columns"], ["some_new_field"])

    def test_google_ads(self) -> None:
        doc = nz.normalize("google_ads", RAW / "google_ads_gaql.json")
        self.assertValid(doc)
        r = doc["rows"][0]
        self.assertEqual((r["spend"], r["source"], r["platform"], r["account_id"]), (12.34, "google_mcp", "google", "3000000003"))
        self.assertEqual((r["conversions"], r["conversion_value"]), ({"conversion": 3}, 150.5))
        self.assertEqual(doc["unmapped_columns"], [])  # ctr hosila, resourceName e'tiborsiz

    def test_google_ads_adgroup_snake_case_and_stream(self) -> None:
        doc = nz.normalize("google_ads", RAW / "google_ads_adgroup.json")
        self.assertValid(doc)
        self.assertEqual((doc["rows"][0]["level"], doc["rows"][0]["entity_id"], doc["rows"][0]["currency"]), ("adset", "ag1", "EUR"))
        stream = [{"results": json.loads((RAW / "google_ads_gaql.json").read_text())["results"]}]
        d2 = nz.normalize_google_ads(stream, synthetic=True)
        self.assertEqual(len(d2["rows"]), 2)

    def test_google_ads_missing_date_errors(self) -> None:
        with self.assertRaises(nz.NormalizeError):
            nz.normalize_google_ads({"results": [{"campaign": {"id": "1"}, "metrics": {"costMicros": 5}}]}, currency="USD")

    def test_tiktok_csv_skips_total_and_reports_unmapped(self) -> None:
        doc = nz.normalize("tiktok_csv", RAW / "tiktok.csv", synthetic=True)
        self.assertValid(doc)
        self.assertEqual(len(doc["rows"]), 2)
        self.assertEqual(doc["skipped_rows"], 1)
        self.assertEqual(doc["unmapped_columns"], ["Video Views at 100%"])
        r = doc["rows"][0]
        self.assertEqual((r["platform"], r["entity_id"], r["currency"]), ("tiktok", "t1", "USD"))
        self.assertEqual(r["conversions"], {"conversion": 5, "purchase": 2})
        self.assertEqual(r["conversion_value"], 99.9)

    def test_telegram_csv_header_currency_and_date_format(self) -> None:
        doc = nz.normalize("telegram_csv", RAW / "telegram.csv", synthetic=True)
        self.assertValid(doc)
        r = doc["rows"][0]
        self.assertEqual((r["date"], r["currency"], r["level"], r["platform"]), ("2026-11-01", "TON", "ad", "telegram"))
        self.assertEqual((r["impressions"], r["clicks"], r["conversions"]), (5000, 120, {"join": 18}))

    def test_generic_csv_localized_numbers_and_header_currency(self) -> None:
        doc = nz.normalize("generic_csv", RAW / "generic.csv", synthetic=True)
        self.assertValid(doc)
        r = doc["rows"][0]
        self.assertEqual((r["spend"], r["currency"], r["frequency"]), (1200000, "UZS", 1.25))
        self.assertEqual(doc["unmapped_columns"], ["Mystery Col"])
        self.assertEqual(doc["skipped_rows"], 1)

    def test_generic_csv_default_date_and_currency_flag(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.csv"
            p.write_text("Campaign name,Spend,Impressions\nA,10,100\n", encoding="utf-8")
            doc = nz.normalize("generic_csv", p, currency="usd", date="2026-11-09", platform="Meta")
            self.assertEqual((doc["rows"][0]["date"], doc["rows"][0]["currency"], doc["rows"][0]["platform"]), ("2026-11-09", "USD", "meta"))
            self.assertFalse(doc["rows"][0]["synthetic"])


class ErrorTests(unittest.TestCase):
    def test_no_spend_column_lists_unmapped(self) -> None:
        p = _run("generic_csv", "-i", str(RAW / "generic_no_spend.csv"))
        self.assertEqual(p.returncode, 2)
        out = json.loads(p.stdout)
        self.assertIn("Sarf", out["error"])
        self.assertEqual(out["unmapped_columns"], ["Foo", "Bar"])

    def test_missing_currency_not_guessed(self) -> None:
        p = _run("generic_csv", "-i", str(RAW / "generic_no_currency.csv"), "--date", "2026-11-01")
        self.assertEqual(p.returncode, 2)
        self.assertIn("valyuta", json.loads(p.stdout)["error"])

    def test_missing_file_and_bad_json_and_unknown_adapter(self) -> None:
        self.assertEqual(_run("meta_graph", "-i", "/nonexistent/x.json").returncode, 2)
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            self.assertEqual(_run("meta_graph", "-i", str(bad)).returncode, 2)
        self.assertEqual(_run("nope", "-i", "x").returncode, 2)
        self.assertEqual(_run("meta_graph").returncode, 2)

    def test_negative_spend_rejected(self) -> None:
        with self.assertRaises(nz.NormalizeError):
            nz.normalize_meta({"data": [{"date_start": "2026-11-01", "spend": "-5", "campaign_id": "1", "currency": "USD"}]}, source="meta_graph")

    def test_bad_level(self) -> None:
        with self.assertRaises(nz.NormalizeError):
            nz.normalize_meta({"data": []}, source="meta_graph", level="galaxy")


class CliTests(unittest.TestCase):
    def test_out_file_and_validate_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "m.json"
            p = _run("meta_graph", "-i", str(RAW / "meta_graph_insights.json"), "-o", str(out))
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["rows"], 3)
            v = _run("validate", str(out))
            self.assertEqual(v.returncode, 0)
            self.assertTrue(json.loads(v.stdout)["valid"])
            self.assertEqual(len(nz.load_metrics_file(out)), 3)

    def test_committed_fixtures_validate(self) -> None:
        for f in MET.glob("*.json"):
            doc = json.loads(f.read_text())
            self.assertEqual(nz.validate_metrics(doc), [], f.name)
            self.assertTrue(all(r["synthetic"] for r in nz.rows_of(doc)), f.name)

    def test_list(self) -> None:
        p = _run("list")
        self.assertEqual(p.returncode, 0)
        self.assertIn("meta_mcp", p.stdout)


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = json.loads((MET / "sample_valid.json").read_text())

    def test_valid(self) -> None:
        self.assertEqual(nz.validate_metrics(self.doc), [])
        self.assertEqual(nz.validate_metrics(self.doc["rows"]), [])  # yalang ro'yxat

    def _bad(self, mutate):
        d = copy.deepcopy(self.doc)
        mutate(d["rows"][0])
        return nz.validate_metrics(d)

    def test_missing_required(self) -> None:
        errs = self._bad(lambda r: r.pop("spend"))
        self.assertTrue(any("spend" in e for e in errs))

    def test_bad_enum_and_source(self) -> None:
        self.assertTrue(self._bad(lambda r: r.update(level="galaxy")))
        self.assertTrue(self._bad(lambda r: r.update(source="telepathy")))
        self.assertTrue(self._bad(lambda r: r.update(evidence_label="TRUST_ME")))

    def test_bad_types_and_ranges(self) -> None:
        self.assertTrue(self._bad(lambda r: r.update(spend=-1)))
        self.assertTrue(self._bad(lambda r: r.update(spend="10")))
        self.assertTrue(self._bad(lambda r: r.update(spend=True)))
        self.assertTrue(self._bad(lambda r: r.update(conversions={"lead": "2"})))
        self.assertTrue(self._bad(lambda r: r.update(synthetic="yes")))

    def test_bad_date(self) -> None:
        self.assertTrue(self._bad(lambda r: r.update(date="01.11.2026")))
        errs = self._bad(lambda r: r.update(date="2026-13-45"))
        self.assertTrue(any("sana" in e for e in errs))

    def test_bad_envelope(self) -> None:
        self.assertTrue(nz.validate_metrics({"schema": "metrics.v2", "rows": []}))
        self.assertTrue(nz.validate_metrics({"schema": "metrics.v1"}))
        self.assertTrue(nz.validate_metrics("x"))

    def test_extra_fields_allowed(self) -> None:
        self.assertEqual(self._bad(lambda r: r.update(custom_field=1)), [])

    def test_load_metrics_file_rejects_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text(json.dumps({"schema": "metrics.v1", "rows": [{"date": "x"}]}), encoding="utf-8")
            with self.assertRaises(nz.NormalizeError):
                nz.load_metrics_file(p)


class HelperTests(unittest.TestCase):
    def test_parse_date(self) -> None:
        for raw, exp in (("2026-11-01", "2026-11-01"), ("2026-11-01T10:00:00Z", "2026-11-01"), ("01.11.2026", "2026-11-01"),
                         ("11/01/2026", "2026-11-01"), ("20261101", "2026-11-01"), ("", None), ("junk", None), (None, None)):
            self.assertEqual(nz.parse_date(raw), exp, raw)

    def test_num(self) -> None:
        self.assertEqual(nz.num("1 200 000"), 1200000)
        self.assertIsNone(nz.num("--"))
        self.assertIsNone(nz.num(True))
        self.assertIsNone(nz.num(float("nan")))
        self.assertEqual(nz.num(5), 5.0)


if __name__ == "__main__":
    unittest.main()
