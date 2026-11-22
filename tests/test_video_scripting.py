"""Video pre-production tizimi: `creative-matrix.py video-script --mode ...`, JSON sxemalar, reference/shablon/buyruq/agent/eval butunligi.

LLM chaqirmaydi, tarmoq kerak emas. Montaj/render fayllariga tegilmaganini ham tekshiradi (scope chegarasi).
"""

from __future__ import annotations

import importlib
import itertools
import json
import re
import subprocess
import unittest

from tests._helpers import VAULT, run_tool_inproc

cm = importlib.import_module("creative-matrix")

MODES = ("sales", "organic", "plan", "motion")
REFS = ("sales-video-scripting", "organic-video-content", "video-content-planning", "motion-video-scripting", "script-quality-rubric")
TEMPLATES = ("sales-video-script", "organic-video-script", "video-content-plan", "motion-video-blueprint")
COMMAND_PAIRS = (("video-ssenariy", "video-script"), ("video-reja", "video-plan"), ("motion-ssenariy", "motion-script"))
EVALS = ("sales-video-uz-1", "organic-video-uz-1", "video-plan-uz-1", "motion-script-uz-1")


def validate(instance, schema, root=None, path="$") -> list[str]:
    """Kichik stdlib JSON-Schema tekshiruvchisi (type/const/enum/required/properties/items/min*/pattern/allOf-if-then)."""
    root = root or schema
    errs: list[str] = []
    t = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool}
    if t and not (isinstance(instance, types[t]) and not (t in ("integer", "number") and isinstance(instance, bool))):
        return [f"{path}: type {t} kutilgan, {type(instance).__name__} keldi"]
    if "const" in schema and instance != schema["const"]:
        errs.append(f"{path}: const {schema['const']!r} != {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{path}: {instance!r} enum'da yo'q")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errs.append(f"{path}: {instance} < minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errs.append(f"{path}: {instance} > maximum")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errs.append(f"{path}: {instance} <= exclusiveMinimum")
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errs.append(f"{path}: pattern mos emas ({instance!r})")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errs.append(f"{path}: juda qisqa")
    if isinstance(instance, dict):
        for k in schema.get("required", []):
            if k not in instance:
                errs.append(f"{path}: '{k}' yo'q")
        for k, sub in schema.get("properties", {}).items():
            if k in instance:
                errs += validate(instance[k], sub, root, f"{path}.{k}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errs.append(f"{path}: {len(instance)} < minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errs.append(f"{path}: {len(instance)} > maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, el in enumerate(instance):
                errs += validate(el, schema["items"], root, f"{path}[{i}]")
    for clause in schema.get("allOf", []):
        cond = clause.get("if")
        if cond is None or not validate(instance, cond, root, path):
            errs += validate(instance, clause.get("then", {}), root, path)
    return errs


def automated_ok(res: dict) -> bool:
    return all(v for k, v in res["self_audit_checklist"]["automated_checks"].items() if k != "issues")


class VideoBlueprintGeneratorTests(unittest.TestCase):
    def test_all_modes_langs_durations_pass_automated_checks(self) -> None:
        for mode, lang, dur in itertools.product(MODES, ("uz", "ru", "en"), cm.VIDEO_DURATIONS):
            with self.subTest(mode=mode, lang=lang, duration=dur):
                res = cm.generate_video_blueprint(mode, product="Ingliz tili kursi", problem="gapira olmaslik", lang=lang, duration_sec=dur)
                self.assertTrue(automated_ok(res), res["self_audit_checklist"]["automated_checks"]["issues"])
                self.assertFalse(cm.lint_unverified_claims(res)["needs_verification"], "skelet o'zida da'vo (foiz/kafolat/...) yaratmasligi kerak")

    def test_sales_modular_structure_and_time_sum(self) -> None:
        for hooks in (3, 4, 5):
            res = cm.generate_video_blueprint("sales", product="Implant", problem="tish yo'qotilishi", duration_sec=30, hooks=hooks)
            mods = res["modules"]
            self.assertEqual(len(mods["hooks"]), hooks)
            self.assertEqual(len({h["mechanism"] for h in mods["hooks"]}), hooks, "hook mexanizmlari farqli bo'lishi kerak")
            self.assertEqual(len(mods["bodies"]), 2)
            self.assertEqual({c["type"] for c in mods["ctas"]}, {"direct", "soft"})
            self.assertEqual(len(mods["combinations"]), hooks * 4)
            for h in mods["hooks"]:
                self.assertTrue(h["visual_0_3s"] and h["on_screen_text"] and h["spoken_line"])
            rows = res["av_table"]
            self.assertEqual(rows[0]["start_s"], 0.0)
            self.assertEqual(rows[-1]["end_s"], 30.0)
            self.assertTrue(all(b["start_s"] == a["end_s"] for a, b in zip(rows, rows[1:])))
            self.assertTrue(all(r["end_s"] - r["start_s"] <= 5.0 for r in rows), "har ~2-4 s da o'zgarish: qator 5 s dan uzun bo'lmasin")

    def test_sales_uses_price_only_when_provided(self) -> None:
        no_price = cm.generate_video_blueprint("sales", product="Kurs", duration_sec=30)
        with_price = cm.generate_video_blueprint("sales", product="Kurs", duration_sec=30, price=1500000, currency="UZS")
        self.assertNotIn("1 500 000", json.dumps(no_price))
        self.assertIn("1 500 000 UZS", json.dumps(with_price, ensure_ascii=False))

    def test_organic_formats_all_supported(self) -> None:
        for fmt in cm.ORGANIC_FORMATS:
            with self.subTest(fmt=fmt):
                res = cm.generate_video_blueprint("organic", product="Ekspert", content_format=fmt, duration_sec=45)
                self.assertEqual(res["content_format"], fmt)
                self.assertTrue(automated_ok(res))
                self.assertIn("save_or_share_reason", res["brief"])
                self.assertEqual(res["av_table"][-1]["end_s"], 45.0)

    def test_plan_funnel_balance_formats_and_batch_days(self) -> None:
        for weeks, per_week in ((1, 5), (2, 5), (4, 7), (4, 14)):
            res = cm.generate_video_blueprint("plan", weeks=weeks, per_week=per_week, start_date="2026-12-01")
            total = weeks * per_week
            counts = res["funnel_mix"]["counts"]
            self.assertEqual(sum(counts.values()), total)
            self.assertGreaterEqual(counts["BOFU"], 1)
            self.assertGreater(counts["TOFU"], counts["BOFU"])
            self.assertEqual(len(res["content_matrix"]), total)
            for w in range(weeks):
                wk = res["content_matrix"][w * per_week:(w + 1) * per_week]
                if per_week >= 3:
                    self.assertGreaterEqual(len({m["format"] for m in wk}), 3)
            self.assertEqual(sum(d["video_count"] for d in res["batch_shooting_plan"]), total)
            self.assertTrue(all(d["video_count"] <= 10 for d in res["batch_shooting_plan"]))
            self.assertTrue(re.match(r"\d{4}-\d{2}-\d{2}", res["content_matrix"][0]["date"]))
        fmts = [m["format"] for m in cm.generate_video_blueprint("plan", weeks=2, per_week=5)["content_matrix"]]
        self.assertTrue(all(a != b for a, b in zip(fmts, fmts[1:])), "ketma-ket bir xil format bo'lmasin")

    def test_motion_types_storyboard_integrity(self) -> None:
        for mtype in cm.MOTION_TYPES:
            for dur in ((5, 8, 10) if mtype == "bumper" else (15, 30, 45, 60)):
                with self.subTest(type=mtype, duration=dur):
                    res = cm.generate_video_blueprint("motion", motion_type=mtype, duration_sec=dur)
                    sb = res["storyboard"]
                    self.assertAlmostEqual(sum(s["duration_s"] for s in sb), dur, places=2)
                    self.assertTrue(all(s["duration_s"] >= 1.5 for s in sb))
                    if mtype != "bumper":
                        self.assertLessEqual(sb[0]["duration_s"], 3.0)
                    self.assertTrue(all(s["motion_cue"] and s["sfx_music"] and s["vo_word_limit"] >= 0 for s in sb))
                    self.assertGreaterEqual(len(res["asset_checklist"]), 5)
        bumper = cm.generate_video_blueprint("motion", motion_type="bumper", duration_sec=8)
        self.assertAlmostEqual(sum(s["duration_s"] for s in bumper["storyboard"]), 8, places=2)

    def test_motion_ratio_changes_safe_zone(self) -> None:
        self.assertIn("720x1200", cm.generate_video_blueprint("motion", ratio="9:16")["brief"]["safe_zone"])
        self.assertNotIn("720x1200", cm.generate_video_blueprint("motion", ratio="16:9")["brief"]["safe_zone"])

    def test_invalid_parameters_raise(self) -> None:
        bad = [
            dict(mode="nope"), dict(mode="sales", duration_sec=20), dict(mode="sales", lang="fr"), dict(mode="sales", hooks=2),
            dict(mode="sales", hooks=6), dict(mode="plan", weeks=3), dict(mode="plan", per_week=0), dict(mode="plan", start_date="2026-13-40"),
            dict(mode="motion", ratio="4:5"), dict(mode="motion", motion_type="bumper", duration_sec=30), dict(mode="sales", duration_sec=8), dict(mode="sales", awareness="x"), dict(mode="organic", content_format="x"),
        ]
        for kw in bad:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                cm.generate_video_blueprint(**kw)

    def test_check_av_table_detects_defects(self) -> None:
        good = cm.generate_video_blueprint("sales", product="X", duration_sec=30)["av_table"]
        self.assertTrue(cm.check_av_table(good, 30, 3)["time_sum_matches_duration"])
        self.assertFalse(cm.check_av_table(good, 45, 3)["time_sum_matches_duration"])
        gap = [dict(r) for r in good]
        gap[2]["start_s"] += 1
        self.assertFalse(cm.check_av_table(gap, 30)["time_sum_matches_duration"])
        wordy = [dict(r) for r in good]
        wordy[0]["vo"] = "bir ikki uch to'rt besh olti yetti sakkiz to'qqiz o'n"
        self.assertFalse(cm.check_av_table(wordy, 30)["vo_within_word_limit"])
        greet = [dict(r) for r in good]
        greet[0]["vo"] = "Assalomu alaykum, bugun"
        self.assertFalse(cm.check_av_table(greet, 30)["no_greeting_open"])
        self.assertFalse(cm.check_av_table([], 30)["time_sum_matches_duration"])


class VideoCliAndSchemaTests(unittest.TestCase):
    def test_cli_modes_json_and_schema_validation(self) -> None:
        sv = json.loads((VAULT / "schemas" / "video-script-schema.json").read_text(encoding="utf-8"))
        sm = json.loads((VAULT / "schemas" / "motion-blueprint-schema.json").read_text(encoding="utf-8"))
        for mode in MODES:
            with self.subTest(mode=mode):
                proc = run_tool_inproc("creative-matrix.py", "video-script", "--mode", mode, "--lang", "uz", "--duration", "30", "--hooks", "3",
                                       "--product", "Tish implantatsiyasi", "--problem", "tish yo'qotilishi", "--json")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                res = json.loads(proc.stdout)
                self.assertEqual(res["mode"], mode)
                self.assertIn("claim_safety", res)
                self.assertFalse(res["claim_safety"]["needs_verification"])
                self.assertEqual(validate(res, sm if mode == "motion" else sv), [])

    def test_schemas_validate_all_langs_and_durations(self) -> None:
        sv = json.loads((VAULT / "schemas" / "video-script-schema.json").read_text(encoding="utf-8"))
        sm = json.loads((VAULT / "schemas" / "motion-blueprint-schema.json").read_text(encoding="utf-8"))
        for mode, lang, dur in itertools.product(MODES, ("uz", "ru", "en"), (15, 30, 45, 60)):
            res = cm.generate_video_blueprint(mode, product="CRM", lang=lang, duration_sec=dur)
            self.assertEqual(validate(res, sm if mode == "motion" else sv), [], (mode, lang, dur))

    def test_schema_rejects_broken_documents(self) -> None:
        sv = json.loads((VAULT / "schemas" / "video-script-schema.json").read_text(encoding="utf-8"))
        res = cm.generate_video_blueprint("sales", product="X")
        broken = json.loads(json.dumps(res))
        del broken["av_table"]
        self.assertTrue(validate(broken, sv))
        broken = json.loads(json.dumps(res))
        broken["modules"]["hooks"] = broken["modules"]["hooks"][:2]
        self.assertTrue(validate(broken, sv))

    def test_cli_invalid_args_exit_2(self) -> None:
        for args in (("--mode", "sales", "--duration", "20"), ("--mode", "sales", "--lang", "uz_cyrillic"), ("--mode", "plan", "--weeks", "3"), ("--mode", "sales", "--hooks", "9")):
            proc = run_tool_inproc("creative-matrix.py", "video-script", "--product", "X", *args)
            self.assertEqual(proc.returncode, 2, args)
            self.assertIn("Xato", proc.stderr)

    def test_legacy_video_script_unchanged_without_mode(self) -> None:
        proc = run_tool_inproc("creative-matrix.py", "video-script", "--product", "Kurs", "--problem", "x", "--json")
        self.assertEqual(proc.returncode, 0)
        res = json.loads(proc.stdout)
        self.assertEqual(res["schema"], "tyrion.video_ad_script/v7")
        self.assertIn("hook_variations_0_3s", res)
        self.assertEqual(len(res["hook_variations_0_3s"]), 3)
        legacy = cm.generate_video_script(product="Kurs", problem="x", duration_sec=20)
        self.assertEqual(legacy["duration_sec"], 20)  # eski rejim ixtiyoriy davomiylikni saqlaydi

    def test_tool_stays_stdlib_only(self) -> None:
        src = (VAULT / "tools" / "creative-matrix.py").read_text(encoding="utf-8")
        mods = set(re.findall(r"^(?:import|from)\s+([A-Za-z_][\w]*)", src, re.M))
        allowed = {"argparse", "datetime", "json", "math", "re", "sys", "pathlib", "typing", "__future__", "market_locale", "tyrion_core"}
        self.assertLessEqual(mods, allowed, mods - allowed)


class VideoKnowledgeLayerTests(unittest.TestCase):
    def read(self, rel: str) -> str:
        return (VAULT / rel).read_text(encoding="utf-8")

    def test_references_exist_and_are_listed_in_skill(self) -> None:
        skill = self.read("skills/video/SKILL.md")
        for name in REFS:
            path = f"skills/video/references/{name}.md"
            self.assertTrue((VAULT / path).is_file(), path)
            self.assertIn(path, skill, f"{path} SKILL.md da ro'yxatlanmagan")
        for legacy in ("reels-scripting", "video-editing", "video-motion-graphics"):
            self.assertIn(f"skills/video/references/{legacy}.md", skill)
        self.assertIn("--mode <sales|organic|plan|motion>", skill)

    def test_skill_router_has_four_pillars_and_keeps_old_triggers(self) -> None:
        skill = self.read("skills/video/SKILL.md")
        for pillar in ("Sales Video Script", "Organic Video", "Video Content Plan", "Motion Blueprint", "Post-Production"):
            self.assertIn(pillar, skill)
        for trig in ("reels skript", "montaj qil", "kinetik tipografiya", "сценарий рилс", "motion ssenariy", "video kontent reja"):
            self.assertIn(f'- "{trig}"', skill)
        self.assertLess(len(skill), 9000, "SKILL.md ixcham bo'lishi kerak (progressive disclosure)")

    def test_rubric_is_100_points_with_85_gate(self) -> None:
        rubric = self.read("skills/video/references/script-quality-rubric.md")
        points = [int(m) for m in re.findall(r"\|\s*\*\*[^|]+\*\*\s*\|\s*(\d+)\s*\|", rubric)]
        self.assertEqual(sum(points), 100, points)
        self.assertEqual(len(points), 6)
        self.assertIn("85", rubric)
        for lang_marker in ("Siz ham charchadingizmi", "Лучшее качество по доступной цене", "Game-changer"):
            self.assertIn(lang_marker, rubric)

    def test_single_source_of_truth_dedup(self) -> None:
        spec = self.read("skills/creative/references/ad-creative/references/video-ad-scripts-and-specs.md")
        self.assertIn("sales-video-scripting.md", spec)
        self.assertLess(len(spec.splitlines()), 20, "creative spec endi qisqa xulosa + havola bo'lishi kerak")
        sform = self.read("skills/content/references/social/references/short-form-video.md")
        self.assertIn("organic-video-content.md", sform)
        self.assertIn("video-content-planning.md", sform)
        canonical = self.read("skills/video/references/sales-video-scripting.md")
        self.assertIn("720×1200", canonical)
        self.assertIn("3-Capture", canonical)
        reels = self.read("skills/video/references/reels-scripting.md")
        self.assertIn("sales-video-scripting.md", reels)
        self.assertIn("performance-video-system.md", reels)  # orqaga moslik havolasi saqlangan

    def test_templates_exist_with_required_sections(self) -> None:
        for name in TEMPLATES:
            text = self.read(f"templates/{name}.md")
            self.assertTrue(text.startswith("---\nname: " + name), name)
        for name in ("sales-video-script", "organic-video-script"):
            text = self.read(f"templates/{name}.md")
            self.assertIn("Creative Brief Header", text)
            self.assertIn("| Vaqt | Bosqich | Vizual / Kadr (A-Roll & B-Roll) | Spiker nutqi / VO | Ekrandagi matn (Safe-Zone 720x1200) | Kamera, Ritm & SFX |", text)
            self.assertIn("Self-Audit", text)
        self.assertIn("Motion Storyboard", self.read("templates/motion-video-blueprint.md"))
        self.assertIn("Asset Checklist", self.read("templates/motion-video-blueprint.md"))
        self.assertIn("Batch Shooting Plan", self.read("templates/video-content-plan.md"))

    def test_commands_en_uz_pairs_and_mirrors(self) -> None:
        for uz, en in COMMAND_PAIRS:
            for name in (uz, en):
                for base in ("commands", ".claude/commands"):
                    self.assertTrue((VAULT / base / f"{name}.md").is_file(), f"{base}/{name}.md")
            en_text = self.read(f"commands/{en}.md")
            self.assertIn(f"alias_of: {uz}", en_text)
            self.assertIn("--mode", en_text)
            self.assertIn("script-quality-rubric.md", en_text)
            uz_text = self.read(f"commands/{uz}.md")
            self.assertIn("disable-model-invocation: true", uz_text)
            self.assertIn("$ARGUMENTS", uz_text)
            self.assertIn("creative-matrix.py video-script --mode", uz_text)
            self.assertEqual(uz_text, self.read(f".claude/commands/{uz}.md"))

    def test_agents_wired_and_mirrors_in_sync(self) -> None:
        vp = self.read("agents/video-producer.md")
        for token in ("`sales`", "`organic`", "`plan`", "`motion`", "85/100", "script-quality-rubric.md", "6 ustunli AV-jadval", "Handoff"):
            self.assertIn(token, vp)
        mirror = self.read(".claude/agents/video-producer.md")
        self.assertIn("85/100", mirror)
        self.assertIn("GENERATED from agents/video-producer.md", mirror)
        self.assertNotIn("mcp__plugin_tyrion_", mirror.split("---")[1])
        for agent in ("content-planner", "creative-strategist"):
            for base in ("agents", ".claude/agents"):
                text = self.read(f"{base}/{agent}.md")
                self.assertIn("video-producer", text)
                self.assertIn("Video handoff", text)
        self.assertIn("video-content-planning.md", self.read("agents/content-planner.md"))
        self.assertIn("script-quality-rubric.md", self.read("agents/creative-strategist.md"))

    def test_wiki_synced_and_links_resolve(self) -> None:
        for note in ("video-kreativ-tizimi", "video-skript-shablonlari"):
            text = self.read(f"wiki/{note}.md")
            self.assertIn("2026-11-22", text)
            for target in set(re.findall(r"\[\[([^\]|#]+)", text)):
                self.assertTrue((VAULT / "wiki" / f"{target}.md").is_file() or any((VAULT / d / f"{target}.md").is_file() for d in ("rules", "playbooks", "contexts")), f"{note}: [[{target}]]")
        self.assertIn("sales-video-script.md", self.read("wiki/video-skript-shablonlari.md"))
        self.assertIn("4 ustunli tizim", self.read("wiki/video-kreativ-tizimi.md"))

    def test_reference_wikilinks_resolve(self) -> None:
        for name in REFS:
            text = self.read(f"skills/video/references/{name}.md")
            for target in set(re.findall(r"\[\[([^\]|#]+)", text)):
                found = (VAULT / "wiki" / f"{target}.md").is_file() or (VAULT / "rules" / f"{target}.md").is_file()
                self.assertTrue(found, f"{name}: [[{target}]]")

    def test_referenced_paths_exist(self) -> None:
        paths = set()
        for name in REFS:
            paths |= set(re.findall(r"`((?:skills|templates|schemas|tools|rules)/[\w./-]+\.(?:md|json|py))`", self.read(f"skills/video/references/{name}.md")))
        for tmpl in TEMPLATES:
            paths |= set(re.findall(r"`((?:skills|templates|schemas|tools|rules)/[\w./-]+\.(?:md|json|py))`", self.read(f"templates/{tmpl}.md")))
        self.assertTrue(paths)
        for p in sorted(paths):
            self.assertTrue((VAULT / p).is_file(), p)

    def test_eval_suites_added(self) -> None:
        for name in EVALS:
            d = VAULT / "evals" / name
            self.assertTrue((d / "prompt.md").is_file(), name)
            self.assertGreaterEqual(len(list((d / "graders").glob("*.md"))), 5, name)
            prompt = (d / "prompt.md").read_text(encoding="utf-8")
            self.assertIn("lang:uz-latn", prompt)
            self.assertIn(f"name: {name}", prompt)
        for old in ("reels-script-uz-1", "reels-script-ru-1"):
            self.assertTrue((VAULT / "evals" / old / "prompt.md").is_file())
        ids = {s["id"] for s in json.loads(self.read("evals/scenarios.json"))["scenarios"]}
        self.assertTrue({"E13_skill_route_sales_video", "E14_skill_route_video_plan", "E15_skill_route_motion_blueprint"} <= ids)

    def test_router_sends_video_pre_production_queries_to_video_skill(self) -> None:
        ss = importlib.import_module("skill-search")
        for q in ("sotuvchi video ssenariy yozib ber", "2 haftalik video kontent reja va syomka kuni rejasi",
                  "motion video ssenariy va storyboard", "сценарий продающего видео для клиники", "bergan videomni montaj qilib ber"):
            with self.subTest(q=q):
                plan = ss.route_task(q, load=False)
                self.assertIn("video", plan["required_skills"] + plan["supporting_skills"])

    def test_scope_boundary_render_and_edit_pipeline_untouched(self) -> None:
        try:
            out = subprocess.run(["git", "diff", "--name-only", "main", "--", "tools/video-run.py", "skills/video/references/video-editing.md",
                                  "skills/video/references/video-editing", "skills/video/references/video-motion-graphics.md"],
                                 cwd=VAULT, capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            self.skipTest("git mavjud emas")
        if out.returncode != 0:
            self.skipTest("main branch mavjud emas")
        self.assertEqual(out.stdout.strip(), "", "montaj/render qatlamiga tegilmasligi kerak")


if __name__ == "__main__":
    unittest.main()
