#!/usr/bin/env python3
"""Tyrion Quality Eval Runner (deterministik qism, 0 token).

`evals/quality/scenarios.json` dagi deterministik tekshiruvlarni berilgan
runs papkasidagi artifact matnlariga qo'llaydi va (ixtiyoriy) hakam-agent
ballarini birlashtirib, yagona JSON hisobot yozadi.

Deterministik tekshiruv turlari:
  contains_any   — qiymatlardan kamida bittasi artifactda (case-insensitive) bor
  contains_all   — barcha qiymatlar artifactda bor
  forbidden_any  — qiymatlardan hech biri artifactda bo'lmasligi kerak
  regex_any      — regexlardan kamida bittasi mos keladi
  no_cyrillic    — artifactda kirill harfi bo'lmasligi kerak
  line_limit     — `prefix` bilan boshlanuvchi kamida `min_count` qator,
                   har biri `max_chars` belgidan oshmasin

Ishlatish:
  python3 evals/quality/run.py --runs evals/quality/runs/baseline \
      [--judge evals/quality/judge-scores.json] \
      [--out evals/quality/baseline.json] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

QUALITY_DIR = Path(__file__).resolve().parent
SCENARIOS_FILE = QUALITY_DIR / "scenarios.json"
RUBRIC_FILE = QUALITY_DIR / "rubric.json"
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
KNOWN_CHECK_TYPES = {"contains_any", "contains_all", "forbidden_any", "regex_any", "no_cyrillic", "line_limit"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_one(check: dict[str, Any], text: str) -> tuple[bool, str]:
    """Bitta deterministik tekshiruvni artifact matniga qo'llaydi."""
    ctype = check.get("type", "")
    values = check.get("values", [])
    lowered = text.lower()

    if ctype == "contains_any":
        ok = any(str(v).lower() in lowered for v in values)
        return ok, "any(" + ", ".join(str(v) for v in values[:3]) + ")"

    if ctype == "contains_all":
        missing = [v for v in values if str(v).lower() not in lowered]
        return (not missing), "all; missing=" + repr(missing)

    if ctype == "forbidden_any":
        found = [v for v in values if str(v).lower() in lowered]
        return (not found), "found=" + repr(found)

    if ctype == "regex_any":
        ok = any(re.search(str(v), text, re.IGNORECASE) for v in values)
        return ok, "regex(" + ", ".join(str(v) for v in values[:3]) + ")"

    if ctype == "no_cyrillic":
        found = CYRILLIC_RE.findall(text)
        return (not found), f"cyrillic_chars={len(found)}"

    if ctype == "line_limit":
        prefix = str(check.get("prefix", ""))
        min_count = int(check.get("min_count", 1))
        max_chars = int(check.get("max_chars", 10_000))
        lines = [ln for ln in text.splitlines() if ln.strip().lower().startswith(prefix.lower())]
        over = [ln for ln in lines if len(ln.strip()) > max_chars]
        ok = len(lines) >= min_count and not over
        detail = f"lines={len(lines)}/{min_count}, over_limit={len(over)}"
        return ok, detail

    # Noma'lum tekshiruv turi — muvaffaqiyatsiz deb hisoblanadi (xavfsiz tomon).
    return False, f"unknown_check_type={ctype!r}"


def evaluate_runs(runs_dir: Path, scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Har stsenariy uchun deterministik natijani hisoblaydi."""
    results: list[dict[str, Any]] = []
    for sc in scenarios:
        sid = sc["id"]
        artifact_path = runs_dir / sid / "artifact.md"
        checks_results: list[dict[str, Any]] = []
        if not artifact_path.exists():
            for ch in sc.get("checks", []):
                checks_results.append({"id": ch["id"], "passed": False, "detail": "artifact_missing"})
        else:
            text = artifact_path.read_text(encoding="utf-8", errors="replace")
            for ch in sc.get("checks", []):
                ok, detail = check_one(ch, text)
                checks_results.append({"id": ch["id"], "passed": ok, "detail": detail})

        passed = sum(1 for c in checks_results if c["passed"])
        total = len(checks_results)
        results.append(
            {
                "id": sid,
                "job": sc.get("job"),
                "worker_agent": sc.get("worker_agent"),
                "deterministic": {
                    "passed": passed,
                    "total": total,
                    "share": round(passed / total, 3) if total else 0.0,
                    "checks": checks_results,
                },
            }
        )
    return results


def merge_judge(results: list[dict[str, Any]], judge: dict[str, Any], rubric: dict[str, Any]) -> None:
    """Hakam-agent ballarini (0-2, 4 mezon) natijalarga qo'shadi."""
    criteria = list(rubric.get("criteria", {}).keys())
    scored = {s.get("id"): s for s in judge.get("scenarios", [])}
    for res in results:
        js = scored.get(res["id"], {})
        scores = {}
        for crit in criteria:
            raw = js.get("scores", {}).get(crit)
            if raw is None:
                scores[crit] = None
            else:
                scores[crit] = max(0, min(2, int(raw)))
        present = [v for v in scores.values() if v is not None]
        res["judge"] = {
            "scores": scores,
            "score": sum(present) if len(present) == len(criteria) else None,
            "notes": js.get("notes", ""),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Tyrion quality eval runner (deterministik + hakam birlashtirish)")
    parser.add_argument("--runs", required=True, help="runs papkasi (har stsenariy <runs>/<id>/artifact.md)")
    parser.add_argument("--judge", help="hakam-agent JSON fayli (ixtiyoriy)")
    parser.add_argument("--out", default="evals/quality/baseline.json", help="chiqish JSON fayli")
    parser.add_argument("--json", action="store_true", help="stdout ga JSON chiqarish")
    args = parser.parse_args()

    scenarios_doc = load_json(SCENARIOS_FILE)
    rubric = load_json(RUBRIC_FILE)
    scenarios = scenarios_doc.get("scenarios", [])

    runs_dir = Path(args.runs)
    results = evaluate_runs(runs_dir, scenarios)

    judge_summary: dict[str, Any] | None = None
    if args.judge:
        judge = load_json(Path(args.judge))
        merge_judge(results, judge, rubric)
        judge_summary = {"file": str(args.judge), "model": judge.get("model", ""), "date": judge.get("date", "")}

    det_max = sum(r["deterministic"]["total"] for r in results)
    det_score = sum(r["deterministic"]["passed"] for r in results)
    judge_scores = [r["judge"]["score"] for r in results if r.get("judge") and r["judge"]["score"] is not None]
    # Har mezon 0-2 ballgacha: maksimum = stsenariylar x mezonlar x 2
    judge_max = len(scenarios) * len(rubric.get("criteria", {})) * 2 if judge_scores else None

    report: dict[str, Any] = {
        "schema": "tyrion-quality-eval/v1",
        "runs_dir": str(runs_dir),
        "scenarios_count": len(scenarios),
        "totals": {
            "deterministic_score": det_score,
            "deterministic_max": det_max,
            "judge_score": sum(judge_scores) if judge_scores else None,
            "judge_max": judge_max,
        },
        "judge": judge_summary,
        "scenarios": results,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Quality eval: {len(scenarios)} stsenariy")
        print(f"  Deterministik: {det_score}/{det_max}")
        if judge_scores:
            print(f"  Hakam (0-2 x {len(rubric['criteria'])}): {sum(judge_scores)}/{judge_max}")
        for r in results:
            det = r["deterministic"]
            judge_part = ""
            if r.get("judge") and r["judge"]["score"] is not None:
                judge_part = f" | hakam {r['judge']['score']}/8"
            print(f"  {r['id']}: det {det['passed']}/{det['total']}{judge_part}")
        print(f"Natija yozildi: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
