#!/usr/bin/env python3
"""call-insights.py — sotuvchi qo'ng'iroq transkriptlari → reklama bo'yicha e'tirozlar va kreativ g'oyalar. Stdlib, 0 token.

Transkripsiya (audio → matn) bu asbobdan TASHQARIDA qilinadi (Whisper, ElevenLabs, telefoniya/CRM'ning
o'z matni). Asbob tayyor matnni deterministik tahlil qiladi.

Kirish: JSON (ro'yxat yoki {"calls": [...]}), CSV yoki papka (*.json/*.csv/*.txt).
Maydonlar: call_id, ad, campaign, outcome, duration_sec, consent, transcript.
  outcome: won | qualified | lost | unqualified | no_answer (boshqasi "other")
  consent: "no"/"false"/"0" bo'lsa qo'ng'iroq tashlanadi (xuddi crm-bridge kabi).

Buyruqlar:
  report --input P [--group-by ad|campaign] [--min-calls 30]   reklama bo'yicha e'tiroz va natija jadvali
  brief  --input P [--group-by ad|campaign] [--min-calls 30]   e'tirozdan kreativ burchak (angle) nomzodlari

Xavfsizlik: telefon/email/uzun raqamlar chop etishdan oldin [REDACTED] bilan almashtiriladi; asbob
hisobga hech narsa yozmaydi. Natija — HEURISTIC_PRIOR_MODEL (kalit so'z lug'ati), isbot emas:
lug'at UZ (lotin/kirill) va RU uchun, qo'lda tekshirilmagan; kichik namunada xulosa qilinmaydi.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

OUTCOMES = {"won", "qualified", "lost", "unqualified", "no_answer"}
GOOD = {"won", "qualified"}
FALSE = {"0", "false", "no", "yoq", "yo'q", "нет", "n"}

# e'tiroz → (kalit so'zlar, kreativ burchak nomzodi). Matn kichik harfga o'tkaziladi.
OBJECTIONS: dict[str, tuple[tuple[str, ...], str]] = {
    "narx": (("qimmat", "narxi", "narx ", "pul yo'q", "pulim yo'q", "дорого", "цена", "стоимость", "дороговато"),
             "Narxni oldindan ochiq ayt: aniq narx/diapazon + nima kiradi (qiymat tushuntirishi)"),
    "bolib_tolash": (("bo'lib to'la", "bolib tola", "muddatli", "rassrochka", "рассрочка", "в кредит", "кредит"),
                     "Bo'lib to'lash shartlarini kreativda ko'rsat (oyiga qancha, necha oy)"),
    "ishonch": (("ishonmayman", "aldov", "firibgar", "kafolat", "отзыв", "гарантия", "не верю", "обман", "sharh"),
                "Ijtimoiy isbot: haqiqiy mijoz sharhi, kafolat, natija oldin/keyin"),
    "vaqt": (("keyinroq", "hozir emas", "o'ylab ko'r", "oylab kor", "позже", "подумаю", "потом", "vaqtim yo'q"),
             "Shoshilinchlik yoki oson birinchi qadam (bepul konsultatsiya, kichik sinov)"),
    "raqobatchi": (("boshqa joyda", "arzonroq", "u yerda", "у других", "конкурент", "в другом месте", "дешевле"),
                   "Raqobatchidan farq: nima uchun aynan biz (3 ta aniq farq)"),
    "joylashuv": (("uzoq", "manzil", "qayerda", "lokatsiya", "далеко", "адрес", "где находится"),
                  "Manzil/yetkazib berish va qulayliklarni kreativga qo'sh"),
    "vada_mos_emas": (("reklamada", "e'londa", "в рекламе", "в объявлении", "instagramda ko'rdim", "aksiya deb"),
                      "Reklama va'dasi va sotuvchi gapi mos emas: kreativdagi va'dani sotuv skripti bilan tenglashtir"),
    "sorov_yoq": (("so'ramaganman", "soramagan", "qoldirmaganman", "не оставлял", "не заказывал", "ошиблись", "adashib"),
                  "Tasodifiy lid: forma/kreativ filtrini kuchaytir (narx va shart oldindan)"),
}
BUY_SIGNALS = ("qachon kelay", "manzilni yuboring", "yozilaman", "buyurtma bering", "когда приехать",
               "запишите", "беру", "оформляйте", "to'lov qilaman", "tolov qilaman")

_PHONE = re.compile(r"\+?\d[\d\s\-().]{7,}\d")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def redact(text: str) -> str:
    return _PHONE.sub("[REDACTED]", _EMAIL.sub("[REDACTED]", text))


def _norm_call(raw: dict, fallback_id: str) -> dict | None:
    consent = str(raw.get("consent", "")).strip().lower()
    if consent in FALSE:
        return None
    outcome = str(raw.get("outcome", "")).strip().lower()
    try:
        dur = float(raw.get("duration_sec") or 0)
    except (TypeError, ValueError):
        dur = 0.0
    return {
        "call_id": str(raw.get("call_id") or fallback_id),
        "ad": str(raw.get("ad") or "(noma'lum)"),
        "campaign": str(raw.get("campaign") or "(noma'lum)"),
        "outcome": outcome if outcome in OUTCOMES else "other",
        "duration_sec": dur,
        "transcript": str(raw.get("transcript") or ""),
    }


def load_calls(path: Path) -> tuple[list[dict], int]:
    """(qo'ng'iroqlar, consent sababli tashlanganlar soni)."""
    raws: list[tuple[dict, str]] = []

    def read_file(p: Path) -> None:
        if p.suffix == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
            items = data.get("calls", []) if isinstance(data, dict) else data
            raws.extend((r, f"{p.stem}-{i}") for i, r in enumerate(items))
        elif p.suffix == ".csv":
            with p.open(encoding="utf-8", newline="") as fh:
                raws.extend((r, f"{p.stem}-{i}") for i, r in enumerate(csv.DictReader(fh)))
        elif p.suffix == ".txt":
            raws.append(({"call_id": p.stem, "transcript": p.read_text(encoding="utf-8")}, p.stem))

    if path.is_dir():
        for p in sorted(path.iterdir()):
            read_file(p)
    elif path.exists():
        read_file(path)
    else:
        raise FileNotFoundError(str(path))
    calls, dropped = [], 0
    for raw, fid in raws:
        c = _norm_call(raw, fid)
        if c is None:
            dropped += 1
        else:
            calls.append(c)
    return calls, dropped


def detect(transcript: str) -> tuple[set[str], bool]:
    low = transcript.lower().replace("’", "'").replace("ʻ", "'").replace("`", "'")
    found = {name for name, (kws, _) in OBJECTIONS.items() if any(k in low for k in kws)}
    return found, any(k in low for k in BUY_SIGNALS)


def analyze(calls: list[dict], group_by: str = "ad") -> dict[str, dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in calls:
        groups[c[group_by]].append(c)
    out: dict[str, dict] = {}
    for key, items in groups.items():
        obj, outcomes, buy = Counter(), Counter(), 0
        for c in items:
            found, has_buy = detect(c["transcript"])
            obj.update(found)
            outcomes[c["outcome"]] += 1
            buy += has_buy
        n = len(items)
        answered = [c for c in items if c["outcome"] != "no_answer"]
        out[key] = {
            "calls": n,
            "good_rate": round(sum(outcomes[o] for o in GOOD) / n, 3),
            "no_answer_rate": round(outcomes["no_answer"] / n, 3),
            "avg_duration_sec": round(sum(c["duration_sec"] for c in answered) / len(answered), 1) if answered else 0.0,
            "buy_signal_rate": round(buy / n, 3),
            "objections": {k: round(v / n, 3) for k, v in obj.most_common()},
            "outcomes": dict(outcomes),
        }
    return out


def _fmt_pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def cmd_report(args: argparse.Namespace) -> int:
    calls, dropped = load_calls(Path(args.input))
    stats = analyze(calls, args.group_by)
    print(f"Qo'ng'iroqlar: {len(calls)} (consent yo'q, tashlandi: {dropped}) | guruh: {args.group_by}")
    print("Manba: HEURISTIC_PRIOR_MODEL (kalit so'z lug'ati); outcome — CRM'dan (MEASURED, agar to'g'ri kiritilgan)\n")
    for key, s in sorted(stats.items(), key=lambda kv: -kv[1]["calls"]):
        warn = "  [KICHIK NAMUNA — xulosa qilinmaydi]" if s["calls"] < args.min_calls else ""
        print(f"{key}: {s['calls']} qo'ng'iroq | sifatli {_fmt_pct(s['good_rate'])} | "
              f"javobsiz {_fmt_pct(s['no_answer_rate'])} | o'rt. davomiylik {s['avg_duration_sec']}s{warn}")
        top = list(s["objections"].items())[:3]
        print("  e'tirozlar:", ", ".join(f"{k} {_fmt_pct(v)}" for k, v in top) or "aniqlanmadi")
    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


def cmd_brief(args: argparse.Namespace) -> int:
    calls, _ = load_calls(Path(args.input))
    stats = analyze(calls, args.group_by)
    print("Kreativ burchak nomzodlari (HEURISTIC_PRIOR_MODEL — A/B bilan tekshiring, `experiments`):\n")
    shown = 0
    for key, s in sorted(stats.items(), key=lambda kv: -kv[1]["calls"]):
        if s["calls"] < args.min_calls:
            print(f"- {key}: namuna kichik ({s['calls']} < {args.min_calls}), o'tkazib yuborildi")
            continue
        for name, share in list(s["objections"].items())[:2]:
            if share >= 0.15:
                print(f"- {key} | {name} ({_fmt_pct(share)}): {OBJECTIONS[name][1]}")
                shown += 1
    if not shown:
        print("(yetarli namunali va 15% dan yuqori e'tiroz topilmadi)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Qo'ng'iroq transkriptlari tahlili (0 token)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("report", cmd_report), ("brief", cmd_brief)):
        sp = sub.add_parser(name)
        sp.add_argument("--input", required=True)
        sp.add_argument("--group-by", choices=["ad", "campaign"], default="ad")
        sp.add_argument("--min-calls", type=int, default=30)
        if name == "report":
            sp.add_argument("--json", action="store_true")
        sp.set_defaults(fn=fn)
    args = p.parse_args(argv)
    try:
        return args.fn(args)
    except FileNotFoundError as exc:
        print(f"Xato: fayl topilmadi: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
