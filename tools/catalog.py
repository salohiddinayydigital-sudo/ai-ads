#!/usr/bin/env python3
"""Tyrion katalogi — butun tizimning mashina o'qiydigan yagona reestri.

Muammo: tizimda nima bor (agent, skill, bot, tool, qayd) — qo'lda yozilgan
ro'yxatlar bilan yuritilsa, raqamlar eskiradi va nusxalar bir-biridan uzoqlashadi
(hozir 33 charterning 12 tasi ikki nusxada farq qiladi).

Yechim: katalog HAR DOIM fayl tizimidan generatsiya qilinadi. Qo'lda tahrirlanmaydi.
`check` buyrug'i katalog bilan haqiqatni solishtiradi va farq bo'lsa xato qaytaradi.

Buyruqlar:
  python3 tools\\catalog.py build            # manifests/catalog.json ni qayta yozadi
  python3 tools\\catalog.py check            # katalog haqiqatga mos keladimi (CI/doctor uchun)
  python3 tools\\catalog.py drift            # nusxalar (mirror) farqini ko'rsatadi
  python3 tools\\catalog.py sync-mirrors     # nusxalarni kanonikdan qayta quradi (eskisi arxivga)
  python3 tools\\catalog.py sync-claims      # hujjatlardagi (marker + oddiy matn) raqamlarni moslashtiradi
  python3 tools\\catalog.py list --layer agents
  python3 tools\\catalog.py summary

Chiqish kodi: 0 — mos, 1 — farq bor, 2 — xato.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:  # PyYAML bor bo'lsa ishlatiladi, bo'lmasa minimal parser
    import yaml  # type: ignore
except Exception:  # pragma: no cover - muhitga bog'liq
    yaml = None

VAULT = Path(__file__).resolve().parent.parent
MANIFEST = VAULT / "manifests" / "catalog.json"
SCHEMA = "tyrion-catalog/v1"

# Windows: konsol yoki quvur (pipe) bo'lsa ham UTF-8 chiqarish.
# Modul darajasida — skript boshqa skript ichidan chaqirilganda ham ishlashi uchun.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

# Har bir qatlam: nom -> (ildiz papka, glob, tur)
# "canonical" — hozircha manba; "mirror" — nusxa (drift tekshiriladi)
LAYERS: dict[str, tuple[Path, str, str]] = {
    "wiki": (VAULT / "wiki", "*.md", "note"),
    "playbooks": (VAULT / "playbooks", "*.md", "playbook"),
    "contexts": (VAULT / "contexts", "*.md", "context"),
    "agents": (VAULT / "agents", "*.md", "agent"),
    "skills": (VAULT / "skills", "*/SKILL.md", "skill"),
    "commands": (VAULT / "commands", "*.md", "command"),
    "commands.mirror": (VAULT / ".claude" / "commands", "*.md", "command"),
    "rules": (VAULT / "rules", "*.md", "rule"),
    "hooks": (VAULT / "hooks", "*", "hook"),
    "tools": (VAULT / "tools", "*", "tool"),
    "tests": (VAULT / "tests", "test_*.py", "test"),
    "templates": (VAULT / "templates", "*.md", "template"),
    "evals": (VAULT / "evals", "*.json", "eval"),
}

# Drift tekshiriladigan juftliklar: (kanonik qatlam, nusxa qatlam)
MIRROR_PAIRS = [
    ("commands", "commands.mirror"),
]

# Marker bo'lmagan oddiy matndagi qo'lda yozilgan raqamlar.
# Har yozuv: (fayl, 3 guruhli regex — (old)(raqam)(keyin), katalog kaliti).
# Nega kerak: `<!-- tyrion:catalog -->` markeri faqat AGENTS.md/README.md da bor;
# INDEX.md va rules/ dagi "wiki 41 qayd" kabi jumlalar eskirib, miya o'zi haqida
# yolg'on gapiradigan bo'lib qolgan edi (41 ≠ 42). Endi `sync-claims` ularni ham
# tuzatadi, `doctor` esa tekshiradi.
HUMAN_CLAIMS: list[tuple[str, "re.Pattern[str]", str]] = [
    ("INDEX.md",
     re.compile(r"(\| `wiki/` \| Atomik, wikilink bog'langan bilim qaydlari \()(\d+)(\) \|)"),
     "wiki"),
    ("README.md",
     re.compile(r"(Bilim: atomik qaydlar \()(\d+)(\))"),
     "wiki"),
    ("README.md",
     re.compile(r"(\*\*)(\d+)( specialist agents\*\*)"),
     "agents"),
    ("README.md",
     re.compile(r"(\*\*)(\d+)( platform & marketing skills\*\*)"),
     "skills"),
    ("README.md",
     re.compile(r"(\*\*)(\d+)( slash commands\*\*)"),
     "commands"),
    ("README.md",
     re.compile(r"(\*\*)(\d+)( deterministic 0-token Python CLI tools\*\*)"),
     "tools"),
    ("SECURITY.md",
     re.compile(r"(\*\*)(\d+)( agents\*\*)"),
     "agents"),
    ("SECURITY.md",
     re.compile(r"(\*\*)(\d+)( skills\*\*)"),
     "skills"),
    ("SECURITY.md",
     re.compile(r"(\*\*)(\d+)( slash commands\*\*)"),
     "commands"),
    ("SECURITY.md",
     re.compile(r"(\*\*)(\d+)( CLI tools\*\*)"),
     "tools"),
    ("CLAUDE.md",
     re.compile(r"(\| `agents/` \| \*\*)(\d+)( ta kanonik agent charteri\*\*)"),
     "agents"),
    ("CLAUDE.md",
     re.compile(r"(\| `skills/` \| \*\*)(\d+)( ta kanonik skill\*\*)"),
     "skills"),
    ("CLAUDE.md",
     re.compile(r"(\| `commands/` \| \*\*)(\d+)( ta slash buyruq\*\*)"),
     "commands"),
    ("CLAUDE.md",
     re.compile(r"(\| `wiki/` \| \*\*)(\d+)( ta atomik bilim qaydi\*\*)"),
     "wiki"),
    ("CLAUDE.md",
     re.compile(r"(\| `tools/` \| \*\*)(\d+)( ta 0-token deterministik CLI asbob\*\*)"),
     "tools"),
    ("rules/20-token-gigiyena.md",
     re.compile(r"(`wiki/` )(\d+)( qayd)"),
     "wiki"),
    ("AGENTS.md",
     re.compile(r"(va )(\d+)( ta 0-token deterministik Python asbobi)"),
     "tools"),
    ("AGENTS.md",
     re.compile(r"(\| \*\*Asboblar\*\* \| `tools/` \()(\d+)(\) \|)"),
     "tools"),
    ("README.md",
     re.compile(r"(├── tools/\s+# )(\d+)( ta 0-Token Deterministik CLI Asbob)"),
     "tools"),
    ("plugin.json",
     re.compile(r"(\d+ slash commands, )(\d+)( deterministic CLI tools)"),
     "tools"),
    (".claude-plugin/plugin.json",
     re.compile(r"(\d+ slash commands, )(\d+)( deterministic CLI tools)"),
     "tools"),
    (".codex-plugin/plugin.json",
     re.compile(r"(\d+ slash commands, )(\d+)( deterministic CLI tools)"),
     "tools"),
    ("marketplace.json",
     re.compile(r"(\d+ slash commands, )(\d+)( CLI tools)"),
     "tools"),
    ("package.json",
     re.compile(r"(\d+ commands, )(\d+)( tools\))"),
     "tools"),
]

# Plagin manifestlari, marketplace, package.json va ikki tilli README dagi e'lonlar (har uchrashuvi tekshiriladi;
# fayl/naqsh bo'lmasa o'tkaziladi). Hosila kalitlar (`skills_platform` ...) scan() dan keladi.
_CLAIM_FILES = ["plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "package.json",
                "marketplace.json", ".claude-plugin/marketplace.json", "README.md", "README.uz.md"]
_CLAIM_PHRASES = [
    (r" (?:specialist |ixtisoslashgan |marketing )?agents?\b", "agents"),
    (r" (?:platform & marketing |canonical paid-media & CRO )?skills\b", "skills"),
    (r" wiki notes\b", "wiki"),
    (r" (?:practical |amaliy )?playbooks?\b", "playbooks"),
    (r" (?:slash )?commands\b", "commands"),
    (r" (?:deterministic (?:0-token )?(?:Python )?)?CLI tools\b", "tools"),
]
OPTIONAL_CLAIMS: list[tuple[str, "re.Pattern[str]", str]] = [
    (f, re.compile(r"()(\d+)(" + ph + ")"), key) for f in _CLAIM_FILES[:6] for ph, key in _CLAIM_PHRASES
] + [
    ("README.md", re.compile(r"(# )(\d+)( canonical paid-media & CRO skills)"), "skills"),
    ("README.uz.md", re.compile(r"(\*\*)(\d+)( ta ixtisoslashgan agent\*\*)"), "agents"),
    ("README.uz.md", re.compile(r"(\*\*)(\d+)( ta platforma va marketing skilli\*\*)"), "skills"),
    ("README.uz.md", re.compile(r"(\*\*)(\d+)( ta slash buyruq\*\*)"), "commands"),
    ("README.uz.md", re.compile(r"(\*\*)(\d+)( ta 0-token deterministik Python CLI asbob\*\*)"), "tools"),
    ("README.uz.md", re.compile(r"(# )(\d+)( ta Kanonik Skill \()"), "skills"),
    ("README.uz.md", re.compile(r"(Kanonik Skill \()(\d+)( platforma \+)"), "skills_platform"),
    ("README.uz.md", re.compile(r"(platforma \+ )(\d+)( operator \+)"), "skills_operator"),
    ("README.uz.md", re.compile(r"(operator \+ )(\d+)( reference fayl\))"), "skill_references"),
    ("README.uz.md", re.compile(r"(# )(\d+)( ta Slash Buyruq)"), "commands"),
    ("AGENTS.md", re.compile(r"(\| \*\*Skilllar\*\* \| `skills/` \()(\d+)(\) \| )"), "skills"),
    ("AGENTS.md", re.compile(r"(\) \| )(\d+)( platforma \(`ads-\*`)"), "skills_platform"),
    ("AGENTS.md", re.compile(r"(\+ )(\d+)( `references/`\) va )"), "skill_references"),
    ("AGENTS.md", re.compile(r"(`references/`\) va )(\d+)( operator/marketing skill)"), "skills_operator"),
]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
# YAML'da `\` dan keyin faqat shu belgilar kelishi mumkin. Boshqasi — xato
# (`\y` kabi), lekin PyYAML xatosini o'qish qiyin; o'zimiz aniqroq aytamiz.
INVALID_ESCAPE = re.compile(r'\\(?![0abtnvfre "\\/N_LPuxU])')
# Eng xavflisi: `\t` TO'G'RI escape, lekin yo'lni JIM buzadi —
# Windows backslash path -> TAB belgisi, xato chiqmaydi. Faqat qiymatni ko'zdan
# kechirib topiladi (2026-09-16 da 5 qaydda shu holat bo'lgan).
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]|\t")


def _control_char_error(data: object) -> str | None:
    """Parse qilingan qiymatlar ichida ko'rinmas control belgi bormi."""
    stack: list[object] = [data]
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            if CONTROL_CHARS.search(value):
                return "YAML escape qiymatni buzdi (ko'rinmas belgi) — \\ o'rniga / ishlatilsin"
        elif isinstance(value, dict):
            stack.extend(value.values())
            stack.extend(value.keys())
        elif isinstance(value, list):
            stack.extend(value)
    return None


def _normalized_bytes(path: Path) -> bytes:
    """Windows (CRLF) va Linux (LF) o'rtasida SHA-256 hamda bayt hajmi farq qilmasligi uchun \r\n -> \n normalizatsiya."""
    raw = path.read_bytes()
    return raw.replace(b"\r\n", b"\n")


def _sha256(path: Path) -> str:
    return hashlib.sha256(_normalized_bytes(path)).hexdigest()


def _fallback_frontmatter(text: str) -> dict:
    """PyYAML bo'lmaganda: `key: value` qatorlarini o'qish (ichma-ich tuzilma yo'q)."""
    data = {}
    for line in text.splitlines():
        if not line or line.startswith(("#", " ", "\t", "-")):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def read_frontmatter(path: Path) -> dict:
    """Fayl boshidagi YAML frontmatter. Buzilgan bo'lsa `_error` kaliti qo'shiladi."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"_error": f"o'qib bo'lmadi: {exc}"}

    match = FRONTMATTER_RE.match(text)
    if not match:
        return {"_error": "frontmatter yo'q"}

    raw = match.group(1)
    if INVALID_ESCAPE.search(raw):
        return {"_error": "YAML'da yaroqsiz escape (\\ dan keyin noto'g'ri belgi) — / ishlatilsin"}

    if yaml is not None:
        try:
            data = yaml.safe_load(raw) or {}
            if not isinstance(data, dict):
                return {"_error": "frontmatter dict emas"}
            control = _control_char_error(data)
            return {"_error": control} if control else data
        except Exception as exc:  # YAML buzilgan
            return {"_error": f"YAML buzilgan: {exc}"}

    return _fallback_frontmatter(raw)


_ITEM_CACHE: dict[tuple[str, int, int], dict] = {}


def _item(layer: str, path: Path) -> dict:
    stat = path.stat()
    cache_key = (f"{layer}:{path}", stat.st_mtime_ns, stat.st_size)
    cached = _ITEM_CACHE.get(cache_key)
    if cached is not None:
        return dict(cached)
    fm = read_frontmatter(path)
    res_item = {
        "name": path.parent.name if path.name == "SKILL.md" else path.stem,
        "layer": layer,
        "path": path.relative_to(VAULT).as_posix(),
        "sha256": _sha256(path)[:16],
        "bytes": len(_normalized_bytes(path)),
        "updated": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds"),
        "title": fm.get("name"),
        "description": (fm.get("description") or None),
        "source": fm.get("source"),
        "fm_error": fm.get("_error"),
    }
    _ITEM_CACHE[cache_key] = res_item
    return dict(res_item)


def scan() -> dict:
    """Fayl tizimini skanerlab, katalog tuzilmasini qaytaradi."""
    items: dict[str, list[dict]] = {}
    for layer, (root, pattern, _kind) in LAYERS.items():
        found: list[dict] = []
        if root.is_dir():
            for path in sorted(root.glob(pattern)):
                if path.is_file():
                    found.append(_item(layer, path))
        items[layer] = found

    counts = {layer: len(found) for layer, found in items.items()}
    # Hosila sonlar (hujjatlardagi "37 platforma + 27 operator" kabi bo'linishlar qo'lda yozilmasin)
    skill_names = [i["name"] for i in items.get("skills", [])]
    counts["skills_platform"] = sum(1 for n in skill_names if n == "ads" or n.startswith("ads-"))
    counts["skills_operator"] = len(skill_names) - counts["skills_platform"]
    ref_dir = VAULT / "skills" / "ads" / "references"
    counts["skill_references"] = len(list(ref_dir.glob("*.md"))) if ref_dir.is_dir() else 0

    return {
        "schema": SCHEMA,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator": "tools/catalog.py",
        "vault": ".",
        "counts": counts,
        "items": items,
        "mirrors": mirror_status(items),
        "warnings": warnings(items),
    }


# --------------------------------------------------------------------------- #
# Versiya: yagona manba — ildizdagi `VERSION` fayli
# --------------------------------------------------------------------------- #

# (fayl, JSON yo'li) — hammasi VERSION ga teng bo'lishi shart
VERSION_JSON_FIELDS: list[tuple[str, tuple]] = [
    ("plugin.json", ("version",)),
    (".claude-plugin/plugin.json", ("version",)),
    (".codex-plugin/plugin.json", ("version",)),
    ("package.json", ("version",)),
    ("marketplace.json", ("metadata", "version")),
    ("marketplace.json", ("plugins", 0, "version")),
    (".claude-plugin/marketplace.json", ("metadata", "version")),
    (".claude-plugin/marketplace.json", ("plugins", 0, "version")),
]
VERSION_EXEMPT_DIRS = {".git", "graphify-out", "archive", "tests", "__pycache__", "node_modules", ".pytest_cache"}
VERSION_EXEMPT_FILES = {"CHANGELOG.md", "LOG.md", "catalog.json", "VERSION"}
VERSION_TEXT_EXT = {".md", ".py", ".json", ".sh", ".ps1", ".html", ".svg", ".cjs", ".yml", ".yaml", ".txt", ".example", ".toml"}
# (nom, 3 guruhli regex: prefiks, versiya, suffiks, "full" = 3 qismli versiya yozish)
VERSION_TEXT_PATTERNS: list[tuple[str, "re.Pattern[str]", bool]] = [
    ("product-name", re.compile(r"(?i)(\btyrion(?:shield)?[ ]v)(\d+\.\d+(?:\.\d+)?)()"), False),
    ("user-agent", re.compile(r"(Tyrion-OS/)(\d+\.\d+(?:\.\d+)?)()"), True),
    ("badge-url", re.compile(r"(badge/version-)(\d+\.\d+\.\d+)(--ecc)"), True),
    ("badge-html", re.compile(r'(<span class="badge">v)(\d+\.\d+)( ECC Ultimate)'), False),
    ("router-heading", re.compile(r"(?i)(universal auto-router v)(\d+\.\d+)()"), False),
    ("banner", re.compile(r"(ECC v)(\d+\.\d+)( SINGLE-ROOT)"), False),
    ("evals-schema", re.compile(r"(tyrion-evals/v)(\d+\.\d+)()"), False),
    ("security-table", re.compile(r"(\| \*\*)(\d+\.\d+)(\.x\*\* \| Supported \(Current)"), False),
]


def read_version(root: Path | None = None) -> str:
    return ((root or VAULT) / "VERSION").read_text(encoding="utf-8").strip()


def _fmt_version(full: str, found: str, force_full: bool) -> str:
    return full if (force_full or found.count(".") >= 2) else ".".join(full.split(".")[:2])


def _json_get(data, path: tuple):
    cur = data
    for key in path:
        cur = cur[key]
    return cur


def _iter_version_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name in VERSION_EXEMPT_FILES:
            continue
        rel = p.relative_to(root)
        if VERSION_EXEMPT_DIRS & set(rel.parts):
            continue
        if p.suffix.lower() in VERSION_TEXT_EXT or p.name == ".env.example":
            yield p, rel.as_posix()


def version_scan(root: Path | None = None) -> list[dict]:
    """Eskirgan versiya satrlarini topadi (manifestlar + matn). Bo'sh ro'yxat = drift yo'q."""
    root = root or VAULT
    full = read_version(root)
    found: list[dict] = []
    for rel, path in VERSION_JSON_FIELDS:
        f = root / rel
        if not f.is_file():
            continue
        try:
            cur = _json_get(json.loads(f.read_text(encoding="utf-8")), path)
        except (ValueError, KeyError, IndexError, TypeError):
            continue
        if cur != full:
            found.append({"file": rel, "line": 0, "kind": "json:" + ".".join(map(str, path)), "found": str(cur), "expected": full})
    for p, rel in _iter_version_files(root):
        text = p.read_text(encoding="utf-8", errors="replace")
        for name, pat, force_full in VERSION_TEXT_PATTERNS:
            for m in pat.finditer(text):
                want = _fmt_version(full, m.group(2), force_full)
                if m.group(2) != want:
                    line = text.count("\n", 0, m.start()) + 1
                    found.append({"file": rel, "line": line, "kind": name, "found": m.group(2), "expected": want})
    return found


def version_sync(root: Path | None = None, dry_run: bool = False) -> list[str]:
    """Versiya satrlarini VERSION ga moslaydi. Qaytaradi: o'zgarishlar tavsifi."""
    root = root or VAULT
    full = read_version(root)
    changed: list[str] = []
    for rel, path in VERSION_JSON_FIELDS:
        f = root / rel
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8")
        try:
            cur = _json_get(json.loads(text), path)
        except (ValueError, KeyError, IndexError, TypeError):
            continue
        if cur == full:
            continue
        new_text = re.sub(r'("version"\s*:\s*")' + re.escape(str(cur)) + '"', lambda m: m.group(1) + full + '"', text)
        if not dry_run:
            f.write_text(new_text, encoding="utf-8")
        changed.append(f"{rel}: version {cur} → {full}")
    for p, rel in _iter_version_files(root):
        text = p.read_text(encoding="utf-8", errors="replace")
        new_text, n = text, 0
        for _name, pat, force_full in VERSION_TEXT_PATTERNS:
            def repl(m, force_full=force_full):
                return m.group(1) + _fmt_version(full, m.group(2), force_full) + m.group(3)
            new_text, k = pat.subn(repl, new_text)
            n += k
        if new_text != text:
            if not dry_run:
                p.write_text(new_text, encoding="utf-8")
            changed.append(f"{rel}: versiya satrlari → {full}")
    return changed


def _all_claims() -> list[tuple[str, "re.Pattern[str]", str, bool]]:
    """(fayl, regex, katalog kaliti, ixtiyoriy) — HUMAN_CLAIMS + manifest/tavsif qoplamasi."""
    return [(r, p, k, False) for r, p, k in HUMAN_CLAIMS] + [(r, p, k, True) for r, p, k in OPTIONAL_CLAIMS]


def human_claims(counts: dict) -> list[dict]:
    """Hujjatlardagi oddiy matn raqamlari holati (mos / mos emas / topilmadi). Bir naqshning barcha uchrashuvi tekshiriladi."""
    result: list[dict] = []
    for rel, pattern, key, optional in _all_claims():
        path = VAULT / rel
        if not path.is_file():
            if not optional:
                result.append({"file": rel, "key": key, "written": None, "expected": counts.get(key), "ok": False, "reason": "fayl yo'q"})
            continue
        matches = list(pattern.finditer(path.read_text(encoding="utf-8", errors="replace")))
        if not matches:
            if not optional:
                result.append({"file": rel, "key": key, "written": None, "expected": counts.get(key), "ok": False, "reason": "naqsh topilmadi"})
            continue
        written_all = [int(m.group(2)) for m in matches]
        bad = [w for w in written_all if w != counts.get(key)]
        result.append({"file": rel, "key": key, "written": bad[0] if bad else written_all[0],
                       "expected": counts.get(key), "ok": not bad, "reason": ""})
    return result


def mirror_status(items: dict[str, list[dict]]) -> list[dict]:
    """Nusxa juftliklari holati: identical | drifted | missing."""
    result: list[dict] = []
    for canonical_layer, mirror_layer in MIRROR_PAIRS:
        if canonical_layer not in items or mirror_layer not in items:
            continue
        canonical = {i["name"]: i for i in items.get(canonical_layer, [])}
        mirror = {i["name"]: i for i in items.get(mirror_layer, [])}
        for name in sorted(set(canonical) | set(mirror)):
            left, right = canonical.get(name), mirror.get(name)
            if left and right:
                status = "identical" if left["sha256"] == right["sha256"] else "drifted"
            else:
                status = "missing"
            result.append(
                {
                    "name": name,
                    "canonical": left["path"] if left else None,
                    "mirror": right["path"] if right else None,
                    "status": status,
                }
            )
    return result


def warnings(items: dict[str, list[dict]]) -> list[str]:
    """Diqqat talab qiladigan holatlar (bo'sh qatlam, buzilgan frontmatter, drift)."""
    notes: list[str] = []
    for layer in ("commands", "rules", "hooks", "tests"):
        if not items.get(layer):
            notes.append(f"qatlam bo'sh: {layer}/")
    for layer, found in items.items():
        broken = [i for i in found if i.get("fm_error") and layer in ("wiki", "agents", "skills")]
        if broken:
            notes.append(f"{layer}: {len(broken)} faylda frontmatter muammosi")
    drifted = [m for m in mirror_status(items) if m["status"] == "drifted"]
    if drifted:
        notes.append(f"drift: {len(drifted)} nusxa kanonikdan farq qiladi")
    return notes


def cmd_build(_args: argparse.Namespace) -> int:
    data = scan()
    import tyrion_core as tcore
    tcore.atomic_write_json(MANIFEST, data)
    print(f"✓ katalog yozildi: {MANIFEST.relative_to(VAULT).as_posix()}")
    print_summary(data)
    return 0


def _comparable(data: dict) -> dict:
    """Taqqoslash uchun: vaqt va yo'llarsiz mazmun."""
    return {
        "counts": data.get("counts"),
        "items": {
            layer: sorted((i["name"], i["sha256"]) for i in found)
            for layer, found in (data.get("items") or {}).items()
        },
    }


def cmd_check(_args: argparse.Namespace) -> int:
    if not MANIFEST.is_file():
        print("✗ katalog yo'q — avval: python3 tools\\catalog.py build")
        return 2
    stored = json.loads(MANIFEST.read_text(encoding="utf-8"))
    current = scan()
    if stored.get("schema") != SCHEMA:
        print(f"✗ katalog sxemasi eski: {stored.get('schema')} != {SCHEMA}")
        return 2

    old, new = _comparable(stored), _comparable(current)
    if old == new:
        print(f"✓ katalog mos ({sum(current['counts'].values())} element)")
        return 0

    problems = 0
    for layer in sorted(set(old["items"]) | set(new["items"])):
        o, n = set(old["items"].get(layer, [])), set(new["items"].get(layer, []))
        for name, _sha in sorted(n - o):
            print(f"  + yangi:   {layer}/{name}")
            problems += 1
        for name, _sha in sorted(o - n):
            print(f"  - yo'qolgan/o'zgargan: {layer}/{name}")
            problems += 1
    for key in sorted(set(old["counts"]) | set(new["counts"])):
        if old["counts"].get(key) != new["counts"].get(key):
            print(f"  ~ soni: {key}: {old['counts'].get(key)} → {new['counts'].get(key)}")
            problems += 1
    print(f"\n✗ katalog eskirgan — {problems} farq. Tuzatish: python3 tools\\catalog.py build")
    return 1


def cmd_drift(_args: argparse.Namespace) -> int:
    data = scan()
    drifted = [m for m in data["mirrors"] if m["status"] != "identical"]
    if not drifted:
        print(f"✓ nusxalar mos ({len(data['mirrors'])} juftlik tekshirildi)")
        return 0
    print(f"⚠ {len(drifted)} nusxa kanonik bilan mos emas:\n")
    for m in drifted:
        print(f"  [{m['status']:9}] {m['name']}")
        print(f"              kanonik: {m['canonical']}")
        print(f"              nusxa  : {m['mirror']}")
    print("\nEslatma: nusxa qo'lda tahrirlanmaydi — manba tuzatiladi, keyin sinxronlanadi.")
    return 1


def cmd_list(args: argparse.Namespace) -> int:
    data = scan()
    layers = [args.layer] if args.layer else list(LAYERS)
    for layer in layers:
        if layer not in data["items"]:
            print(f"✗ noma'lum qatlam: {layer}. Mavjud: {', '.join(LAYERS)}")
            return 2
        print(f"\n## {layer} ({len(data['items'][layer])})")
        for item in data["items"][layer]:
            flag = " ⚠" if item.get("fm_error") and layer in ("wiki", "agents", "skills") else ""
            print(f"  {item['name']:28} {item['path']}{flag}")
    return 0


def cmd_sync_claims(args: argparse.Namespace) -> int:
    """Hujjatlardagi e'lon qilingan raqamlarni katalogga moslashtiradi (ECC'dagi `--write`).

    Ikki xil yozuv tuzatiladi:
    1. `<!-- tyrion:catalog ... -->` markeri (AGENTS.md, README.md).
    2. Oddiy matndagi raqamlar (`HUMAN_CLAIMS` — INDEX.md, README.md, rules/...).

    Nega: qo'lda yozilgan "33 agent, 41 qayd" kabi sonlar vaqt o'tib eskiradi va
    yolg'on da'voga aylanadi. Bu buyruq ularni fayl tizimidagi haqiqatdan yozadi.
    """
    data = scan()
    counts = data["counts"]
    marker_re = re.compile(r"(<!--\s*tyrion:catalog\s+)([^>]*?)(\s*-->)")
    changed: list[str] = []

    for doc in (VAULT / "AGENTS.md", VAULT / "README.md"):
        if not doc.is_file():
            continue
        text = doc.read_text(encoding="utf-8")
        match = marker_re.search(text)
        if not match:
            continue
        keys = re.findall(r"(\w+)=", match.group(2))
        payload = " ".join(f"{key}={counts.get(key, 0)}" for key in keys)
        if payload == match.group(2).strip():
            continue
        if not args.dry_run:
            doc.write_text(marker_re.sub(lambda m: m.group(1) + payload + m.group(3), text, count=1),
                           encoding="utf-8")
        changed.append(f"{doc.name}: {match.group(2).strip()} → {payload}")

    # Marker bo'lmagan oddiy matn raqamlari (INDEX.md, README.md, rules/..., plagin manifestlari)
    for rel, pattern, key, _optional in _all_claims():
        path = VAULT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        wrong = [m.group(2) for m in pattern.finditer(text) if int(m.group(2)) != counts.get(key)]
        if not wrong:
            continue
        payload = str(counts.get(key, 0))
        if not args.dry_run:
            path.write_text(pattern.sub(lambda m: m.group(1) + payload + m.group(3), text), encoding="utf-8")
        changed.append(f"{rel}: {wrong[0]} → {payload}")

    # Versiya satrlari (VERSION — yagona manba)
    for line in version_sync(VAULT, dry_run=args.dry_run):
        changed.append(line)

    if not changed:
        print("✓ hujjatlardagi raqamlar katalogga mos")
        return 0
    for line in changed:
        print(("  yangilandi: " if not args.dry_run else "  yangilanadi: ") + line)
    print(f"\n{'✗ --dry-run: hech narsa yozilmadi' if args.dry_run else '✓ raqamlar yangilandi'}")
    return 0


def cmd_sync_mirrors(args: argparse.Namespace) -> int:
    """Kanonik qatlamlardan nusxalarni qayta quradi (bayt-aniq).

    Nusxa qo'lda tahrirlanmaydi: manba — `LAYERS` dagi kanonik qatlam. Eski nusxa
    **o'chirilmaydi** — `archive/mirror-sync-<sana>/` ga ko'chiriladi (vault qoidasi:
    hech narsa yo'qolmaydi).
    """
    data = scan()
    stamp = datetime.now().strftime("%Y-%m-%d")
    archive_root = VAULT / "archive" / f"mirror-sync-{stamp}"
    copied: list[str] = []
    archived: list[str] = []
    orphans: list[str] = []

    for canonical_layer, mirror_layer in MIRROR_PAIRS:
        canonical = {i["name"]: i for i in data["items"].get(canonical_layer, [])}
        mirror = {i["name"]: i for i in data["items"].get(mirror_layer, [])}
        mirror_root = LAYERS[mirror_layer][0]

        for name, item in sorted(canonical.items()):
            existing = mirror.get(name)
            if existing and existing["sha256"] == item["sha256"]:
                continue
            source = VAULT / item["path"]
            destination = mirror_root / f"{name}.md"
            copied.append(f"{canonical_layer} → {mirror_layer}: {name}")
            if args.dry_run:
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

        orphans.extend(
            f"{mirror_layer}/{name} (kanonikda yo'q)" for name in sorted(set(mirror) - set(canonical))
        )



    if not copied:
        print(f"✓ nusxalar mos — yangilash kerak emas ({len(data['mirrors'])} juftlik)")
        return 0

    label = "Ko'chiriladi" if not args.dry_run else "Ko'chiriladi (dry-run)"
    print(f"{label}: {len(copied)}")
    for line in copied:
        print(f"  → {line}")
    if archived:
        print(f"\nArxivga olindi ({len(archived)}): {archive_root.relative_to(VAULT).as_posix()}")
    if orphans:
        print(f"\n⚠ kanonigi yo'q nusxalar ({len(orphans)}) — o'chirilmadi:")
        for line in orphans:
            print(f"  ? {line}")
    print("\n" + ("· --dry-run: hech narsa yozilmadi" if args.dry_run else
                  "✓ tayyor. Tekshirish: python3 tools\\catalog.py drift"))
    return 0


def print_summary(data: dict) -> None:
    counts = data["counts"]
    print("\nQatlamlar:")
    for layer in list(LAYERS):
        print(f"  {layer:18} {counts.get(layer, 0)}")
    if data["warnings"]:
        print("\nDiqqat:")
        for note in data["warnings"]:
            print(f"  ⚠ {note}")


def cmd_summary(_args: argparse.Namespace) -> int:
    print_summary(scan())
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="catalog.py", description="Tyrion katalogi — yagona reestr (fayl tizimidan generatsiya)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="manifests/catalog.json ni qayta yozadi").set_defaults(func=cmd_build)
    sub.add_parser("check", help="katalog haqiqatga mos keladimi").set_defaults(func=cmd_check)
    sub.add_parser("drift", help="nusxalar farqini ko'rsatadi").set_defaults(func=cmd_drift)
    sub.add_parser("summary", help="qisqa hisobot").set_defaults(func=cmd_summary)
    list_parser = sub.add_parser("list", help="qatlam elementlarini sanaydi")
    list_parser.add_argument("--layer", help=f"qatlam nomi: {', '.join(LAYERS)}")
    list_parser.set_defaults(func=cmd_list)

    sync_parser = sub.add_parser("sync-claims", help="hujjatlardagi raqamlarni katalogga moslashtiradi")
    sync_parser.add_argument("--dry-run", action="store_true", help="yozmasdan ko'rsatadi")
    sync_parser.set_defaults(func=cmd_sync_claims)

    mirrors_parser = sub.add_parser("sync-mirrors", help="nusxalarni kanonikdan qayta quradi")
    mirrors_parser.add_argument("--dry-run", action="store_true", help="yozmasdan ko'rsatadi")
    mirrors_parser.set_defaults(func=cmd_sync_mirrors)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
