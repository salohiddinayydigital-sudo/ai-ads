"""ad-export-analyzer.py: haqiqiy eksport sarlavhalari, ajratgichlar, sonlar va xato holatlari."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

import importlib

ae = importlib.import_module("ad-export-analyzer")
import tyrion_core as tcore  # noqa: E402

CSV_COMMA = 'Campaign name,Amount spent (USD),Results,Impressions\nA,"1,234.50",12,10000\n'
CSV_SEMI = 'Campaign name;Amount spent (USD);Results;Impressions\nA;1 234,50;12;10000\n'


def _write(tmp: str, name: str, text: str, encoding: str = "utf-8") -> Path:
    p = Path(tmp) / name
    p.write_bytes(text.encode(encoding))
    return p


class NumberParsingTests(unittest.TestCase):
    def test_localized_numbers(self) -> None:
        cases = {"1,234.50": 1234.5, "1 234,50": 1234.5, "1.234,50": 1234.5, "12,5": 12.5,
                 "$1,234": 1234.0, "1,234,567": 1234567.0, "45%": 45.0, "1234.5": 1234.5}
        for raw, want in cases.items():
            self.assertEqual(tcore.parse_localized_number(raw), want, raw)
        for raw in ("", "abc", "nan", None):
            self.assertIsNone(tcore.parse_localized_number(raw), repr(raw))


class HeaderNormalisationTests(unittest.TestCase):
    def test_meta_comma_quoted_thousands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "a.csv", CSV_COMMA))
        self.assertEqual(res["summary"]["total_spend"], 1234.5)
        self.assertEqual(res["currency"], "USD")
        self.assertAlmostEqual(res["decisions"][0]["cpa"], 102.88, places=2)

    def test_semicolon_and_space_thousands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "a.csv", CSV_SEMI))
        self.assertEqual(res["summary"]["total_spend"], 1234.5)
        self.assertAlmostEqual(res["decisions"][0]["cpa"], 102.88, places=2)

    def test_tab_delimiter_and_bom(self) -> None:
        text = "﻿Campaign name\tAmount spent (USD)\tResults\nA\t200\t10\n"
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "a.tsv", text))
        self.assertEqual(res["summary"]["total_spend"], 200.0)
        self.assertEqual(res["decisions"][0]["name"], "A")

    def test_case_whitespace_and_currency_suffix(self) -> None:
        text = "  CAMPAIGN NAME ,  amount   SPENT (uzs) ,RESULTS\nA,500000,10\n"
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "a.csv", text))
        self.assertEqual(res["summary"]["total_spend"], 500000.0)
        self.assertEqual(res["currency"], "UZS")

    def test_google_ads_headers(self) -> None:
        text = "Campaign,Currency code,Cost,Impr.,Clicks,Conversions,Conv. value\nG1,EUR,100.5,5000,200,10,400\n"
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "g.csv", text))
        d = res["decisions"][0]
        self.assertEqual((d["spend"], d["conversions"], d["revenue"], d["currency"]), (100.5, 10, 400.0, "EUR"))

    def test_telegram_headers(self) -> None:
        text = "Title,Views,Clicks,Spent,Actions\nTG1,50000,400,25.5,17\n"
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "t.csv", text))
        d = res["decisions"][0]
        self.assertEqual((d["name"], d["spend"], d["conversions"]), ("TG1", 25.5, 17))

    def test_russian_headers(self) -> None:
        text = "Название кампании;Расход (RUB);Показы;Клики;Конверсии;Доход\nК1;12 345,60;100000;900;30;60000\n"
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "r.csv", text))
        d = res["decisions"][0]
        self.assertEqual((d["name"], d["spend"], d["conversions"], d["currency"]), ("К1", 12345.6, 30, "RUB"))
        self.assertEqual(d["revenue"], 60000.0)

    def test_unmapped_columns_reported(self) -> None:
        text = "Campaign name,Amount spent (USD),Results,Weird Col,Another\nA,10,1,x,y\n"
        with tempfile.TemporaryDirectory() as tmp:
            res = ae.analyze_export(_write(tmp, "a.csv", text))
        self.assertEqual(sorted(res["unmapped_columns"]), ["Another", "Weird Col"])


class ErrorHandlingTests(unittest.TestCase):
    def test_missing_spend_column_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "a.csv", "Campaign name,Results\nA,3\n")
            with self.assertRaises(ae.ExportFormatError):
                ae.analyze_export(p)
            rc = run_tool_inproc("ad-export-analyzer.py", "analyze", "--file", str(p)).returncode
        self.assertEqual(rc, 2)

    def test_empty_file_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for body in ("", "Campaign name,Amount spent (USD)\n"):
                p = _write(tmp, "e.csv", body)
                proc = run_tool_inproc("ad-export-analyzer.py", "analyze", "--file", str(p))
                self.assertEqual(proc.returncode, 2, body)
                self.assertIn("Xato", proc.stderr)

    def test_missing_file_exit_code(self) -> None:
        proc = run_tool_inproc("ad-export-analyzer.py", "analyze", "--file", "/nonexistent/x.csv")
        self.assertEqual(proc.returncode, 2)

    def test_cli_json_includes_unmapped_and_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "a.csv", CSV_COMMA + "")
            proc = run_tool_inproc("ad-export-analyzer.py", "analyze", "--file", str(p), "--json")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["summary"]["total_spend"], 1234.5)

    def test_non_finite_cli_args_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "a.csv", CSV_COMMA)
            proc = run_tool_inproc("ad-export-analyzer.py", "analyze", "--file", str(p), "--target-cpa", "nan")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
