#!/usr/bin/env python3
"""report-html.py — mijoz hisoboti: bitta mustaqil HTML (+ Markdown), CDN yo'q, light/dark, print CSS.

Kirishlar (hammasi ixtiyoriy, faqat stdlib; noma'lum kalitlarga chidamli):
  state.json    — schemas/client-state.v1.json (maqsadlar: goals.target_cpa / target_roas, next_steps[])
  metrics.json  — schemas/metrics.v1.json ({"rows":[...]} yoki massiv)
  ledger.jsonl  — experiments.py: har qator bir eksperiment (name/id, status, verdict, win_probability|p_win ...)
  pulse.json    — pulse.py: {"findings"|"alerts"|"checks":[{severity, check|title, evidence, next_step, needs_approval}]} yoki massiv

    python3 tools/report-html.py --client demo --root clients --lang uz --out report.html [--md report.md]
    python3 tools/report-html.py --state s.json --metrics m.json --ledger l.jsonl --pulse p.json --out r.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
LOCALES = ROOT / "locales"
MIN_CONV = 10  # kreativ reytingida minimal konversiya (HEURISTIC_PRIOR_MODEL)
SEV_ORDER = {"critical": 0, "high": 0, "warning": 1, "medium": 1, "warn": 1, "info": 2, "low": 2}


def load_labels(lang: str) -> dict:
    out: dict = {}
    for code in ("en", lang):
        p = LOCALES / code / "report.json"
        if p.is_file():
            out.update(json.loads(p.read_text(encoding="utf-8")))
    return out


def _read_json(path: str | None, default):
    if not path:
        return default
    p = Path(path)
    if not p.is_file():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return default


def _read_jsonl(path: str | None) -> list[dict]:
    if not path or not Path(path).is_file():
        return []
    out = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln:
            try:
                v = json.loads(ln)
                if isinstance(v, dict):
                    out.append(v)
            except ValueError:
                pass
    return out


def _f(v) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return 0.0
    return x if x == x and abs(x) != float("inf") else 0.0


def _rows(data) -> list[dict]:
    rows = data.get("rows") if isinstance(data, dict) else data
    return [r for r in (rows or []) if isinstance(r, dict)]


def _conv(r: dict, event: str | None) -> float:
    c = r.get("conversions")
    if not isinstance(c, dict):
        return 0.0
    return _f(c.get(event)) if event and event in c else sum(_f(v) for v in c.values())


def _agg(rows: list[dict], event: str | None) -> dict:
    a = dict(spend=0.0, imp=0.0, clk=0.0, conv=0.0, value=0.0)
    for r in rows:
        a["spend"] += _f(r.get("spend"))
        a["imp"] += _f(r.get("impressions"))
        a["clk"] += _f(r.get("link_clicks")) or _f(r.get("clicks"))
        a["conv"] += _conv(r, event)
        a["value"] += _f(r.get("conversion_value"))
    a["cpa"] = a["spend"] / a["conv"] if a["conv"] else None
    a["ctr"] = a["clk"] / a["imp"] if a["imp"] else None
    a["roas"] = a["value"] / a["spend"] if a["spend"] and a["value"] else None
    return a


def _top_level(rows: list[dict]) -> list[dict]:
    present = {r.get("level") for r in rows}
    lv = next((x for x in ("campaign", "adset", "ad") if x in present), None)
    return [r for r in rows if r.get("level") == lv] if lv else rows


def build_model(state: dict, metrics: list[dict], ledger: list[dict], pulse, lang: str) -> dict:
    L = load_labels(lang)
    goals = state.get("goals") or {}
    event = goals.get("primary_event")
    rows = _top_level(metrics)
    total = _agg(rows, event)
    if rows and not total["conv"] and event:  # hodisa nomi mos kelmasa — hammasi
        event = None
        total = _agg(rows, None)
    dates = sorted({r["date"] for r in rows if isinstance(r.get("date"), str)})
    by_day = []
    for d in dates:
        a = _agg([r for r in rows if r.get("date") == d], event)
        by_day.append({"date": d, "spend": a["spend"], "conv": a["conv"], "cpa": a["cpa"]})
    by_plat: dict[str, list[dict]] = {}
    for r in rows:
        by_plat.setdefault(str(r.get("platform") or "?"), []).append(r)
    channels = [{"platform": k, **_agg(v, event)} for k, v in sorted(by_plat.items())]
    ads = [r for r in metrics if r.get("level") == "ad"]
    by_ad: dict[str, list[dict]] = {}
    for r in ads:
        by_ad.setdefault(str(r.get("entity_name") or r.get("entity_id")), []).append(r)
    creatives = []
    for k, v in by_ad.items():
        a = _agg(v, event)
        creatives.append({"name": k, **a, "small_sample": a["conv"] < MIN_CONV})
    creatives.sort(key=lambda c: (c["cpa"] is None, c["small_sample"], c["cpa"] or 0))
    if isinstance(pulse, dict):
        items = pulse.get("findings") or pulse.get("alerts") or pulse.get("checks") or []
    else:
        items = pulse or []
    alerts = []
    for it in items:
        if isinstance(it, dict):
            alerts.append({"severity": str(it.get("severity", "info")).lower(),
                           "title": str(it.get("title") or it.get("check") or it.get("id") or "—"),
                           "evidence": str(it.get("evidence") or ""), "next_step": str(it.get("next_step") or it.get("recommendation") or ""),
                           "needs_approval": bool(it.get("needs_approval")), "owner": it.get("owner"), "metric": it.get("metric")})
    alerts.sort(key=lambda a: SEV_ORDER.get(a["severity"], 3))
    steps = [dict(s) for s in (state.get("next_steps") or []) if isinstance(s, dict)]
    for a in alerts:
        if a["next_step"]:
            steps.append({"action": a["next_step"], "owner": a["owner"] or "—", "metric": a["metric"] or "—", "due": ""})
    exps = []
    for e in ledger:
        p = e.get("win_probability", e.get("p_win", e.get("prob_win")))
        exps.append({"name": str(e.get("name") or e.get("id") or e.get("hypothesis") or "—"), "status": str(e.get("status") or ""),
                     "verdict": str(e.get("verdict") or ""), "p_win": p if isinstance(p, (int, float)) else None})
    return {"L": L, "lang": lang, "name": state.get("name") or state.get("slug") or "Client",
            "synthetic": bool(state.get("synthetic")) or any(r.get("synthetic") for r in metrics[:50]),
            "period": (dates[0], dates[-1]) if dates else None, "currency": goals.get("currency") or "",
            "target_cpa": goals.get("target_cpa"), "target_roas": goals.get("target_roas"), "event": event or "all",
            "total": total, "by_day": by_day, "channels": channels, "creatives": creatives, "experiments": exps,
            "alerts": alerts, "steps": steps, "baseline": state.get("baseline") or {}}


def _fmt(v, nd=2, pct=False) -> str:
    if v is None:
        return "—"
    return f"{v * 100:.{nd}f}%" if pct else f"{v:,.{nd}f}"


def _tiles(m: dict) -> list[dict]:
    t, L = m["total"], m["L"]

    def goal(val, target, lower_better):
        if val is None or not target:
            return "na", L["no_target"]
        ok = val <= target if lower_better else val >= target
        return ("good" if ok else "bad"), f"{L['target']}: {_fmt(target)}"

    s_cpa, n_cpa = goal(t["cpa"], m["target_cpa"], True)
    s_roas, n_roas = goal(t["roas"], m["target_roas"], False)
    return [
        {"k": L["spend"], "v": _fmt(t["spend"]), "s": "na", "n": m["currency"]},
        {"k": L["conversions"], "v": _fmt(t["conv"], 0), "s": "na", "n": m["event"]},
        {"k": L["cpa"], "v": _fmt(t["cpa"]), "s": s_cpa, "n": n_cpa},
        {"k": L["roas"], "v": _fmt(t["roas"]), "s": s_roas, "n": n_roas},
        {"k": L["ctr"], "v": _fmt(t["ctr"], 2, True), "s": "na", "n": ""},
    ]


def _svg_trend(days: list[dict], key: str, color_var: str) -> str:
    pts = [(i, d[key]) for i, d in enumerate(days) if d.get(key) is not None]
    if len(pts) < 2:
        return ""
    w, h, pad = 560, 120, 8
    mx, mn = max(v for _, v in pts), min(v for _, v in pts)
    span = (mx - mn) or 1.0
    n = max(len(days) - 1, 1)
    coords = " ".join(f"{pad + i / n * (w - 2 * pad):.1f},{h - pad - (v - mn) / span * (h - 2 * pad):.1f}" for i, v in pts)
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(key)}" class="spark">'
            f'<polyline fill="none" stroke="var({color_var})" stroke-width="2" points="{coords}"/></svg>')


CSS = """
:root{--bg:#fff;--fg:#1a1d23;--mut:#5b6472;--card:#f4f6f9;--line:#dde2ea;--good:#1a7f4b;--bad:#c0392b;--warn:#b7791f;--c1:#2563eb;--c2:#7c3aed}
@media (prefers-color-scheme:dark){:root{--bg:#12151a;--fg:#e8ebf0;--mut:#9aa4b2;--card:#1b2028;--line:#2b323d;--good:#4cc38a;--bad:#ff7b6b;--warn:#e8b04b;--c1:#6ea0ff;--c2:#b79bff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px}h1{font-size:1.6rem;margin:.2em 0}h2{font-size:1.1rem;margin:1.6em 0 .6em;border-bottom:1px solid var(--line);padding-bottom:.3em}
.meta{color:var(--mut)}.banner{background:var(--warn);color:#000;padding:4px 10px;border-radius:6px;display:inline-block;font-weight:600;font-size:.8rem}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.tile .k{color:var(--mut);font-size:.8rem}.tile .v{font-size:1.5rem;font-weight:700}.tile .n{font-size:.78rem;color:var(--mut)}.tile.good{border-left:4px solid var(--good)}.tile.bad{border-left:4px solid var(--bad)}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);font-size:.9rem}th{color:var(--mut);font-weight:600}
.sev{font-weight:700;text-transform:uppercase;font-size:.72rem}.sev.critical,.sev.high{color:var(--bad)}.sev.warning,.sev.warn,.sev.medium{color:var(--warn)}
.spark{width:100%;height:auto;max-height:130px;background:var(--card);border-radius:8px}.small{font-size:.8rem;color:var(--mut)}
footer{margin-top:2em;color:var(--mut);font-size:.8rem}@media print{body{background:#fff;color:#000}main{max-width:none;padding:0}.tile,.spark{break-inside:avoid}h2{break-after:avoid}}
"""


def _table(head: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>"


def render_html(m: dict) -> str:
    L, e = m["L"], html.escape
    parts = [f"<h1>{e(L['title'])}: {e(m['name'])}</h1>"]
    if m["period"]:
        parts.append(f"<p class='meta'>{e(L['period'])}: {m['period'][0]} → {m['period'][1]} · {date.today().isoformat()}</p>")
    if m["synthetic"]:
        parts.append(f"<p><span class='banner'>{e(L['synthetic'])}</span></p>")
    parts.append(f"<h2>{e(L['kpi'])}</h2><div class='tiles'>" + "".join(
        f"<div class='tile {t['s']}'><div class='k'>{e(t['k'])}</div><div class='v'>{e(t['v'])}</div><div class='n'>{e(str(t['n']))}</div></div>" for t in _tiles(m)) + "</div>")
    parts.append(f"<h2>{e(L['trend'])}</h2>")
    sp, cp = _svg_trend(m["by_day"], "spend", "--c1"), _svg_trend(m["by_day"], "cpa", "--c2")
    parts.append(f"<p class='small'>{e(L['spend'])}</p>{sp}<p class='small'>{e(L['cpa'])}</p>{cp}" if sp else f"<p>{e(L['no_data'])}</p>")
    parts.append(f"<h2>{e(L['channels'])}</h2>")
    parts.append(_table([L["platform"], L["spend"], L["conversions"], L["cpa"], L["ctr"]],
                        [[c["platform"], _fmt(c["spend"]), _fmt(c["conv"], 0), _fmt(c["cpa"]), _fmt(c["ctr"], 2, True)] for c in m["channels"]]) if m["channels"] else f"<p>{e(L['no_data'])}</p>")
    parts.append(f"<h2>{e(L['experiments'])}</h2>")
    parts.append(_table([L["experiments"], "status", L["verdict"], "P(win)"],
                        [[x["name"], x["status"], x["verdict"], _fmt(x["p_win"], 0, True)] for x in m["experiments"]]) if m["experiments"] else f"<p>{e(L['no_experiments'])}</p>")
    parts.append(f"<h2>{e(L['creatives'])}</h2>")
    parts.append(_table([L["creative"], L["spend"], L["conversions"], L["cpa"], L["ctr"], ""],
                        [[c["name"], _fmt(c["spend"]), _fmt(c["conv"], 0), _fmt(c["cpa"]), _fmt(c["ctr"], 2, True),
                          L["min_sample"].format(n=MIN_CONV) if c["small_sample"] else ""] for c in m["creatives"][:10]]) if m["creatives"] else f"<p>{e(L['no_data'])}</p>")
    parts.append(f"<h2>{e(L['alerts'])}</h2>")
    if m["alerts"]:
        rows = "".join(f"<tr><td><span class='sev {e(a['severity'])}'>{e(a['severity'])}</span></td><td>{e(a['title'])}</td><td>{e(a['evidence'])}</td>"
                       f"<td>{e(a['next_step'])}{' · ' + e(L['needs_approval']) if a['needs_approval'] else ''}</td></tr>" for a in m["alerts"])
        parts.append(f"<table><thead><tr><th>!</th><th></th><th>{e(L['evidence'])}</th><th>{e(L['next_steps'])}</th></tr></thead><tbody>{rows}</tbody></table>")
    else:
        parts.append(f"<p>{e(L['no_alerts'])}</p>")
    parts.append(f"<h2>{e(L['next_steps'])}</h2>")
    parts.append(_table([L["action"], L["owner"], L["metric"], L["due"]],
                        [[s.get("action", ""), s.get("owner") or "—", s.get("metric") or "—", s.get("due") or ""] for s in m["steps"]]) if m["steps"] else f"<p>{e(L['no_data'])}</p>")
    parts.append(f"<footer>{e(L['footer'])}</footer>")
    return (f"<!doctype html><html lang='{e(m['lang'])}'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{e(L['title'])} — {e(m['name'])}</title><style>{CSS}</style></head><body><main>{''.join(parts)}</main></body></html>")


def render_md(m: dict) -> str:
    L = m["L"]
    o = [f"# {L['title']}: {m['name']}", ""]
    if m["period"]:
        o.append(f"{L['period']}: {m['period'][0]} → {m['period'][1]}")
    if m["synthetic"]:
        o.append(f"**{L['synthetic']}**")
    o += ["", f"## {L['kpi']}", ""] + [f"- **{t['k']}:** {t['v']} ({t['n']})" for t in _tiles(m)]
    o += ["", f"## {L['channels']}", "", f"| {L['platform']} | {L['spend']} | {L['conversions']} | {L['cpa']} |", "|---|---|---|---|"]
    o += [f"| {c['platform']} | {_fmt(c['spend'])} | {_fmt(c['conv'], 0)} | {_fmt(c['cpa'])} |" for c in m["channels"]]
    o += ["", f"## {L['experiments']}", ""] + ([f"- {x['name']}: {x['verdict'] or x['status']} (P(win) {_fmt(x['p_win'], 0, True)})" for x in m["experiments"]] or [L["no_experiments"]])
    o += ["", f"## {L['creatives']}", ""] + [f"{i}. {c['name']} — {L['cpa']} {_fmt(c['cpa'])}" + (f" ({L['min_sample'].format(n=MIN_CONV)})" if c["small_sample"] else "") for i, c in enumerate(m["creatives"][:10], 1)]
    o += ["", f"## {L['alerts']}", ""] + ([f"- [{a['severity']}] {a['title']}: {a['evidence']} → {a['next_step']}" for a in m["alerts"]] or [L["no_alerts"]])
    o += ["", f"## {L['next_steps']}", "", f"| {L['action']} | {L['owner']} | {L['metric']} | {L['due']} |", "|---|---|---|---|"]
    o += [f"| {s.get('action','')} | {s.get('owner') or '—'} | {s.get('metric') or '—'} | {s.get('due') or ''} |" for s in m["steps"]]
    o += ["", f"_{L['footer']}_", ""]
    return "\n".join(o)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mijoz hisoboti (HTML + Markdown)")
    ap.add_argument("--client")
    ap.add_argument("--root", default=str(ROOT / "clients"))
    ap.add_argument("--state"); ap.add_argument("--metrics"); ap.add_argument("--ledger"); ap.add_argument("--pulse")
    ap.add_argument("--lang", choices=["uz", "ru", "en"], default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    args = ap.parse_args(argv)
    cdir = Path(args.root) / args.client if args.client else None
    pick = lambda explicit, rel: explicit or (str(cdir / rel) if cdir else None)  # noqa: E731
    sp = pick(args.state, "state.json")
    if not (sp and Path(sp).is_file()) and not args.metrics and not (cdir and (cdir / "data" / "metrics.json").is_file()):
        print("xato: state.json yoki metrics topilmadi", file=sys.stderr)
        return 2
    state = _read_json(sp, {})
    state = state if isinstance(state, dict) else {}
    lang = args.lang or ("uz" if state.get("language") in (None, "uz_cyrillic", "uz") else state.get("language"))
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    metrics = _rows(_read_json(pick(args.metrics, "data/metrics.json"), []))
    model = build_model(state, metrics, _read_jsonl(pick(args.ledger, "ledger.jsonl")), _read_json(pick(args.pulse, "outputs/pulse.json"), []), lang)
    Path(args.out).write_text(render_html(model), encoding="utf-8")
    if args.md:
        Path(args.md).write_text(render_md(model), encoding="utf-8")
    print(json.dumps({"html": args.out, "md": args.md, "lang": lang, "rows": len(metrics)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
