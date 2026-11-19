#!/usr/bin/env python3
"""Demo uchun SINTETIK metrics.v1 yaratadi (deterministik, tarmoqsiz).

Hikoya (hammasi to'qima, `synthetic: true`): "demo-brand" — Toshkentdagi o'quv markazi, Meta Lead kampaniyasi.
- 3 reklama, kunlik qatorlar; oxirgi 3 kunda tracking uzilishi (sarf va klik bor, lid yo'q);
- oxirgi 14 kunda charchoq: frequency o'sadi, CTR tushadi;
- shu sabab CPA ham siljiydi. Pulse shu uchta holatni topishi kerak.
"""
from __future__ import annotations

import datetime as dt
import json
import random
import sys
from pathlib import Path


def build(end: str = "2026-11-18", days: int = 35, seed: int = 7) -> dict:
    rnd = random.Random(seed)
    end_d = dt.date.fromisoformat(end)
    rows = []
    adsets = {"adset_a": ("Toshkent 25-40", 40.0, 0.045), "adset_b": ("Toshkent 18-24", 35.0, 0.040), "adset_c": ("Viloyatlar", 25.0, 0.030)}
    ads = {"ad_1": "adset_a", "ad_2": "adset_b", "ad_3": "adset_c"}
    for i in range(days):
        d = end_d - dt.timedelta(days=days - 1 - i)
        late = i >= days - 3
        for ad, aset in ads.items():
            name, base_spend, cvr = adsets[aset]
            spend = round(base_spend * rnd.uniform(0.93, 1.07), 2)
            imps = int(spend / 0.0055 * rnd.uniform(0.95, 1.05))
            ctr = 0.012
            freq = 1.6
            # charchoq: oxirgi 14 kunda frequency 1.6 -> 3.0, CTR 1.2% -> 0.9% (hamma reklamada)
            t = max(0, i - (days - 14)) / 13
            freq = 1.6 + 1.4 * t
            ctr = 0.012 - 0.003 * t
            clicks = int(imps * ctr)
            leads = int(round(clicks * cvr * 3 * rnd.uniform(0.9, 1.1)))
            if late:
                leads = 0  # tracking uzilishi: sarf bor, konversiya yo'q
            rows.append({
                "date": d.isoformat(), "platform": "meta", "account_id": "act_demo", "level": "ad", "entity_id": ad,
                "entity_name": f"{name} · {ad}", "spend": spend, "currency": "USD", "impressions": imps,
                "reach": int(imps / freq), "frequency": round(freq, 2), "clicks": clicks, "link_clicks": int(clicks * 0.9),
                "conversions": {"Lead": leads}, "conversion_value": 0, "source": "csv",
                "evidence_label": "UNVERIFIED", "synthetic": True,
            })
    return {"schema": "metrics.v1", "synthetic": True, "rows": rows}


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("metrics.v1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)
