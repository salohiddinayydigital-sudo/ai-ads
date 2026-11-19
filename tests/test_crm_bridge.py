"""crm-bridge: hash, dedup, consent, dry-run, hisobot, parserlar (sintetik fixture)."""

from __future__ import annotations

import hashlib
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from tests._helpers import run_tool_inproc

import importlib

crm = importlib.import_module("crm-bridge")
FX = Path(__file__).parent / "fixtures" / "crm"
SM = json.loads((FX / "stage_map.json").read_text())


def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class CrmBridgeTests(unittest.TestCase):
    def leads(self):
        return crm.apply_stage_map(crm.load_leads(FX / "leads.csv", "csv"), SM)

    def test_phone_formats(self) -> None:
        for raw in ("+998 90 123 45 67", "998901234567", "901234567", "0 90 123 45 67", "00998901234567"):
            self.assertEqual(crm.normalize_phone(raw), "998901234567", raw)

    def test_payload_golden(self) -> None:
        p = crm.build_payload(self.leads())
        ids = [e["event_id"] for e in p["data"]]
        self.assertEqual(ids, ["crm_L1_Lead", "crm_L2_QualifiedLead", "crm_L4_Purchase"])
        e0 = p["data"][0]
        self.assertEqual(e0["user_data"]["ph"], [_h("998901234567")])
        self.assertEqual(e0["user_data"]["em"], [_h("ali@example.test")])
        self.assertEqual(p["data"][1]["user_data"]["lead_id"], "111222333")
        self.assertEqual(p["data"][2]["custom_data"]["value"], 3000000)
        self.assertEqual(p["data"][2]["user_data"]["ph"], [_h("998937778899")])

    def test_dedup_consent_unmapped(self) -> None:
        sk = crm.build_payload(self.leads())["skipped"]
        self.assertEqual(sk["duplicate"], 1)
        self.assertEqual(sk["no_consent"], 1)
        self.assertEqual(sk["unmapped_stage"], 1)

    def test_no_raw_pii_in_payload(self) -> None:
        txt = json.dumps(crm.build_payload(self.leads()))
        for raw in ("998901234567", "Ali@Example", "ali@example", "Tashkent", "Sardor"):
            self.assertNotIn(raw, txt)

    def test_report(self) -> None:
        r = crm.report(self.leads())
        c1 = next(x for x in r["by_campaign"] if x["campaign"] == "C1")
        self.assertEqual((c1["leads"], c1["qualified"]), (3, 1))
        self.assertEqual(r["totals"]["unmapped"], 1)

    def test_parsers(self) -> None:
        a = crm.parse_amocrm(json.loads((FX / "amocrm.json").read_text()))
        self.assertEqual((a[0]["lead_id"], a[0]["campaign"], a[0]["phone"]), ("101", "C1", "+998901234567"))
        b = crm.parse_bitrix24(json.loads((FX / "bitrix24.json").read_text()))
        self.assertEqual((b[0]["value"], b[0]["campaign"]), (2500000.0, "C9"))

    def test_send_without_confirm_is_dry_run(self) -> None:
        args = ("send", "--input", str(FX / "leads.csv"), "--stage-map", str(FX / "stage_map.json"), "--dataset-id", "1")
        with mock.patch.object(crm, "send") as sent:
            p = run_tool_inproc("crm-bridge.py", *args)
        sent.assert_not_called()
        self.assertEqual(p.returncode, 0)
        self.assertTrue(json.loads(p.stdout)["dry_run"])

    def test_send_requires_token(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("META_CAPI_TOKEN", None)
            self.assertIn("error", crm.send({"data": []}, "1"))

    def test_bad_input_exit2(self) -> None:
        p = run_tool_inproc("crm-bridge.py", "report", "--input", "/nope.csv", "--stage-map", str(FX / "stage_map.json"))
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
