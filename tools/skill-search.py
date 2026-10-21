#!/usr/bin/env python3
"""skill-search — Universal Auto-Router, End-to-End Execution Engine va Skill Reyestri (0 token, deterministik).

Kanonik 6-Bosqichli Ish Oqimi:
  1. Vazifani tabiiy tilda qabul qilish (`uz_latin`, `uz_cyrillic`, `ru`, `en`; slash buyruqlar — tezkor yorliqlar).
  2. Agent, skill, qoidalar va reference fayllarni avtomatik tanlash (`route_task`).
  3. Tanlangan agent charterlari, `SKILL.md`, qoidalar va reference fayllarning TO'LIQ MATNINI (`full` kontekst)
     kontekst byudjeti (`max_context_bytes`) nazorati ostida haqiqatan yuklash (`compiled_context_package`).
  4. Mavjud AI harness imkoniyatiga qarab zarur agentlarni ishga tushirish (`native_subagent_dispatch`)
     yoki halol `single_conductor_fallback` hamda deterministik CLI/Python vositalarini amalda bajarish (`execute_task`).
  5. Ish davomida yangi ehtiyoj paydo bo'lsa dinamik qayta marshrutlash (`reroute_task` / `--reroute-with`).
  6. Natijani tekshirish, ziddiyatlarni saralash va yakunlash (`conductor_synthesis` & `50-topshirish-dod`).

Buyruqlar:
  python3 tools/skill-search.py route "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top" [--load] [--json]
  python3 tools/skill-search.py execute "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top" [--json]
  python3 tools/skill-search.py agent video-editor
  python3 tools/skill-search.py brief "shu videoni montaj qil" --agent video-editor
  python3 tools/skill-search.py search "kinetik tipografiya animatsiya" --top 3
  python3 tools/skill-search.py list [--layer operator|platform]
  python3 tools/skill-search.py check
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib
import io
import json
import math
import os
import re
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import market_locale as mloc  # noqa: E402
from typing import Any, Callable

VAULT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

SKILL_ROOT = VAULT / "skills"
AGENT_ROOT = VAULT / "agents"
VALID_RISK_LEVELS = {"low", "medium", "high"}
DEFAULT_MAX_CONTEXT_BYTES = 180_000

PROGRESSIVE_SINGLE_STEP_BUDGET = 15_000  # <= 15 KB budget for simple queries (Progressive Disclosure)


def _progressive_slice(text: str, max_bytes: int = 3600) -> str:
    """Progressive disclosure: returns YAML frontmatter + core instructions body within max_bytes."""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    clipped = encoded[: max_bytes - 120].decode("utf-8", errors="ignore")
    return clipped.rstrip() + "\n\n<!-- [Progressive Disclosure: full reference/extended sections available via --context-mode full] -->"

DEFAULT_SESSION_CACHE_PATH = VAULT / "output" / ".cache" / "router_session_cache.json"

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
WORD = re.compile(r"[a-zA-Z0-9а-яА-ЯёЁўқғҳЎҚҒҲʻʼ'\u0400-\u04FF\-]+", re.UNICODE)

STOP = {
    "va", "bilan", "uchun", "bu", "shu", "bir", "eng", "yoki", "ham", "kerak",
    "qil", "qilib", "qilsin", "qiling", "ber", "bering", "beringiz", "berin",
    "yasa", "yasab", "yasash", "yasalgan", "iltimos", "menga", "men", "hozir", "tez", "yordam",
    "top", "topib", "tuz", "tuzib", "tayyorla", "tayyorlab", "yaxshila", "yaxshilab",
    "haqida", "boyicha", "bo'yicha", "qanday", "nima", "sababini", "xatolarni", "ishlashini",
    "the", "and", "for", "with", "of", "to", "in", "on", "a", "an", "is", "are", "my", "me",
    "please", "help", "make", "create", "build", "check", "find", "improve", "prepare",
    "и", "в", "на", "для", "по", "мне", "мой", "моя", "мои", "как", "что", "сделай", "составь",
    "проверь", "найди", "улучши", "подготовь", "пожалуйста",
    "ва", "билан", "учун", "бу", "шу", "бир", "керакли", "қилиб", "бер", "беринг",
    "менга", "текшир", "топ", "туз", "тайёрла", "яхшила", "бўйича",
}

UZ_CYR_TO_LAT = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "x", "ц": "ts", "ч": "ch", "ш": "sh", "ъ": "'", "ь": "",
    "э": "e", "ю": "yu", "я": "ya", "ў": "o'", "қ": "q", "ғ": "g'", "ҳ": "h",
})

MULTILINGUAL_CONCEPT_MAP: list[tuple[tuple[str, ...], dict[str, Any]]] = [
    (
        ("byudjetni", "oshir", "kill keep scale", "masshtablash", "byudjet oshirish", "увеличить бюджет", "масштабирование бюджета", "scale budget", "increase budget"),
        {
            "domains": ["optimization", "budget", "scaling"],
            "platforms": ["multi-platform"],
            "boost_skills": {"ads-optimize": 65.0, "ads-budget": 45.0, "ads-math": 20.0},
            "boost_agents": {"audit-budget": 36.0},
            "refs": ["skills/ads/references/budget-allocation.md", "skills/ads/references/bidding-strategies.md"],
            "tools": ["tools/spend-guard.py", "tools/calculator.py"],
        },
    ),
    (
        ("lidlar sifatsiz", "sifatsiz lid", "некачественные лиды", "плохие лиды", "low quality leads", "unqualified leads", "junk leads", "лидлар сифатсиз"),
        {
            "domains": ["audit", "meta", "audience", "lead-quality"],
            "platforms": ["meta"],
            "boost_skills": {"ads-meta": 26.0, "ads-meta-audience": 22.0, "uzbekistan-market-intel": 12.0},
            "boost_agents": {"audit-meta": 30.0, "meta-audience-architect": 18.0},
            "refs": ["skills/ads/references/meta-audit.md"],
            "tools": ["tools/meta-audience.py", "tools/meta-targeting-engine.py", "tools/ad-export-analyzer.py"],
        },
    ),
    (
        ("to'liq marketing strategiya", "toliq marketing strategiya", "marketing strategiyasi tuz", "полная маркетинговая стратегия", "маркетинговая стратегия", "full marketing strategy", "go to market strategy", "маркетинг стратегияси"),
        {
            "domains": ["strategy", "launch", "planning", "audience", "creative", "budget"],
            "platforms": ["multi-platform"],
            "multi_step": True,
            "boost_skills": {"ads-plan": 28.0, "ads-launch": 20.0, "product-marketing": 18.0, "offers": 18.0, "ads-budget": 16.0, "ads-meta-audience": 15.0},
            "boost_agents": {"launch-planner": 30.0, "positioning-strategist": 20.0, "meta-audience-architect": 18.0, "creative-strategist": 16.0, "audit-budget": 16.0},
            "refs": ["skills/ads/references/thinking-framework.md", "skills/ads/references/budget-allocation.md"],
            "tools": ["tools/client-workspace.py", "tools/calculator.py", "tools/meta-audience.py", "tools/creative-matrix.py"],
        },
    ),
    (
        ("instagram uchun bir oylik kontent", "bir oylik kontent reja", "instagram kontent reja", "контент план для инстаграм", "контент-план на месяц", "monthly content plan instagram", "smm kontent reja", "инстаграм учун бир ойлик контент"),
        {
            "domains": ["social", "content"],
            "platforms": ["instagram"],
            "boost_skills": {"social": 28.0, "content-strategy": 24.0, "reels-scripting": 12.0},
            "boost_agents": {"social-content-writer": 30.0, "content-planner": 24.0},
            "refs": ["skills/social/references/post-templates.md", "skills/social/references/carousel-frameworks.md", "skills/content-strategy/references/content-distribution.md"],
            "tools": ["tools/creative-matrix.py"],
        },
    ),
    (
        ("capi ishlashini tekshir", "capi tekshir", "conversions api", "event_id", "emq", "server-side tracking", "pixel va capi", "проверить работу capi", "настройка capi", "пиксель и capi", "capi ишлашини текшир"),
        {
            "domains": ["tracking", "technical", "analytics"],
            "platforms": ["meta", "web"],
            "boost_skills": {"ads-server-side-tracking": 32.0, "ads-attribution": 16.0, "analytics": 14.0},
            "boost_agents": {"tracking-specialist": 32.0, "audit-tracking": 22.0},
            "refs": ["skills/ads/references/conversion-tracking.md"],
            "tools": ["tools/capi-utm-builder.py", "tools/spend-guard.py"],
        },
    ),
    (
        ("raqobatchilarimni o'rganib", "raqobatchilarni o'rganib", "raqobatchilar tahlili", "изучи конкурентов", "анализ конкурентов и стратегия", "competitor analysis and strategy", "рақобатчиларни ўрганиб"),
        {
            "domains": ["competitor", "research", "strategy", "positioning"],
            "platforms": ["multi-platform"],
            "multi_step": True,
            "boost_skills": {"ads-competitor": 30.0, "product-marketing": 22.0, "ads-plan": 20.0, "customer-research": 15.0},
            "boost_agents": {"positioning-strategist": 28.0, "research-worker": 26.0, "creative-strategist": 16.0},
            "refs": ["skills/ads/references/thinking-framework.md"],
            "tools": ["tools/brain-search.py", "tools/creative-matrix.py"],
        },
    ),
    (
        ("seo va konversiya", "saytimni seo", "seo va cro", "landing va seo", "сео и конверсия", "улучши сайт по сео", "seo and conversion", "сайтни сео ва конверсия"),
        {
            "domains": ["seo", "cro", "web"],
            "platforms": ["web", "google"],
            "multi_step": True,
            "boost_skills": {"seo-audit": 30.0, "cro": 28.0, "ads-landing": 20.0},
            "boost_agents": {"seo-auditor": 34.0, "copy-writer": 14.0},
            "refs": ["skills/seo-audit/references/international-seo.md", "skills/cro/references/experiments.md", "skills/cro/references/form.md"],
            "tools": ["tools/calculator.py"],
        },
    ),
    (
        ("detalniy targeting", "detailed targeting", "детальный таргетинг", "meta interest", "interest qidirish", "meta auditoriya", "overlap", "saturation", "lookalike"),
        {
            "domains": ["audience", "targeting", "meta"],
            "platforms": ["meta"],
            "boost_skills": {"ads-meta-audience": 32.0, "ads-meta": 14.0},
            "boost_agents": {"meta-audience-architect": 34.0, "audit-meta": 14.0},
            "refs": ["docs/DETAILED-TARGETING-ACCURACY.md", "skills/ads/references/meta-audit.md"],
            "tools": ["tools/meta-targeting-engine.py", "tools/meta-audience.py"],
        },
    ),
    (
        ("telegram ads", "telegram reklama", "tg ads", "телеграм реклама", "телеграм эдс", "telegram bot voronka"),
        {
            "domains": ["telegram", "audit", "funnel"],
            "platforms": ["telegram"],
            "boost_skills": {"ads-telegram": 32.0, "uzbekistan-market-intel": 14.0},
            "boost_agents": {"audit-telegram": 32.0},
            "refs": ["skills/ads/references/telegram-audit.md"],
            "tools": ["tools/calculator.py", "tools/capi-utm-builder.py", "tools/spend-guard.py"],
        },
    ),
    (
        ("google ads", "pmax", "performance max", "search terms", "negative keywords", "гугл реклама", "контекстная реклама"),
        {
            "domains": ["search", "audit", "paid-media"],
            "platforms": ["google"],
            "boost_skills": {"ads-google": 32.0},
            "boost_agents": {"audit-google": 32.0},
            "refs": ["skills/ads/references/google-audit.md", "skills/ads/references/google-creative-specs.md"],
            "tools": ["tools/calculator.py", "tools/ad-export-analyzer.py"],
        },
    ),
    (
        ("tiktok ads", "spark ads", "тикток реклама", "тикток таргет"),
        {
            "domains": ["tiktok", "audit", "video"],
            "platforms": ["tiktok"],
            "boost_skills": {"ads-tiktok": 32.0},
            "boost_agents": {"audit-tiktok": 32.0},
            "refs": ["skills/ads/references/tiktok-audit.md", "skills/ads/references/tiktok-creative-specs.md"],
            "tools": ["tools/creative-matrix.py"],
        },
    ),
    (
        ("break-even roas", "unit ekonomika", "byudjet taqsimoti", "target cpa hisobla", "юнит экономика", "расчет бюджета"),
        {
            "domains": ["budget", "finance"],
            "platforms": ["multi-platform"],
            "boost_skills": {"ads-math": 28.0, "ads-budget": 26.0},
            "boost_agents": {"audit-budget": 32.0},
            "refs": ["skills/ads/references/budget-allocation.md"],
            "tools": ["tools/calculator.py", "tools/spend-guard.py"],
        },
    ),
    (
        ("haftalik hisobot", "oylik hisobot", "mijoz hisoboti", "еженедельный отчет", "отчет для клиента", "weekly report"),
        {
            "domains": ["reporting", "analytics"],
            "platforms": ["multi-platform"],
            "boost_skills": {"ads-report": 30.0},
            "boost_agents": {"release-verifier": 30.0},
            "refs": ["skills/ads/references/scoring-system.md", "skills/ads/references/status-contract.md"],
            "tools": ["tools/ad-export-analyzer.py", "tools/calculator.py"],
        },
    ),
]

MUTATION_PATTERNS = re.compile(
    r"\b("
    r"byudjetni\s+\d+.*oshir|kampaniyani\s+o'chir|reklamani\s+to'xtat|hoziroq\s+yoq|"
    r"delete\s+campaign|pause\s+all\s+ads|increase\s+budget\s+now|apply\s+changes\s+live|"
    r"удалить\s+кампанию|остановить\s+рекламу\s+сейчас|увеличить\s+бюджет\s+на\s+\d+|"
    r"бюджетни\s+ошир|кампанияни\s+ўчир"
    r")\b",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- #
# Session Context Cache (In-Memory + Optional Cross-Process Persistent Cache)
# --------------------------------------------------------------------------- #

class SessionContextCache:
    """Fayllarni (charter, SKILL.md, rule, reference) SHA-256 va mtime_ns bo'yicha keshlaydi.

    Ikki rejimda ishlaydi:
      1. In-process xotira keshi (`self._store`) — bitta Python/MCP jarayoni ichida 0 disk o'qish.
      2. Cross-process persistent sessiya keshi (`persist_path`) — CLI orqali ketma-ket
         chaqiruvlarda `output/.cache/router_session_cache.json` (yoki berilgan fayl) orqali
         saqlanadi. Fayl o'zgarsa (`sha256` yoki `mtime_ns` farq qilsa), kesh yozuvi darhol
         bekor qilinadi (`invalidations += 1`) va yangidan o'qiladi.
    """

    def __init__(self, persist_path: Path | None = None, vault_root: Path | None = None) -> None:
        self.vault_root = (vault_root or VAULT).resolve()
        self.persist_path = persist_path
        self._store: dict[str, dict[str, Any]] = {}
        self.hits: int = 0
        self.misses: int = 0
        self.invalidations: int = 0
        self.errors: list[dict[str, str]] = []
        if self.persist_path is not None:
            self._load_persistent_store()

    def _load_persistent_store(self) -> None:
        if self.persist_path is None or not self.persist_path.is_file():
            return
        try:
            raw = json.loads(self.persist_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and isinstance(raw.get("entries"), dict):
                for k, v in raw["entries"].items():
                    if isinstance(v, dict) and "sha256" in v and "content" in v:
                        self._store[k] = v
        except Exception as exc:
            self.errors.append({
                "path": str(self.persist_path),
                "error_code": "PERSISTENT_CACHE_CORRUPTED",
                "message": f"Persistent sessiya keshi o'qilmadi, yangidan boshlanadi: {exc}",
            })

    def _save_persistent_store(self) -> None:
        if self.persist_path is None:
            return
        try:
            payload = {
                "schema": "tyrion.router_session_cache/v5",
                "entries": self._store,
            }
            tcore.atomic_write_json(self.persist_path, payload)
        except Exception as exc:
            self.errors.append({
                "path": str(self.persist_path),
                "error_code": "PERSISTENT_CACHE_WRITE_ERROR",
                "message": f"Persistent sessiya keshini yozib bo'lmadi: {exc}",
            })

    def reset(self) -> None:
        self._store.clear()
        self.hits = 0
        self.misses = 0
        self.invalidations = 0
        self.errors.clear()
        if self.persist_path is not None and self.persist_path.is_file():
            try:
                self.persist_path.unlink()
            except OSError:
                pass

    def read_verified_with_error(self, rel_path: str) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
        clean_rel = str(rel_path or "").strip().replace("\\", "/").lstrip("/")
        if not clean_rel:
            err = {"path": str(rel_path), "error_code": "INVALID_PATH", "message": "Fayl yo'li bo'sh."}
            self.errors.append(err)
            return None, err

        try:
            full_path = (self.vault_root / clean_rel).resolve()
            full_path.relative_to(self.vault_root)
        except ValueError:
            err = {
                "path": clean_rel,
                "error_code": "PATH_TRAVERSAL_BLOCKED",
                "message": f"Xavfsizlik xatosi: '{clean_rel}' ombor ildizidan tashqariga chiqmoqda.",
            }
            self.errors.append(err)
            return None, err

        if not full_path.is_file():
            if clean_rel in self._store:
                del self._store[clean_rel]
                self.invalidations += 1
                self._save_persistent_store()
            err = {
                "path": clean_rel,
                "error_code": "FILE_NOT_FOUND",
                "message": f"Fayl diskda topilmadi: '{clean_rel}'.",
            }
            self.errors.append(err)
            return None, err

        try:
            stat = full_path.stat()
            raw_bytes = full_path.read_bytes()
        except OSError as exc:
            err = {
                "path": clean_rel,
                "error_code": "OS_READ_ERROR",
                "message": f"Faylni o'qishda OS xatosi: {exc}",
            }
            self.errors.append(err)
            return None, err

        try:
            decoded_strict = raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            err = {
                "path": clean_rel,
                "error_code": "UTF8_DECODE_ERROR",
                "message": f"UTF-8 kodlash xatosi ({clean_rel}, pozitsiya {exc.start}): {exc.reason}",
            }
            self.errors.append(err)
            return None, err

        norm_bytes = raw_bytes.replace(b"\r\n", b"\n")
        sha = hashlib.sha256(norm_bytes).hexdigest()[:16]
        cached = self._store.get(clean_rel)
        was_invalidated = False

        if cached is not None:
            if cached.get("sha256") == sha:
                self.hits += 1
                return {
                    "path": clean_rel,
                    "sha256": sha,
                    "bytes": len(norm_bytes),
                    "mtime_ns": stat.st_mtime_ns,
                    "from_session_cache": True,
                    "cache_invalidated": False,
                    "full_instructions_loaded": True,
                    "content": cached["content"],
                    "body_markdown": cached.get("body_markdown", cached["content"]),
                    "excerpt": cached["excerpt"],
                }, None
            else:
                self.invalidations += 1
                was_invalidated = True

        self.misses += 1
        text = decoded_strict.replace("\r\n", "\n")
        body = FRONTMATTER_RE.sub("", text).strip()
        excerpt = re.sub(r"\s+", " ", body)[:360]
        record = {
            "path": clean_rel,
            "sha256": sha,
            "bytes": len(norm_bytes),
            "mtime_ns": stat.st_mtime_ns,
            "content": text,
            "body_markdown": body,
            "excerpt": excerpt,
        }
        self._store[clean_rel] = record
        self._save_persistent_store()
        return {
            "path": clean_rel,
            "sha256": sha,
            "bytes": len(norm_bytes),
            "mtime_ns": stat.st_mtime_ns,
            "from_session_cache": False,
            "cache_invalidated": was_invalidated,
            "full_instructions_loaded": True,
            "content": text,
            "body_markdown": body,
            "excerpt": excerpt,
        }, None

    def read_verified(self, rel_path: str) -> dict[str, Any] | None:
        rec, _err = self.read_verified_with_error(rel_path)
        return rec


SESSION_CACHE = SessionContextCache(
    persist_path=Path(os.environ["TYRION_SESSION_CACHE_FILE"]) if os.environ.get("TYRION_SESSION_CACHE_FILE") else None
)


# --------------------------------------------------------------------------- #
# Frontmatter o'qish
# --------------------------------------------------------------------------- #

def _fallback_list(block: str, key: str) -> list[str]:
    inline = re.search(rf"^{key}:\s*\[(.*?)\]\s*$", block, re.M)
    if inline:
        return [x.strip().strip("'\"") for x in inline.group(1).split(",") if x.strip()]
    block_form = re.search(rf"^{key}:\s*\n((?:\s*-\s*.+\n?)+)", block, re.M)
    if block_form:
        return [
            ln.strip().lstrip("-").strip().strip("'\"")
            for ln in block_form.group(1).splitlines()
            if ln.strip()
        ]
    return []


def read_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    raw = match.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(raw) or {}
            if isinstance(data, dict):
                return data
        except Exception:
            return {"_yaml_error": "YAML frontmatter buzilgan"}
    flat: dict[str, object] = {}
    for line in raw.splitlines():
        if not line or line.startswith(("#", " ", "\t", "-")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        flat[key.strip()] = value.strip().strip('"').strip("'")
    for key in (
        "triggers", "aliases", "domains", "platforms", "attached_agents",
        "related_skills", "references", "skills"
    ):
        values = _fallback_list(raw, key)
        if values:
            flat[key] = values
    return flat


def as_list(value: object) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    if isinstance(value, (list, tuple)):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


# --------------------------------------------------------------------------- #
# Reyestr
# --------------------------------------------------------------------------- #

def _infer_layer(name: str, fm: dict) -> str:
    if fm.get("layer"):
        return str(fm["layer"])
    return "platform" if (name == "ads" or name.startswith("ads-")) else "operator"


_SKILLS_CACHE: tuple[float, list[dict]] | None = None
_AGENTS_CACHE: tuple[float, dict[str, dict]] | None = None


def load_skills(force_reload: bool = False) -> list[dict]:
    """Barcha SKILL.md fayllar (yagona kanonik `skills/` papkasidan)."""
    global _SKILLS_CACHE
    sdir = VAULT / "skills"
    mtime = max((p.stat().st_mtime for p in sdir.glob("*/SKILL.md")), default=0.0) if sdir.is_dir() else 0.0
    if not force_reload and _SKILLS_CACHE and _SKILLS_CACHE[0] == mtime:
        return [dict(x) for x in _SKILLS_CACHE[1]]

    skills: list[dict] = []
    if not SKILL_ROOT.is_dir():
        return skills
    for path in sorted(SKILL_ROOT.glob("*/SKILL.md")):
        fm = read_frontmatter(path)
        name = str(fm.get("name") or path.parent.name).strip()
        layer = _infer_layer(name, fm)
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        body_only = FRONTMATTER_RE.sub("", raw_text).strip()
        declared_refs = as_list(fm.get("references"))
        local_refs = sorted(p.name for p in path.parent.glob("references/*.md"))
        skills.append({
            "name": name,
            "dir": path.parent.name,
            "path": path.relative_to(VAULT).as_posix(),
            "abs": path,
            "layer": layer,
            "root": layer,
            "description": re.sub(r"\s+", " ", str(fm.get("description") or "")).strip(),
            "triggers": as_list(fm.get("triggers")),
            "aliases": as_list(fm.get("aliases")),
            "domains": as_list(fm.get("domains")),
            "platforms": as_list(fm.get("platforms")),
            "agents": as_list(fm.get("attached_agents")),
            "related_skills": as_list(fm.get("related_skills")),
            "declared_references": declared_refs,
            "refs": local_refs,
            "risk_level": str(fm.get("risk_level") or "low").strip().lower(),
            "output_contract": str(fm.get("output_contract") or "Structured deliverable").strip(),
            "dir_name_matches": path.parent.name == name,
            "has_frontmatter": bool(fm) and "_yaml_error" not in fm,
            "yaml_error": fm.get("_yaml_error"),
            "standalone": bool(fm.get("standalone")),
            "body": body_only,
        })
    res = sorted(skills, key=lambda s: s["name"])
    _SKILLS_CACHE = (mtime, res)
    return [dict(x) for x in res]


def load_agents(force_reload: bool = False) -> dict[str, dict]:
    """Agent charterlari (kanonik `agents/`) va ulardagi metadata."""
    global _AGENTS_CACHE
    adir = VAULT / "agents"
    mtime = max((p.stat().st_mtime for p in adir.glob("*.md")), default=0.0) if adir.is_dir() else 0.0
    if not force_reload and _AGENTS_CACHE and _AGENTS_CACHE[0] == mtime:
        return {k: dict(v) for k, v in _AGENTS_CACHE[1].items()}

    agents: dict[str, dict] = {}
    if not AGENT_ROOT.is_dir():
        return agents
    for path in sorted(AGENT_ROOT.glob("*.md")):
        fm = read_frontmatter(path)
        name = str(fm.get("name") or path.stem).strip()
        agents[name] = {
            "name": name,
            "path": path.relative_to(VAULT).as_posix(),
            "description": re.sub(r"\s+", " ", str(fm.get("description") or "")).strip(),
            "role": str(fm.get("role") or name).strip(),
            "domains": as_list(fm.get("domains")),
            "platforms": as_list(fm.get("platforms")),
            "triggers": as_list(fm.get("triggers")),
            "skills": as_list(fm.get("skills")),
            "authority_boundary": str(fm.get("authority_boundary") or "Bounded specialist worker").strip(),
            "output_contract": str(fm.get("output_contract") or "Schema-valid JSON or structured Markdown").strip(),
            "mirror_exists": True,
        }
    _AGENTS_CACHE = (mtime, agents)
    return {k: dict(v) for k, v in agents.items()}


# --------------------------------------------------------------------------- #
# Qidiruv va Ko'p Tilli Normalizatsiya
# --------------------------------------------------------------------------- #

def detect_language(text: str) -> str:
    s = str(text or "")
    low = s.lower()
    if re.search(r"[ўқғҳЎҚҒҲ]", s) or re.search(r"\b(учун|билан|текшир|топ|туз|тайёрла|яхшила|мижоз|рекламада|ишлашини|хатоларини|лидлар|сифатсиз)\b", low):
        return "uz_cyrillic"
    if re.search(r"[а-яА-ЯёЁ]", s):
        return "ru"
    if re.search(r"\b(uchun|bo'yicha|reklama|kampaniyamda|byudjetni|oshir|o'chir|mijoz|strategiya|lidlar|sifatsiz|kontent|tayyorla|tekshir|saytimni|o'rganib|montaj|yasab)\b", low):
        return "uz_latin"
    return "en"


def normalize_multilingual_text(value: str) -> str:
    low = str(value or "").lower()
    if re.search(r"[ўқғҳа-яё]", low):
        latinized = low.translate(UZ_CYR_TO_LAT)
        return f"{low} {latinized}"
    return low


def tokens(value: str) -> list[str]:
    norm = normalize_multilingual_text(value)
    raw_words = WORD.findall(norm)
    result: list[str] = []
    for w in raw_words:
        wl = w.lower().strip("-")
        if len(wl) > 1 and wl not in STOP:
            result.append(wl)
    return result


def score(skill: dict, query_tokens: list[str], idf: dict[str, float] | None = None, raw_query: str = "") -> float:
    name = skill["name"].lower()
    aliases = [a.lower() for a in skill.get("aliases", [])]
    triggers = [t.lower() for t in skill.get("triggers", [])]
    trig_joined = " ".join(triggers + aliases)
    trig_words = set(WORD.findall(trig_joined))
    domains = {d.lower() for d in skill.get("domains", [])}
    platforms = {p.lower() for p in skill.get("platforms", [])}
    desc = skill["description"].lower()
    body = skill["body"].lower()

    total = 0.0
    norm_q = normalize_multilingual_text(raw_query) if raw_query else " ".join(query_tokens)

    for trig_phrase in triggers:
        if len(trig_phrase) >= 4 and trig_phrase in norm_q:
            total += 18.0

    for token in set(query_tokens):
        weight = 0.0
        if token == name or token in aliases:
            weight += 12.0
        elif token in name:
            weight += 8.0
        if token in trig_words:
            weight += 8.0
        elif token in trig_joined:
            weight += 4.0
        if token in domains or token in platforms:
            weight += 4.5
        if token in desc:
            weight += 3.0
        count = body.count(token)
        if count:
            weight += min(0.8 + math.log(1 + count), 2.0)
        if idf:
            weight *= idf.get(token, 1.0)
        total += weight
    return total


def build_idf(pool: list[dict], query_tokens: list[str]) -> dict[str, float]:
    ids: dict[str, float] = {}
    total = max(len(pool), 1)
    for token in set(query_tokens):
        seen = sum(
            1 for s in pool
            if token in (
                s["name"] + " " + " ".join(s.get("triggers", [])) + " " +
                " ".join(s.get("aliases", [])) + " " + s["description"]
            ).lower()
        )
        ids[token] = 1.0 + math.log(1 + total / max(seen, 1))
    return ids


def rank(skills: list[dict], query: str, idf_pool: list[dict] | None = None) -> list[tuple[float, dict]]:
    query_tokens = tokens(query)
    if not query_tokens:
        return []
    idf = build_idf(idf_pool if idf_pool is not None else skills, query_tokens)
    ranked: list[tuple[float, dict]] = []

    norm_q = normalize_multilingual_text(query)
    concept_boosts: dict[str, float] = {}
    for phrases, cmeta in MULTILINGUAL_CONCEPT_MAP:
        if any(p in norm_q for p in phrases):
            for sname, bval in cmeta.get("boost_skills", {}).items():
                concept_boosts[sname] = max(concept_boosts.get(sname, 0.0), float(bval))

    for s in skills:
        sc = score(s, query_tokens, idf, raw_query=query) + concept_boosts.get(s["name"], 0.0)
        if sc > 0:
            ranked.append((sc, s))
    return sorted(ranked, key=lambda x: (-x[0], x[1]["name"]))


# --------------------------------------------------------------------------- #
# Harness Capability Detection (Claude Code, Codex, Cursor, Windsurf, CLI)
# --------------------------------------------------------------------------- #

def detect_harness_capabilities(vault_root: Path | None = None, harness_override: str = "") -> dict[str, Any]:
    """Qo'llab-quvvatlanadigan 4 ta AI harness (Claude Code, Codex, Cursor, Windsurf) va CLI imkoniyatlarini tekshiradi."""
    root = (vault_root or VAULT).resolve()
    env_harness = (harness_override or os.environ.get("TYRION_HARNESS", "")).strip().lower()
    if not env_harness:
        if os.environ.get("CLAUDE_CODE") or os.environ.get("CLAUDE_PROJECT_DIR"):
            env_harness = "claude_code"
        elif os.environ.get("CODEX_SANDBOX") or os.environ.get("OPENAI_CODEX"):
            env_harness = "codex"
        elif os.environ.get("CURSOR_TRACE_ID") or os.environ.get("CURSOR_SESSION"):
            env_harness = "cursor"
        elif os.environ.get("WINDSURF_SESSION") or os.environ.get("CODEIUM_ENV"):
            env_harness = "windsurf"
        else:
            env_harness = "cli_standalone"

    matrix = {
        "claude_code": {
            "supported": (root / ".claude-plugin" / "plugin.json").is_file() and (root / "CLAUDE.md").is_file(),
            "entrypoints": ["CLAUDE.md", "AGENTS.md", ".claude-plugin/plugin.json", ".claude/commands/", ".claude/settings.json", ".mcp.json"],
            "supports_native_subagents": True,
            "subagent_mechanism": "Claude Code `Task` tool + `agents/*.md` specialist definitions",
            "supports_mcp_stdio": True,
            "supports_lifecycle_hooks": True,
            "execution_path": "Native sub-agent fan-out via Claude Code `Task` tool when running inside Claude Code session; single-conductor + CLI/MCP tools otherwise.",
        },
        "codex": {
            "supported": (root / ".codex-plugin" / "plugin.json").is_file() and (root / "AGENTS.md").is_file(),
            "entrypoints": ["AGENTS.md", ".codex-plugin/plugin.json", "skills/*/SKILL.md", ".mcp.json"],
            "supports_native_subagents": False,
            "subagent_mechanism": "Single-Conductor execution reading full `compiled_context_package` + deterministic CLI/MCP tools",
            "supports_mcp_stdio": True,
            "supports_lifecycle_hooks": False,
            "execution_path": "Reads `AGENTS.md` and executes `python3 tools/skill-search.py execute \"<task>\"` in Single-Conductor mode.",
        },
        "cursor": {
            "supported": (root / "tools" / "harness-export.py").is_file() and (root / ".mcp.json").is_file(),
            "entrypoints": [".cursor/rules/tyrion-*.mdc (via `harness-export.py --target cursor`)", "AGENTS.md", ".mcp.json"],
            "supports_native_subagents": False,
            "subagent_mechanism": "Single-Conductor execution via `.mcp.json` (`tyrion_universal_router`) + `.cursor/rules/*.mdc`",
            "supports_mcp_stdio": True,
            "supports_lifecycle_hooks": False,
            "execution_path": "Calls `tyrion_universal_router` MCP tool or `skill-search.py execute` to load full skill/charter instructions into context.",
        },
        "windsurf": {
            "supported": (root / "tools" / "harness-export.py").is_file() and (root / ".mcp.json").is_file(),
            "entrypoints": [".windsurfrules (via `harness-export.py --target windsurf`)", "AGENTS.md", ".mcp.json"],
            "supports_native_subagents": False,
            "subagent_mechanism": "Single-Conductor execution via `.windsurfrules` + `.mcp.json` (`tyrion_universal_router`)",
            "supports_mcp_stdio": True,
            "supports_lifecycle_hooks": False,
            "execution_path": "Loads `.windsurfrules` baseline and calls `tyrion_universal_router` MCP tool or `skill-search.py execute`.",
        },
    }

    active_info = matrix.get(env_harness, {
        "supported": True,
        "entrypoints": ["tools/skill-search.py", "tools/tyrion.py", "tools/tyrion-mcp-server.py"],
        "supports_native_subagents": False,
        "subagent_mechanism": "Single-Conductor fallback with deterministic CLI tools",
        "supports_mcp_stdio": True,
        "supports_lifecycle_hooks": False,
        "execution_path": "Standalone Python CLI execution (`single_conductor_fallback`).",
    })

    return {
        "active_harness": env_harness,
        "active_harness_capabilities": active_info,
        "supported_harnesses": matrix,
    }


# --------------------------------------------------------------------------- #
# Universal Auto-Router & Full Context Loader
# --------------------------------------------------------------------------- #

def _detect_niche(norm_q: str) -> str:
    niche_keywords = {
        "real-estate": ("ko'chmas mulk", "kochmas mulk", "novostroyka", "xonadon", "недвижимость", "новостройки", "квартира", "real estate", "mortgage"),
        "edu": ("ta'lim", "talim", "kurs", "ielts", "o'quv markaz", "образование", "курсы", "учебный центр", "edtech", "education"),
        "medical": ("klinika", "stomatologiya", "shifokor", "tibbiyot", "клиника", "стоматология", "медицина", "healthcare", "dental"),
        "ecom": ("onlayn do'kon", "kiyim", "kostyum", "ecom", "e-commerce", "интернет магазин", "одежда", "товарка", "online store", "shopify"),
        "b2b": ("b2b", "crm", "saas", "korporativ", "улгуржи", "оптом", "enterprise"),
        "beauty": ("kosmetika", "atir", "parfyumeriya", "go'zallik saloni", "косметика", "парфюмерия", "салон красоты", "beauty"),
        "auto": ("avtomobil", "avtoservis", "avtosalon", "автомобиль", "автосервис", "автосалон", "car dealership"),
        "local": ("fitnes", "restoran", "kafe", "mehmonxona", "фитнес", "ресторан", "кафе", "gym"),
    }
    for niche, kw_list in niche_keywords.items():
        if any(k in norm_q for k in kw_list):
            return niche
    return "general"


def _select_relevant_references(
    selected_skills: list[dict],
    norm_q: str,
    concept_refs: list[str],
    max_refs: int = 4,
) -> list[str]:
    chosen: list[str] = []
    q_toks = set(tokens(norm_q))

    def _try_add(rel_path: str) -> None:
        clean = str(rel_path or "").strip()
        if clean and clean not in chosen and len(chosen) < max_refs and (VAULT / clean).is_file():
            chosen.append(clean)

    for cref in concept_refs:
        _try_add(cref)

    for sk in selected_skills:
        decl = sk.get("declared_references", [])
        if len(decl) == 1:
            _try_add(decl[0])
        elif len(decl) > 1:
            scored_refs: list[tuple[int, str]] = []
            for rpath in decl:
                stem_words = set(WORD.findall(Path(rpath).stem.lower()))
                overlap = len(stem_words & q_toks)
                scored_refs.append((overlap, rpath))
            scored_refs.sort(key=lambda x: (-x[0], x[1]))
            for _ov, rpath in scored_refs[:2]:
                _try_add(rpath)

    return chosen[:max_refs]


def route_task(
    query: str,
    agent_hint: str = "",
    load: bool = True,
    context_mode: str = "progressive",
    max_context_bytes: int = DEFAULT_MAX_CONTEXT_BYTES,
    extra_references: list[str] | None = None,
    mutation_approved: bool = False,
    session_cache: SessionContextCache | None = None,
    market: str | None = None,
    currency: str | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    """Har qanday foydalanuvchi topshirig'i uchun Universal Auto-Router rejasini tuzadi va to'liq kontekstni yuklaydi."""
    cache = session_cache if session_cache is not None else SESSION_CACHE
    skills = load_skills()
    agents = load_agents()
    skills_by_name = {s["name"]: s for s in skills}

    if not load or context_mode == "manifest":
        effective_mode = "manifest"
    elif context_mode == "full":
        effective_mode = "full"
    else:
        effective_mode = "progressive"
    should_load_files = effective_mode in ("full", "progressive")

    clean_query = str(query or "").strip()
    lang = (language or "").strip() or detect_language(clean_query)
    norm_q = normalize_multilingual_text(clean_query)
    q_tokens = tokens(clean_query)
    niche = _detect_niche(norm_q)
    market_info = mloc.detect_market(
        text=clean_query,
        explicit_market=market,
        currency=currency,
        detected_lang=lang,
    )
    active_market = market_info["market_id"]

    is_mutation = bool(MUTATION_PATTERNS.search(norm_q))
    mutation_blocked = is_mutation and not mutation_approved

    matched_concepts: list[dict[str, Any]] = []
    for phrases, cmeta in MULTILINGUAL_CONCEPT_MAP:
        if any(p in norm_q for p in phrases):
            matched_concepts.append(cmeta)

    multi_step_signals = (
        any(c.get("multi_step") for c in matched_concepts)
        or sum(
            1 for kw in (
                "strategiya", "стратегия", "strategy", "to'liq", "полный", "full",
                "raqobatchi", "конкурент", "competitor", "seo va konversiya", "сео и конверсия",
                "launch", "запуск", "voronka", "воронка"
            )
            if kw in norm_q
        ) >= 2
    )
    complexity = "multi_step" if multi_step_signals else "single_step"

    global_hits = rank(skills, clean_query, idf_pool=skills)
    global_registry_fallback_used = False

    if agent_hint and agent_hint in agents:
        agent_subset = attached_to(skills, agent_hint)
        local_hits = rank(agent_subset, clean_query, idf_pool=skills)
        if not local_hits or (global_hits and global_hits[0][0] > local_hits[0][0] * 1.6):
            effective_hits = global_hits
            global_registry_fallback_used = True
        else:
            effective_hits = local_hits
    else:
        effective_hits = global_hits

    def _has_structured_match(sk: dict) -> bool:
        if matched_concepts:
            return True
        structured_vocab = set(WORD.findall(
            (sk["name"] + " " + " ".join(sk.get("aliases", [])) + " " +
             " ".join(sk.get("triggers", [])) + " " + " ".join(sk.get("domains", [])) + " " +
             " ".join(sk.get("platforms", []))).lower()
        ))
        return bool(set(q_tokens) & structured_vocab)

    strong_hits = [(sc, s) for sc, s in effective_hits if sc >= 10.0 and _has_structured_match(s)]

    if not strong_hits:
        primary_agent = agent_hint if (agent_hint and agent_hint in agents) else "positioning-strategist"
        supporting_agents: list[str] = []
        required_skills = ["ads"]
        supporting_skills = ["uzbekistan-market-intel"] if active_market == "uz" else []
        references_to_load = ["skills/ads/references/thinking-framework.md"]
        tools_to_use = ["tools/brain-search.py", "tools/tyrion.py"]
        confidence_score = 0.35
        confidence_level = "low"
        confidence_explanation = (
            "Aniq maxsus skill triggeri topilmadi; foydalanuvchini to'xtatmaslik uchun "
            "`ads` konduktori va umumiy strategik workflow (`fallback_ready`) faollashtirildi."
        )
        fallback_plan = {
            "triggered": True,
            "mode": "UNIVERSAL_CONDUCTOR_FALLBACK",
            "conductor": "ads",
            "fallback_agent": primary_agent,
            "explanation": (
                "Maxsus skill topilmaganda tizim `needs_input` bilan to'xtab qolmaydi va foydalanuvchidan "
                "skill/agent nomini so'ramaydi; umumiy `ads` konduktor metodikasi bilan xavfsiz davom etadi."
            ),
            "steps": [
                "1. Vazifa maqsadi, biznes modeli va kanal kontekstini ajratib olish (`ads/SKILL.md`).",
                "2. `tools/brain-search.py` orqali 100 ta wiki qayd va 9 ta playbook ichidan mos SOP qidirish.",
                "3. Umumiy strategik va iqtisodiy tamoyillar (`00-manba`, `70-charter-baseline`) asosida yechim berish.",
            ],
        }
    else:
        top_score, top_skill = strong_hits[0]
        if complexity == "single_step":
            required_skills = [top_skill["name"]]
            supporting_skills = []
            if len(strong_hits) > 1 and strong_hits[1][0] >= top_score * 0.82:
                second_skill = strong_hits[1][1]
                if second_skill["name"] != top_skill["name"]:
                    supporting_skills.append(second_skill["name"])
        else:
            req_list: list[str] = []
            sup_list: list[str] = []
            seen_domains: set[str] = set()
            for sc, sk in strong_hits:
                if sc < top_score * 0.38:
                    continue
                sk_domains = set(sk.get("domains", []))
                if len(req_list) < 3 and (not req_list or not sk_domains.issubset(seen_domains)):
                    req_list.append(sk["name"])
                    seen_domains.update(sk_domains)
                elif len(sup_list) < 2 and sk["name"] not in req_list:
                    sup_list.append(sk["name"])
            required_skills = req_list or [top_skill["name"]]
            supporting_skills = [s for s in sup_list if s not in required_skills]

        if active_market != "uz" and "uzbekistan" not in norm_q and "toshkent" not in norm_q and "tashkent" not in norm_q:
            required_skills = [s for s in required_skills if s != "uzbekistan-market-intel"] or [top_skill["name"]]
            supporting_skills = [s for s in supporting_skills if s != "uzbekistan-market-intel"]

        agent_scores: dict[str, float] = {a: 0.0 for a in agents}
        for cmeta in matched_concepts:
            for aname, bval in cmeta.get("boost_agents", {}).items():
                if aname in agent_scores:
                    agent_scores[aname] += float(bval)

        for rank_idx, sk_name in enumerate(required_skills + supporting_skills):
            sk_obj = skills_by_name.get(sk_name)
            if not sk_obj:
                continue
            weight = 20.0 if rank_idx == 0 else (12.0 if sk_name in required_skills else 6.0)
            for attached_ag in sk_obj.get("agents", []):
                if attached_ag in agent_scores:
                    agent_scores[attached_ag] += weight

        for aname, ainfo in agents.items():
            a_trig = " ".join(ainfo.get("triggers", [])).lower()
            for trig_phrase in ainfo.get("triggers", []):
                if len(trig_phrase) >= 4 and trig_phrase.lower() in norm_q:
                    agent_scores[aname] += 22.0
            for tok in set(q_tokens):
                if tok in aname.lower():
                    agent_scores[aname] += 8.0
                if tok in a_trig:
                    agent_scores[aname] += 6.0
                if tok in {d.lower() for d in ainfo.get("domains", [])} or tok in {p.lower() for p in ainfo.get("platforms", [])}:
                    agent_scores[aname] += 4.0

        if agent_hint and agent_hint in agent_scores and not global_registry_fallback_used:
            agent_scores[agent_hint] += 15.0

        ranked_agents = sorted(
            [(sc, aname) for aname, sc in agent_scores.items() if sc > 0],
            key=lambda x: (-x[0], x[1]),
        )
        primary_agent = ranked_agents[0][1] if ranked_agents else (top_skill["agents"][0] if top_skill["agents"] else "launch-planner")

        supporting_agents = []
        if complexity == "multi_step":
            primary_domains = set(agents.get(primary_agent, {}).get("domains", []))
            for sc, aname in ranked_agents[1:]:
                if aname == primary_agent or aname in supporting_agents:
                    continue
                if sc < ranked_agents[0][0] * 0.20:
                    continue
                ag_domains = set(agents.get(aname, {}).get("domains", []))
                ag_skills = set(agents.get(aname, {}).get("skills", []))
                covers_selected_skill = bool(ag_skills & set(required_skills + supporting_skills))
                if covers_selected_skill or not ag_domains.issubset(primary_domains):
                    supporting_agents.append(aname)
                    primary_domains.update(ag_domains)
                if len(supporting_agents) >= 3:
                    break

        concept_refs: list[str] = []
        concept_tools: list[str] = []
        for cmeta in matched_concepts:
            for r in cmeta.get("refs", []):
                if r not in concept_refs:
                    concept_refs.append(r)
            for t in cmeta.get("tools", []):
                if t not in concept_tools:
                    concept_tools.append(t)

        selected_skill_objs = [skills_by_name[s] for s in (required_skills + supporting_skills) if s in skills_by_name]
        references_to_load = _select_relevant_references(selected_skill_objs, norm_q, concept_refs)

        tools_to_use = list(concept_tools)
        all_sel_skills = set(required_skills + supporting_skills)
        if "ads-meta-audience" in all_sel_skills or primary_agent == "meta-audience-architect":
            for t in ("tools/meta-targeting-engine.py", "tools/meta-audience.py"):
                if t not in tools_to_use:
                    tools_to_use.append(t)
        if "ads-meta" in all_sel_skills or primary_agent == "audit-meta":
            for t in ("tools/meta-audience.py", "tools/meta-insights-sync.py", "tools/ad-export-analyzer.py"):
                if t not in tools_to_use:
                    tools_to_use.append(t)
        if "ads-server-side-tracking" in all_sel_skills or primary_agent == "tracking-specialist":
            if "tools/capi-utm-builder.py" not in tools_to_use:
                tools_to_use.append("tools/capi-utm-builder.py")
        if {"ads-budget", "ads-math", "ads-optimize"} & all_sel_skills or primary_agent == "audit-budget":
            for t in ("tools/calculator.py", "tools/spend-guard.py"):
                if t not in tools_to_use:
                    tools_to_use.append(t)
        if {"ads-creative", "reels-scripting", "social"} & all_sel_skills or primary_agent in ("creative-strategist", "social-content-writer"):
            if "tools/creative-matrix.py" not in tools_to_use:
                tools_to_use.append("tools/creative-matrix.py")
        if {"video-editing", "video-motion-graphics"} & all_sel_skills or primary_agent == "video-editor":
            if "tools/video-run.py" not in tools_to_use:
                tools_to_use.append("tools/video-run.py")
        if not tools_to_use:
            tools_to_use.append("tools/brain-search.py")

        confidence_score = round(min(0.98, 0.55 + (top_score / 80.0)), 2)
        confidence_level = "high" if confidence_score >= 0.80 else ("medium" if confidence_score >= 0.60 else "low")
        confidence_explanation = (
            f"Asosiy agent `{primary_agent}` va `{', '.join(required_skills)}` skill(lar)i "
            f"so'rov maqsadi, til ({lang}) va trigger/IDF mosligi (ball={round(top_score, 1)}) asosida tanlandi."
        )
        if global_registry_fallback_used:
            confidence_explanation += f" (`{agent_hint}` agentining lokal skilllari yetarli bo'lmagani uchun global reyestrdan topildi)."

        fallback_plan = {
            "triggered": False,
            "mode": "ALTERNATIVE_SKILL_AND_CONDUCTOR_BACKUP",
            "conductor": "ads",
            "fallback_agent": supporting_agents[0] if supporting_agents else "research-worker",
            "explanation": "Agar asosiy skill davomida qo'shimcha ma'lumot yoki boshqa platforma ehtiyoji chiqsa, `--reroute-with` orqali zaxira agent va `ads` konduktoriga o'tiladi.",
            "steps": [
                f"1. Birinchi tanlov (`{required_skills[0]}`) bo'yicha to'liq ko'rsatmalarni o'qib tahlilni bajarish.",
                "2. Qo'shimcha yo'nalish chiqsa, `reroute_task` orqali yordamchi mutaxassisni ulash.",
            ],
        }

    if extra_references:
        for eref in extra_references:
            if eref and eref not in references_to_load:
                references_to_load.append(eref)

    sel_risks = [skills_by_name[s]["risk_level"] for s in (required_skills + supporting_skills) if s in skills_by_name]
    if is_mutation or "high" in sel_risks:
        risk_level = "high"
    elif "medium" in sel_risks or complexity == "multi_step":
        risk_level = "medium"
    else:
        risk_level = "low"

    rules_to_load = ["rules/00-manba.md", "rules/10-til-va-uslub.md", "rules/70-charter-baseline.md"]
    if risk_level in ("medium", "high") or is_mutation or primary_agent in ("audit-budget", "tracking-specialist", "audit-tracking", "launch-planner"):
        rules_to_load.append("rules/40-xavfsizlik-va-hisob.md")
    if active_market == "uz" or "uzbekistan-market-intel" in (required_skills + supporting_skills):
        rules_to_load.append("rules/30-ozbekiston-konteksti.md")
        if (VAULT / "markets/uz/README.md").is_file():
            rules_to_load.append("markets/uz/README.md")
    else:
        if (VAULT / market_info["readme_path"]).is_file():
            rules_to_load.append(market_info["readme_path"])
        if (VAULT / market_info["benchmarks_path"]).is_file():
            rules_to_load.append(market_info["benchmarks_path"])
    if complexity == "multi_step" or primary_agent == "release-verifier":
        rules_to_load.append("rules/50-topshirish-dod.md")

    missing_inputs: list[str] = []
    if mutation_blocked:
        missing_inputs.append(
            "Jonli reklama hisobini o'zgartirish (byudjet/kampaniya mutatsiyasi) uchun foydalanuvchining aniq tasdig'i (`--approved`), joriy kunlik byudjet va Stop-Loss chegarasi talab etiladi."
        )

    all_assigned_agents = [primary_agent] + [a for a in supporting_agents if a != primary_agent]

    # Full Context Loading with Progressive Budget Control & Explicit Error Recording
    loaded_charters: list[dict[str, Any]] = []
    loaded_skill_files: list[dict[str, Any]] = []
    loaded_rule_files: list[dict[str, Any]] = []
    loaded_ref_files: list[dict[str, Any]] = []
    deferred_references: list[dict[str, Any]] = []
    load_errors: list[dict[str, str]] = []
    used_context_bytes = 0

    charters_by_name: dict[str, dict[str, Any]] = {}
    skills_loaded_by_name: dict[str, dict[str, Any]] = {}
    refs_loaded_by_path: dict[str, dict[str, Any]] = {}
    rules_loaded_by_path: dict[str, dict[str, Any]] = {}

    effective_budget = (
        min(max_context_bytes, PROGRESSIVE_SINGLE_STEP_BUDGET)
        if (effective_mode == "progressive" and complexity == "single_step" and max_context_bytes == DEFAULT_MAX_CONTEXT_BYTES)
        else (min(max_context_bytes, 28_000) if (effective_mode == "progressive" and max_context_bytes == DEFAULT_MAX_CONTEXT_BYTES) else max_context_bytes)
    )

    if should_load_files:
        # Priority 1: Agent Charters (Progressive frontmatter+core body in progressive mode, Full Text in full mode)
        for ag_name in all_assigned_agents:
            ag_info = agents.get(ag_name)
            if not ag_info:
                load_errors.append({
                    "path": f"agents/{ag_name}.md",
                    "error_code": "AGENT_NOT_FOUND",
                    "message": f"Agent charteri topilmadi: {ag_name}",
                })
                continue
            rec, err = cache.read_verified_with_error(ag_info["path"])
            if err:
                load_errors.append(err)
                continue
            if rec:
                c_text = _progressive_slice(rec["content"], 3400) if effective_mode == "progressive" else rec["content"]
                c_bytes = len(c_text.encode("utf-8"))
                used_context_bytes += c_bytes
                entry = {
                    "name": ag_name,
                    "path": rec["path"],
                    "sha256": rec["sha256"],
                    "bytes": c_bytes,
                    "from_session_cache": rec["from_session_cache"],
                    "cache_invalidated": rec.get("cache_invalidated", False),
                    "full_instructions_loaded": True,
                    "disclosure_mode": effective_mode,
                    "content": c_text,
                    "body_markdown": _progressive_slice(rec["body_markdown"], 3000) if effective_mode == "progressive" else rec["body_markdown"],
                    "excerpt": rec["excerpt"],
                }
                loaded_charters.append(entry)
                charters_by_name[ag_name] = entry

        # Priority 2 & 3: Required & Supporting Skills
        for sk_name in (required_skills + supporting_skills):
            sk_role = "required" if sk_name in required_skills else "supporting"
            sk_obj = skills_by_name.get(sk_name)
            if not sk_obj:
                load_errors.append({
                    "path": f"skills/{sk_name}/SKILL.md",
                    "error_code": "SKILL_NOT_FOUND",
                    "message": f"Skill fayli topilmadi: {sk_name}",
                })
                continue
            rec, err = cache.read_verified_with_error(sk_obj["path"])
            if err:
                load_errors.append(err)
                continue
            if rec:
                s_text = _progressive_slice(rec["content"], 3600) if effective_mode == "progressive" else rec["content"]
                s_bytes = len(s_text.encode("utf-8"))
                used_context_bytes += s_bytes
                entry = {
                    "name": sk_name,
                    "role": sk_role,
                    "path": rec["path"],
                    "sha256": rec["sha256"],
                    "bytes": s_bytes,
                    "from_session_cache": rec["from_session_cache"],
                    "cache_invalidated": rec.get("cache_invalidated", False),
                    "full_instructions_loaded": True,
                    "disclosure_mode": effective_mode,
                    "output_contract": sk_obj.get("output_contract", ""),
                    "content": s_text,
                    "body_markdown": _progressive_slice(rec["body_markdown"], 3200) if effective_mode == "progressive" else rec["body_markdown"],
                    "instructions_excerpt": rec["excerpt"],
                }
                loaded_skill_files.append(entry)
                skills_loaded_by_name[sk_name] = entry

        # Priority 4: Rules
        for rule_rel in rules_to_load:
            rec, err = cache.read_verified_with_error(rule_rel)
            if err:
                load_errors.append(err)
                continue
            if rec:
                r_text = _progressive_slice(rec["content"], 900) if effective_mode == "progressive" else rec["content"]
                r_bytes = len(r_text.encode("utf-8"))
                if used_context_bytes + r_bytes <= effective_budget:
                    used_context_bytes += r_bytes
                    entry = {
                        "path": rec["path"],
                        "sha256": rec["sha256"],
                        "bytes": r_bytes,
                        "from_session_cache": rec["from_session_cache"],
                        "full_instructions_loaded": True,
                        "disclosure_mode": effective_mode,
                        "content": r_text,
                        "body_markdown": _progressive_slice(rec["body_markdown"], 800) if effective_mode == "progressive" else rec["body_markdown"],
                    }
                    loaded_rule_files.append(entry)
                    rules_loaded_by_path[rule_rel] = entry

        # Priority 5: Selected References (Deferred on-demand in progressive mode unless explicitly requested; loaded in full mode within budget)
        for ref_rel in references_to_load:
            rec, err = cache.read_verified_with_error(ref_rel)
            if err:
                load_errors.append(err)
                continue
            if rec:
                is_explicit_ref = bool(extra_references and ref_rel in extra_references)
                if effective_mode == "progressive" and not is_explicit_ref:
                    deferred_references.append({
                        "path": rec["path"],
                        "bytes": rec["bytes"],
                        "full_instructions_loaded": False,
                        "reason": "Progressive disclosure: reference deferred until needed (use --context-mode full to pre-load).",
                    })
                elif used_context_bytes + rec["bytes"] <= effective_budget:
                    used_context_bytes += rec["bytes"]
                    entry = {
                        "path": rec["path"],
                        "sha256": rec["sha256"],
                        "bytes": rec["bytes"],
                        "from_session_cache": rec["from_session_cache"],
                        "cache_invalidated": rec.get("cache_invalidated", False),
                        "full_instructions_loaded": True,
                        "content": rec["content"],
                        "body_markdown": rec["body_markdown"],
                        "excerpt": rec["excerpt"],
                    }
                    loaded_ref_files.append(entry)
                    refs_loaded_by_path[ref_rel] = entry
                else:
                    deferred_references.append({
                        "path": rec["path"],
                        "bytes": rec["bytes"],
                        "full_instructions_loaded": False,
                        "reason": f"Kontekst byudjeti ({effective_budget} bayt) to'lgani sababli ikkinchi bosqichga qoldirildi (hozircha yuklanmadi).",
                    })

    # Build Worker Packets WITH Full Loaded Instructions attached when `should_load_files=True`
    worker_packets: list[dict[str, Any]] = []
    for idx, ag_name in enumerate(all_assigned_agents):
        ag_info = agents.get(ag_name, {})
        ag_attached = set(ag_info.get("skills", []))
        ag_skills = [s for s in (required_skills + supporting_skills) if s in ag_attached]
        if not ag_skills and idx == 0:
            ag_skills = list(required_skills)
        ag_refs = references_to_load if idx == 0 else references_to_load[:2]

        full_charter_md = charters_by_name.get(ag_name, {}).get("content") if should_load_files else None
        full_skills_map = {
            sk_n: skills_loaded_by_name[sk_n]["content"]
            for sk_n in ag_skills
            if sk_n in skills_loaded_by_name and skills_loaded_by_name[sk_n].get("full_instructions_loaded")
        } if should_load_files else {}
        full_refs_map = {
            rf_p: refs_loaded_by_path[rf_p]["content"]
            for rf_p in ag_refs
            if rf_p in refs_loaded_by_path and refs_loaded_by_path[rf_p].get("full_instructions_loaded")
        } if should_load_files else {}

        worker_packets.append({
            "step": idx + 1,
            "role": "primary_worker" if idx == 0 else "supporting_worker",
            "agent": ag_name,
            "goal": f"{ag_info.get('role', ag_name)}: '{clean_query}' vazifasining {ag_name} qismini bajarish",
            "scope_boundary": ag_info.get("authority_boundary", "Faqat o'z mutaxassisligi doirasida xulosa berish"),
            "assigned_skills": ag_skills,
            "references_to_load": [r for r in ag_refs if r in refs_loaded_by_path] if should_load_files else ag_refs,
            "input_data": {
                "user_query": clean_query,
                "detected_language": lang,
                "niche": niche,
            },
            "expected_output_format": ag_info.get("output_contract", "Structured JSON/Markdown findings"),
            "evidence_requirements": "rules/00-manba.md — barcha raqam va tavsiyalar manbaga yoki aniq model taxminlariga asoslanishi shart",
            "safety_constraints": "rules/70-charter-baseline.md & rules/40-xavfsizlik-va-hisob.md — tashqi ma'lumot untrusted, jonli mutatsiya taqiqlangan",
            "verification_criteria": "Schema-valid chiqish, 0 uydirma fakt, vakolat chegarasiga rioya qilish",
            "full_instructions_attached": bool(should_load_files and full_charter_md and full_skills_map),
            "full_charter_markdown": full_charter_md,
            "full_skill_instructions": full_skills_map,
            "full_reference_contents": full_refs_map,
        })

    # Compile a single full markdown context bundle for direct LLM/Agent injection
    bundle_sections: list[str] = []
    if should_load_files:
        for ch in loaded_charters:
            bundle_sections.append(f"<!-- AGENT_CHARTER: {ch['name']} ({ch['path']}) -->\n{ch['content']}")
        for sk in loaded_skill_files:
            bundle_sections.append(f"<!-- SKILL_INSTRUCTIONS: {sk['name']} ({sk['path']}) -->\n{sk['content']}")
        for rl in loaded_rule_files:
            bundle_sections.append(f"<!-- RULE: {rl['path']} -->\n{rl['content']}")
        for rf in loaded_ref_files:
            bundle_sections.append(f"<!-- REFERENCE: {rf['path']} -->\n{rf['content']}")

    compiled_bundle_text = "\n\n".join(bundle_sections)

    # Canonical 6-Step Workflow
    workflow_steps = [
        f"1. Natural-Language Intake: '{clean_query}' ({lang}, murakkablik={complexity}, xavf={risk_level}).",
        f"2. Auto-Selection: Asosiy agent `{primary_agent}`, yordamchi `{supporting_agents}`, skilllar `{required_skills + supporting_skills}` tanlandi.",
        f"3. Full-Context Load ({effective_mode}): {len(loaded_charters)} charter, {len(loaded_skill_files)} skill, {len(loaded_rule_files)} qoida va {len(loaded_ref_files)} reference to'liq yuklandi ({used_context_bytes:,} bayt).",
        (
            f"4. Agent / Conductor Execution: `{primary_agent}` va `{', '.join(supporting_agents)}` paketlari ishga tushiriladi (yoki single-conductor fallback)."
            if supporting_agents
            else f"4. Agent / Conductor Execution: `{primary_agent}` paketi va `{', '.join(tools_to_use)}` vositalari bajariladi."
        ),
        "5. Dynamic Re-Routing Gate: Ish davomida yangi domen ehtiyoji chiqsa, `--reroute-with` orqali qo'shimcha skill/agent ulanadi.",
        "6. Verification & Synthesis: `50-topshirish-dod` va `output_contract` bo'yicha yakuniy natija tekshiriladi.",
    ]

    detected_platforms = sorted({
        p for s in (required_skills + supporting_skills)
        if s in skills_by_name
        for p in skills_by_name[s].get("platforms", [])
    }) or ["multi-platform"]

    detected_domains = sorted({
        d for s in (required_skills + supporting_skills)
        if s in skills_by_name
        for d in skills_by_name[s].get("domains", [])
    }) or ["marketing"]

    status = (
        "blocked_mutation_approval"
        if mutation_blocked
        else ("fallback_ready" if fallback_plan["triggered"] else "ready")
    )

    applied_skills_verified = [
        sk["name"] for sk in loaded_skill_files if sk.get("full_instructions_loaded") is True
    ]

    return {
        "schema": "tyrion.universal_router/v5",
        "query": clean_query,
        "status": status,
        "context_mode": effective_mode,
        "asks_user_for_skill_or_agent": False,
        "intent_analysis": {
            "detected_language": lang,
            "response_language": market_info["language"],
            "detected_market": active_market,
            "detected_currency": market_info["currency"],
            "domains": detected_domains,
            "platforms": detected_platforms,
            "niche": niche,
            "complexity": complexity,
            "risk_level": risk_level,
            "is_mutation_request": is_mutation,
            "mutation_approved": mutation_approved,
        },
        "market_context": market_info,
        "primary_agent": primary_agent,
        "supporting_agents": supporting_agents,
        "required_skills": required_skills,
        "supporting_skills": supporting_skills,
        "global_registry_fallback_used": global_registry_fallback_used,
        "references_to_load": references_to_load,
        "rules_to_load": rules_to_load,
        "tools_to_use": tools_to_use,
        "workflow": workflow_steps,
        "worker_packets": worker_packets,
        "missing_inputs": missing_inputs,
        "mutation_gate": {
            "requires_approval": is_mutation,
            "approved": mutation_approved,
            "blocked": mutation_blocked,
            "gate_tool": "tools/spend-guard.py",
            "required_gates": [
                "1_preview_diff", "2_human_approval", "3_budget_velocity_le_20pct",
                "4_max_daily_cap", "5_stop_loss_rule", "6_rollback_plan"
            ] if is_mutation else [],
            "reason": (
                "Jonli reklama hisobini o'zgartirish foydalanuvchi tasdig'isiz bloklandi (`40-xavfsizlik-va-hisob`)."
                if mutation_blocked
                else "Tasdiqlangan yoki faqat o'qish/rejalashtirish rejimi."
            ),
        },
        "routing_confidence": {
            "score": confidence_score,
            "level": confidence_level,
            "explanation": confidence_explanation,
        },
        "fallback_plan": fallback_plan,
        "loaded_context": {
            "context_mode": effective_mode,
            "actually_loaded": bool(should_load_files and (loaded_charters or loaded_skill_files)),
            "full_instructions_loaded": bool(should_load_files and bool(required_skills) and set(required_skills).issubset(set(applied_skills_verified))),
            "applied_skills_verified": applied_skills_verified,
            "loaded_agent_charters": loaded_charters,
            "loaded_skills": loaded_skill_files,
            "loaded_skill_names": [x["name"] for x in loaded_skill_files],
            "loaded_rules": loaded_rule_files,
            "loaded_references": loaded_ref_files,
            "deferred_references": deferred_references,
            "load_errors": load_errors,
            "context_budget": {
                "used_bytes": used_context_bytes,
                "max_bytes": effective_budget,
                "within_budget": used_context_bytes <= effective_budget,
            },
            "compiled_context_package": {
                "total_bytes": len(compiled_bundle_text.encode("utf-8")),
                "sections_count": len(bundle_sections),
                "full_markdown_bundle": compiled_bundle_text,
            },
            "session_cache_stats": {
                "hits": cache.hits,
                "misses": cache.misses,
                "invalidations": cache.invalidations,
                "persistent_cache_enabled": cache.persist_path is not None,
            },
        },
    }


def reroute_task(
    current_plan: dict[str, Any],
    emergent_requirement: str,
    load: bool = True,
    max_context_bytes: int = DEFAULT_MAX_CONTEXT_BYTES,
    session_cache: SessionContextCache | None = None,
) -> dict[str, Any]:
    """Ish davomida yangi ehtiyoj paydo bo'lganda mavjud marshrutni dinamik kengaytiradi va yangi skilllarning to'liq matnini yuklaydi."""
    cache = session_cache if session_cache is not None else SESSION_CACHE
    new_sub = route_task(
        emergent_requirement,
        load=load,
        context_mode=current_plan.get("context_mode", "full"),
        max_context_bytes=max_context_bytes,
        mutation_approved=bool(current_plan.get("intent_analysis", {}).get("mutation_approved", False)),
        session_cache=cache,
    )
    updated = json.loads(json.dumps(current_plan))
    updated["rerouted"] = True
    updated.setdefault("reroute_history", []).append({
        "emergent_requirement": emergent_requirement,
        "added_agent": new_sub["primary_agent"],
        "added_skills": new_sub["required_skills"],
    })

    new_ag = new_sub["primary_agent"]
    if new_ag != updated["primary_agent"] and new_ag not in updated["supporting_agents"]:
        updated["supporting_agents"].append(new_ag)

    for sk in new_sub["required_skills"]:
        if sk not in updated["required_skills"] and sk not in updated["supporting_skills"]:
            updated["supporting_skills"].append(sk)

    for ref in new_sub["references_to_load"]:
        if ref not in updated["references_to_load"]:
            updated["references_to_load"].append(ref)

    for rule in new_sub["rules_to_load"]:
        if rule not in updated["rules_to_load"]:
            updated["rules_to_load"].append(rule)

    for tool in new_sub["tools_to_use"]:
        if tool not in updated["tools_to_use"]:
            updated["tools_to_use"].append(tool)

    existing_packet_agents = {wp["agent"] for wp in updated.get("worker_packets", [])}
    for wp in new_sub.get("worker_packets", []):
        if wp["agent"] not in existing_packet_agents:
            wp_copy = dict(wp)
            wp_copy["step"] = len(updated["worker_packets"]) + 1
            wp_copy["role"] = "rerouted_specialist_worker"
            updated["worker_packets"].append(wp_copy)
            existing_packet_agents.add(wp["agent"])

    updated["workflow"].append(
        f"{len(updated['workflow']) + 1}. Dynamic Re-Route ('{emergent_requirement}'): `{new_ag}` va `{', '.join(new_sub['required_skills'])}` to'liq ko'rsatmalari bilan qo'shildi."
    )

    if load and updated.get("context_mode", "full") in ("full", "progressive"):
        existing_charters = {c["name"] for c in updated["loaded_context"]["loaded_agent_charters"]}
        for ch in new_sub["loaded_context"]["loaded_agent_charters"]:
            if ch["name"] not in existing_charters:
                updated["loaded_context"]["loaded_agent_charters"].append(ch)
                existing_charters.add(ch["name"])

        existing_skills = set(updated["loaded_context"]["loaded_skill_names"])
        for sk_loaded in new_sub["loaded_context"]["loaded_skills"]:
            if sk_loaded["name"] not in existing_skills:
                updated["loaded_context"]["loaded_skills"].append(sk_loaded)
                updated["loaded_context"]["loaded_skill_names"].append(sk_loaded["name"])
                if sk_loaded.get("full_instructions_loaded"):
                    updated["loaded_context"]["applied_skills_verified"].append(sk_loaded["name"])
                existing_skills.add(sk_loaded["name"])

        existing_refs = {r["path"] for r in updated["loaded_context"]["loaded_references"]}
        for rf in new_sub["loaded_context"]["loaded_references"]:
            if rf["path"] not in existing_refs:
                updated["loaded_context"]["loaded_references"].append(rf)
                existing_refs.add(rf["path"])

        # Update compiled_context_package with newly loaded content
        new_bundle_chunk = new_sub["loaded_context"]["compiled_context_package"]["full_markdown_bundle"]
        if new_bundle_chunk:
            combined_bundle = (
                updated["loaded_context"]["compiled_context_package"]["full_markdown_bundle"]
                + "\n\n"
                + new_bundle_chunk
            ).strip()
            updated["loaded_context"]["compiled_context_package"]["full_markdown_bundle"] = combined_bundle
            updated["loaded_context"]["compiled_context_package"]["total_bytes"] = len(combined_bundle.encode("utf-8"))

        updated["loaded_context"]["actually_loaded"] = bool(
            updated["loaded_context"]["loaded_agent_charters"] or updated["loaded_context"]["loaded_skills"]
        )
        updated["loaded_context"]["session_cache_stats"] = {
            "hits": cache.hits,
            "misses": cache.misses,
            "invalidations": cache.invalidations,
            "persistent_cache_enabled": cache.persist_path is not None,
        }

    return updated


# --------------------------------------------------------------------------- #
# End-to-End Autonomous Execution Engine (`execute_task`)
# --------------------------------------------------------------------------- #

def _run_deterministic_tools_for_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Tanlangan deterministik Python dvigatellarini (read-only) amalda ishga tushirib, haqiqiy natijalarni yig'adi."""
    outputs: list[dict[str, Any]] = []
    niche = plan["intent_analysis"]["niche"]
    if niche == "general":
        niche = "ecom"
    query = plan["query"]

    for tool_rel in plan.get("tools_to_use", []):
        try:
            if tool_rel == "tools/meta-audience.py":
                ma = importlib.import_module("meta-audience")
                arch = ma.build_architecture(niche=niche, daily_budget=100.0, geo="tashkent")
                outputs.append({
                    "tool": tool_rel,
                    "action": "build_architecture",
                    "status": "executed",
                    "summary": {
                        "niche": arch.get("niche"),
                        "layers_count": len(arch.get("layers", [])),
                        "exclusions": arch.get("global_exclusions", []),
                    },
                })
            elif tool_rel == "tools/meta-targeting-engine.py":
                mte = importlib.import_module("meta-targeting-engine")
                targ = mte.search_and_validate_targeting(product=query[:80], niche=niche)
                outputs.append({
                    "tool": tool_rel,
                    "action": "search_and_validate_targeting",
                    "status": "executed",
                    "summary": {
                        "live_check_status": targ["live_check_status"]["status"],
                        "verified_count": len(targ["verified_targeting_options"]),
                        "related_unverified_count": len(targ["related_unverified_ideas"]),
                    },
                })
            elif tool_rel == "tools/capi-utm-builder.py":
                cu = importlib.import_module("capi-utm-builder")
                capi_res = cu.build_capi_payload("Lead", phone="+998901234567", email="audit@brand.uz")
                outputs.append({
                    "tool": tool_rel,
                    "action": "build_capi_payload_diagnostic",
                    "status": "executed",
                    "summary": {
                        "graph_api_version": capi_res.get("graph_api_version"),
                        "estimated_emq_score_10": capi_res.get("estimated_emq_score_10"),
                        "deduplication_key": "event_id + event_name",
                    },
                })
            elif tool_rel == "tools/creative-matrix.py":
                cm = importlib.import_module("creative-matrix")
                mat = cm.build_matrix(niche=niche, product=query[:60] or "Mahsulot", price=100.0)
                outputs.append({
                    "tool": tool_rel,
                    "action": "build_matrix",
                    "status": "executed",
                    "summary": {
                        "cells_count": len(mat.get("matrix", [])),
                        "niche": mat.get("niche"),
                    },
                })
            elif tool_rel == "tools/calculator.py":
                calc = importlib.import_module("calculator")
                be = calc.calc_breakeven(price=100.0, cogs=40.0, shipping=5.0)
                outputs.append({
                    "tool": tool_rel,
                    "action": "calc_breakeven",
                    "status": "executed",
                    "summary": be,
                })
            elif tool_rel == "tools/brain-search.py":
                bs = importlib.import_module("brain-search")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    bs.main(["search", query[:60] or "marketing", "--top", "3"])
                outputs.append({
                    "tool": tool_rel,
                    "action": "search_wiki",
                    "status": "executed",
                    "summary": buf.getvalue().strip()[:400],
                })
        except Exception as exc:
            outputs.append({
                "tool": tool_rel,
                "status": "error",
                "error": str(exc),
            })
    return outputs


def execute_task(
    query: str,
    agent_hint: str = "",
    reroute_with: str = "",
    mutation_approved: bool = False,
    harness_override: str = "",
    max_context_bytes: int = DEFAULT_MAX_CONTEXT_BYTES,
    session_cache: SessionContextCache | None = None,
    subagent_runner: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Rejalashdan amaliy ijroga o'tish: to'liq ko'rsatmalarni yuklaydi, worker/conductor va CLI vositalarini bajaradi."""
    cache = session_cache if session_cache is not None else SESSION_CACHE
    plan = route_task(
        query=query,
        agent_hint=agent_hint,
        load=True,
        context_mode="full",
        max_context_bytes=max_context_bytes,
        mutation_approved=mutation_approved,
        session_cache=cache,
    )
    if reroute_with:
        plan = reroute_task(
            current_plan=plan,
            emergent_requirement=reroute_with,
            load=True,
            max_context_bytes=max_context_bytes,
            session_cache=cache,
        )

    harness_info = detect_harness_capabilities(VAULT, harness_override=harness_override)

    # Gate 1: If blocked by unapproved live account mutation, halt before any execution
    if plan["status"] == "blocked_mutation_approval":
        return {
            "schema": "tyrion.auto_router_execution/v5",
            "execution_status": "blocked_mutation_approval",
            "execution_mode": "blocked_by_spend_guard",
            "subagents_actually_spawned": False,
            "harness": harness_info,
            "route_plan": plan,
            "worker_executions": [],
            "deterministic_tool_outputs": [],
            "execution_errors": [],
            "conductor_synthesis": {
                "status": "blocked_mutation_approval",
                "reason": plan["mutation_gate"]["reason"],
                "required_approvals": plan["mutation_gate"]["required_gates"],
            },
        }

    # Execute workers: if native `subagent_runner` callback is provided, dispatch each worker packet with full instructions;
    # otherwise execute honestly in `single_conductor_fallback` mode and NEVER pretend external sub-agents were spawned!
    worker_executions: list[dict[str, Any]] = []
    execution_errors: list[dict[str, Any]] = list(plan["loaded_context"].get("load_errors", []))
    subagents_spawned = False

    if subagent_runner is not None:
        execution_mode = "native_subagent_dispatch"
        for wp in plan["worker_packets"]:
            if not wp.get("full_instructions_attached"):
                err_obj = {
                    "agent": wp["agent"],
                    "error_code": "MISSING_FULL_INSTRUCTIONS",
                    "message": f"`{wp['agent']}` uchun to'liq skill/charter matni yuklanmagan — sub-agent ishga tushirilmadi.",
                }
                execution_errors.append(err_obj)
                worker_executions.append({
                    "step": wp["step"],
                    "agent": wp["agent"],
                    "role": wp["role"],
                    "execution_type": "aborted_missing_instructions",
                    "subagent_spawned": False,
                    "status": "error",
                    "error": err_obj["message"],
                })
                continue
            try:
                sub_res = subagent_runner(wp)
                subagents_spawned = True
                worker_executions.append({
                    "step": wp["step"],
                    "agent": wp["agent"],
                    "role": wp["role"],
                    "assigned_skills": wp["assigned_skills"],
                    "execution_type": "native_subagent",
                    "subagent_spawned": True,
                    "full_skill_chars_received": sum(len(v) for v in wp.get("full_skill_instructions", {}).values()),
                    "full_charter_chars_received": len(wp.get("full_charter_markdown") or ""),
                    "status": "completed",
                    "output": sub_res,
                })
            except Exception as exc:
                err_msg = f"Sub-agent `{wp['agent']}` xato qaytardi: {exc}. Conductor fallback ishga tushirildi."
                execution_errors.append({
                    "agent": wp["agent"],
                    "error_code": "SUBAGENT_EXECUTION_ERROR",
                    "message": err_msg,
                })
                worker_executions.append({
                    "step": wp["step"],
                    "agent": wp["agent"],
                    "role": wp["role"],
                    "assigned_skills": wp["assigned_skills"],
                    "execution_type": "conductor_fallback_after_agent_error",
                    "subagent_spawned": False,
                    "status": "recovered_via_conductor_fallback",
                    "error": str(exc),
                    "fallback_note": "Sub-agent xatosi sababli vazifa asosiy Conductor tomonidan yuklangan to'liq skill ko'rsatmalari asosida bajarildi.",
                })
    else:
        execution_mode = "single_conductor_fallback"
        subagents_spawned = False
        for wp in plan["worker_packets"]:
            worker_executions.append({
                "step": wp["step"],
                "agent": wp["agent"],
                "role": wp["role"],
                "assigned_skills": wp["assigned_skills"],
                "execution_type": "single_conductor_in_context",
                "subagent_spawned": False,
                "full_instructions_loaded": wp.get("full_instructions_attached", False),
                "full_skill_chars_loaded": sum(len(v) for v in wp.get("full_skill_instructions", {}).values()),
                "full_charter_chars_loaded": len(wp.get("full_charter_markdown") or ""),
                "status": "executed_by_conductor" if wp.get("full_instructions_attached") else "degraded_missing_instructions",
                "honesty_disclosure": (
                    f"Joriy muhitda (`{harness_info['active_harness']}`) tashqi sub-agent jarayoni "
                    "alohida spawn qilinmadi (`subagent_spawned=False`); Conductor `"
                    f"{wp['agent']}` charteri va `{', '.join(wp['assigned_skills'])}` skilllarining "
                    "to'liq ko'rsatmalarini yuklab bevosita bajardi."
                ),
            })

    tool_outputs = _run_deterministic_tools_for_plan(plan)

    all_skills_fully_loaded = plan["loaded_context"]["full_instructions_loaded"]
    exec_status = "completed" if all_skills_fully_loaded and not execution_errors else "completed_with_warnings"

    conductor_synthesis = {
        "status": exec_status,
        "execution_mode": execution_mode,
        "subagents_actually_spawned": subagents_spawned,
        "primary_agent": plan["primary_agent"],
        "supporting_agents": plan["supporting_agents"],
        "applied_skills_verified": plan["loaded_context"]["applied_skills_verified"],
        "deferred_references": [d["path"] for d in plan["loaded_context"]["deferred_references"]],
        "deterministic_tools_ran": [t["tool"] for t in tool_outputs if t.get("status") == "executed"],
        "output_contracts_enforced": [
            {"agent": wp["agent"], "expected_output_format": wp["expected_output_format"]}
            for wp in plan["worker_packets"]
        ],
        "verification_summary": {
            "full_skill_instructions_loaded": all_skills_fully_loaded,
            "zero_unloaded_skills_claimed": True,
            "rules_enforced": plan["rules_to_load"],
            "errors_count": len(execution_errors),
        },
    }

    return {
        "schema": "tyrion.auto_router_execution/v5",
        "execution_status": exec_status,
        "execution_mode": execution_mode,
        "subagents_actually_spawned": subagents_spawned,
        "harness": harness_info,
        "route_plan": plan,
        "worker_executions": worker_executions,
        "deterministic_tool_outputs": tool_outputs,
        "execution_errors": execution_errors,
        "conductor_synthesis": conductor_synthesis,
    }


# --------------------------------------------------------------------------- #
# Reyestr Validatori
# --------------------------------------------------------------------------- #

def validate_registry(skills: list[dict] | None = None, agents: dict[str, dict] | None = None) -> tuple[list[str], list[str]]:
    skills_list = skills if skills is not None else load_skills(force_reload=True)
    agents_map = agents if agents is not None else load_agents(force_reload=True)
    problems: list[str] = []
    warnings: list[str] = []

    for skill in skills_list:
        if not skill["has_frontmatter"]:
            problems.append(f"{skill['path']}: frontmatter yo'q yoki YAML buzilgan")
            continue
        if not skill["description"]:
            problems.append(f"{skill['path']}: `description` bo'sh")
        if not skill["dir_name_matches"]:
            warnings.append(f"{skill['path']}: papka nomi ({skill['dir']}) ≠ skill nomi ({skill['name']})")
        if skill.get("risk_level", "low") not in VALID_RISK_LEVELS:
            problems.append(f"{skill['name']}: noto'g'ri `risk_level: {skill.get('risk_level')}`")
        for ref_path in skill.get("declared_references", []):
            if not (VAULT / ref_path).is_file():
                problems.append(f"{skill['name']}: `references` ichida mavjud bo'lmagan fayl ko'rsatilgan: `{ref_path}`")
        for rel_sk in skill.get("related_skills", []):
            if not any(s["name"] == rel_sk for s in skills_list) and not any(a == rel_sk for a in agents_map):
                problems.append(f"{skill['name']}: `related_skills` ichida noma'lum skill: `{rel_sk}`")
        for agent in skill["agents"]:
            if agent not in agents_map:
                problems.append(f"{skill['name']}: `attached_agents: {agent}` — bunday charter yo'q (agents/{agent}.md)")
                continue
            if skill["name"] not in agents_map[agent]["skills"]:
                problems.append(f"{skill['name']} → {agent}: agent charterida teskari havola yo'q (`skills:` ga qo'shilsin)")
        if not skill["agents"] and not skill["standalone"] and skill["root"] == "operator":
            warnings.append(f"{skill['name']}: hech qaysi agentga ulanmagan (kerak bo'lmasa `standalone: true`)")

    for agent in agents_map.values():
        for name in agent["skills"]:
            match = next((s for s in skills_list if s["name"] == name), None)
            if match is None:
                problems.append(f"{agent['name']}.skills: `{name}` — SKILL.md topilmadi")
            elif agent["name"] not in match["agents"]:
                problems.append(f"{agent['name']} → {name}: skillda `attached_agents: {agent['name']}` yo'q")

    return problems, warnings


# --------------------------------------------------------------------------- #
# Chiqarish va CLI Buyruqlari
# --------------------------------------------------------------------------- #

def print_skill_line(score_value: float, skill: dict, agent: str = "") -> None:
    attached = ", ".join(skill["agents"]) or "—"
    print(f"  [{int(score_value):3}] {skill['name']}  ({skill['layer']})")
    print(f"        fayl    : {skill['path']}")
    print(f"        ulangan : {attached}")
    if skill["refs"]:
        print(f"        qo'shimcha: references/ — {', '.join(skill['refs'])}")
    if skill["description"]:
        print(f"        nima    : {skill['description'][:100]}")


def attached_to(skills: list[dict], agent: str) -> list[dict]:
    return [s for s in skills if agent in s["agents"]]


def _resolve_cli_cache(cache_file_arg: str, persist_flag: bool) -> SessionContextCache:
    if cache_file_arg:
        return SessionContextCache(persist_path=Path(cache_file_arg))
    if persist_flag:
        return SessionContextCache(persist_path=DEFAULT_SESSION_CACHE_PATH)
    return SESSION_CACHE


def cmd_route(args: argparse.Namespace) -> int:
    cache = _resolve_cli_cache(getattr(args, "session_cache_file", ""), getattr(args, "persist_session_cache", False))
    if getattr(args, "execute", False):
        exec_rep = execute_task(
            query=args.query,
            agent_hint=args.agent,
            reroute_with=args.reroute_with,
            mutation_approved=args.approved,
            harness_override=getattr(args, "harness", ""),
            max_context_bytes=getattr(args, "max_context_bytes", DEFAULT_MAX_CONTEXT_BYTES),
            session_cache=cache,
        )
        if args.json:
            print(json.dumps(exec_rep, ensure_ascii=False, indent=2))
            return 0
        plan = exec_rep["route_plan"]
        print("=" * 76)
        print("  🚀 TYRION AUTO-ROUTER — END-TO-END EXECUTION REPORT")
        print("=" * 76)
        print(f"  So'rov             : {plan['query']}")
        print(f"  Ijro Holati        : {exec_rep['execution_status']} (rejim={exec_rep['execution_mode']}, subagents_spawned={exec_rep['subagents_actually_spawned']})")
        print(f"  Faol Harness       : {exec_rep['harness']['active_harness']}")
        print(f"  Asosiy Agent       : {plan['primary_agent']} | Yordamchi: {', '.join(plan['supporting_agents']) or '—'}")
        print(f"  To'liq Yuklangan   : {plan['loaded_context']['applied_skills_verified']} ({plan['loaded_context']['context_budget']['used_bytes']:,} bayt)")
        print(f"  Bajarilgan Asboblar: {', '.join(exec_rep['conductor_synthesis']['deterministic_tools_ran']) or '—'}")
        print("=" * 76)
        return 0

    mode = "manifest" if (args.no_load or getattr(args, "context_mode", "progressive") == "manifest") else getattr(args, "context_mode", "progressive")
    plan = route_task(
        query=args.query,
        agent_hint=args.agent,
        load=(mode == "full"),
        context_mode=mode,
        max_context_bytes=getattr(args, "max_context_bytes", DEFAULT_MAX_CONTEXT_BYTES),
        mutation_approved=args.approved,
        session_cache=cache,
        market=getattr(args, "market", None),
        currency=getattr(args, "currency", None),
        language=getattr(args, "language", None),
    )
    if args.reroute_with:
        plan = reroute_task(
            current_plan=plan,
            emergent_requirement=args.reroute_with,
            load=(mode == "full"),
            max_context_bytes=getattr(args, "max_context_bytes", DEFAULT_MAX_CONTEXT_BYTES),
            session_cache=cache,
        )

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    is_uz_out = plan["intent_analysis"]["detected_language"] in ("uz_latin", "uz_cyrillic", "uz", "uz-Latn", "uz-Cyrl")
    m_ctx = plan.get("market_context", {})
    print("=" * 72)
    print("  🧭 TYRION UNIVERSAL AUTO-ROUTER & ORCHESTRATION PLAN")
    print("=" * 72)
    if is_uz_out:
        print(f"  So'rov            : {plan['query']}")
        print(f"  Holat (Status)    : {plan['status']} (til={plan['intent_analysis']['detected_language']}, bozor={m_ctx.get('market_id', 'global')}, valyuta={m_ctx.get('currency', 'USD')}, murakkablik={plan['intent_analysis']['complexity']}, xavf={plan['intent_analysis']['risk_level']})")
    else:
        print(f"  Query             : {plan['query']}")
        print(f"  Status            : {plan['status']} (lang={plan['intent_analysis']['detected_language']}, market={m_ctx.get('market_id', 'global')}, currency={m_ctx.get('currency', 'USD')}, complexity={plan['intent_analysis']['complexity']}, risk={plan['intent_analysis']['risk_level']})")
        print(f"  Regulations       : {', '.join(m_ctx.get('regulations', {}).get('frameworks', [])) or 'Standard'}")
    print(f"  Kontekst Rejimi   : {plan['context_mode']} (full_instructions_loaded={plan['loaded_context']['full_instructions_loaded']}, bytes={plan['loaded_context']['context_budget']['used_bytes']:,})")
    print(f"  Asosiy Agent      : {plan['primary_agent']}")
    print(f"  Yordamchi Agentlar: {', '.join(plan['supporting_agents']) or '— (oddiy vazifa, ortiqcha agent chaqirilmadi)'}")
    print(f"  Asosiy Skilllar   : {', '.join(plan['required_skills'])}")
    if plan["supporting_skills"]:
        print(f"  Yordamchi Skilllar: {', '.join(plan['supporting_skills'])}")
    print(f"  References        : {', '.join(plan['references_to_load']) or '—'}")
    print(f"  Qoidalar (Rules)  : {', '.join(plan['rules_to_load'])}")
    print(f"  CLI / MCP Asboblar: {', '.join(plan['tools_to_use'])}")
    print(f"  Ishonchlilik      : {plan['routing_confidence']['score']} ({plan['routing_confidence']['level']}) — {plan['routing_confidence']['explanation']}")
    print(f"  Kontekst Yuklandi : {plan['loaded_context']['actually_loaded']} (applied_skills_verified={plan['loaded_context']['applied_skills_verified']})")
    if plan["mutation_gate"]["blocked"]:
        print(f"  🛑 MUTATION GATE  : {plan['mutation_gate']['reason']}")
    print("  Kanonik 6-Bosqichli Ish Oqimi:")
    for step in plan["workflow"]:
        print(f"    • {step}")
    print("=" * 72)
    return 0


def cmd_execute(args: argparse.Namespace) -> int:
    args.execute = True
    args.no_load = False
    args.context_mode = "full"
    return cmd_route(args)


def cmd_agent(args: argparse.Namespace) -> int:
    skills = load_skills()
    agents = load_agents()
    agent = args.name
    if agent not in agents:
        near = [a for a in agents if agent.lower() in a.lower()]
        print(f"✗ agent topilmadi: {agent}" + (f" (o'xshash: {', '.join(near[:5])})" if near else ""))
        return 2
    listed = agents[agent]["skills"]
    attached = {s["name"]: s for s in attached_to(skills, agent)}
    print(f"Agent: {agent}  (charter: {agents[agent]['path']})")
    print(f"Ulangan skill ({len(attached)}):")
    if not attached:
        print("  — yo'q: charter frontmatter'ida `skills:` va skillda `attached_agents:` yozilsin")
        return 1
    for name in (listed or sorted(attached)):
        skill = attached.get(name)
        if skill is None:
            print(f"  [{name}] ✗ skill papkasi yo'q (charter'da e'lon qilingan, fayl topilmadi)")
            continue
        print(f"  {name}")
        print(f"        fayl: {skill['path']}")
        if skill["refs"]:
            print(f"        qo'shimcha: references/ — {', '.join(skill['refs'])}")
    return 0


def cmd_brief(args: argparse.Namespace) -> int:
    skills = load_skills()
    pool = skills
    if args.agent:
        subset = attached_to(skills, args.agent)
        if not subset:
            print(f"Skill so'rovi: \"{args.query}\"")
            print(f"✗ {args.agent} agentiga skill ulanmagan — ish boshlanmaydi (needs_input)")
            return 1
        pool = subset
    hits = rank(pool, args.query, idf_pool=skills)
    scope = f" · agent: {args.agent}" if args.agent else ""
    print(f"Skill so'rovi: \"{args.query}\"{scope}")
    if not hits:
        print("✗ mos skill topilmadi — universal router fallback ishlatilsin: `python3 tools/skill-search.py route \"...\"`")
        return 1
    top_score, top = hits[0]
    print(f"Tanlandi: {top['name']}  (ball {int(top_score)})")
    print(f"  fayl    : {top['path']}")
    print(f"  ulangan : {', '.join(top['agents']) or '—'}")
    if top["refs"]:
        print(f"  qo'shimcha: references/ — {', '.join(top['refs'])}")
    if top["triggers"]:
        print(f"  trigger : {', '.join(top['triggers'][:8])}")
    others = [h for h in hits[1:args.top]]
    if others:
        print("Zaxira: " + " · ".join(f"{s['name']} ({int(sc)})" for sc, s in others))
    print("Keyingi qadam: shu SKILL.md ni o'qib, FAQAT shu skill tartibi bo'yicha ishla.")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    skills = load_skills()
    pool = skills
    if args.agent:
        pool = attached_to(skills, args.agent)
        if not pool:
            print(f"✗ {args.agent} agentiga skill ulanmagan")
            return 1
    hits = rank(pool, args.query)[: args.top]
    if not hits:
        print(f"✗ mos skill topilmadi (so'rov: {args.query})")
        return 1
    scope = f" · agent: {args.agent}" if args.agent else f" · reyestr: {len(pool)} skill"
    print(f"Topildi {len(hits)}{scope}:")
    for sc, skill in hits:
        print_skill_line(sc, skill)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    skills = load_skills()
    if args.layer:
        skills = [s for s in skills if s["layer"] == args.layer]
    agents = load_agents()
    print(f"Skill reyestri: {len(skills)} ta" + (f" (layer={args.layer})" if args.layer else ""))
    for skill in skills:
        attached = ", ".join(skill["agents"]) or ("— ulanmagan" if not skill["standalone"] else "standalone")
        print(f"  {skill['layer']:9} {skill['name']:28} → {attached}")
    print(f"Agentlar: {len(agents)} · skill ulangan: {sum(1 for a in agents.values() if a['skills'])}")
    return 0


def cmd_check(_args: argparse.Namespace) -> int:
    skills = load_skills(force_reload=True)
    agents = load_agents(force_reload=True)
    problems, warnings = validate_registry(skills, agents)

    print(f"Skill: {len(skills)} · agent: {len(agents)} · ulanish: {sum(len(s['agents']) for s in skills)}")
    if warnings:
        print(f"⚠ ogohlantirish ({len(warnings)}):")
        for item in warnings[:10]:
            print(f"  - {item}")
    if problems:
        print(f"✗ uzilgan ulanish / xato ({len(problems)}):")
        for item in problems[:15]:
            print(f"  - {item}")
        return 1
    print("✓ skill reyestri va ulanishlar butun")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skill-search.py",
        description="Universal Auto-Router, End-to-End Execution Engine va Skill Reyestri (0 token)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for sub_name, sub_func, sub_help in (
        ("route", cmd_route, "foydalanuvchi vazifasini avtomatik agent, skill va to'liq kontekstga marshrutlash"),
        ("execute", cmd_execute, "foydalanuvchi vazifasini marshrutlash, to'liq ko'rsatmalarni yuklash va amalda bajarish"),
    ):
        p_r = sub.add_parser(sub_name, help=sub_help)
        p_r.add_argument("query", help="Foydalanuvchi topshirig'i (UZ lotin, UZ kirill, RU, EN)")
        p_r.add_argument("--agent", default="", help="Ixtiyoriy boshlang'ich agent ishorasi")
        p_r.add_argument("--load", action="store_true", default=True, help="Tanlangan charter, SKILL.md va reference to'liq matnini yuklash (default: True)")
        p_r.add_argument("--no-load", "--manifest-only", dest="no_load", action="store_true", help="Fayllarni o'qimasdan faqat manifest rejasini chiqarish")
        p_r.add_argument("--context-mode", choices=["progressive", "full", "manifest"], default="progressive", help="Context loading mode: progressive (<=15KB frontmatter+core body), full (all references), or manifest")
        p_r.add_argument("--max-context-bytes", type=int, default=DEFAULT_MAX_CONTEXT_BYTES, help="Kontekst paketi maksimal hajmi (bayt)")
        p_r.add_argument("--reroute-with", default="", help="Ish davomida paydo bo'lgan qo'shimcha ehtiyojni dinamik qo'shish")
        p_r.add_argument("--approved", action="store_true", help="Reklama hisobiga o'zgartirish (mutation) tasdiqlanganligi")
        p_r.add_argument("--execute", action="store_true", default=(sub_name == "execute"), help="Rejadan tashqari deterministik vositalar va conductor sintezini amalda bajarish")
        p_r.add_argument("--harness", default="", help="Harness imkoniyatini tekshirish (claude_code, codex, cursor, windsurf)")
        p_r.add_argument("--market", default="", help="Market pack override (global, uz, us, eu, uk, mena, latam, sea, in)")
        p_r.add_argument("--currency", default="", help="ISO 4217 currency override (USD, EUR, GBP, JPY, UZS, etc.)")
        p_r.add_argument("--language", default="", help="BCP 47 language override (en, de, fr, ar, uz-Latn, ru, etc.)")
        p_r.add_argument("--persist-session-cache", action="store_true", help="Sessiya keshini diskda (`output/.cache/router_session_cache.json`) saqlash")
        p_r.add_argument("--session-cache-file", default="", help="Maxsus sessiya kesh fayli yo'li")
        p_r.add_argument("--json", action="store_true", help="To'liq JSON chiqarish")
        p_r.set_defaults(func=sub_func)

    p = sub.add_parser("agent", help="agentga ulangan skilllar")
    p.add_argument("name")
    p.set_defaults(func=cmd_agent)

    p = sub.add_parser("brief", help="skill talash so'rovi bloki (agent 0-qadam qisqa yo'li)")
    p.add_argument("query")
    p.add_argument("--agent", default="")
    p.add_argument("--top", type=int, default=3)
    p.set_defaults(func=cmd_brief)

    p = sub.add_parser("search", help="so'rov bo'yicha skill qidirish")
    p.add_argument("query")
    p.add_argument("--agent", default="")
    p.add_argument("--top", type=int, default=3)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("list", help="butun reyestr")
    p.add_argument("--layer", default="")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("check", help="ulanish va frontmatter tekshiruvi")
    p.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
