#!/usr/bin/env python3
"""pulse.py — kundalik hisob kuzatuvi (read-only). HECH NARSANI O'ZI BAJARMAYDI.

metrics.v1 (schemas/metrics.v1.json) va clients/<slug>/state.json dan quyidagilarni tekshiradi:
  pacing · cpa_drift · roas_drift · fatigue (frequency↑ + CTR↓) · tracking_break · spend_spike
  · delivery_status (learning-limited / rejected, ma'lumot bo'lsa) · platform_anomaly (ixtiyoriy signal fayli)

Chegaralar `state.json -> pulse_config` da; standart qiymatlar `HEURISTIC_PRIOR_MODEL`.
Har topilma: severity, evidence, next_step, needs_approval. Hisob o'zgarishi faqat Spend-Guard + tasdiq bilan.

    python3 tools/pulse.py run --client demo [--metrics f.json] [--format json|md|both] [--write]
Chiqish: 0 ok · 1 --fail-on darvozasi · 2 validatsiya xatosi.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import statistics
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import tyrion_core as tcore  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

ROOT = _TOOLS_DIR.parent
CONFIG_LABEL = "HEURISTIC_PRIOR_MODEL"
DEFAULT_CONFIG: dict = {
    "window_days": 7,
    "baseline_days": 21,
    "pacing_tolerance_pct": 15.0,
    "min_conversions": 30,
    "alpha": 0.05,
    "cpa_drift_pct": 25.0,
    "roas_drift_pct": 25.0,
    "min_impressions": 5000,
    "freq_growth_pct": 20.0,
    "ctr_drop_pct": 15.0,
    "tracking_window_days": 3,
    "tracking_drop_pct": 60.0,
    "tracking_min_traffic_pct": 70.0,
    "spend_spike_factor": 2.0,
    "min_spike_history_days": 5,
}
LEVELS = ("campaign", "adset", "ad")
SEV_ORDER = {"critical": 3, "warning": 2, "info": 1}
BAD_DELIVERY = {
    "learning_limited": ("warning", "Learning-limited: byudjet/audit yetarli emas, tuzilmani birlashtirishni ko'rib chiqing"),
    "rejected": ("critical", "Reklama rad etilgan: policy sababini o'qing va tuzatilgan variantni yuboring"),
    "disapproved": ("critical", "Reklama rad etilgan: policy sababini o'qing va tuzatilgan variantni yuboring"),
}


class PulseError(ValueError):
    """Kirish xatosi (exit 2)."""


# ───────────────────────────── yordamchilar ─────────────────────────────
def _load_json(path: Path, what: str):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PulseError(f"{what} topilmadi: {path}")
    except json.JSONDecodeError as exc:
        raise PulseError(f"{what} JSON emas: {path} ({exc})")


def load_rows(doc) -> list[dict]:
    rows = doc.get("rows") if isinstance(doc, dict) else doc
    if not isinstance(rows, list):
        raise PulseError("metrics fayli {'rows': [...]} yoki massiv bo'lishi kerak")
    out = []
    for r in rows:
        if not isinstance(r, dict) or "date" not in r:
            raise PulseError("har qatorda 'date' bo'lishi shart")
        try:
            r = dict(r)
            r["_d"] = dt.date.fromisoformat(str(r["date"]))
        except ValueError:
            raise PulseError(f"noto'g'ri sana: {r.get('date')!r}")
        out.append(r)
    return out


def pick_level(rows: list[dict], level: str | None = None) -> list[dict]:
    """Ikki marta sanamaslik uchun bitta daraja (campaign > adset > ad)."""
    present = {r.get("level") for r in rows}
    if level:
        chosen = level
    else:
        chosen = next((lv for lv in LEVELS if lv in present), None)
    return [r for r in rows if chosen is None or r.get("level") == chosen]


def _num(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    return v if math.isfinite(v) else 0.0


def goal_event(rows: list[dict], state: dict) -> str | None:
    ev = (state.get("goals") or {}).get("conversion_event")
    if ev:
        return ev
    totals: dict[str, float] = {}
    for r in rows:
        for k, v in (r.get("conversions") or {}).items():
            totals[k] = totals.get(k, 0.0) + _num(v)
    return max(totals, key=totals.get) if totals else None


def aggregate(rows: list[dict], start: dt.date, end: dt.date, event: str | None) -> dict:
    sel = [r for r in rows if start <= r["_d"] <= end]
    days = sorted({r["_d"] for r in sel})
    impr = sum(_num(r.get("impressions")) for r in sel)
    clicks = sum(_num(r.get("link_clicks") or r.get("clicks")) for r in sel)
    conv = 0.0
    for r in sel:
        c = r.get("conversions") or {}
        conv += _num(c.get(event)) if event else sum(_num(v) for v in c.values())
    return {
        "days": len(days),
        "spend": sum(_num(r.get("spend")) for r in sel),
        "impressions": impr,
        "clicks": clicks,
        "conversions": conv,
        "value": sum(_num(r.get("conversion_value")) for r in sel),
        "freq_w": sum(_num(r.get("frequency")) * _num(r.get("impressions")) for r in sel),
    }


def _ratio(a: float, b: float) -> float | None:
    return a / b if b else None


def _pct(new: float, old: float) -> float | None:
    return (new / old - 1.0) * 100.0 if old else None


def _norm_two_sided_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def rate_ratio_p(c1: float, s1: float, c2: float, s2: float) -> float:
    """H0: konversiya sarfga proporsional (CPA bir xil). Shartli binomial z-test, ikki tomonlama p."""
    n = c1 + c2
    if n <= 0 or s1 <= 0 or s2 <= 0:
        return 1.0
    q = s1 / (s1 + s2)
    var = n * q * (1 - q)
    if var <= 0:
        return 1.0
    return _norm_two_sided_p((c1 - n * q) / math.sqrt(var))


def _r(x, nd=2):
    return None if x is None else round(x, nd)


def _finding(check, severity, status, evidence, next_step, needs_approval, entity=None) -> dict:
    return {
        "id": f"{check}:{entity}" if entity else check,
        "check": check,
        "severity": severity,
        "status": status,
        "evidence": evidence,
        "evidence_label": "MEASURED_ACCOUNT_DATA",
        "next_step": next_step,
        "needs_approval": needs_approval,
    }


# ───────────────────────────── tekshiruvlar ─────────────────────────────
class Ctx:
    def __init__(self, rows, state, cfg):
        self.all_rows = rows
        self.rows = pick_level(rows, cfg.get("level"))
        self.state = state
        self.cfg = cfg
        self.event = goal_event(self.rows, state)
        self.as_of = max(r["_d"] for r in self.rows) if self.rows else None
        w = int(cfg["window_days"])
        self.recent_start = self.as_of - dt.timedelta(days=w - 1) if self.as_of else None
        self.prior_end = self.recent_start - dt.timedelta(days=1) if self.as_of else None
        self.prior_start = self.prior_end - dt.timedelta(days=int(cfg["baseline_days"]) - 1) if self.as_of else None
        self.recent = aggregate(self.rows, self.recent_start, self.as_of, self.event) if self.as_of else None
        self.prior = aggregate(self.rows, self.prior_start, self.prior_end, self.event) if self.as_of else None

    def windows(self) -> dict:
        return {
            "as_of": str(self.as_of),
            "recent": [str(self.recent_start), str(self.as_of)],
            "baseline": [str(self.prior_start), str(self.prior_end)],
            "level": self.rows[0].get("level") if self.rows else None,
            "conversion_event": self.event,
        }


def check_pacing(ctx: Ctx):
    planned = _num((ctx.state.get("goals") or {}).get("daily_budget"))
    if planned <= 0:
        return "skipped", None, "state.goals.daily_budget yo'q"
    rec = ctx.recent
    if not rec["days"]:
        return "insufficient_data", None, "oxirgi oynada ma'lumot yo'q"
    avg = rec["spend"] / rec["days"]
    dev = (avg / planned - 1) * 100
    tol = ctx.cfg["pacing_tolerance_pct"]
    ev = {"planned_daily": planned, "actual_daily_avg": _r(avg), "deviation_pct": _r(dev), "tolerance_pct": tol, "days": rec["days"]}
    if abs(dev) <= tol:
        return "ok", None, ev
    sev = "critical" if abs(dev) > 2 * tol else "warning"
    over = dev > 0
    step = ("Sarf rejadan yuqori: kampaniya limitlari va yangi faol reklamalarni tekshiring; byudjetni kamaytirish — Spend-Guard paketi va tasdiq bilan."
            if over else
            "Sarf rejadan past: yetkazib berish holati, rad etilgan reklamalar va auktsion cheklovlarini tekshiring; byudjetni o'zgartirish — Spend-Guard paketi va tasdiq bilan.")
    return "flagged", _finding("pacing", sev, "flagged", ev, step, True), ev


def _drift_inputs(ctx: Ctx):
    mc = ctx.cfg["min_conversions"]
    r, p = ctx.recent, ctx.prior
    if r["conversions"] < mc or p["conversions"] < mc:
        ev = {"recent_conversions": r["conversions"], "baseline_conversions": p["conversions"], "min_conversions": mc}
        return None, ev
    return (r, p), None


def check_cpa_drift(ctx: Ctx):
    pair, ev0 = _drift_inputs(ctx)
    if pair is None:
        f = _finding("cpa_drift", "info", "insufficient_data", ev0,
                     "Ma'lumot yetarli emas: xulosa chiqarmang, konversiya soni to'planguncha kuzating.", False)
        return "insufficient_data", f, ev0
    r, p = pair
    cpa_r, cpa_p = r["spend"] / r["conversions"], p["spend"] / p["conversions"]
    chg = _pct(cpa_r, cpa_p)
    pv = rate_ratio_p(p["conversions"], p["spend"], r["conversions"], r["spend"])
    ev = {"cpa_recent": _r(cpa_r), "cpa_baseline": _r(cpa_p), "change_pct": _r(chg), "p_value": round(pv, 5),
          "alpha": ctx.cfg["alpha"], "test": "conditional binomial rate-ratio (konversiya ~ sarf)",
          "recent_conversions": r["conversions"], "baseline_conversions": p["conversions"]}
    if chg is not None and chg >= ctx.cfg["cpa_drift_pct"] and pv < ctx.cfg["alpha"]:
        sev = "critical" if chg >= 2 * ctx.cfg["cpa_drift_pct"] else "warning"
        step = "CPA bazadan statistik ishonchli oshgan: avval tracking va kreativ charchoqni tekshiring, so'ng kreativ almashtirish/byudjet — Spend-Guard paketi va tasdiq bilan."
        return "flagged", _finding("cpa_drift", sev, "flagged", ev, step, True), ev
    return "ok", None, ev


def check_roas_drift(ctx: Ctx):
    pair, ev0 = _drift_inputs(ctx)
    if pair is None or not (ctx.recent["value"] or ctx.prior["value"]):
        if pair is None:
            f = _finding("roas_drift", "info", "insufficient_data", ev0,
                         "Ma'lumot yetarli emas: ROAS bo'yicha xulosa chiqarmang.", False)
            return "insufficient_data", f, ev0
        return "skipped", None, "conversion_value yo'q"
    r, p = pair
    roas_r, roas_p = _ratio(r["value"], r["spend"]) or 0.0, _ratio(p["value"], p["spend"]) or 0.0
    chg = _pct(roas_r, roas_p)
    ev = {"roas_recent": _r(roas_r), "roas_baseline": _r(roas_p), "change_pct": _r(chg),
          "test": "faqat chegara (ROAS dispersiyasi yo'q — statistik test o'tkazilmadi)"}
    if chg is not None and chg <= -ctx.cfg["roas_drift_pct"]:
        step = "ROAS bazadan pasaygan: buyurtma qiymati, tracking va auditoriya to'yinishini tekshiring; o'zgartirishlar tasdiq bilan."
        return "flagged", _finding("roas_drift", "warning", "flagged", ev, step, True), ev
    return "ok", None, ev


def check_fatigue(ctx: Ctx):
    r, p, cfg = ctx.recent, ctx.prior, ctx.cfg
    if r["impressions"] < cfg["min_impressions"] or p["impressions"] < cfg["min_impressions"]:
        return "insufficient_data", None, {"min_impressions": cfg["min_impressions"]}
    fr, fp = r["freq_w"] / r["impressions"], p["freq_w"] / p["impressions"]
    ctr_r, ctr_p = r["clicks"] / r["impressions"], p["clicks"] / p["impressions"]
    fg, cd = _pct(fr, fp), _pct(ctr_r, ctr_p)
    ev = {"frequency_recent": _r(fr), "frequency_baseline": _r(fp), "frequency_growth_pct": _r(fg),
          "ctr_recent_pct": _r(ctr_r * 100, 3), "ctr_baseline_pct": _r(ctr_p * 100, 3), "ctr_change_pct": _r(cd)}
    if fg is not None and cd is not None and fg >= cfg["freq_growth_pct"] and cd <= -cfg["ctr_drop_pct"]:
        step = "Frequency o'sib CTR tushgan (charchoq): yangi angle/format tayyorlang (creative-analytics); almashtirish tasdiq bilan."
        return "flagged", _finding("fatigue", "warning", "flagged", ev, step, True), ev
    return "ok", None, ev


def check_tracking_break(ctx: Ctx):
    cfg = ctx.cfg
    tw = int(cfg["tracking_window_days"])
    t_start = ctx.as_of - dt.timedelta(days=tw - 1)
    ref_end = t_start - dt.timedelta(days=1)
    ref_start = ref_end - dt.timedelta(days=int(cfg["baseline_days"]) - 1)
    t = aggregate(ctx.rows, t_start, ctx.as_of, ctx.event)
    ref = aggregate(ctx.rows, ref_start, ref_end, ctx.event)
    if ref["conversions"] < cfg["min_conversions"] or not ref["days"] or not t["days"]:
        return "insufficient_data", None, {"baseline_conversions": ref["conversions"], "min_conversions": cfg["min_conversions"]}
    t_conv, ref_conv = t["conversions"] / t["days"], ref["conversions"] / ref["days"]
    t_spend, ref_spend = t["spend"] / t["days"], ref["spend"] / ref["days"]
    t_clk, ref_clk = t["clicks"] / t["days"], ref["clicks"] / ref["days"]
    drop = (1 - t_conv / ref_conv) * 100
    traffic_pct = (t_clk / ref_clk * 100) if ref_clk else None
    spend_pct = (t_spend / ref_spend * 100) if ref_spend else 0.0
    ratio_t, ratio_ref = _ratio(t["conversions"], t["clicks"]), _ratio(ref["conversions"], ref["clicks"])
    ev = {"window_days": tw, "conv_per_day_recent": _r(t_conv), "conv_per_day_baseline": _r(ref_conv), "conversion_drop_pct": _r(drop),
          "spend_vs_baseline_pct": _r(spend_pct), "clicks_vs_baseline_pct": _r(traffic_pct),
          "click_to_event_recent": _r(ratio_t, 4), "click_to_event_baseline": _r(ratio_ref, 4)}
    traffic_ok = traffic_pct is None or traffic_pct >= cfg["tracking_min_traffic_pct"]
    if spend_pct >= 50 and drop >= cfg["tracking_drop_pct"] and traffic_ok:
        step = ("Sarf va trafik bor, konversiya keskin tushgan — tracking uzilishi ehtimoli: Pixel/CAPI/GTM, event_id dedup va forma/bot webhookni darhol tekshiring. "
                "Hali kampaniyani to'xtatmang: avval o'lchovni tasdiqlang.")
        return "flagged", _finding("tracking_break", "critical", "flagged", ev, step, False), ev
    return "ok", None, ev


def check_spend_spike(ctx: Ctx):
    cfg = ctx.cfg
    daily: dict[dt.date, float] = {}
    for r in ctx.rows:
        daily[r["_d"]] = daily.get(r["_d"], 0.0) + _num(r.get("spend"))
    hist = [v for d, v in daily.items() if d < ctx.as_of]
    if len(hist) < cfg["min_spike_history_days"]:
        return "insufficient_data", None, {"history_days": len(hist), "min": cfg["min_spike_history_days"]}
    med = statistics.median(hist[-int(cfg["baseline_days"]):])
    last = daily.get(ctx.as_of, 0.0)
    ev = {"last_day": str(ctx.as_of), "last_day_spend": _r(last), "median_prior": _r(med), "factor": _r(last / med) if med else None,
          "spike_factor": cfg["spend_spike_factor"]}
    if med > 0 and last >= cfg["spend_spike_factor"] * med:
        step = "Sarf sakrashi: oxirgi kunda yangi reklama/limit o'zgarishi yoki bid xatosi bormi, faollik jurnalini tekshiring (shikoyat bo'lsa platformaga murojaat)."
        return "flagged", _finding("spend_spike", "warning", "flagged", ev, step, False), ev
    return "ok", None, ev


def check_delivery(ctx: Ctx):
    seen_field = any(("delivery_status" in r or "effective_status" in r) for r in ctx.all_rows)
    if not seen_field:
        return "skipped", [], "delivery_status/effective_status maydoni yo'q"
    findings = []
    last = {}
    for r in ctx.all_rows:
        key = (r.get("level"), r.get("entity_id"))
        if key not in last or r["_d"] >= last[key]["_d"]:
            last[key] = r
    for (lvl, eid), r in sorted(last.items(), key=lambda kv: str(kv[0])):
        if r["_d"] < ctx.as_of - dt.timedelta(days=1):
            continue
        status = str(r.get("delivery_status") or r.get("effective_status") or "").lower().replace("-", "_").replace(" ", "_")
        if status in BAD_DELIVERY:
            sev, step = BAD_DELIVERY[status]
            findings.append(_finding("delivery_status", sev, "flagged",
                                     {"level": lvl, "entity_id": eid, "entity_name": r.get("entity_name"), "status": status, "date": str(r["_d"])},
                                     step, True, entity=eid))
    return ("flagged" if findings else "ok"), findings, {"flagged": len(findings)}


def check_anomaly(signal_doc):
    sigs = signal_doc.get("signals") if isinstance(signal_doc, dict) else signal_doc
    if not isinstance(sigs, list):
        raise PulseError("anomaly-signal fayli {'signals': [...]} yoki massiv bo'lishi kerak")
    out = []
    for i, s in enumerate(sigs):
        if not isinstance(s, dict):
            continue
        f = _finding("platform_anomaly", s.get("severity") if s.get("severity") in SEV_ORDER else "info", "flagged", s,
                     "Platforma anomaliya signali (qo'shimcha dalil): o'z o'lchovlaringiz bilan solishtiring, tasdiqlansa tegishli tekshiruvga o'ting.",
                     False, entity=str(s.get("entity_id") or i))
        f["evidence_label"] = "PLATFORM_SIGNAL (ads_insights_anomaly_signal)"
        out.append(f)
    return out


CHECKS = [
    ("pacing", check_pacing),
    ("cpa_drift", check_cpa_drift),
    ("roas_drift", check_roas_drift),
    ("fatigue", check_fatigue),
    ("tracking_break", check_tracking_break),
    ("spend_spike", check_spend_spike),
]


def run_pulse(rows_doc, state: dict | None = None, anomaly_doc=None, client: str = "") -> dict:
    state = state or {}
    cfg = dict(DEFAULT_CONFIG)
    user_cfg = state.get("pulse_config") or {}
    cfg.update({k: v for k, v in user_cfg.items() if k in DEFAULT_CONFIG or k == "level"})
    rows = load_rows(rows_doc)
    if not rows:
        raise PulseError("metrics bo'sh: pulse uchun kamida bir qator kerak")
    ctx = Ctx(rows, state, cfg)
    checks, findings = [], []
    for name, fn in CHECKS:
        status, f, detail = fn(ctx)
        checks.append({"check": name, "status": status, "detail": detail})
        if f:
            findings.append(f)
    status, dfs, detail = check_delivery(ctx)
    checks.append({"check": "delivery_status", "status": status, "detail": detail})
    findings.extend(dfs)
    if anomaly_doc is not None:
        an = check_anomaly(anomaly_doc)
        checks.append({"check": "platform_anomaly", "status": "flagged" if an else "ok", "detail": {"signals": len(an)}})
        findings.extend(an)
    findings.sort(key=lambda f: -SEV_ORDER.get(f["severity"], 0))
    synthetic = all(bool(r.get("synthetic")) for r in rows)
    return {
        "schema": "pulse.v1",
        "client": client,
        "read_only": True,
        "executed_actions": [],
        "synthetic": synthetic,
        "windows": ctx.windows(),
        "config": {k: cfg[k] for k in DEFAULT_CONFIG},
        "config_label": CONFIG_LABEL + (" (state.pulse_config bilan qayta yozilgan: " + ", ".join(sorted(user_cfg)) + ")" if user_cfg else ""),
        "summary": {s: sum(1 for f in findings if f["severity"] == s) for s in ("critical", "warning", "info")},
        "findings": findings,
        "checks": checks,
    }


def render_markdown(rep: dict) -> str:
    w = rep["windows"]
    lines = [f"# Pulse — {rep['client'] or 'mijoz'} · {w['as_of']}", "",
             f"Oyna: oxirgi {w['recent'][0]}…{w['recent'][1]}, baza {w['baseline'][0]}…{w['baseline'][1]} · daraja: {w['level']} · hodisa: {w['conversion_event']}",
             f"Chegaralar: `{rep['config_label']}`" + (" · **sintetik ma'lumot**" if rep["synthetic"] else ""),
             "Pulse faqat o'qiydi: hech qanday hisob o'zgarishi bajarilmagan.", ""]
    s = rep["summary"]
    lines.append(f"**Jami:** {s['critical']} critical · {s['warning']} warning · {s['info']} info")
    lines.append("")
    if not rep["findings"]:
        lines.append("Muammo topilmadi.")
    for f in rep["findings"]:
        lines.append(f"## [{f['severity'].upper()}] {f['id']}")
        lines.append(f"- Dalil ({f['evidence_label']}): `{json.dumps(f['evidence'], ensure_ascii=False)}`")
        lines.append(f"- Keyingi qadam: {f['next_step']}")
        lines.append(f"- Tasdiq kerak: {'ha' if f['needs_approval'] else 'yo`q (faqat tekshiruv)'}")
        lines.append("")
    lines.append("## Tekshiruvlar")
    for c in rep["checks"]:
        lines.append(f"- {c['check']}: {c['status']}")
    return "\n".join(lines) + "\n"


# ───────────────────────────── CLI ─────────────────────────────
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tyrion Pulse — kundalik kuzatuv (read-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="Tekshiruvlarni ishga tushirish")
    run.add_argument("--client", required=True, help="mijoz slug")
    run.add_argument("--clients-dir", default=str(ROOT / "clients"))
    run.add_argument("--metrics", help="metrics.v1 fayli (default clients/<slug>/data/metrics.v1.json)")
    run.add_argument("--state", help="state.json yo'li (default clients/<slug>/state.json; yo'q bo'lsa {} )")
    run.add_argument("--anomaly-signal", help="ads_insights_anomaly_signal natijasi (JSON)")
    run.add_argument("--format", choices=["json", "md", "both"], default="json")
    run.add_argument("--write", action="store_true", help="clients/<slug>/pulse/<sana>.json|md ga yozish")
    run.add_argument("--fail-on", choices=["critical", "warning"], help="shu darajada exit 1")
    args = ap.parse_args(argv)

    slug = tcore.safe_slug(args.client)
    cdir = Path(args.clients_dir) / slug
    try:
        mpath = Path(args.metrics) if args.metrics else cdir / "data" / "metrics.v1.json"
        spath = Path(args.state) if args.state else cdir / "state.json"
        state = _load_json(spath, "state.json") if spath.exists() else {}
        if args.state and not spath.exists():
            raise PulseError(f"state.json topilmadi: {spath}")
        rep = run_pulse(_load_json(mpath, "metrics"), state,
                        _load_json(Path(args.anomaly_signal), "anomaly-signal") if args.anomaly_signal else None, client=slug)
    except PulseError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return tcore.EXIT_VALIDATION
    md = render_markdown(rep)
    if args.write:
        out = cdir / "pulse"
        out.mkdir(parents=True, exist_ok=True)
        stamp = rep["windows"]["as_of"]
        tcore.atomic_write_json(out / f"{stamp}.json", rep)
        tcore.atomic_write_text(out / f"{stamp}.md", md)
    if args.format == "md":
        print(md)
    elif args.format == "both":
        rep_out = dict(rep)
        rep_out["markdown"] = md
        print(json.dumps(rep_out, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    if args.fail_on:
        floor = SEV_ORDER[args.fail_on]
        if any(SEV_ORDER[f["severity"]] >= floor for f in rep["findings"]):
            return tcore.EXIT_GATE_BLOCKED
    return tcore.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
