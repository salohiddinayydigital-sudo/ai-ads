#!/usr/bin/env python3
"""audit_scoring.py — Audit balli v2: har tekshiruv `id`, `status`, `evidence_label`, `severity` bilan.

Natija IKKI raqam:
  * health            — faqat BAHOLANGAN (pass/warn/fail) tekshiruvlar bo'yicha 0–100 (unknown/n_a hisobga olinmaydi);
  * evidence_coverage — qo'llanadigan (n_a emas) tekshiruvlarning necha foizi baholangan (unknown emas).
Hech narsa baholanmagan bo'lsa health = None ("ma'lumot yetarli emas").

    python3 tools/audit_scoring.py score --checks checks.json [--json]
    python3 tools/audit_scoring.py validate --checks checks.json

Kirish: [{"id","status","evidence_label","severity", ...}] yoki {"checks":[...]}.
Og'irliklar (HEURISTIC_PRIOR_MODEL): critical 5, high 3, medium 2, low 1. pass=1, warn=0.5, fail=0.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

STATUSES = ("pass", "warn", "fail", "unknown", "n_a")
SEVERITIES = ("critical", "high", "medium", "low")
EVIDENCE_LABELS = ("MEASURED_ACCOUNT_DATA", "PLATFORM_BENCHMARK", "HEURISTIC_PRIOR_MODEL", "USER_PROVIDED", "UNVERIFIED")
WEIGHTS = {"critical": 5.0, "high": 3.0, "medium": 2.0, "low": 1.0}
CREDIT = {"pass": 1.0, "warn": 0.5, "fail": 0.0}
WEIGHT_LABEL = "HEURISTIC_PRIOR_MODEL"


def validate_checks(checks: object) -> list[str]:
    errs: list[str] = []
    if not isinstance(checks, list):
        return ["checks ro'yxat bo'lishi shart"]
    seen: set[str] = set()
    for i, c in enumerate(checks):
        if not isinstance(c, dict):
            errs.append(f"[{i}] obyekt emas")
            continue
        cid = c.get("id")
        if not cid or not isinstance(cid, str):
            errs.append(f"[{i}] id yo'q")
        elif cid in seen:
            errs.append(f"[{i}] takroriy id: {cid}")
        else:
            seen.add(cid)
        if c.get("status") not in STATUSES:
            errs.append(f"[{cid or i}] status {STATUSES} dan biri bo'lishi shart")
        if c.get("severity") not in SEVERITIES:
            errs.append(f"[{cid or i}] severity {SEVERITIES} dan biri bo'lishi shart")
        if c.get("evidence_label") not in EVIDENCE_LABELS:
            errs.append(f"[{cid or i}] evidence_label {EVIDENCE_LABELS} dan biri bo'lishi shart")
        elif c.get("status") in CREDIT and c.get("evidence_label") == "UNVERIFIED":
            errs.append(f"[{cid or i}] baholangan tekshiruv UNVERIFIED dalil bilan bo'lolmaydi")
    return errs


def score(checks: list[dict]) -> dict:
    errs = validate_checks(checks)
    if errs:
        return {"error": "noto'g'ri tekshiruvlar", "details": errs}
    applicable = [c for c in checks if c["status"] != "n_a"]
    scored = [c for c in applicable if c["status"] in CREDIT]
    unknown = [c for c in applicable if c["status"] == "unknown"]
    wsum = sum(WEIGHTS[c["severity"]] for c in scored)
    health = None
    if wsum > 0:
        health = round(100.0 * sum(WEIGHTS[c["severity"]] * CREDIT[c["status"]] for c in scored) / wsum, 1)
    coverage = round(100.0 * len(scored) / len(applicable), 1) if applicable else None
    measured = sum(1 for c in scored if c["evidence_label"] in ("MEASURED_ACCOUNT_DATA", "PLATFORM_BENCHMARK"))
    return {
        "health": health,
        "evidence_coverage_pct": coverage,
        "measured_share_pct": round(100.0 * measured / len(scored), 1) if scored else None,
        "counts": {s: sum(1 for c in checks if c["status"] == s) for s in STATUSES},
        "critical_failures": [c["id"] for c in scored if c["status"] == "fail" and c["severity"] == "critical"],
        "unknown_ids": [c["id"] for c in unknown],
        "weights": WEIGHTS,
        "weights_label": WEIGHT_LABEL,
        "note": "health faqat baholangan tekshiruvlar bo'yicha; evidence_coverage past bo'lsa health ishonchsiz." if scored else
                "Hech narsa baholanmadi — health hisoblanmadi (ma'lumot yetarli emas).",
    }


def _load(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get("checks") if isinstance(data, dict) else data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit balli v2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("score", "validate"):
        p = sub.add_parser(name)
        p.add_argument("--checks", required=True)
        p.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        checks = _load(args.checks)
    except (OSError, ValueError) as exc:
        print(f"xato: {exc}", file=sys.stderr)
        return 2
    if args.cmd == "validate":
        errs = validate_checks(checks)
        print(json.dumps({"valid": not errs, "errors": errs}, ensure_ascii=False, indent=2))
        return 0 if not errs else 2
    res = score(checks)
    if res.get("error"):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 2
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        h = "n/a" if res["health"] is None else f"{res['health']}/100"
        print(f"Health: {h} · Evidence coverage: {res['evidence_coverage_pct']}% · measured: {res['measured_share_pct']}%")
        if res["critical_failures"]:
            print("Kritik xatolar: " + ", ".join(res["critical_failures"]))
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows cp1252 konsolida --help/hisobotdagi '→' kabi belgilar yiqilmasin
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
