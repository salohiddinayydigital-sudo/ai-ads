"""experiments.py: ma'lum qiymatlar bilan hisoblar, ledger, promote va packet."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._helpers import run_tool_inproc

import experiments as ex  # noqa: E402


class DesignMath(unittest.TestCase):
    def test_sample_size_known_values(self):
        # qo'lda: p1=.05,p2=.06,alpha=.05,power=.8 -> ((1.95996*0.32242)+(0.84162*0.32233))^2/0.0001 ~ 8157.x -> 8158
        self.assertEqual(ex.sample_size_per_arm(0.05, 0.06), 8158)
        self.assertEqual(ex.sample_size_per_arm(0.10, 0.12), 3841)
        self.assertEqual(ex.sample_size_per_arm(0.50, 0.55, 0.05, 0.9), 2095)

    def test_design_relative_vs_absolute_equivalent(self):
        a = ex.design(0.05, mde=0.2)
        b = ex.design(0.05, mde_abs=0.01)
        self.assertEqual(a["n_per_arm"], b["n_per_arm"])
        self.assertEqual(a["n_total"], 2 * 8158)

    def test_design_budget_and_days(self):
        r = ex.design(0.05, mde=0.2, cost_per_unit=0.4, daily_budget=500, target_cpa=10)
        self.assertAlmostEqual(r["budget"]["total"], 16316 * 0.4, places=2)
        self.assertEqual(r["budget"]["days_needed"], 14)  # 6526.4/500 = 13.05 -> 14
        self.assertIn("learning_phase", r)
        self.assertEqual(ex.design(0.05, mde=0.2, cost_per_unit=1, daily_budget=10000)["budget"]["days_recommended"], 7)

    def test_bonferroni_for_three_arms(self):
        r = ex.design(0.05, mde=0.2, arms=3)
        self.assertAlmostEqual(r["alpha_adjusted"], 0.025)
        self.assertGreater(r["n_per_arm"], 8158)

    def test_design_validation(self):
        for kw in (dict(baseline=float("nan"), mde=0.2), dict(baseline=0.05), dict(baseline=0.05, mde=0.2, mde_abs=0.01),
                   dict(baseline=1.5, mde=0.2), dict(baseline=0.9, mde_abs=0.2), dict(baseline=0.05, mde=0.2, daily_budget=10)):
            with self.assertRaises(ex.ExperimentError, msg=str(kw)):
                ex.design(**kw)


class Readout(unittest.TestCase):
    def test_known_stats(self):
        r = ex.readout(1000, 100, 1000, 130)
        self.assertAlmostEqual(r["z"], 2.1025, places=3)
        self.assertAlmostEqual(r["p_value"], 0.0355, places=3)
        self.assertAlmostEqual(r["ci_diff"][0], 0.002066, places=4)
        self.assertAlmostEqual(r["ci_diff"][1], 0.057934, places=4)
        self.assertAlmostEqual(r["relative_lift"], 0.3)
        self.assertEqual(r["verdict"], "WIN")
        self.assertTrue(any("Rejalashtirilgan" in w for w in r["warnings"]))

    def test_bayes_deterministic_and_sane(self):
        a = ex.readout(1000, 100, 1000, 130, seed=1)["bayes"]
        b = ex.readout(1000, 100, 1000, 130, seed=1)["bayes"]
        self.assertEqual(a, b)
        self.assertGreater(a["prob_variant_better"], 0.95)
        self.assertLess(ex.bayes_prob_best(1000, 130, 1000, 100)["prob_variant_better"], 0.05)

    def test_loss(self):
        self.assertEqual(ex.readout(1000, 130, 1000, 100)["verdict"], "LOSS")

    def test_inconclusive_no_difference(self):
        r = ex.readout(1000, 100, 1000, 102)
        self.assertEqual(r["verdict"], "INCONCLUSIVE")
        self.assertFalse(r["significant"])

    def test_underpowered_never_wins(self):
        r = ex.readout(1000, 100, 1000, 130, planned_n_per_arm=5000)
        self.assertEqual(r["verdict"], "INCONCLUSIVE")
        self.assertTrue(r["significant_but_underpowered"])
        self.assertTrue(any("kichik" in w for w in r["warnings"]))

    def test_low_conversions_never_decisive(self):
        r = ex.readout(100, 2, 100, 12, planned_n_per_arm=50)
        self.assertEqual(r["verdict"], "INCONCLUSIVE")
        self.assertTrue(any("kam" in w for w in r["warnings"]))

    def test_validation(self):
        for args in ((0, 0, 10, 1), (10, 11, 10, 1), (10, -1, 10, 1), (10, float("nan"), 10, 1)):
            with self.assertRaises(ex.ExperimentError):
                ex.readout(*args)


class LedgerFlow(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.path = ex.ledger_path(self.td.name, "syn-client")

    def tearDown(self):
        self.td.cleanup()

    def _reg(self, **kw):
        base = dict(name="Hook UGC vs studio", hypothesis="UGC hook CPL ni kamaytiradi", metric="lead_rate", baseline=0.10, mde=0.2,
                    n_per_arm=900, owner="media-buyer", synthetic=True)
        base.update(kw)
        return ex.register(self.path, **base)

    def test_register_ids_increment(self):
        self.assertEqual(self._reg()["id"], "EXP-0001")
        self.assertEqual(self._reg(name="ikkinchi")["id"], "EXP-0002")
        self.assertEqual(len(ex.read_ledger(self.path)), 2)

    def test_register_requires_fields(self):
        with self.assertRaises(ex.ExperimentError):
            self._reg(name="")

    def test_readout_writes_event_with_plan(self):
        self._reg()
        res = ex.do_readout(self.path, "EXP-0001", 1000, 100, 1000, 130)
        self.assertEqual(res["verdict"], "WIN")
        events = ex.read_ledger(self.path)
        self.assertEqual(events[-1]["event"], "readout")
        self.assertEqual(events[-1]["id"], "EXP-0001")
        with self.assertRaises(ex.ExperimentError):
            ex.do_readout(self.path, "EXP-9999", 10, 1, 10, 1)

    def test_promote_flow_with_fake_runner(self):
        self._reg()
        with self.assertRaises(ex.ExperimentError):  # readout yo'q
            ex.promote(self.path, "EXP-0001", dry_run=True)
        ex.do_readout(self.path, "EXP-0001", 1000, 100, 1000, 102)
        with self.assertRaises(ex.ExperimentError):  # INCONCLUSIVE
            ex.promote(self.path, "EXP-0001", dry_run=True)
        ex.do_readout(self.path, "EXP-0001", 1000, 100, 1000, 140)
        calls = []

        def fake(argv, **kw):
            calls.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

        res = ex.promote(self.path, "EXP-0001", runner=fake)
        self.assertTrue(res["ok"])
        self.assertIn("instincts.py", calls[0][1])
        a = calls[0]
        self.assertEqual(a[a.index("--domain") + 1], "meta")
        self.assertEqual(a[a.index("--confidence") + 1], "3")
        self.assertIn("[SYNTHETIC]", a[a.index("--evidence") + 1])
        self.assertEqual(ex.read_ledger(self.path)[-1]["event"], "promoted")

    def test_promote_dry_run_calls_real_instincts_without_writing(self):
        self._reg()
        ex.do_readout(self.path, "EXP-0001", 1000, 100, 1000, 140)
        manifest = ex.ROOT / "manifests" / "instincts.json"
        before = manifest.read_text(encoding="utf-8")
        res = ex.promote(self.path, "EXP-0001", dry_run=True)
        self.assertTrue(res["ok"], res)
        self.assertEqual(before, manifest.read_text(encoding="utf-8"))
        self.assertNotEqual(ex.read_ledger(self.path)[-1]["event"], "promoted")

    def test_replicated_raises_confidence(self):
        self._reg()
        ex.do_readout(self.path, "EXP-0001", 1000, 100, 1000, 140)
        ex.do_readout(self.path, "EXP-0001", 2000, 200, 2000, 280)
        res = ex.promote(self.path, "EXP-0001", dry_run=True, runner=lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "", ""))
        self.assertTrue(res["replicated"])
        self.assertIn("4", res["argv"])

    def test_packet_never_autocreates_and_has_rollback(self):
        reg = self._reg()
        for kind, tool in (("native_ab", "ads_experiment_abtest_create_test"), ("lift", "ads_experiment_lift_create_test")):
            pkt = ex.build_packet(reg, kind)
            self.assertEqual(pkt["proposed_tool"], tool)
            self.assertFalse(pkt["approved_by_user"])
            self.assertFalse(pkt["auto_created"])
            self.assertTrue(pkt["rollback"])
            self.assertTrue(pkt["synthetic"])
        with self.assertRaises(ex.ExperimentError):
            ex.build_packet(reg, "bogus")


class CLI(unittest.TestCase):
    def _run(self, *a):
        return run_tool_inproc("experiments.py", *a)

    def test_design_cli(self):
        p = self._run("design", "--baseline", "0.05", "--mde", "0.2")
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout)["n_per_arm"], 8158)

    def test_design_cli_errors_exit2(self):
        self.assertEqual(self._run("design", "--baseline", "nan", "--mde", "0.2").returncode, 2)
        self.assertEqual(self._run("design", "--baseline", "0.05").returncode, 2)

    def test_readout_cli_no_ledger(self):
        p = self._run("readout", "--control-n", "1000", "--control-conv", "100", "--variant-n", "1000", "--variant-conv", "130")
        self.assertEqual(json.loads(p.stdout)["verdict"], "WIN")

    def test_full_cli_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            c = ["--client", "syn", "--clients-dir", td]
            r = self._run("register", *c, "--name", "t", "--hypothesis", "h", "--metric", "m", "--baseline", "0.1", "--mde", "0.2",
                          "--n-per-arm", "900", "--synthetic")
            self.assertEqual(r.returncode, 0)
            p = self._run("packet", *c, "--id", "EXP-0001", "--kind", "lift")
            self.assertEqual(p.returncode, 0)
            self.assertTrue((Path(td) / "syn" / "changes" / "EXP-0001-lift.json").exists())
            ro = self._run("readout", *c, "--id", "EXP-0001", "--control-n", "1000", "--control-conv", "100",
                           "--variant-n", "1000", "--variant-conv", "140")
            self.assertEqual(json.loads(ro.stdout)["verdict"], "WIN")
            bad = self._run("readout", "--id", "EXP-0001", "--control-n", "1", "--control-conv", "0", "--variant-n", "1", "--variant-conv", "0")
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(self._run("packet", *c, "--id", "EXP-0099", "--kind", "lift").returncode, 2)


if __name__ == "__main__":
    unittest.main()
