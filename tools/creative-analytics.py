#!/usr/bin/env python3
"""creative-analytics.py — haqiqiy ma'lumotdan kreativ tahlili (metrics.v1 + creatives.json). Stdlib.

    python3 tools/creative-analytics.py analyze --metrics M.json --creatives C.json [--event Lead]
    python3 tools/creative-analytics.py suggest-tags --metrics M.json     # nomlashdan teg taklifi

Nomlash: ANGLE_HOOK_FORMAT_PERSONA_vN (masalan PRICE_QUESTION_UGC_MOM_v2).
Ta'riflar: hook rate = video_3s / impressions · hold rate = thruplay / video_3s · CTR = clicks / impressions ·
CPA = spend / conversions · ROAS = conversion_value / spend. Wilson 95% ishonch oralig'i.
Minimal namuna (standart): >=1000 impression va >=10 konversiya; undan kam bo'lsa hukm "ma'lumot yetarli emas".
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

DIMS = ["angle", "hook_type", "format", "persona", "offer", "awareness", "visual_first_3s", "language"]
DIVERSITY_DIMS = ["angle", "hook_type", "format", "persona"]
MIN_IMPRESSIONS = 1000
MIN_CONVERSIONS = 10
Z = 1.96


def wilson(k: float, n: float, z: float = Z) -> tuple[float, float] | None:
    if n <= 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round(max(0.0, (c - h) / d), 5), round(min(1.0, (c + h) / d), 5)


def parse_name(name: str) -> dict:
    """ANGLE_HOOK_FORMAT_PERSONA_vN → teg taklifi (HEURISTIC_PRIOR_MODEL: faqat taklif, tasdiqlash kerak)."""
    parts = str(name or "").split("_")
    if len(parts) >= 4 and parts[-1].lower().startswith("v") and parts[-1][1:].isdigit():
        return {"angle": parts[0].lower(), "hook_type": parts[1].lower(), "format": parts[2].lower(),
                "persona": parts[3].lower(), "version": parts[-1].lower()}
    return {}


def load_rows(path: str) -> list[dict]:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = d["rows"] if isinstance(d, dict) else d
    return [r for r in rows if r.get("level", "ad") == "ad"]


def _conv(row: dict, event: str | None) -> float:
    c = row.get("conversions") or {}
    return float(c.get(event, 0)) if event else float(sum(c.values()))


def _metrics(a: dict) -> dict:
    imp, sp, conv = a["impressions"], a["spend"], a["conversions"]
    out = {
        "spend": round(sp, 2), "impressions": int(imp), "clicks": int(a["clicks"]), "conversions": conv,
        "ctr": round(a["clicks"] / imp, 5) if imp else None,
        "hook_rate": round(a["video_3s"] / imp, 5) if imp and a["video_3s"] else None,
        "hold_rate": round(a["thruplay"] / a["video_3s"], 5) if a["video_3s"] else None,
        "cpa": round(sp / conv, 2) if conv else None,
        "roas": round(a["value"] / sp, 3) if sp and a["value"] else None,
        "cvr_ci95": wilson(conv, a["clicks"]),
        "hook_rate_ci95": wilson(a["video_3s"], imp) if a["video_3s"] else None,
    }
    out["sufficient"] = imp >= MIN_IMPRESSIONS and conv >= MIN_CONVERSIONS
    out["verdict_note"] = "yetarli" if out["sufficient"] else "ma'lumot yetarli emas"
    return out


def _new() -> dict:
    return {"spend": 0.0, "impressions": 0.0, "clicks": 0.0, "video_3s": 0.0, "thruplay": 0.0, "conversions": 0.0, "value": 0.0}


def _add(a: dict, r: dict, event: str | None) -> None:
    a["spend"] += float(r.get("spend", 0)); a["impressions"] += float(r.get("impressions", 0))
    a["clicks"] += float(r.get("link_clicks") or r.get("clicks") or 0)
    a["video_3s"] += float(r.get("video_3s", 0)); a["thruplay"] += float(r.get("thruplay", 0))
    a["conversions"] += _conv(r, event); a["value"] += float(r.get("conversion_value", 0))


def diversity_score(active_tags: list[dict]) -> dict:
    """Andromeda xilma-xillik bali 0–100: dim bo'yicha normallangan Shannon entropiyasi o'rtachasi."""
    per, n = {}, len(active_tags)
    for d in DIVERSITY_DIMS:
        vals = [t.get(d) for t in active_tags if t.get(d)]
        if len(vals) < 2:
            per[d] = 0.0
            continue
        cnt: dict = defaultdict(int)
        for v in vals:
            cnt[v] += 1
        ent = -sum(c / len(vals) * math.log(c / len(vals)) for c in cnt.values())
        per[d] = round(100 * ent / math.log(len(vals)), 1)
    return {"score": round(sum(per.values()) / len(per), 1) if n else 0.0, "per_dimension": per,
            "active_creatives": n, "label": "HEURISTIC_PRIOR_MODEL"}


def analyze(rows: list[dict], creatives: dict, event: str | None = None) -> dict:
    by_ad: dict = defaultdict(_new)
    names: dict = {}
    for r in rows:
        _add(by_ad[r["entity_id"]], r, event)
        names[r["entity_id"]] = r.get("entity_name", "")
    tags: dict = {}
    for ad in by_ad:
        t = dict((creatives.get(ad) or {}))
        for k, v in parse_name(names.get(ad, "")).items():
            t.setdefault(k, v)
        tags[ad] = t
    ads = {ad: {"name": names[ad], "tags": tags[ad], **_metrics(a)} for ad, a in by_ad.items()}

    by_tag: dict = {}
    for d in DIMS:
        g: dict = defaultdict(_new)
        for ad, a in by_ad.items():
            v = tags[ad].get(d)
            if v:
                for k in a:
                    g[v][k] += a[k]
        if g:
            by_tag[d] = {v: _metrics(a) for v, a in sorted(g.items())}

    winners: dict = {}
    for d, vals in by_tag.items():
        ok = [(v, m) for v, m in vals.items() if m["sufficient"] and m["cpa"]]
        if ok:
            v, m = min(ok, key=lambda x: x[1]["cpa"])
            winners[d] = {"value": v, "cpa": m["cpa"], "cvr_ci95": m["cvr_ci95"]}

    cpas = sorted(m["cpa"] for m in ads.values() if m["sufficient"] and m["cpa"])
    med = cpas[len(cpas) // 2] if cpas else None
    kill = []
    for ad, m in ads.items():
        if m["impressions"] >= MIN_IMPRESSIONS and m["conversions"] == 0 and med and m["spend"] >= 2 * med:
            kill.append({"ad_id": ad, "name": m["name"], "reason": f"sarf {m['spend']} ≥ 2×median CPA, konversiya 0"})
        elif m["sufficient"] and med and m["cpa"] and m["cpa"] > 1.5 * med and (m["cvr_ci95"] or [1, 1])[1] < (
                (wilson(sum(x["conversions"] for x in ads.values() if x["sufficient"]),
                        sum(x["clicks"] for x in ads.values() if x["sufficient"])) or [0, 0])[0]):
            kill.append({"ad_id": ad, "name": m["name"], "reason": "CPA > 1.5×median va CVR ishonch oralig'i guruhdan past"})

    briefs = _briefs(winners, by_tag, tags)
    return {
        "label": "MEASURED_ACCOUNT_DATA", "event": event or "all",
        "definitions": {"hook_rate": "video_3s / impressions", "hold_rate": "thruplay / video_3s", "ctr": "clicks / impressions",
                        "cpa": "spend / conversions", "roas": "conversion_value / spend", "ci": "Wilson 95%",
                        "min_sample": f"impressions>={MIN_IMPRESSIONS} va conversions>={MIN_CONVERSIONS}"},
        "ads": ads, "by_tag": by_tag, "winner_dna": winners, "kill_list": kill, "next_briefs": briefs,
        "diversity": diversity_score(list(tags.values())),
        "median_cpa_sufficient": med,
    }


def _briefs(winners: dict, by_tag: dict, tags: dict) -> list[dict]:
    if not winners:
        return [{"note": "g'olib DNK aniqlanmadi: namuna yetarli emas — avval test byudjetini oshiring"}]
    tested = {(t.get("angle"), t.get("hook_type"), t.get("format")) for t in tags.values()}
    angle = winners.get("angle", {}).get("value")
    hook = winners.get("hook_type", {}).get("value")
    fmt = winners.get("format", {}).get("value")
    all_fmt = list(by_tag.get("format", {})) or [fmt]
    all_hook = list(by_tag.get("hook_type", {})) or [hook]
    all_angle = list(by_tag.get("angle", {})) or [angle]
    cands = []
    for a in [angle] + [x for x in all_angle if x != angle]:
        for h in [hook] + [x for x in all_hook if x != hook]:
            for f in [fmt] + [x for x in all_fmt if x != fmt]:
                if (a, h, f) not in tested:
                    novelty = (a != angle) + (h != hook) + (f != fmt)
                    cands.append((novelty, a, h, f))
    cands.sort(key=lambda c: (abs(c[0] - 1), c[0]))  # g'olibga yaqin (1 o'zgarish) afzal
    return [{"angle": a, "hook_type": h, "format": f, "why": "g'olib DNK'dan 1–2 o'zgarish, hali sinalmagan kombinatsiya (gipoteza)"}
            for _, a, h, f in cands[:3]] or [{"note": "yangi kombinatsiya qolmadi — yangi angle kiriting"}]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Creative analytics (metrics.v1)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze")
    a.add_argument("--metrics", required=True); a.add_argument("--creatives", required=True); a.add_argument("--event")
    s = sub.add_parser("suggest-tags")
    s.add_argument("--metrics", required=True)
    args = ap.parse_args(argv)
    try:
        rows = load_rows(args.metrics)
        if args.cmd == "suggest-tags":
            seen = {r["entity_id"]: r.get("entity_name", "") for r in rows}
            out = {"label": "HEURISTIC_PRIOR_MODEL (taklif, tasdiqlang)",
                   "suggestions": {ad: parse_name(n) or {"unparsed": n} for ad, n in seen.items()}}
        else:
            raw = json.loads(Path(args.creatives).read_text(encoding="utf-8"))
            out = analyze(rows, raw.get("creatives", raw), args.event)
    except (OSError, ValueError, KeyError) as e:
        print(f"xato: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
