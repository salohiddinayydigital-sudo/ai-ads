"""pulse.py: har tekshiruv uchun 'topadi' va 'topmaydi' (sintetik ma'lumot)."""

from __future__ import annotations

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

import pulse  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "pulse"
END = dt.date(2026, 11, 15)


def make_rows(n=35, mod=None, **base):
    """Sintetik kunlik qatorlar. mod(back, row) — back=0 oxirgi kun."""
    rows = []
    for i in range(n):
        back = n - 1 - i
        r = {"date": str(END - dt.timedelta(days=back)), "platform": "meta", "account_id": "act_syn", "level": "campaign",
             "entity_id": "c1", "entity_name": "SYN", "spend": 100.0 + (i % 3 - 1) * 2, "currency": "USD",
             "impressions": 20000, "frequency": 1.5, "clicks": 500, "conversions": {"Lead": 10}, "conversion_value": 400.0,
             "source": "csv", "evidence_label": "MEASURED_ACCOUNT_DATA", "synthetic": True}
        r.update(base)
        if mod:
            mod(back, r)
        rows.append(r)
    return rows


def run(rows, state=None, anomaly=None):
    return pulse.run_pulse({"rows": rows}, state or {"goals": {"daily_budget": 100, "conversion_event": "Lead"}}, anomaly, client="syn")


def status(rep, check):
    return next(c["status"] for c in rep["checks"] if c["check"] == check)


def ids(rep):
    return {f["id"] for f in rep["findings"]}


class PulseChecks(unittest.TestCase):
    # ── pacing
    def test_pacing_finds(self):
        rep = run(make_rows(mod=lambda b, r: r.update(spend=160.0) if b < 7 else None))
        self.assertEqual(status(rep, "pacing"), "flagged")
        f = next(f for f in rep["findings"] if f["id"] == "pacing")
        self.assertEqual(f["severity"], "critical")
        self.assertTrue(f["needs_approval"])

    def test_pacing_ok(self):
        self.assertEqual(status(run(make_rows()), "pacing"), "ok")

    def test_pacing_skipped_without_budget(self):
        self.assertEqual(status(pulse.run_pulse({"rows": make_rows()}, {}), "pacing"), "skipped")

    # ── CPA drift
    def test_cpa_drift_finds(self):
        rep = run(make_rows(mod=lambda b, r: r.update(conversions={"Lead": 5}) if b < 7 else None))
        self.assertEqual(status(rep, "cpa_drift"), "flagged")
        f = next(f for f in rep["findings"] if f["check"] == "cpa_drift")
        self.assertLess(f["evidence"]["p_value"], 0.05)
        self.assertGreater(f["evidence"]["change_pct"], 25)

    def test_cpa_drift_ok_stable(self):
        self.assertEqual(status(run(make_rows()), "cpa_drift"), "ok")

    def test_cpa_drift_small_sample_says_insufficient(self):
        rep = run(make_rows(mod=lambda b, r: r.update(conversions={"Lead": 1}) if b < 7 else None))
        self.assertEqual(status(rep, "cpa_drift"), "insufficient_data")
        f = next(f for f in rep["findings"] if f["id"] == "cpa_drift")
        self.assertEqual(f["severity"], "info")

    def test_cpa_not_flagged_when_not_significant(self):
        # 25%+ farq, lekin konversiya kam => p yuqori (min_conversions pasaytirilgan)
        state = {"goals": {"daily_budget": 100, "conversion_event": "Lead"}, "pulse_config": {"min_conversions": 3}}
        rows = make_rows(n=14, conversions={"Lead": 0}, mod=lambda b, r: r.update(conversions={"Lead": 1 if b % 2 else 0}) if b >= 7 else r.update(conversions={"Lead": 1 if b in (0, 3, 5) else 0}))
        rep = pulse.run_pulse({"rows": rows}, state, None)
        self.assertNotEqual(status(rep, "cpa_drift"), "flagged")

    def test_rate_ratio_p_known(self):
        self.assertAlmostEqual(pulse.rate_ratio_p(100, 1000, 100, 1000), 1.0, places=6)
        self.assertLess(pulse.rate_ratio_p(200, 1000, 100, 1000), 1e-6)

    # ── ROAS drift
    def test_roas_drift_finds(self):
        rep = run(make_rows(mod=lambda b, r: r.update(conversion_value=200.0) if b < 7 else None))
        self.assertEqual(status(rep, "roas_drift"), "flagged")

    def test_roas_drift_ok(self):
        self.assertEqual(status(run(make_rows()), "roas_drift"), "ok")

    # ── fatigue
    def test_fatigue_finds(self):
        rep = run(make_rows(mod=lambda b, r: r.update(frequency=2.4, clicks=380) if b < 7 else None))
        self.assertEqual(status(rep, "fatigue"), "flagged")

    def test_fatigue_ok_when_only_frequency_up(self):
        rep = run(make_rows(mod=lambda b, r: r.update(frequency=2.4) if b < 7 else None))
        self.assertEqual(status(rep, "fatigue"), "ok")

    # ── tracking break
    def test_tracking_break_finds(self):
        rep = run(make_rows(mod=lambda b, r: r.update(conversions={"Lead": 0}) if b < 3 else None))
        self.assertEqual(status(rep, "tracking_break"), "flagged")
        f = next(f for f in rep["findings"] if f["id"] == "tracking_break")
        self.assertEqual(f["severity"], "critical")
        self.assertFalse(f["needs_approval"])

    def test_tracking_ok_when_traffic_also_collapsed(self):
        def mod(b, r):
            if b < 3:
                r.update(conversions={"Lead": 0}, clicks=50, spend=10.0)
        self.assertEqual(status(run(make_rows(mod=mod)), "tracking_break"), "ok")

    def test_tracking_ok_healthy(self):
        self.assertEqual(status(run(make_rows()), "tracking_break"), "ok")

    # ── spend spike
    def test_spend_spike_finds(self):
        rep = run(make_rows(mod=lambda b, r: r.update(spend=400.0) if b == 0 else None))
        self.assertEqual(status(rep, "spend_spike"), "flagged")

    def test_spend_spike_ok(self):
        self.assertEqual(status(run(make_rows()), "spend_spike"), "ok")

    # ── delivery
    def test_delivery_finds_rejected_and_learning_limited(self):
        def mod(b, r):
            if b == 0:
                r["delivery_status"] = "learning_limited"
        rows = make_rows(mod=mod)
        rows.append(dict(rows[-1], level="ad", entity_id="ad9", delivery_status="REJECTED"))
        rep = run(rows)
        self.assertEqual(status(rep, "delivery_status"), "flagged")
        self.assertIn("delivery_status:ad9", ids(rep))
        self.assertIn("delivery_status:c1", ids(rep))

    def test_delivery_ok_and_skipped(self):
        rows = make_rows(delivery_status="active")
        self.assertEqual(status(run(rows), "delivery_status"), "ok")
        self.assertEqual(status(run(make_rows()), "delivery_status"), "skipped")

    # ── anomaly signal
    def test_anomaly_signal_included_and_absent(self):
        rep = run(make_rows(), anomaly={"signals": [{"metric": "cpa", "severity": "warning", "entity_id": "c1"}]})
        self.assertIn("platform_anomaly:c1", ids(rep))
        self.assertNotIn("platform_anomaly", {c["check"] for c in run(make_rows())["checks"]})

    # ── umumiy
    def test_healthy_has_no_findings_and_is_readonly(self):
        rep = run(make_rows())
        self.assertEqual(rep["findings"], [])
        self.assertTrue(rep["read_only"])
        self.assertEqual(rep["executed_actions"], [])
        self.assertTrue(rep["synthetic"])
        self.assertTrue(rep["config_label"].startswith("HEURISTIC_PRIOR_MODEL"))

    def test_pulse_config_override(self):
        state = {"goals": {"daily_budget": 100, "conversion_event": "Lead"}, "pulse_config": {"pacing_tolerance_pct": 80}}
        rep = pulse.run_pulse({"rows": make_rows(mod=lambda b, r: r.update(spend=160.0) if b < 7 else None)}, state)
        self.assertEqual(status(rep, "pacing"), "ok")
        self.assertIn("pacing_tolerance_pct", rep["config_label"])

    def test_bad_input(self):
        with self.assertRaises(pulse.PulseError):
            pulse.run_pulse({"rows": []}, {})
        with self.assertRaises(pulse.PulseError):
            pulse.run_pulse({"rows": [{"spend": 1}]}, {})
        with self.assertRaises(pulse.PulseError):
            pulse.run_pulse({"rows": [{"date": "2026-13-45"}]}, {})

    def test_markdown_has_sections(self):
        md = pulse.render_markdown(run(make_rows(mod=lambda b, r: r.update(spend=160.0) if b < 7 else None)))
        self.assertIn("## [CRITICAL] pacing", md)
        self.assertIn("Tasdiq kerak", md)


class PulseCLI(unittest.TestCase):
    def _run(self, *a):
        return run_tool_inproc("pulse.py", *a)

    def test_cli_problem_fixture(self):
        p = self._run("run", "--client", "syn", "--metrics", str(FIX / "problem.metrics.json"), "--state", str(FIX / "state.json"),
                      "--anomaly-signal", str(FIX / "anomaly.json"))
        self.assertEqual(p.returncode, 0)
        rep = json.loads(p.stdout)
        self.assertGreaterEqual(rep["summary"]["critical"], 3)
        self.assertTrue({"pacing", "tracking_break", "fatigue", "spend_spike"} <= {f["check"] for f in rep["findings"]})

    def test_cli_healthy_fixture_clean(self):
        p = self._run("run", "--client", "syn", "--metrics", str(FIX / "healthy.metrics.json"), "--state", str(FIX / "state.json"), "--fail-on", "warning")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout)["findings"], [])

    def test_cli_fail_on(self):
        p = self._run("run", "--client", "syn", "--metrics", str(FIX / "problem.metrics.json"), "--state", str(FIX / "state.json"), "--fail-on", "critical")
        self.assertEqual(p.returncode, 1)

    def test_cli_missing_metrics_exit2(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._run("run", "--client", "nobody", "--clients-dir", td)
        self.assertEqual(p.returncode, 2)

    def test_cli_write_and_default_paths(self):
        with tempfile.TemporaryDirectory() as td:
            cdir = Path(td) / "syn"
            (cdir / "data").mkdir(parents=True)
            (cdir / "data" / "metrics.v1.json").write_text((FIX / "healthy.metrics.json").read_text(encoding="utf-8"), encoding="utf-8")
            (cdir / "state.json").write_text((FIX / "state.json").read_text(encoding="utf-8"), encoding="utf-8")
            p = self._run("run", "--client", "syn", "--clients-dir", td, "--format", "md", "--write")
            self.assertEqual(p.returncode, 0)
            self.assertTrue((cdir / "pulse" / "2026-11-15.json").exists())
            self.assertTrue((cdir / "pulse" / "2026-11-15.md").exists())


if __name__ == "__main__":
    unittest.main()
