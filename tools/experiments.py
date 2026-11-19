#!/usr/bin/env python3
"""experiments.py — eksperiment ledger'i: dizayn, ro'yxat, natija o'qish, instinktga ko'tarish, change packet.

    design   --baseline 0.05 --mde 0.2 [--alpha 0.05 --power 0.8 --cost-per-unit 0.4 --daily-budget 50]
    register --client <slug> --name ... --hypothesis ... --metric ... --baseline 0.05 --mde 0.2 --n-per-arm N
    readout  --client <slug> --id EXP-0001 --control-n N --control-conv X --variant-n N --variant-conv X
    promote  --client <slug> --id EXP-0001 [--dry-run]       (tools/instincts.py add ga uzatadi)
    packet   --client <slug> --id EXP-0001 --kind native_ab|lift   (change packet JSON; testni AVTO-YARATMAYDI)

Ledger: clients/<slug>/ledger.jsonl (har qator bir hodisa). Faqat stdlib. Hisoblar deterministik (--seed).
Chiqish: 0 ok · 2 validatsiya xatosi.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import random
import re
import subprocess
import sys
from pathlib import Path
from statistics import NormalDist

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
LEDGER_SCHEMA = "ledger.v1"
MIN_CONV_PER_ARM = 30
BAYES_DRAWS = 20000
PROB_BEST_THRESHOLD = 0.95
DOMAINS = ("meta", "google", "telegram", "kreativ", "tracking", "tizim")
PACKET_KINDS = {"native_ab": "ads_experiment_abtest_create_test", "lift": "ads_experiment_lift_create_test"}


class ExperimentError(ValueError):
    """Kirish xatosi (exit 2)."""


def _num(v, name, **kw) -> float:
    try:
        return tcore.require_number(v, name, **kw)
    except tcore.NumberValidationError as exc:
        raise ExperimentError(str(exc))


# ───────────────────────────── hisob ─────────────────────────────
def sample_size_per_arm(p1: float, p2: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Ikki proporsiya, ikki tomonlama z-test: har guruhga kerak n (yuqoriga yaxlitlangan)."""
    if not (0 < p1 < 1 and 0 < p2 < 1) or p1 == p2:
        raise ExperimentError("baseline va nishon ehtimollari (0,1) oralig'ida va farqli bo'lishi shart")
    if not (0 < alpha < 1 and 0 < power < 1):
        raise ExperimentError("alpha va power (0,1) oralig'ida bo'lishi shart")
    nd = NormalDist()
    za, zb = nd.inv_cdf(1 - alpha / 2), nd.inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return int(math.ceil(num / (p2 - p1) ** 2))


def design(baseline, mde=None, mde_abs=None, alpha=0.05, power=0.8, arms=2, unit="unit",
           cost_per_unit=None, daily_budget=None, target_cpa=None, currency="USD") -> dict:
    p1 = _num(baseline, "baseline", positive=True, max_val=0.999999)
    if (mde is None) == (mde_abs is None):
        raise ExperimentError("mde (nisbiy) yoki mde_abs (mutlaq) dan aynan bittasini bering")
    p2 = p1 * (1 + _num(mde, "mde", positive=True)) if mde is not None else p1 + _num(mde_abs, "mde_abs", positive=True)
    if p2 >= 1:
        raise ExperimentError("nishon ehtimol 1 dan kichik bo'lishi shart")
    alpha = _num(alpha, "alpha", positive=True, max_val=0.5)
    power = _num(power, "power", positive=True, max_val=0.999)
    arms = int(_num(arms, "arms", min_val=2))
    adj_alpha = alpha / (arms - 1)  # Bonferroni (nazoratga nisbatan har variant)
    n = sample_size_per_arm(p1, p2, adj_alpha, power)
    res = {
        "baseline": p1, "target_rate": round(p2, 6), "mde_relative": round(p2 / p1 - 1, 6), "mde_absolute": round(p2 - p1, 6),
        "alpha": alpha, "alpha_adjusted": round(adj_alpha, 6), "power": power, "arms": arms, "unit": unit,
        "n_per_arm": n, "n_total": n * arms,
        "method": "ikki proporsiya z-test (pooled), ikki tomonlama; arms>2 da Bonferroni",
        "label": "HEURISTIC_PRIOR_MODEL (baseline foydalanuvchi/akkaunt ma'lumotidan; formula standart)",
    }
    if cost_per_unit is not None:
        cpu = _num(cost_per_unit, "cost_per_unit", positive=True)
        total = n * arms * cpu
        res["budget"] = {"currency": currency, "cost_per_unit": cpu, "total": round(total, 2)}
        if daily_budget is not None:
            db = _num(daily_budget, "daily_budget", positive=True)
            res["budget"]["daily_budget"] = db
            res["budget"]["days_needed"] = int(math.ceil(total / db))
            res["budget"]["days_recommended"] = max(7, int(math.ceil(total / db)))
            res["budget"]["note"] = "kamida 7 kun (hafta kun-tsikli); kunlar = jami byudjet / kunlik byudjet"
            if target_cpa is not None:
                import calculator
                res["learning_phase"] = calculator.calc_meta_155(db, _num(target_cpa, "target_cpa", positive=True), currency)["learning_phase_math"]
    elif daily_budget is not None:
        raise ExperimentError("daily_budget uchun cost_per_unit ham kerak")
    return res


def _prop_stats(n1, x1, n2, x2, alpha):
    p1, p2 = x1 / n1, x2 / n2
    pooled = (x1 + x2) / (n1 + n2)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se0 if se0 > 0 else 0.0
    p = math.erfc(abs(z) / math.sqrt(2))
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    zc = NormalDist().inv_cdf(1 - alpha / 2)
    return p1, p2, z, p, (p2 - p1 - zc * se, p2 - p1 + zc * se)


def bayes_prob_best(n1, x1, n2, x2, seed=7, draws=BAYES_DRAWS) -> dict:
    """Beta(1+x, 1+n-x) posterior'lar; P(variant > control) va kutilgan nisbiy lift (deterministik seed)."""
    rng = random.Random(seed)
    wins, lift_sum = 0, 0.0
    for _ in range(draws):
        a = rng.betavariate(1 + x1, 1 + n1 - x1)
        b = rng.betavariate(1 + x2, 1 + n2 - x2)
        wins += b > a
        lift_sum += (b / a - 1) if a > 0 else 0.0
    return {"prob_variant_better": round(wins / draws, 4), "expected_relative_lift": round(lift_sum / draws, 4), "draws": draws, "seed": seed}


def readout(control_n, control_conv, variant_n, variant_conv, alpha=0.05, planned_n_per_arm=None, seed=7) -> dict:
    n1, n2 = int(_num(control_n, "control_n", positive=True)), int(_num(variant_n, "variant_n", positive=True))
    x1, x2 = int(_num(control_conv, "control_conv", non_negative=True)), int(_num(variant_conv, "variant_conv", non_negative=True))
    if x1 > n1 or x2 > n2:
        raise ExperimentError("konversiya soni namuna hajmidan katta bo'lishi mumkin emas")
    alpha = _num(alpha, "alpha", positive=True, max_val=0.5)
    p1, p2, z, p, ci = _prop_stats(n1, x1, n2, x2, alpha)
    bay = bayes_prob_best(n1, x1, n2, x2, seed=seed)
    rel = (p2 / p1 - 1) if p1 > 0 else None
    warnings: list[str] = []
    if min(x1, x2) < MIN_CONV_PER_ARM:
        warnings.append(f"Konversiya soni kam (<{MIN_CONV_PER_ARM}/guruh): normal yaqinlashuv ishonchsiz, natijani qaror uchun ishlatmang.")
    under_planned = bool(planned_n_per_arm) and min(n1, n2) < planned_n_per_arm
    if under_planned:
        warnings.append(f"Namuna rejalashtirilgan hajmdan kichik ({min(n1, n2)} < {int(planned_n_per_arm)}): erta to'xtatish yolg'on 'g'olib' xavfini oshiradi.")
    if not planned_n_per_arm:
        warnings.append("Rejalashtirilgan namuna hajmi (design/register) yo'q: peeking xavfini tekshirib bo'lmaydi.")
    significant = p < alpha
    pb = bay["prob_variant_better"]
    if under_planned or min(x1, x2) < MIN_CONV_PER_ARM:
        verdict = "INCONCLUSIVE"
    elif significant and p2 > p1 and pb >= PROB_BEST_THRESHOLD:
        verdict = "WIN"
    elif significant and p2 < p1 and pb <= 1 - PROB_BEST_THRESHOLD:
        verdict = "LOSS"
    else:
        verdict = "INCONCLUSIVE"
    return {
        "verdict": verdict,
        "control": {"n": n1, "conversions": x1, "rate": round(p1, 6)},
        "variant": {"n": n2, "conversions": x2, "rate": round(p2, 6)},
        "relative_lift": None if rel is None else round(rel, 4),
        "absolute_diff": round(p2 - p1, 6),
        "z": round(z, 4), "p_value": round(p, 6), "alpha": alpha, "significant": significant,
        "ci_diff": [round(ci[0], 6), round(ci[1], 6)], "ci_level": round(1 - alpha, 4),
        "bayes": bay,
        "significant_but_underpowered": bool(significant and (under_planned or min(x1, x2) < MIN_CONV_PER_ARM)),
        "warnings": warnings,
        "label": "MEASURED_ACCOUNT_DATA (kiruvchi sonlar foydalanuvchi/akkauntdan; hukm qoidasi: p<alpha va P(best)>=0.95 va reja hajmi bajarilgan)",
    }


# ───────────────────────────── ledger ─────────────────────────────
def ledger_path(clients_dir, slug) -> Path:
    return Path(clients_dir) / tcore.safe_slug(slug) / "ledger.jsonl"


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                raise ExperimentError(f"{path}:{i} JSON emas")
    return out


def append_event(path: Path, event: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    event = dict(event, schema=LEDGER_SCHEMA, at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def find_experiment(events: list[dict], exp_id: str) -> dict:
    reg = next((e for e in events if e.get("event") == "registered" and e.get("id") == exp_id), None)
    if not reg:
        raise ExperimentError(f"{exp_id} ledger'da yo'q")
    return reg


def register(path: Path, name, hypothesis, metric, baseline, mde, n_per_arm, alpha=0.05, power=0.8, variants=("control", "variant"),
             owner="", start=None, domain="meta", synthetic=False) -> dict:
    events = read_ledger(path)
    n_reg = sum(1 for e in events if e.get("event") == "registered")
    rec = {
        "event": "registered", "id": f"EXP-{n_reg + 1:04d}", "name": name, "hypothesis": hypothesis, "metric": metric,
        "baseline": _num(baseline, "baseline", positive=True), "mde_relative": _num(mde, "mde", positive=True),
        "n_per_arm": int(_num(n_per_arm, "n_per_arm", positive=True)), "alpha": alpha, "power": power,
        "variants": list(variants), "owner": owner, "start": start or dt.date.today().isoformat(), "domain": domain,
        "status": "running", "synthetic": bool(synthetic),
    }
    if not name or not hypothesis or not metric:
        raise ExperimentError("name, hypothesis va metric majburiy")
    return append_event(path, rec)


def do_readout(path: Path | None, exp_id: str | None, control_n, control_conv, variant_n, variant_conv, alpha=None, seed=7) -> dict:
    planned = None
    reg = None
    if path is not None and exp_id:
        reg = find_experiment(read_ledger(path), exp_id)
        planned = reg.get("n_per_arm")
        alpha = alpha if alpha is not None else reg.get("alpha", 0.05)
    res = readout(control_n, control_conv, variant_n, variant_conv, alpha=alpha if alpha is not None else 0.05, planned_n_per_arm=planned, seed=seed)
    if reg is not None:
        res["id"] = exp_id
        append_event(path, {"event": "readout", "id": exp_id, "verdict": res["verdict"], "result": res, "domain": reg.get("domain", "meta")})
    return res


def _slug(text: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", str(text).lower())).strip("-")[:40] or "test"


def instinct_args(reg: dict, last_readout: dict, replicated: bool) -> list[str]:
    res = last_readout["result"]
    direction = "yutdi" if last_readout["verdict"] == "WIN" else "yutqazdi"
    evidence = (f"{reg['id']} ledger: {direction}, nisbiy lift {res['relative_lift']}, p={res['p_value']}, P(best)={res['bayes']['prob_variant_better']}, "
                f"n/guruh={res['control']['n']}/{res['variant']['n']}" + (", takrorlangan" if replicated else ""))
    if reg.get("synthetic"):
        evidence += " [SYNTHETIC]"
    action = f"Variant {direction}: " + reg["hypothesis"]
    return ["--id", f"exp-{reg['id'].lower()}-{_slug(reg['name'])}", "--domain", reg.get("domain", "meta") if reg.get("domain") in DOMAINS else "meta",
            "--trigger", f"Shunga o'xshash test: {reg['name']}", "--action", action, "--evidence", evidence,
            "--confidence", "4" if replicated else "3"]


def promote(path: Path, exp_id: str, dry_run=False, runner=subprocess.run) -> dict:
    events = read_ledger(path)
    reg = find_experiment(events, exp_id)
    reads = [e for e in events if e.get("event") == "readout" and e.get("id") == exp_id]
    if not reads:
        raise ExperimentError(f"{exp_id} uchun readout yo'q: avval natijani o'qing")
    last = reads[-1]
    if last["verdict"] not in ("WIN", "LOSS"):
        raise ExperimentError(f"{exp_id} hukmi {last['verdict']}: instinktga faqat WIN/LOSS ko'tariladi")
    decisive = [e for e in reads if e["verdict"] == last["verdict"]]
    same_hyp = [e for e in events if e.get("event") == "registered" and e.get("hypothesis") == reg["hypothesis"] and e["id"] != exp_id]
    replicated = len(decisive) >= 2 or any(
        any(r.get("event") == "readout" and r.get("id") == o["id"] and r["verdict"] == last["verdict"] for r in events) for o in same_hyp)
    argv = [sys.executable, str(_TOOLS_DIR / "instincts.py"), "add", *instinct_args(reg, last, replicated)]
    if dry_run:
        argv.append("--dry-run")
    proc = runner(argv, capture_output=True, text=True, encoding="utf-8")
    ok = proc.returncode == 0
    if ok and not dry_run:
        append_event(path, {"event": "promoted", "id": exp_id, "instinct_id": argv[argv.index("--id") + 1]})
    return {"id": exp_id, "ok": ok, "dry_run": dry_run, "replicated": replicated, "argv": argv[2:], "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}


def build_packet(reg: dict, kind: str, budget_note: str = "") -> dict:
    if kind not in PACKET_KINDS:
        raise ExperimentError(f"kind: {', '.join(PACKET_KINDS)}")
    return {
        "schema": "change-packet.v1", "kind": f"experiment_{kind}", "experiment_id": reg["id"], "entity": reg["id"],
        "platform": "meta", "proposed_tool": PACKET_KINDS[kind], "auto_created": False,
        "proposal": {"name": reg["name"], "hypothesis": reg["hypothesis"], "primary_metric": reg["metric"], "variants": reg["variants"],
                     "n_per_arm": reg["n_per_arm"], "alpha": reg["alpha"], "power": reg["power"], "start": reg["start"]},
        "baseline": {"rate": reg["baseline"], "mde_relative": reg["mde_relative"]},
        "risk": "Test byudjetining bir qismini kamroq samarali variantga yo'naltiradi; tasdiqlanmagan testni boshlamang." + (" " + budget_note if budget_note else ""),
        "stop_loss": "Variant CPA nazoratdan 2x yomon bo'lsa va har guruhda >=30 konversiya bo'lsa to'xtatish uchun taklif qiling (tasdiq bilan).",
        "rollback": "Rasmiy Meta MCP'da undo yo'q: testni to'xtating (ads_update_entity status), asl byudjet taqsimotini qaytaring, faollik jurnalini (ads_account_get_activity_logs) saqlang.",
        "approved_by_user": False, "approved_at": None, "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "synthetic": bool(reg.get("synthetic")),
        "note": "Bu faqat taklif: Tyrion testni avto-yaratmaydi. Spend-Guard tekshiruvi va foydalanuvchi tasdig'idan keyin yozish asbobi chaqiriladi.",
    }


# ───────────────────────────── CLI ─────────────────────────────
def _emit(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tyrion Experiments — dizayn, ledger, readout")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def client_args(p):
        p.add_argument("--client", required=True)
        p.add_argument("--clients-dir", default=str(ROOT / "clients"))

    d = sub.add_parser("design")
    d.add_argument("--baseline", required=True)
    d.add_argument("--mde", help="nisbiy MDE (0.2 = +20%%)")
    d.add_argument("--mde-abs", help="mutlaq MDE (0.01 = +1 p.p.)")
    d.add_argument("--alpha", default="0.05")
    d.add_argument("--power", default="0.8")
    d.add_argument("--arms", default="2")
    d.add_argument("--unit", default="click")
    d.add_argument("--cost-per-unit")
    d.add_argument("--daily-budget")
    d.add_argument("--target-cpa")
    d.add_argument("--currency", default="USD")

    r = sub.add_parser("register")
    client_args(r)
    r.add_argument("--name", required=True)
    r.add_argument("--hypothesis", required=True)
    r.add_argument("--metric", required=True)
    r.add_argument("--baseline", required=True)
    r.add_argument("--mde", required=True)
    r.add_argument("--n-per-arm", required=True)
    r.add_argument("--alpha", default="0.05")
    r.add_argument("--power", default="0.8")
    r.add_argument("--variants", default="control,variant")
    r.add_argument("--owner", default="")
    r.add_argument("--start")
    r.add_argument("--domain", default="meta", choices=DOMAINS)
    r.add_argument("--synthetic", action="store_true")

    o = sub.add_parser("readout")
    o.add_argument("--client")
    o.add_argument("--clients-dir", default=str(ROOT / "clients"))
    o.add_argument("--id")
    o.add_argument("--control-n", required=True)
    o.add_argument("--control-conv", required=True)
    o.add_argument("--variant-n", required=True)
    o.add_argument("--variant-conv", required=True)
    o.add_argument("--alpha")
    o.add_argument("--seed", type=int, default=7)

    pr = sub.add_parser("promote")
    client_args(pr)
    pr.add_argument("--id", required=True)
    pr.add_argument("--dry-run", action="store_true")

    pk = sub.add_parser("packet")
    client_args(pk)
    pk.add_argument("--id", required=True)
    pk.add_argument("--kind", required=True, choices=list(PACKET_KINDS))
    pk.add_argument("--stdout", action="store_true", help="faylga yozmasdan chiqarish")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "design":
            _emit(design(args.baseline, args.mde, args.mde_abs, args.alpha, args.power, args.arms, args.unit,
                         args.cost_per_unit, args.daily_budget, args.target_cpa, args.currency))
        elif args.cmd == "register":
            _emit(register(ledger_path(args.clients_dir, args.client), args.name, args.hypothesis, args.metric, args.baseline, args.mde,
                           args.n_per_arm, float(_num(args.alpha, "alpha", positive=True)), float(_num(args.power, "power", positive=True)),
                           [v.strip() for v in args.variants.split(",") if v.strip()], args.owner, args.start, args.domain, args.synthetic))
        elif args.cmd == "readout":
            path = ledger_path(args.clients_dir, args.client) if args.client and args.id else None
            if args.id and not args.client:
                raise ExperimentError("--id uchun --client ham kerak")
            _emit(do_readout(path, args.id, args.control_n, args.control_conv, args.variant_n, args.variant_conv,
                             None if args.alpha is None else _num(args.alpha, "alpha", positive=True), args.seed))
        elif args.cmd == "promote":
            res = promote(ledger_path(args.clients_dir, args.client), args.id, dry_run=args.dry_run)
            _emit(res)
            return tcore.EXIT_OK if res["ok"] else tcore.EXIT_VALIDATION
        elif args.cmd == "packet":
            reg = find_experiment(read_ledger(ledger_path(args.clients_dir, args.client)), args.id)
            pkt = build_packet(reg, args.kind)
            if not args.stdout:
                out = Path(args.clients_dir) / tcore.safe_slug(args.client) / "changes" / f"{args.id}-{args.kind}.json"
                tcore.atomic_write_json(out, pkt)
                pkt["written_to"] = str(out)
            _emit(pkt)
    except ExperimentError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return tcore.EXIT_VALIDATION
    return tcore.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
