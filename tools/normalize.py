#!/usr/bin/env python3
"""normalize.py — turli manbalarni `metrics.v1` (schemas/metrics.v1.json) formatiga keltiradi.

Adapterlar: meta_mcp · meta_graph · google_ads · tiktok_csv · telegram_csv · generic_csv

    python3 tools/normalize.py meta_graph --input raw.json --out metrics.json [--level ad] [--account-id act_1] [--currency USD]
    python3 tools/normalize.py generic_csv --input export.csv --platform meta --currency UZS --date 2026-11-01
    python3 tools/normalize.py validate metrics.json
    python3 tools/normalize.py list

Chiqish kodlari: 0 muvaffaqiyat · 2 xato (JSON `{"error":..., "unmapped_columns":[...]}` stdout'ga yoziladi).
Noma'lum maydonlar xatoga olib kelmaydi: ular `unmapped_columns` ro'yxatiga tushadi. Valyuta, sana yoki
sarf aniqlanmasa, taxmin qilinmaydi (xato). `--synthetic` yoki xom fayldagi `"synthetic": true` -> har qator
`synthetic: true`, `evidence_label: UNVERIFIED`; aks holda `MEASURED_ACCOUNT_DATA`.

Manba holati (source_status):
- meta_graph — Graph API insights formati (`spend`, `actions`, `action_values`, `date_start`) repo kodidan
  (`meta-insights-sync.py`) olingan: verified-in-repo. `video_view` (3s) va `video_thruplay_watched_actions`
  maydonlari: source_status: unverified (repo'da yo'q; developers.facebook.com bu muhitda tekshirilmagan).
- meta_mcp — rasmiy Meta Ads MCP javob shakli: source_status: unverified. Adapter Graph-mos maydonlarni
  (`data|rows|entities|results` o'rami, `date|date_start`, `entity_id|*_id`) qabul qiladi.
- google_ads — GAQL natijalari (`metrics.cost_micros`, `segments.date`, `campaign.id`, camelCase yoki snake_case):
  source_status: unverified (developers.google.com bu muhitda tekshirilmagan).
- tiktok_csv, telegram_csv — ustun nomlari: source_status: unverified; sarlavha taxalluslari tolerant.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from datetime import date as _date
from datetime import datetime
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

SCHEMA_PATH = ROOT / "schemas" / "metrics.v1.json"
SCHEMA_ID = "metrics.v1"
ADAPTERS = ("meta_mcp", "meta_graph", "google_ads", "tiktok_csv", "telegram_csv", "generic_csv")
SOURCES = ("meta_mcp", "meta_graph", "google_mcp", "csv", "screenshot")


class NormalizeError(ValueError):
    """Aniq xato; `unmapped` — tushunilmagan ustunlar."""

    def __init__(self, message: str, unmapped: list[str] | None = None):
        super().__init__(message)
        self.unmapped = list(unmapped or [])


# --------------------------------------------------------------------------- lazy sibling imports
_ANALYZER = None
_SYNC = None


def _analyzer():
    global _ANALYZER
    if _ANALYZER is None:
        _ANALYZER = importlib.import_module("ad-export-analyzer")
    return _ANALYZER


def _sync():
    global _SYNC
    if _SYNC is None:
        _SYNC = importlib.import_module("meta-insights-sync")
    return _SYNC


# --------------------------------------------------------------------------- umumiy yordamchilar
def num(value: Any) -> float | None:
    """Son yoki None (bo'sh, '-', tushunilmagan). bool qabul qilinmaydi."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        f = float(value)
        return f if f == f and f not in (float("inf"), float("-inf")) else None
    s = str(value).strip()
    if not s or s in {"-", "--", "—", "n/a", "N/A", "null", "None"}:
        return None
    s = s.rstrip("%").strip()
    parsed = tcore.parse_localized_number(s)
    return parsed


def _nonneg(value: float | None, where: str, field: str) -> float | None:
    if value is not None and value < 0:
        raise NormalizeError(f"{where}: {field} manfiy bo'lolmaydi ({value})")
    return value


_DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y", "%m/%d/%Y", "%Y%m%d")


def parse_date(raw: Any) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = re.match(r"^(\d{4}-\d{2}-\d{2})(?:[T ].*)?$", s)
    if m:
        s = m.group(1)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _num_str(x: float) -> float | int:
    return int(x) if float(x).is_integer() else round(x, 6)


def _clean_num(x: float | None) -> float | int | None:
    return None if x is None else _num_str(x)


def _envelope(raw: Any, keys: tuple[str, ...]) -> tuple[list[Any], bool]:
    """Xom JSON'dan satrlar ro'yxati va `synthetic` bayrog'ini ajratadi."""
    synthetic = False
    if isinstance(raw, dict):
        synthetic = raw.get("synthetic") is True
        for k in keys:
            if isinstance(raw.get(k), list):
                return raw[k], synthetic
        return [raw], synthetic
    if isinstance(raw, list):
        # Google searchStream: [{"results":[...]}, ...]
        if raw and all(isinstance(b, dict) and isinstance(b.get("results"), list) for b in raw):
            out: list[Any] = []
            for b in raw:
                out.extend(b["results"])
            return out, False
        return raw, False
    raise NormalizeError("Xom JSON ildizi ro'yxat yoki obyekt bo'lishi shart.")


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise NormalizeError(f"Fayl topilmadi: {path}")
    if path.stat().st_size > tcore.MAX_FILE_BYTES:
        raise NormalizeError(f"Fayl 25 MB dan katta: {path}")
    if path.stat().st_size == 0:
        raise NormalizeError(f"Fayl bo'sh: {path}")
    try:
        return json.loads(path.read_bytes().decode("utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise NormalizeError(f"JSON o'qib bo'lmadi ({path.name}): {exc}") from None


def _labels(synthetic: bool) -> tuple[str, bool]:
    return ("UNVERIFIED", True) if synthetic else ("MEASURED_ACCOUNT_DATA", False)


def _base_row(*, date: str, platform: str, account_id: str, level: str, entity_id: str, entity_name: str,
              spend: float, currency: str, source: str, synthetic: bool) -> dict[str, Any]:
    label, syn = _labels(synthetic)
    return {
        "date": date, "platform": platform, "account_id": account_id, "level": level,
        "entity_id": entity_id, "entity_name": entity_name, "spend": _num_str(round(spend, 6)),
        "currency": currency, "source": source, "evidence_label": label, "synthetic": syn,
    }


def _set_opt(row: dict, key: str, value: float | None) -> None:
    if value is not None:
        row[key] = _clean_num(value)


def _finish(rows: list[dict], unmapped: set[str] | list[str], skipped: int = 0, synthetic: bool = False) -> dict:
    doc: dict[str, Any] = {"schema": SCHEMA_ID, "rows": rows}
    if synthetic or (rows and all(r.get("synthetic") for r in rows)):
        doc["synthetic"] = True
    doc["unmapped_columns"] = sorted(unmapped)
    if skipped:
        doc["skipped_rows"] = skipped
    return doc


# --------------------------------------------------------------------------- Meta (graph + mcp)
_META_KNOWN = {
    "account_id", "account_currency", "currency", "date_start", "date_stop", "date", "level", "ad_id", "ad_name",
    "adset_id", "adset_name", "campaign_id", "campaign_name", "entity_id", "entity_name", "id", "name", "spend",
    "impressions", "reach", "frequency", "clicks", "inline_link_clicks", "actions", "action_values",
    "video_thruplay_watched_actions", "video_3_sec_watched_actions", "conversions", "revenue", "conversion_value",
    "synthetic",
}


def _action_list(row: dict, key: str) -> list | None:
    v = row.get(key)
    return v if isinstance(v, list) else None


def _action_value(items: list | None, action_type: str) -> float | None:
    if not items:
        return None
    for it in items:
        if isinstance(it, dict) and str(it.get("action_type", "")).strip() == action_type:
            return num(it.get("value"))
    return None


def _expand_meta_rows(rows: list[Any]) -> list[dict]:
    """MCP entity-o'ramlari: {"id","name","level","insights":{"data":[...]}} -> tekis insights qatorlari."""
    out: list[dict] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        ins = r.get("insights")
        data = ins.get("data") if isinstance(ins, dict) else ins if isinstance(ins, list) else None
        if isinstance(data, list):
            for d in data:
                if isinstance(d, dict):
                    merged = {k: v for k, v in r.items() if k != "insights"}
                    merged.update(d)
                    out.append(merged)
        else:
            out.append(r)
    return out


def normalize_meta(raw: Any, *, source: str, level: str | None = None, account_id: str | None = None,
                   currency: str | None = None, synthetic: bool = False) -> dict:
    sync = _sync()
    rows_in, env_syn = _envelope(raw, ("data", "rows", "entities", "results", "insights"))
    rows_in = _expand_meta_rows(rows_in)
    synthetic = synthetic or env_syn
    if level and level not in ("campaign", "adset", "ad"):
        raise NormalizeError(f"Noto'g'ri level: {level!r} (campaign|adset|ad)")
    out: list[dict] = []
    unmapped: set[str] = set()
    for idx, r in enumerate(rows_in, 1):
        where = f"qator {idx}"
        unmapped.update(k for k in r if k not in _META_KNOWN)
        date = parse_date(r.get("date_start") or r.get("date"))
        if not date:
            raise NormalizeError(f"{where}: sana (date_start/date) yo'q yoki noto'g'ri")
        spend = _nonneg(num(r.get("spend")), where, "spend")
        if spend is None:
            raise NormalizeError(f"{where}: spend yo'q")
        ccy = str(r.get("account_currency") or r.get("currency") or currency or "").strip().upper()
        if not ccy:
            raise NormalizeError(f"{where}: valyuta aniqlanmadi (--currency bering yoki account_currency maydoni kerak)")
        lvl = level or (r.get("level") if r.get("level") in ("campaign", "adset", "ad") else None)
        if not lvl:
            lvl = "ad" if r.get("ad_id") else "adset" if r.get("adset_id") else "campaign"
        id_key, name_key = {"ad": ("ad_id", "ad_name"), "adset": ("adset_id", "adset_name"),
                            "campaign": ("campaign_id", "campaign_name")}[lvl]
        eid = str(r.get(id_key) or r.get("entity_id") or r.get("id") or "").strip()
        if not eid:
            raise NormalizeError(f"{where}: entity ID ({id_key}/entity_id) yo'q")
        ename = str(r.get(name_key) or r.get("entity_name") or r.get("name") or "").strip()
        row = _base_row(date=date, platform="meta", account_id=str(r.get("account_id") or account_id or "unknown"),
                        level=lvl, entity_id=eid, entity_name=ename, spend=spend, currency=ccy,
                        source=source, synthetic=synthetic)
        actions = _action_list(r, "actions")
        impressions = _nonneg(num(r.get("impressions")), where, "impressions")
        reach = _nonneg(num(r.get("reach")), where, "reach")
        freq = _nonneg(num(r.get("frequency")), where, "frequency")
        if freq is None and reach and impressions:
            freq = round(impressions / reach, 4)
        link_clicks = _nonneg(num(r.get("inline_link_clicks")), where, "inline_link_clicks")
        if link_clicks is None:
            link_clicks = _action_value(actions, "link_click")
        _set_opt(row, "impressions", impressions)
        _set_opt(row, "reach", reach)
        _set_opt(row, "frequency", freq)
        _set_opt(row, "clicks", _nonneg(num(r.get("clicks")), where, "clicks"))
        _set_opt(row, "link_clicks", link_clicks)
        v3 = _action_value(actions, "video_view")
        if v3 is None:
            v3 = _action_value(_action_list(r, "video_3_sec_watched_actions"), "video_view")
        _set_opt(row, "video_3s", v3)
        _set_opt(row, "thruplay", _action_value(_action_list(r, "video_thruplay_watched_actions"), "video_view"))
        conv: dict[str, float | int] = {}
        for fam, keys in sync.CONVERSION_FAMILIES.items():
            val, _t = sync._extract_action_metric(actions, keys)
            if val > 0:
                conv[fam.lower()] = _num_str(val)
        if not conv:
            direct = num(r.get("conversions")) if not isinstance(r.get("conversions"), list) else None
            if direct and direct > 0:
                conv["conversion"] = _num_str(direct)
        if conv:
            row["conversions"] = conv
        rev, _t = sync._extract_action_metric(_action_list(r, "action_values"), sync.REVENUE_ACTION_PRIORITY)
        if not rev:
            rev = num(r.get("conversion_value")) or num(r.get("revenue")) or 0.0
        if rev:
            row["conversion_value"] = _num_str(_nonneg(rev, where, "conversion_value") or 0)
        out.append(row)
    return _finish(out, unmapped, synthetic=synthetic)


# --------------------------------------------------------------------------- Google Ads (GAQL)
def _snake(s: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def _flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{_snake(str(k))}" if prefix else _snake(str(k))
            if isinstance(v, dict):
                flat.update(_flatten(v, key))
            else:
                flat[key] = v
    return flat


_GADS_KNOWN = {
    "customer.id", "customer.currency_code", "campaign.id", "campaign.name", "ad_group.id", "ad_group.name",
    "ad_group_ad.ad.id", "ad_group_ad.ad.name", "segments.date", "metrics.cost_micros", "metrics.impressions",
    "metrics.clicks", "metrics.conversions", "metrics.all_conversions", "metrics.conversions_value",
    "metrics.all_conversions_value", "metrics.video_views", "synthetic",
}
# resource_name va ierarxiya ID'lari xato emas — tanilgan, ammo ishlatilmaydi
_GADS_IGNORED = {"resource_name"}
_GADS_DERIVED = {"metrics.ctr", "metrics.average_cpc", "metrics.average_cpm", "metrics.cost_per_conversion",
                 "metrics.conversions_from_interactions_rate"}  # hosila: tanilgan, qayta hisoblanadi


def normalize_google_ads(raw: Any, *, level: str | None = None, account_id: str | None = None,
                         currency: str | None = None, synthetic: bool = False) -> dict:
    rows_in, env_syn = _envelope(raw, ("results", "rows", "data"))
    synthetic = synthetic or env_syn
    out: list[dict] = []
    unmapped: set[str] = set()
    for idx, r in enumerate(rows_in, 1):
        if not isinstance(r, dict):
            continue
        f = _flatten(r)
        where = f"qator {idx}"
        for k in f:
            if k not in _GADS_KNOWN and k not in _GADS_DERIVED and k.rsplit(".", 1)[-1] not in _GADS_IGNORED:
                unmapped.add(k)
        date = parse_date(f.get("segments.date"))
        if not date:
            raise NormalizeError(f"{where}: segments.date yo'q yoki noto'g'ri (GAQL so'roviga segments.date qo'shing)", sorted(unmapped))
        micros = _nonneg(num(f.get("metrics.cost_micros")), where, "metrics.cost_micros")
        if micros is None:
            raise NormalizeError(f"{where}: metrics.cost_micros yo'q", sorted(unmapped))
        has_ad = "ad_group_ad.ad.id" in f
        has_ag = "ad_group.id" in f
        lvl = level or ("ad" if has_ad else "adset" if has_ag else "campaign")
        id_key, name_key = {"ad": ("ad_group_ad.ad.id", "ad_group_ad.ad.name"), "adset": ("ad_group.id", "ad_group.name"),
                            "campaign": ("campaign.id", "campaign.name")}[lvl]
        eid = str(f.get(id_key) or "").strip()
        if not eid:
            raise NormalizeError(f"{where}: {id_key} yo'q (level={lvl})", sorted(unmapped))
        ccy = str(f.get("customer.currency_code") or currency or "").strip().upper()
        if not ccy:
            raise NormalizeError(f"{where}: valyuta aniqlanmadi (customer.currency_code yoki --currency)", sorted(unmapped))
        row = _base_row(date=date, platform="google", account_id=str(f.get("customer.id") or account_id or "unknown"),
                        level=lvl, entity_id=eid, entity_name=str(f.get(name_key) or ""), spend=micros / 1_000_000,
                        currency=ccy, source="google_mcp", synthetic=synthetic)
        for src, dst in (("metrics.impressions", "impressions"), ("metrics.clicks", "clicks")):
            _set_opt(row, dst, _nonneg(num(f.get(src)), where, src))
        conv = num(f.get("metrics.conversions"))
        if conv is None:
            conv = num(f.get("metrics.all_conversions"))
        if conv:
            row["conversions"] = {"conversion": _num_str(_nonneg(conv, where, "conversions") or 0)}
        val = num(f.get("metrics.conversions_value"))
        if val is None:
            val = num(f.get("metrics.all_conversions_value"))
        if val:
            row["conversion_value"] = _num_str(_nonneg(val, where, "conversions_value") or 0)
        out.append(row)
    return _finish(out, unmapped, synthetic=synthetic)


# --------------------------------------------------------------------------- CSV adapterlari
# kalit = ad-export-analyzer.normalize_header() chiqishi (registr/qavs/valyuta olib tashlangan)
_EXTRA_HEADERS: dict[str, tuple[str, str | None]] = {}


def _reg(field: str, event: str | None, *keys: str) -> None:
    for k in keys:
        _EXTRA_HEADERS[k] = (field, event)


_reg("date", None, "date", "day", "reporting starts", "stat time day", "report date", "segments date", "date start", "дата", "день")
_reg("campaign_id", None, "campaign id")
_reg("adset_id", None, "ad set id", "adset id", "ad group id")
_reg("ad_id", None, "ad id")
_reg("entity_id", None, "id", "entity id")
_reg("reach", None, "reach", "охват")
_reg("link_clicks", None, "link clicks", "inline link clicks")
_reg("clicks", None, "clicks", "clicks all", "клики", "click")
_reg("video_3s", None, "3 second video plays", "3s video views", "video views 3s", "3 second video views", "video plays 3s")
_reg("thruplay", None, "thruplays", "thruplay", "video thruplay", "thru plays")
_reg("event", "purchase", "purchases", "purchase", "website purchases", "complete payment", "покупки", "заказы")
_reg("event", "lead", "leads", "lead", "website leads", "form submit", "лиды", "заявки")
_reg("event", "conversion", "conversions", "results", "conversion", "all conversions", "конверсии", "результаты")
_reg("event", "join", "joins", "subscribers", "new subscribers", "подписки", "подписчики")
_reg("event", "bot_start", "starts", "bot starts")
_reg("event", "messaging", "messages", "messaging conversations started")
_reg("conversion_value", None, "revenue", "purchase value", "conversion value", "purchases conversion value",
     "website purchases conversion value", "total conversion value", "complete payment value", "доход", "выручка",
     "ценность конверсий")
_reg("frequency", None, "frequency", "avg frequency", "частота")
_reg("currency", None, "currency", "account currency", "currency code", "валюта")
_reg("name", None, "name", "campaign name", "campaign", "ad set name", "adset name", "ad group name", "ad name",
     "ad title", "title", "название кампании", "кампания", "название объявления", "объявление", "название")
_reg("spend", None, "spend", "amount spent", "cost", "spent", "total spend", "расход", "расходы", "затраты", "потрачено")
_reg("impressions", None, "impressions", "impr", "views", "показы", "просмотры")
# Hosila ko'rsatkichlar: tanilgan, qayta hisoblanadi (unmapped emas)
_DERIVED = {"cpa", "cpm", "cpc", "ctr", "roas", "cost per result", "cost per conversion", "cost per purchase",
            "цена конверсии", "цена цели", "budget"}

_PLATFORM_DEFAULTS = {"tiktok_csv": ("tiktok", "campaign"), "telegram_csv": ("telegram", "ad"),
                      "generic_csv": ("generic", "campaign")}


def _resolve_header(h: str) -> tuple[str, str | None] | None:
    an = _analyzer()
    key, _ccy = an.normalize_header(h)
    if key in _EXTRA_HEADERS:
        return _EXTRA_HEADERS[key]
    hit = an._ALIAS_INDEX.get(key)
    if hit and hit[0] in ("name", "spend", "impressions", "clicks", "frequency", "revenue", "currency"):
        return ("conversion_value" if hit[0] == "revenue" else hit[0], None)
    if hit and hit[0] in ("purchases", "leads", "conversions"):
        return ("event", {"purchases": "purchase", "leads": "lead", "conversions": "conversion"}[hit[0]])
    if key in _DERIVED or (hit and hit[0] in ("cpa", "roas", "ctr", "cpm")):
        return ("derived", None)
    return None


def normalize_csv(path: Path, adapter: str, *, level: str | None = None, account_id: str | None = None,
                  currency: str | None = None, platform: str | None = None, default_date: str | None = None,
                  synthetic: bool = False) -> dict:
    an = _analyzer()
    try:
        rows_in = an.load_rows(path)
    except FileNotFoundError:
        raise NormalizeError(f"Fayl topilmadi: {path}") from None
    except ValueError as exc:  # ExportFormatError ham ValueError
        raise NormalizeError(str(exc)) from None
    if not rows_in:
        raise NormalizeError("CSV'da ma'lumot qatorlari yo'q.")
    default_platform, default_level = _PLATFORM_DEFAULTS[adapter]
    plat = (platform or default_platform).strip().lower()
    lvl_default = level or default_level
    if lvl_default not in ("campaign", "adset", "ad"):
        raise NormalizeError(f"Noto'g'ri level: {lvl_default!r} (campaign|adset|ad)")
    headers: list[str] = []
    for r in rows_in:
        for k in r:
            if k not in headers:
                headers.append(str(k))
    chosen: dict[str, str] = {}  # maydon (yoki event:<nom>) -> asl sarlavha
    colmap: dict[str, tuple[str, str | None]] = {}
    unmapped: list[str] = []
    spend_ccy: str | None = None
    for h in headers:
        res = _resolve_header(h)
        if res is None or not h.strip():
            if h.strip():
                unmapped.append(h)
            continue
        field, event = res
        if field == "derived":
            continue
        slot = f"event:{event}" if field == "event" else field
        if slot in chosen:
            unmapped.append(h)  # takroriy/noaniq ustun: birinchisi ishlatiladi
            continue
        chosen[slot] = h
        colmap[h] = (field, event)
        if field == "spend":
            spend_ccy = an.normalize_header(h)[1]
    if "spend" not in chosen:
        raise NormalizeError("Sarf (spend/cost/amount spent) ustuni topilmadi.", unmapped or headers)
    out: list[dict] = []
    skipped = 0
    for idx, r in enumerate(rows_in, 1):
        where = f"qator {idx}"
        vals = {slot: r.get(h) for slot, h in chosen.items()}
        name = str(vals.get("name") or "").strip()
        first_cell = str(next(iter(r.values()), "") or "").strip()
        if (name and an._TOTAL_ROW_RE.match(name)) or (first_cell and an._TOTAL_ROW_RE.match(first_cell)):
            skipped += 1
            continue
        raw_spend = vals.get("spend")
        spend = num(raw_spend)
        if spend is None:
            if raw_spend is None or str(raw_spend).strip() in ("", "-", "--"):
                skipped += 1
                continue
            raise NormalizeError(f"{where}: spend tushunilmadi: {raw_spend!r}", unmapped)
        _nonneg(spend, where, "spend")
        date = parse_date(vals.get("date")) if "date" in chosen else None
        if not date:
            date = parse_date(default_date)
        if not date:
            raise NormalizeError(f"{where}: sana ustuni yo'q yoki noto'g'ri (CSV'da Date ustuni kerak yoki --date bering)", unmapped)
        ccy = str(vals.get("currency") or "").strip().upper() or (spend_ccy or "") or (currency or "").strip().upper()
        if not ccy:
            raise NormalizeError(f"{where}: valyuta aniqlanmadi (sarlavhada '(UZS)', Currency ustuni yoki --currency)", unmapped)
        lvl = lvl_default
        id_slot = {"ad": "ad_id", "adset": "adset_id", "campaign": "campaign_id"}[lvl]
        eid = str(vals.get(id_slot) or vals.get("entity_id") or "").strip()
        if not eid:
            if not name:
                raise NormalizeError(f"{where}: entity ID ham, nom ham yo'q", unmapped)
            eid = tcore.safe_slug(name, fallback="entity", max_len=64)
        row = _base_row(date=date, platform=plat, account_id=account_id or "unknown", level=lvl, entity_id=eid,
                        entity_name=name, spend=spend, currency=ccy, source="csv", synthetic=synthetic)
        for fld in ("impressions", "reach", "frequency", "clicks", "link_clicks", "video_3s", "thruplay"):
            if fld in chosen:
                _set_opt(row, fld, _nonneg(num(vals.get(fld)), where, fld))
        if "frequency" not in row and row.get("reach") and row.get("impressions"):
            row["frequency"] = round(row["impressions"] / row["reach"], 4)
        conv: dict[str, float | int] = {}
        for slot in chosen:
            if slot.startswith("event:"):
                v = _nonneg(num(vals.get(slot)), where, slot)
                if v:
                    conv[slot.split(":", 1)[1]] = _num_str(v)
        if conv:
            row["conversions"] = conv
        cv = _nonneg(num(vals.get("conversion_value")), where, "conversion_value") if "conversion_value" in chosen else None
        if cv:
            row["conversion_value"] = _num_str(cv)
        out.append(row)
    if not out:
        raise NormalizeError("Hech bir yaroqli qator topilmadi (hammasi jami/bo'sh qator).", unmapped)
    return _finish(out, unmapped, skipped, synthetic)


# --------------------------------------------------------------------------- dispatcher
def normalize(adapter: str, input_path: Path, **opts: Any) -> dict:
    if adapter not in ADAPTERS:
        raise NormalizeError(f"Noma'lum adapter: {adapter!r} ({', '.join(ADAPTERS)})")
    synthetic = bool(opts.get("synthetic"))
    if adapter in ("meta_mcp", "meta_graph"):
        return normalize_meta(_load_json(input_path), source=adapter, level=opts.get("level"),
                              account_id=opts.get("account_id"), currency=opts.get("currency"), synthetic=synthetic)
    if adapter == "google_ads":
        return normalize_google_ads(_load_json(input_path), level=opts.get("level"),
                                    account_id=opts.get("account_id"), currency=opts.get("currency"), synthetic=synthetic)
    return normalize_csv(input_path, adapter, level=opts.get("level"), account_id=opts.get("account_id"),
                         currency=opts.get("currency"), platform=opts.get("platform"),
                         default_date=opts.get("date"), synthetic=synthetic)


# --------------------------------------------------------------------------- minimal JSON-Schema validator (stdlib)
def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _resolve_ref(ref: str, root: dict) -> dict:
    node: Any = root
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def _check(value: Any, schema: dict, root: dict, path: str, errs: list[str]) -> None:
    if "$ref" in schema:
        schema = _resolve_ref(schema["$ref"], root)
    t = schema.get("type")
    if t:
        ok = {
            "object": isinstance(value, dict), "array": isinstance(value, list), "string": isinstance(value, str),
            "boolean": isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool) and value == value,
        }.get(t, True)
        if not ok:
            errs.append(f"{path}: {t} kutilgan, {type(value).__name__} keldi")
            return
    if "const" in schema and value != schema["const"]:
        errs.append(f"{path}: {schema['const']!r} bo'lishi shart")
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} ruxsat etilgan qiymatlardan emas ({', '.join(map(str, schema['enum']))})")
    if "minimum" in schema and isinstance(value, (int, float)) and not isinstance(value, bool) and value < schema["minimum"]:
        errs.append(f"{path}: {value} < {schema['minimum']}")
    if "pattern" in schema and isinstance(value, str) and not re.search(schema["pattern"], value):
        errs.append(f"{path}: {value!r} namunaga mos emas")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errs.append(f"{path}: majburiy maydon yo'q: {req}")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for k, v in value.items():
            if k in props:
                _check(v, props[k], root, f"{path}.{k}", errs)
            elif isinstance(extra, dict):
                _check(v, extra, root, f"{path}.{k}", errs)
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            _check(v, schema["items"], root, f"{path}[{i}]", errs)


def validate_metrics(doc: Any) -> list[str]:
    """`metrics.v1` hujjatini (yoki yalang qatorlar ro'yxatini) tekshiradi. Xatolar ro'yxati; bo'sh = to'g'ri."""
    schema = _load_schema()
    if isinstance(doc, list):
        doc = {"schema": SCHEMA_ID, "rows": doc}
    errs: list[str] = []
    _check(doc, schema, schema, "$", errs)
    if isinstance(doc, dict) and isinstance(doc.get("rows"), list):
        for i, r in enumerate(doc["rows"]):
            if isinstance(r, dict) and isinstance(r.get("date"), str) and re.match(r"^\d{4}-\d{2}-\d{2}$", r["date"]):
                try:
                    _date.fromisoformat(r["date"])
                except ValueError:
                    errs.append(f"$.rows[{i}].date: mavjud bo'lmagan sana {r['date']!r}")
    return errs


def rows_of(doc: Any) -> list[dict]:
    """Hujjat yoki ro'yxatdan qatorlar."""
    if isinstance(doc, dict):
        return list(doc.get("rows") or [])
    return list(doc or [])


def load_metrics_file(path: str | Path) -> list[dict]:
    """Boshqa asboblar uchun: faylni o'qiydi, validatsiya qiladi, qatorlarni qaytaradi (NormalizeError)."""
    doc = _load_json(Path(path))
    errs = validate_metrics(doc)
    if errs:
        raise NormalizeError("metrics.v1 yaroqsiz: " + "; ".join(errs[:5]) + (f" (+{len(errs) - 5} ta)" if len(errs) > 5 else ""))
    return rows_of(doc)


# --------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Manbalarni metrics.v1 ga normallashtirish")
    ap.add_argument("adapter", help="|".join(ADAPTERS) + "|validate|list")
    ap.add_argument("target", nargs="?", help="validate uchun fayl")
    ap.add_argument("--input", "-i")
    ap.add_argument("--out", "-o")
    ap.add_argument("--level", choices=["campaign", "adset", "ad"])
    ap.add_argument("--account-id")
    ap.add_argument("--currency")
    ap.add_argument("--platform")
    ap.add_argument("--date", help="CSV'da sana ustuni bo'lmasa, standart sana (YYYY-MM-DD)")
    ap.add_argument("--synthetic", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    def fail(msg: str, unmapped: list[str] | None = None) -> int:
        print(json.dumps({"error": msg, "unmapped_columns": unmapped or []}, ensure_ascii=False, indent=2))
        print(f"xato: {msg}", file=sys.stderr)
        return tcore.EXIT_VALIDATION

    if args.adapter == "list":
        print("\n".join(ADAPTERS))
        return 0
    if args.adapter == "validate":
        if not args.target:
            return fail("validate uchun fayl yo'li kerak")
        try:
            doc = _load_json(Path(args.target))
        except NormalizeError as exc:
            return fail(str(exc))
        errs = validate_metrics(doc)
        print(json.dumps({"valid": not errs, "errors": errs, "rows": len(rows_of(doc))}, ensure_ascii=False, indent=2))
        return 0 if not errs else tcore.EXIT_VALIDATION
    if not args.input:
        return fail("--input kerak")
    try:
        doc = normalize(args.adapter, Path(args.input), level=args.level, account_id=args.account_id,
                        currency=args.currency, platform=args.platform, date=args.date, synthetic=args.synthetic)
    except NormalizeError as exc:
        return fail(str(exc), exc.unmapped)
    errs = validate_metrics(doc)
    if errs:
        return fail("normalizatsiya natijasi sxemaga mos emas: " + "; ".join(errs[:5]), doc.get("unmapped_columns"))
    text = json.dumps(doc, ensure_ascii=False, indent=2)
    if args.out:
        tcore.atomic_write_text(Path(args.out), text + "\n")
        print(json.dumps({"written": args.out, "rows": len(doc["rows"]), "unmapped_columns": doc["unmapped_columns"]}, ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows cp1252 konsolida --help/hisobotdagi '→' kabi belgilar yiqilmasin
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
