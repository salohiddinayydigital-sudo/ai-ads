#!/usr/bin/env python3
"""crm-bridge.py — CRM lid sifati → Meta CAPI (Lead Quality Loop). Stdlib, 0 token.

Kirish: AmoCRM JSON, Bitrix24 JSON, generic/Google Sheets CSV.
Buyruqlar:
  report  --input F --format amocrm|bitrix24|csv --stage-map M.json   lead→qualified hisoboti
  payload --input F ... [--out P.json]                                 CAPI batch (dry-run, standart)
  send    --input F ... --dataset-id ID --confirm                      faqat --confirm + env META_CAPI_TOKEN

Xavfsizlik: PII (telefon, email, ism) hech qachon chop etilmaydi/log qilinmaydi — faqat SHA-256 xeshlar
payload'da. Consent yo'q lidlar tashlanadi. Standart rejim dry-run.

source_status: unverified — `action_source: "system_generated"` va `custom_data.lead_event_source`/
`event_source: "CRM"` maydonlari Meta rasmiy "Conversion Leads / CRM events" hujjatidan bu muhitda
tasdiqlanmadi (developers.facebook.com ochilmaydi); ishlatishdan oldin hujjat bilan solishtiring.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

STAGES = ["Lead", "QualifiedLead", "Appointment", "Shown", "Purchase"]
EVENT_NAMES = {"Lead": "Lead", "QualifiedLead": "QualifiedLead", "Appointment": "Schedule", "Shown": "Shown", "Purchase": "Purchase"}
ACTION_SOURCE = "system_generated"  # unverified, modul docstring'iga qarang
TRUE = {"1", "true", "yes", "ha", "да", "y", "granted"}


def _load_capi():
    spec = importlib.util.spec_from_file_location("capi_utm_builder", TOOLS / "capi-utm-builder.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256_norm(val: str) -> str:
    return hashlib.sha256((val or "").strip().lower().encode("utf-8")).hexdigest()


def normalize_phone(phone: str) -> str:
    """Faqat raqamlar; +998 / 998 / 9 xonali mahalliy / 0-bilan boshlanuvchi formatlar → 998XXXXXXXXX."""
    d = re.sub(r"\D+", "", str(phone or ""))
    if d.startswith("00"):
        d = d[2:]
    if len(d) == 10 and d.startswith("0"):
        d = d[1:]
    if len(d) == 9:
        d = "998" + d
    return d


def _custom(fields: list, *keys: str) -> str:
    for f in fields or []:
        k = str(f.get("field_code") or f.get("field_name") or "").lower()
        if k in keys:
            vals = f.get("values") or []
            if vals:
                return str(vals[0].get("value", ""))
    return ""


def parse_amocrm(data: dict) -> list[dict]:
    leads = (data.get("_embedded") or {}).get("leads") or data.get("leads") or []
    out = []
    for l in leads:
        cf = l.get("custom_fields_values") or []
        out.append({
            "lead_id": str(l.get("id", "")), "stage": str(l.get("status_id", l.get("status", ""))),
            "value": float(l.get("price") or 0), "phone": _custom(cf, "phone"), "email": _custom(cf, "email"),
            "first_name": str(l.get("name", "")).split(" ")[0], "city": _custom(cf, "city"),
            "consent": _custom(cf, "consent"), "campaign": _custom(cf, "utm_campaign"),
            "adset": _custom(cf, "utm_term"), "ad": _custom(cf, "utm_content"), "form": _custom(cf, "form"),
            "event_time": int(l.get("updated_at") or l.get("created_at") or 0),
            "meta_lead_id": _custom(cf, "meta_lead_id"),
        })
    return out


def parse_bitrix24(data: dict) -> list[dict]:
    rows = data.get("result") or []
    first = lambda arr: str((arr or [{}])[0].get("VALUE", ""))  # noqa: E731
    out = []
    for r in rows:
        out.append({
            "lead_id": str(r.get("ID", "")), "stage": str(r.get("STAGE_ID") or r.get("STATUS_ID") or ""),
            "value": float(r.get("OPPORTUNITY") or 0), "phone": first(r.get("PHONE")), "email": first(r.get("EMAIL")),
            "first_name": str(r.get("NAME", "")), "city": str(r.get("CITY", "")),
            "consent": str(r.get("UF_CRM_CONSENT", "")), "campaign": str(r.get("UTM_CAMPAIGN", "")),
            "adset": str(r.get("UTM_TERM", "")), "ad": str(r.get("UTM_CONTENT", "")), "form": str(r.get("UF_CRM_FORM", "")),
            "event_time": int(r.get("UF_CRM_EVENT_TS") or 0), "meta_lead_id": str(r.get("UF_CRM_META_LEAD_ID", "")),
        })
    return out


def parse_csv(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            r = {str(k).strip().lower(): (v or "").strip() for k, v in r.items() if k}
            try:
                value = float(r.get("value") or 0)
            except ValueError:
                value = 0.0
            out.append({
                "lead_id": r.get("lead_id", ""), "stage": r.get("stage", ""), "value": value,
                "phone": r.get("phone", ""), "email": r.get("email", ""), "first_name": r.get("first_name", ""),
                "city": r.get("city", ""), "consent": r.get("consent", ""), "campaign": r.get("campaign", ""),
                "adset": r.get("adset", ""), "ad": r.get("ad", ""), "form": r.get("form", ""),
                "event_time": int(float(r.get("event_time") or 0)), "meta_lead_id": r.get("meta_lead_id", ""),
            })
    return out


def load_leads(path: Path, fmt: str) -> list[dict]:
    if fmt == "csv":
        return parse_csv(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return parse_amocrm(data) if fmt == "amocrm" else parse_bitrix24(data)


def apply_stage_map(leads: list[dict], stage_map: dict) -> list[dict]:
    """CRM bosqichini kanonik bosqichga (STAGES) o'giradi; xaritada yo'qlari 'unmapped' bo'ladi."""
    out = []
    for l in leads:
        s = stage_map.get(l["stage"], stage_map.get(str(l["stage"]).lower()))
        l = dict(l)
        l["canon"] = s if s in STAGES else None
        out.append(l)
    return out


def build_payload(leads: list[dict], currency: str = "UZS") -> dict:
    """CAPI batch. Dedup: event_id = crm_<lead_id>_<Event>. Consent yo'q → tashlanadi. PII faqat xesh."""
    events, seen, skipped = [], set(), defaultdict(int)
    for l in leads:
        if l.get("canon") is None:
            skipped["unmapped_stage"] += 1
            continue
        if str(l.get("consent", "")).strip().lower() not in TRUE:
            skipped["no_consent"] += 1
            continue
        name = EVENT_NAMES[l["canon"]]
        eid = f"crm_{re.sub(r'[^A-Za-z0-9]+', '', l['lead_id'])}_{name}"
        if eid in seen:
            skipped["duplicate"] += 1
            continue
        ud: dict = {}
        ph = normalize_phone(l.get("phone", ""))
        if ph:
            ud["ph"] = [sha256_norm(ph)]
        if l.get("email"):
            ud["em"] = [sha256_norm(l["email"])]
        if l.get("first_name"):
            ud["fn"] = [sha256_norm(l["first_name"])]
        if l.get("city"):
            ud["ct"] = [sha256_norm(l["city"])]
        ud["country"] = [sha256_norm("uz")]
        if l.get("meta_lead_id"):
            ud["lead_id"] = l["meta_lead_id"]
        if len(ud) <= 1:
            skipped["no_identifiers"] += 1
            continue
        seen.add(eid)
        ev = {
            "event_name": name, "event_time": int(l.get("event_time") or 0), "action_source": ACTION_SOURCE,
            "event_id": eid, "user_data": ud,
            "custom_data": {"lead_event_source": "CRM", "event_source": "crm", "stage": l["canon"]},
        }
        if l["canon"] == "Purchase" or l["value"]:
            ev["custom_data"].update({"value": round(l["value"], 2), "currency": currency})
        events.append(ev)
    return {"synthetic_note": "dry-run; PII xeshlangan", "data": events, "skipped": dict(skipped),
            "source_status": "unverified"}


def report(leads: list[dict]) -> dict:
    out: dict = {"label": "MEASURED_ACCOUNT_DATA (CRM eksporti)", "totals": {}}
    qual_set = {"QualifiedLead", "Appointment", "Shown", "Purchase"}

    def agg(key: str) -> list[dict]:
        g: dict = defaultdict(lambda: {"leads": 0, "qualified": 0, "purchases": 0, "revenue": 0.0})
        for l in leads:
            if l.get("canon") is None:
                continue
            b = g[l.get(key) or "(yo'q)"]
            b["leads"] += 1
            b["qualified"] += l["canon"] in qual_set
            if l["canon"] == "Purchase":
                b["purchases"] += 1
                b["revenue"] += l["value"]
        rows = []
        for k, b in sorted(g.items()):
            rows.append({key: k, **b, "revenue": round(b["revenue"], 2),
                         "lead_to_qualified": round(b["qualified"] / b["leads"], 4) if b["leads"] else None})
        return rows

    for dim in ("campaign", "adset", "ad", "form"):
        out[f"by_{dim}"] = agg(dim)
    n = sum(1 for l in leads if l.get("canon"))
    q = sum(1 for l in leads if l.get("canon") in qual_set)
    out["totals"] = {"leads": n, "qualified": q, "lead_to_qualified": round(q / n, 4) if n else None,
                     "unmapped": sum(1 for l in leads if not l.get("canon"))}
    return out


def send(payload: dict, dataset_id: str, version: str = "v26.0") -> dict:
    token = os.environ.get("META_CAPI_TOKEN", "")
    if not token:
        return {"error": "META_CAPI_TOKEN env o'rnatilmagan"}
    body = json.dumps({"data": payload["data"]}).encode()
    req = urllib.request.Request(f"https://graph.facebook.com/{version}/{dataset_id}/events?access_token={token}",
                                 data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310
            return {"status": r.status, "events_sent": len(payload["data"])}
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        return {"error": f"tarmoq: {type(e.reason).__name__}"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="CRM → Meta CAPI lid sifati ko'prigi")
    ap.add_argument("cmd", choices=["report", "payload", "send"])
    ap.add_argument("--input", required=True)
    ap.add_argument("--format", choices=["amocrm", "bitrix24", "csv"], default="csv")
    ap.add_argument("--stage-map", required=True, help="JSON: CRM bosqich → Lead|QualifiedLead|Appointment|Shown|Purchase")
    ap.add_argument("--currency", default="UZS")
    ap.add_argument("--out")
    ap.add_argument("--dataset-id")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args(argv)
    try:
        leads = apply_stage_map(load_leads(Path(a.input), a.format), json.loads(Path(a.stage_map).read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError) as e:
        print(f"xato: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if a.cmd == "report":
        print(json.dumps(report(leads), ensure_ascii=False, indent=2))
        return 0
    payload = build_payload(leads, a.currency)
    if a.cmd == "payload" or not a.confirm:
        if a.cmd == "send":
            payload["dry_run"] = True
            payload["note"] = "--confirm berilmadi: yuborilmadi"
        if a.out:
            Path(a.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if not a.dataset_id:
        print("xato: --dataset-id kerak", file=sys.stderr)
        return 2
    res = send(payload, a.dataset_id)
    print(json.dumps(res))
    return 2 if "error" in res else 0


if __name__ == "__main__":
    sys.exit(main())
