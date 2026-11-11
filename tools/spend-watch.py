#!/usr/bin/env python3
"""Tyrion Sarf Kuzatuvchisi — kunlik byudjet og'ishini fonda xabar qiladi (faqat o'qish).

Claude Code uni `monitors/monitors.json` orqali sessiya bilan birga ishga tushiradi; stdout'dagi har bir
satr — bitta xabar. Faqat holat O'ZGARGANDA xabar beriladi (spam yo'q). Hisobga hech narsa yozmaydi:
pauza yoki byudjet o'zgartirish yo'q, faqat Graph API GET so'rovlari.

Monitor jarayoni plugin sozlamalarini (`userConfig`) olmaydi, shuning uchun token muhit o'zgaruvchisidan
(`META_ACCESS_TOKEN`) yoki `.env` dan olinadi (`tyrion_core.load_settings`). Token yo'q bo'lsa bitta
satr yozib, jim chiqadi.

Ishlatish:
  python3 tools/spend-watch.py                 # doimiy (har 30 daqiqada)
  python3 tools/spend-watch.py --once          # bir marta tekshirib chiqadi
  python3 tools/spend-watch.py --interval 600  # 10 daqiqa (eng kami 300 s)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

MIN_INTERVAL = 300
OVERPACE_RATIO = 1.2     # sarf rejadagidan 20% ortiq
OVERPACE_FROM_DAY = 0.15  # kunning 15% idan keyin
UNDERPACE_RATIO = 0.5    # sarf rejaning yarmidan kam
UNDERPACE_FROM_DAY = 0.6  # kunning 60% idan keyin
ZERO_DECIMAL = {"JPY", "KRW", "VND", "CLP", "ISK", "PYG", "UGX", "XAF", "XOF", "XPF", "RWF", "KMF", "GNF", "DJF", "VUV"}


def evaluate(spend: float, daily_budget: float, elapsed: float) -> tuple[str, str]:
    """(holat, izoh). Holatlar: OK, NO_BUDGET, OVER_BUDGET, OVERPACE, UNDERPACE."""
    if daily_budget <= 0:
        return "NO_BUDGET", "faol kunlik byudjet topilmadi"
    elapsed = min(max(elapsed, 0.0), 1.0)
    expected = daily_budget * elapsed
    if spend > daily_budget:
        return "OVER_BUDGET", f"sarf {spend:.2f} kunlik byudjetdan ({daily_budget:.2f}) oshdi"
    if elapsed >= OVERPACE_FROM_DAY and spend > expected * OVERPACE_RATIO:
        return "OVERPACE", f"sarf {spend:.2f}, kun o'tgan {elapsed:.0%} ga reja {expected:.2f}"
    if elapsed >= UNDERPACE_FROM_DAY and spend < expected * UNDERPACE_RATIO:
        return "UNDERPACE", f"sarf {spend:.2f}, kun o'tgan {elapsed:.0%} ga reja {expected:.2f}"
    return "OK", f"sarf {spend:.2f} / byudjet {daily_budget:.2f}"


def day_fraction(now: datetime) -> float:
    return (now.hour * 3600 + now.minute * 60 + now.second) / 86400


def budget_offset(currency: str, override: int | None) -> int:
    if override:
        return override
    return 1 if currency.upper() in ZERO_DECIMAL else 100


def total_daily_budget(campaigns: list[dict], adsets: list[dict], offset: int) -> tuple[float, int]:
    """Faol kampaniya (CBO) byudjetlari + byudjeti adset darajasida bo'lgan adsetlar. (jami, lifetime-only soni)."""
    cbo = {c.get("id") for c in campaigns if tcore.safe_float(c.get("daily_budget"), default=0.0, min_val=0.0) > 0}
    total = sum(tcore.safe_float(c.get("daily_budget"), default=0.0, min_val=0.0) for c in campaigns if c.get("id") in cbo)
    lifetime_only = 0
    for a in adsets:
        if a.get("campaign_id") in cbo:
            continue
        b = tcore.safe_float(a.get("daily_budget"), default=0.0, min_val=0.0)
        if b > 0:
            total += b
        elif tcore.safe_float(a.get("lifetime_budget"), default=0.0, min_val=0.0) > 0:
            lifetime_only += 1
    return total / offset, lifetime_only


def graph_fetcher() -> Callable[[str, dict[str, str]], dict[str, Any]]:
    base = os.environ.get("META_GRAPH_API_BASE_URL", "https://graph.facebook.com").strip().rstrip("/")
    version = os.environ.get("META_GRAPH_API_VERSION", tcore.DEFAULT_GRAPH_API_VERSION).strip() or tcore.DEFAULT_GRAPH_API_VERSION
    headers = {"Authorization": f"Bearer {os.environ['META_ACCESS_TOKEN'].strip()}"}

    def fetch(path: str, params: dict[str, str]) -> dict[str, Any]:
        url = f"{base}/{version}/{path}?{urllib.parse.urlencode(params)}"
        data = tcore.http_get_json_with_backoff(url, headers=headers, timeout=15.0, max_retries=2)
        if "error" in data:
            raise RuntimeError(tcore.redact_secrets(str(data["error"])))
        return data

    return fetch


def account_timezone(info: dict[str, Any]):
    """Akkaunt vaqt mintaqasi. Windows'da `tzdata` bo'lmasligi mumkin, shunda Meta bergan UTC siljishiga o'tadi
    (UTC ga jimgina o'tish kun ulushini noto'g'ri hisoblardi)."""
    try:
        return ZoneInfo(str(info.get("timezone_name") or ""))
    except Exception:
        hours = tcore.safe_float(info.get("timezone_offset_hours_utc"), default=0.0, min_val=-14.0, max_val=14.0)
        return timezone(timedelta(hours=hours))


def check_once(account: str, fetch: Callable[[str, dict[str, str]], dict[str, Any]], now: datetime | None = None,
               offset_override: int | None = None) -> dict[str, Any]:
    info = fetch(account, {"fields": "name,currency,timezone_name,timezone_offset_hours_utc"})
    currency = str(info.get("currency", "USD"))
    tz = account_timezone(info)
    local_now = (now or datetime.now(tz)).astimezone(tz)
    active = json.dumps(["ACTIVE"])
    campaigns = fetch(f"{account}/campaigns", {"fields": "id,daily_budget", "effective_status": active, "limit": "200"}).get("data", [])
    adsets = fetch(f"{account}/adsets", {"fields": "campaign_id,daily_budget,lifetime_budget", "effective_status": active, "limit": "200"}).get("data", [])
    rows = fetch(f"{account}/insights", {"fields": "spend", "date_preset": "today"}).get("data", [])
    spend = tcore.safe_float(rows[0].get("spend") if rows else 0, default=0.0, min_val=0.0)
    budget, lifetime_only = total_daily_budget(campaigns, adsets, budget_offset(currency, offset_override))
    state, detail = evaluate(spend, budget, day_fraction(local_now))
    return {"account": account, "name": info.get("name", ""), "currency": currency, "state": state,
            "detail": detail, "spend": spend, "budget": budget, "lifetime_only": lifetime_only,
            "day": local_now.strftime("%Y-%m-%d")}


def message(result: dict[str, Any]) -> str:
    return f"Tyrion sarf [{result['state']}] {result['name'] or result['account']}: {result['detail']} {result['currency']}"


def should_emit(previous: tuple[str, str] | None, result: dict[str, Any]) -> bool:
    """Kunning birinchi tekshiruvida faqat muammo xabar qilinadi; keyin — faqat holat o'zgarganda."""
    state = result["state"]
    if previous is None:
        return state != "OK"
    if previous[0] != result["day"]:
        return state not in ("OK", "NO_BUDGET")
    return previous[1] != state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spend-watch.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--account-id", default="")
    parser.add_argument("--interval", type=int, default=1800, help=f"soniya (eng kami {MIN_INTERVAL})")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--budget-offset", type=int, default=0, help="byudjet minor birligi (standart: 100, JPY/KRW/VND kabilar uchun 1)")
    args = parser.parse_args(argv)

    tcore.load_settings(VAULT)
    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    raw_account = args.account_id or os.environ.get("META_AD_ACCOUNT_ID", "")
    if not token or not raw_account:
        print("Tyrion sarf kuzatuvchisi o'chiq: META_ACCESS_TOKEN va META_AD_ACCOUNT_ID kerak "
              "(muhit o'zgaruvchisi yoki loyiha `.env`; monitor plugin sozlamalarini olmaydi).", flush=True)
        return 0
    account = raw_account if raw_account.startswith("act_") else f"act_{raw_account}"
    fetch = graph_fetcher()
    interval = max(MIN_INTERVAL, args.interval)
    previous: tuple[str, str] | None = None
    failing = False
    while True:
        try:
            result = check_once(account, fetch, offset_override=args.budget_offset or None)
            failing = False
            if should_emit(previous, result):
                print(message(result), flush=True)
            if result["lifetime_only"] and previous is None:
                print(f"Tyrion sarf: {result['lifetime_only']} ta adset lifetime byudjetli — kunlik og'ish hisobiga kirmaydi.", flush=True)
            previous = (result["day"], result["state"])
        except Exception as exc:
            if not failing:  # bir xil xatoni takrorlamaydi
                print(f"Tyrion sarf kuzatuvchisi: so'rov xatosi — {tcore.redact_secrets(str(exc))[:160]}", flush=True)
            failing = True
        if args.once:
            return 0
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
