#!/usr/bin/env python3
"""adlib-mine.py — raqobatchi reklamalari (Ad Library eksporti / ads_library_search natijasi) tahlili. Stdlib.

    python3 tools/adlib-mine.py mine --input ads.json|ads.csv [--today YYYY-MM-DD]

Kirish maydonlari (moslashuvchan): id, advertiser, text/body, start_date/ad_delivery_start_time,
end_date/ad_delivery_stop_time (bo'sh = hali faol), creative_group/variant_of (ixtiyoriy).
DIQQAT: faollik muddati natijaning isboti EMAS — faqat PROXY (`ACTIVITY_DURATION_PROXY`). Reklama uzoq
yurishi foydali bo'lganini ham, byudjet borligini ham anglatishi mumkin.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ANGLES = {
    "narx": ["narx", "arzon", "chegirma", "skidka", "цена", "дешев", "скидк", "price", "discount", "cheap", "%", "bepul", "free", "бесплатно"],
    "ishonch": ["kafolat", "ishonch", "sertifikat", "гарант", "довер", "отзыв", "guarantee", "trusted", "review", "mijoz", "клиент"],
    "tezlik": ["tez", "bugun", "darhol", "быстро", "сегодня", "fast", "today", "minut", "daqiqa", "срочно"],
    "natija": ["natija", "oldin", "keyin", "результат", "до и после", "result", "before", "after"],
    "taqchillik": ["cheklangan", "oxirgi", "faqat", "ограничен", "последн", "limited", "last", "only"],
    "bo'lib to'lash": ["bo'lib", "muddatli", "nasiya", "рассрочк", "installment", "0%"],
}
OFFER_PATTERNS = {
    "foizli chegirma": r"\b\d{1,2}\s?%",
    "bepul konsultatsiya/sinov": r"(bepul|бесплатн|free)\s+(konsult|maslahat|консульт|trial|sinov|дегустац|пробн|demo)",
    "bo'lib to'lash": r"(nasiya|bo'lib|рассрочк|installment)",
    "bonus/sovg'a": r"(sovg'a|bonus|подарок|gift)",
    "ro'yxatdan o'tish/lead magnet": r"(ro'yxat|yozil|запиш|register|sign up|checklist|чек-лист)",
}
COUNTER = {
    "narx": "Qiymat va natija angle: nega arzonligi emas, nima olishi (ROI, kafolat)",
    "ishonch": "Tezkor natija + jonli dalil (UGC, ish jarayoni) bilan ishonchni 'ko'rsat, aytma' tarzida",
    "tezlik": "Sifat/puxtalik angle: 'tez' emas, 'bir marta va to'g'ri'",
    "natija": "Mijoz hikoyasi / jarayon angle (natijadan oldingi yo'l), ishonchli sertifikat bilan",
    "taqchillik": "Aniq va halol sabab bilan taklif (soxta cheklov emas), kafolat bilan",
    "bo'lib to'lash": "Umumiy qiymat va to'lov soddaligi angle (Payme/Click/Uzum Nasiya aniq shartlari bilan)",
    "(aniqlanmadi)": "Raqobatchida aniq angle yo'q: o'z angle'ingizni birinchi bo'lib egallang",
}


def _d(v: str | None) -> date | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).strip()[:10]).date()
    except ValueError:
        return None


def load(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return [{str(k).strip().lower(): v for k, v in r.items() if k} for r in csv.DictReader(fh)]
    d = json.loads(path.read_text(encoding="utf-8"))
    return d if isinstance(d, list) else (d.get("ads") or d.get("data") or [])


def _pick(r: dict, *keys: str) -> str:
    for k in keys:
        v = r.get(k)
        if v:
            if isinstance(v, list):
                v = " ".join(map(str, v))
            return str(v)
    return ""


def angle_of(text: str) -> str:
    t = text.lower()
    scores = {a: sum(t.count(k) for k in kws) for a, kws in ANGLES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "(aniqlanmadi)"


def mine(ads: list[dict], today: date | None = None) -> dict:
    today = today or date.today()
    adv: dict = defaultdict(lambda: {"ads": 0, "active_now": 0, "durations": [], "variants": Counter(), "angles": Counter(),
                                      "offers": Counter()})
    for r in ads:
        name = _pick(r, "advertiser", "page_name") or "(noma'lum)"
        text = _pick(r, "text", "body", "ad_creative_bodies", "primary_text")
        s = _d(_pick(r, "start_date", "ad_delivery_start_time"))
        e = _d(_pick(r, "end_date", "ad_delivery_stop_time"))
        a = adv[name]
        a["ads"] += 1
        if s:
            end = e or today
            a["durations"].append(max(0, (end - s).days))
        if not e:
            a["active_now"] += 1
        a["variants"][_pick(r, "creative_group", "variant_of") or _pick(r, "id")] += 1
        a["angles"][angle_of(text)] += 1
        for label, pat in OFFER_PATTERNS.items():
            if re.search(pat, text.lower()):
                a["offers"][label] += 1
    out = {"label": "ACTIVITY_DURATION_PROXY — faollik muddati natija isboti EMAS; MEASURED_ACCOUNT_DATA emas",
           "advertisers": {}, "counter_briefs": []}
    for name, a in sorted(adv.items()):
        dur = sorted(a["durations"])
        top_angle = [x for x, _ in a["angles"].most_common() if x != "(aniqlanmadi)"][:1] or ["(aniqlanmadi)"]
        out["advertisers"][name] = {
            "ads": a["ads"], "active_now": a["active_now"],
            "activity_days": {"max": dur[-1] if dur else None, "median": dur[len(dur) // 2] if dur else None, "label": "PROXY"},
            "variants_per_creative_group": dict(a["variants"].most_common(5)),
            "angle_clusters": dict(a["angles"].most_common()), "offer_patterns": dict(a["offers"].most_common()),
        }
        out["counter_briefs"].append({"vs": name, "their_dominant_angle": top_angle[0], "counter_angle": COUNTER[top_angle[0]],
                                      "status": "gipoteza — A/B bilan sinang"})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ad Library mining")
    ap.add_argument("cmd", choices=["mine"])
    ap.add_argument("--input", required=True)
    ap.add_argument("--today")
    a = ap.parse_args(argv)
    try:
        ads = load(Path(a.input))
        res = mine(ads, _d(a.today))
    except (OSError, ValueError) as e:
        print(f"xato: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows cp1252 konsolida --help/hisobotdagi '→' kabi belgilar yiqilmasin
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
