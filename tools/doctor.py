#!/usr/bin/env python3
"""Tyrion doctor — butun tizimning sog'liq hisoboti (yagona buyruq).

Nega kerak: har qatlamning o'z tekshiruvi bor (vault-audit, catalog, drift), lekin
"tizim sog'lommi?" degan savolga bitta javob yo'q edi. doctor ularni yig'adi,
ustiga o'zi ham tekshiradi (raqamlar eskirganmi, graf yangimi, sir oshkor bo'lganmi,
botlar joyidami, testlar o'tadimi).

Ishlatish:
  python3 tools\\doctor.py            # to'liq hisobot
  python3 tools\\doctor.py --quick    # testlarsiz (tezkor rejim)
  python3 tools\\doctor.py --json     # mashina o'qiydigan chiqish

Chiqish kodi: 0 — hammasi joyida, 1 — ❌ bor, 2 — ishga tushirish xatosi.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent

sys.path.insert(0, str(TOOLS))
import catalog as cat  # noqa: E402  (bir papkadagi yordamchi)

# Windows: konsol yoki quvur bo'lsa ham UTF-8 (catalog moduli ham o'zi qiladi)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

OK, WARN, FAIL, SKIP = "ok", "warn", "fail", "skip"
ICON = {OK: "✓", WARN: "⚠", FAIL: "✗", SKIP: "·"}

# Tizim ishlashi uchun majburiy fayllar
REQUIRED = [
    "AGENTS.md", "CLAUDE.md", "MEMORY.md", "INDEX.md", "LOG.md",
    "rules/README.md", "contexts/README.md", "playbooks/README.md",
    "tools/catalog.py", "tools/doctor.py", "tools/vault-audit.py",
    "manifests/catalog.json", "skills/ads/SKILL.md",
]

# Sir (secret) naqshlari — faqat yuqori ishonchli belgilar
SECRET_PATTERNS = [
    (r"\bsk-[A-Za-z0-9]{20,}", "OpenAI uslubidagi kalit"),
    (r"\bsk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic kaliti"),
    (r"\bAIza[0-9A-Za-z_\-]{30,}", "Google API kaliti"),
    (r"\bEAA[A-Za-z0-9]{40,}", "Meta access token"),
    (r"\b\d{8,10}:AA[A-Za-z0-9_\-]{30,}", "Telegram bot tokeni"),
    (r"\bghp_[A-Za-z0-9]{30,}", "GitHub tokeni"),
]

SECRET_NAME_RE = re.compile(r"(^|/)(\.env|.*\.pem|.*\.key|.*credential.*|.*secret.*)$", re.I)

# `graphify extract` semantik qatlam uchun LLM kalitini talab qiladi (2026-09-16 da aniqlandi)
LLM_KEY_ENV = ("DEEPSEEK_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY",
               "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "MOONSHOT_API_KEY")

# operator xotirasi fayli o'zining ixchamlik shartini buzmasin (memory.md: "90 qatordan oshmasin")
MEMORY_LIMIT = 90


def llm_key_present() -> bool:
    import os
    return any(os.environ.get(name) for name in LLM_KEY_ENV)


class Report:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.rows.append({"check": name, "status": status, "detail": detail})

    def count(self, status: str) -> int:
        return sum(1 for r in self.rows if r["status"] == status)

    @property
    def failed(self) -> int:
        return self.count(FAIL)


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(cwd or VAULT), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )


# --------------------------------------------------------------------------- #
# Tekshiruvlar
# --------------------------------------------------------------------------- #

def check_required(report: Report) -> None:
    missing = [rel for rel in REQUIRED if not (VAULT / rel).is_file()]
    if missing:
        report.add("Majburiy fayllar", FAIL, f"yo'q: {', '.join(missing)}")
    else:
        report.add("Majburiy fayllar", OK, f"{len(REQUIRED)} fayl joyida")


def check_vault(report: Report, data: dict) -> None:
    """Bilim qatlami: vault-audit.py natijasini o'qiydi."""
    script = TOOLS / "vault-audit.py"
    if not script.is_file():
        report.add("Bilim qatlami (vault-audit)", SKIP, "skript yo'q")
        return
    try:
        proc = run([sys.executable, str(script), str(VAULT)])
    except Exception as exc:  # pragma: no cover
        report.add("Bilim qatlami (vault-audit)", FAIL, f"ishga tushmadi: {exc}")
        return

    out = proc.stdout or ""
    match = re.search(r"JAMI MUAMMO \(bilim qatlami\): (\d+)", out)
    total = int(match.group(1)) if match else -1
    wiki = data["counts"].get("wiki", 0)

    if total < 0:
        report.add("Bilim qatlami (vault-audit)", WARN, "hisobotni o'qib bo'lmadi")
    elif total == 0:
        report.add("Bilim qatlami (vault-audit)", OK, f"{wiki} qayd, muammo yo'q")
    else:
        report.add("Bilim qatlami (vault-audit)", FAIL, f"{total} muammo (batafsil: vault-audit.py)")


def check_frontmatter(report: Report, data: dict) -> None:
    broken = []
    for layer in ("wiki", "agents", "skills"):
        for item in data["items"].get(layer, []):
            if item.get("fm_error"):
                broken.append(f"{item['path']} ({item['fm_error'][:40]})")
    if broken:
        report.add("Frontmatter / YAML", FAIL, f"{len(broken)} muammo: {broken[0]}")
    else:
        report.add("Frontmatter / YAML", OK, "barcha qayd va charterlarda to'g'ri")


def check_catalog(report: Report, data: dict) -> None:
    manifest = VAULT / "manifests" / "catalog.json"
    if not manifest.is_file():
        report.add("Katalog", FAIL, "manifests/catalog.json yo'q — `catalog.py build` kerak")
        return
    stored = json.loads(manifest.read_text(encoding="utf-8"))
    if cat._comparable(stored) == cat._comparable(data):
        total = sum(data["counts"].values())
        report.add("Katalog", OK, f"haqiqatga mos ({total} element)")
    else:
        report.add("Katalog", FAIL, "eskirgan — `python3 tools\\catalog.py build`")


def check_drift(report: Report, data: dict) -> None:
    drifted = [m for m in data["mirrors"] if m["status"] != "identical"]
    if not drifted:
        report.add("Nusxa drifti", OK, f"{len(data['mirrors'])} juftlik mos")
    else:
        names = ", ".join(m["name"] for m in drifted[:6])
        more = f" +{len(drifted) - 6}" if len(drifted) > 6 else ""
        report.add("Nusxa drifti", WARN, f"{len(drifted)} nusxa farqli: {names}{more}")


def check_claims(report: Report, data: dict) -> None:
    """AGENTS.md dagi raqamlar katalogga mos keladimi (qo'lda yozilgan da'vo eskimasin)."""
    agents_md = VAULT / "AGENTS.md"
    if not agents_md.is_file():
        report.add("Raqamlar (AGENTS.md)", SKIP, "fayl yo'q")
        return
    match = re.search(r"<!--\s*tyrion:catalog\s+([^>]+?)-->", agents_md.read_text(encoding="utf-8"))
    if not match:
        report.add("Raqamlar (AGENTS.md)", WARN, "katalog belgisi yo'q (<!-- tyrion:catalog ... -->)")
        return

    claimed = dict(re.findall(r"(\w+)=(\d+)", match.group(1)))
    stale = [
        f"{key}: yozilgan {value}, aslida {data['counts'].get(key, '?')}"
        for key, value in claimed.items()
        if str(data["counts"].get(key)) != value
    ]
    if stale:
        report.add("Raqamlar (AGENTS.md)", WARN, "; ".join(stale))
    else:
        report.add("Raqamlar (AGENTS.md)", OK, f"{len(claimed)} raqam katalogga mos")

    _check_human_claims(report, data)


def _check_human_claims(report: Report, data: dict) -> None:
    """Oddiy matndagi raqamlar (INDEX.md, README.md, rules/...) katalogga mosmi."""
    claims = cat.human_claims(data["counts"])
    if not claims:
        report.add("Raqamlar (hujjatlar)", SKIP, "nazorat qilinadigan raqam yo'q")
        return
    broken = [
        f"{c['file']}: yozilgan {c['written'] if c['written'] is not None else '—'}, "
        f"aslida {c['expected']}" + (f" ({c['reason']})" if c["reason"] else "")
        for c in claims if not c["ok"]
    ]
    if broken:
        report.add("Raqamlar (hujjatlar)", WARN, "; ".join(broken))
    else:
        report.add("Raqamlar (hujjatlar)", OK, f"{len(claims)} hujjatdagi raqam mos")


PLATFORM_TAG_WORDS = ("meta", "google", "telegram", "tiktok", "youtube", "linkedin", "instagram", "facebook", "andromeda", "pixel", "capi",
                      "api", "ads", "reklama", "platforma", "yandex", "amazon", "snapchat", "pinterest", "reddit")


def check_wiki_freshness(report: Report, root: Path | None = None, max_age_days: int = 180, today: "datetime | None" = None) -> None:
    """Platformaga oid wiki qaydi (Meta/Google/Telegram... API va qoidalari tez eskiradi) `max_age_days` dan eski bo'lsa ogohlantiradi."""
    root = root or VAULT
    now = (today or datetime.now()).date()
    stale: list[str] = []
    platform_notes = 0
    for p in sorted((root / "wiki").glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        tags = re.search(r"(?m)^tags:\s*(.*)$", text)
        if not any(w in (tags.group(1).lower() if tags else "") for w in PLATFORM_TAG_WORDS):
            continue
        platform_notes += 1
        upd = re.search(r"(?m)^updated:\s*['\"]?(\d{4}-\d{2}-\d{2})", text)
        if not upd:
            stale.append(f"{p.name} (updated yo'q)")
            continue
        age = (now - datetime.strptime(upd.group(1), "%Y-%m-%d").date()).days
        if age > max_age_days:
            stale.append(f"{p.name} ({age} kun)")
    if stale:
        more = f" +{len(stale) - 5}" if len(stale) > 5 else ""
        report.add("Platforma qaydlari yangiligi", WARN, f"{len(stale)}/{platform_notes} qayd >{max_age_days} kun eski: {', '.join(stale[:5])}{more}")
    else:
        report.add("Platforma qaydlari yangiligi", OK, f"{platform_notes} platforma qaydi ≤{max_age_days} kun ichida yangilangan")


def check_version(report: Report, root: Path | None = None) -> None:
    """Versiya: VERSION (yagona manba) ↔ plagin manifestlari ↔ hujjat/SKILL shablon/skript satrlari."""
    root = root or VAULT
    try:
        expected = cat.read_version(root)
    except OSError:
        report.add("Versiya (VERSION)", FAIL, "ildizda VERSION fayli yo'q")
        return
    drift = cat.version_scan(root)
    if drift:
        sample = "; ".join(f"{d['file']}:{d['line']} {d['found']}→{d['expected']}" for d in drift[:4])
        more = f" +{len(drift) - 4}" if len(drift) > 4 else ""
        report.add("Versiya (VERSION)", FAIL, f"{len(drift)} eskirgan versiya satri: {sample}{more} — `catalog.py sync-claims`")
    else:
        report.add("Versiya (VERSION)", OK, f"{expected} — manifestlar va hujjatlar mos")


def check_memory(report: Report) -> None:
    """Operator xotirasi (memory.md) o'zining ixchamlik chegarasiga sig'adimi."""
    path = VAULT / "MEMORY.md"
    if not path.is_file():
        report.add("Xotira (MEMORY.md)", SKIP, "fayl yo'q")
        return
    lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    if lines > MEMORY_LIMIT:
        report.add("Xotira (MEMORY.md)", WARN,
                   f"{lines} qator > {MEMORY_LIMIT} chegara — ixchamlashtirilsin")
    else:
        report.add("Xotira (MEMORY.md)", OK, f"{lines}/{MEMORY_LIMIT} qator")


_ENV_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def _expand_env(text: str, env: dict[str, str]) -> str:
    """Claude Code'ning `${VAR}` / `${VAR:-default}` kengaytirishini taqlid qiladi (aniqlanmasa literal qoladi)."""
    def repl(m: "re.Match[str]") -> str:
        if m.group(1) in env:
            return env[m.group(1)]
        return m.group(2) if m.group(2) is not None else m.group(0)
    return _ENV_REF_RE.sub(repl, text)


def mcp_handshake(
    cfg_path: Path,
    server_name: str = "tyrion-core",
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    timeout: float = 20.0,
) -> dict:
    """`.mcp.json` dagi AYNAN o'sha buyruqni ishga tushirib, stdio handshake (initialize + tools/list) qiladi.

    `env` — Claude Code serverga beradigan qo'shimcha o'zgaruvchilar (masalan, faqat CLAUDE_PROJECT_DIR);
    CLAUDE_PLUGIN_ROOT / CLAUDE_PROJECT_DIR meros olinmaydi, shuning uchun natija deterministik."""
    result: dict = {"ok": False, "tool_count": 0, "tools": [], "detail": ""}
    try:
        cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
        entry = cfg["mcpServers"][server_name]
        command = str(entry["command"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result["detail"] = f"{server_name} yozuvi o'qilmadi: {exc!r}"
        return result
    import os
    child_env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PROJECT_DIR")}
    child_env.update(env or {})
    for k, v in (entry.get("env") or {}).items():
        child_env[k] = _expand_env(str(v), child_env)
    argv = [_expand_env(command, child_env)] + [_expand_env(str(a), child_env) for a in entry.get("args", [])]
    resolved = shutil.which(argv[0], path=child_env.get("PATH"))
    if resolved is None:
        result["detail"] = f"buyruq topilmadi: {argv[0]}"
        return result
    argv[0] = resolved
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "tyrion-doctor", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    ]
    payload = "".join(json.dumps(m) + "\n" for m in msgs)
    try:
        proc = subprocess.run(
            argv, input=payload, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, cwd=str(cwd or VAULT), env=child_env,
        )
    except subprocess.TimeoutExpired:
        result["detail"] = f"handshake {timeout:g}s ichida tugamadi"
        return result
    except OSError as exc:
        result["detail"] = f"ishga tushmadi: {exc}"
        return result
    replies: dict = {}
    for line in proc.stdout.splitlines():
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if isinstance(msg, dict) and "id" in msg:
            replies[msg["id"]] = msg
    if 1 not in replies or "result" not in replies[1]:
        result["detail"] = "initialize javobi yo'q: " + (proc.stderr.strip()[-160:] or f"exit {proc.returncode}")
        return result
    tools = (replies.get(2, {}).get("result") or {}).get("tools")
    if not isinstance(tools, list):
        result["detail"] = "tools/list javobi yo'q"
        return result
    result.update(ok=True, tool_count=len(tools), tools=[t.get("name") for t in tools if isinstance(t, dict)], detail="handshake OK")
    return result


def check_mcp(report: Report, cfg_path: Path | None = None, env: dict[str, str] | None = None, cwd: Path | None = None) -> None:
    """MCP: .mcp.json buyrug'i CLAUDE_PLUGIN_ROOT'siz (ombor loyiha sifatida ochilgan holat) ham haqiqiy handshake qiladimi."""
    cfg = cfg_path or (VAULT / ".mcp.json")
    if not cfg.is_file():
        report.add("MCP Server (.mcp.json)", FAIL, f"{cfg.name} yo'q")
        return
    project_env = env if env is not None else {"CLAUDE_PROJECT_DIR": str(VAULT)}
    res = mcp_handshake(cfg, "tyrion-core", env=project_env, cwd=cwd or VAULT)
    if res["ok"]:
        report.add("MCP Server (.mcp.json)", OK, f"tyrion-core handshake OK ({res['tool_count']} MCP tool, CLAUDE_PLUGIN_ROOT'siz)")
    else:
        report.add("MCP Server (.mcp.json)", FAIL, res["detail"])


def check_mcp_and_evals(report: Report) -> None:
    """MCP Server (.mcp.json, haqiqiy stdio handshake) va Behavioral Evals (skill-eval.py) tekshiruvi."""
    import importlib
    check_mcp(report)

    eval_srv = TOOLS / "skill-eval.py"
    if not eval_srv.is_file():
        report.add("Eval Suite (skill-eval)", SKIP, "skill-eval.py yo'q")
        return
    try:
        se_mod = importlib.import_module("skill-eval")
        payload = se_mod.run_evals()
        if payload.get("failed", 1) == 0:
            report.add("Eval Suite (skill-eval)", OK, f"{payload.get('passed', 0)}/{payload.get('total', 0)} stsenariy (100% pass)")
        else:
            report.add("Eval Suite (skill-eval)", FAIL, f"{payload.get('failed')} stsenariy xato")
    except Exception as exc:
        report.add("Eval Suite (skill-eval)", WARN, f"tekshirib bo'lmadi: {exc}")


def check_graph(report: Report, data: dict) -> None:
    graph = VAULT / "graphify-out" / "graph.json"
    if not graph.is_file():
        report.add("Bilim grafi", SKIP, "graf ixtiyoriy (graphify-out/graph.json yo'q)")
        return
    graph_time = graph.stat().st_mtime
    notes = [VAULT / i["path"] for i in data["items"].get("wiki", [])]
    newest = max((p.stat().st_mtime for p in notes if p.is_file()), default=0)
    if newest > graph_time:
        days = (newest - graph_time) / 86400
        hint = "" if llm_key_present() else " — LLM kaliti yo'q; lokal Ollama bilan: tools\\gy.cmd refresh"
        report.add("Bilim grafi", WARN,
                   f"eskirgan - qaydlar grafdan {days:.1f} kun yangi (gy.cmd refresh){hint}")
    else:
        size_kb = graph.stat().st_size / 1024
        report.add("Bilim grafi", OK, f"yangilangan ({size_kb:.0f} KB)")


def check_secrets(report: Report) -> None:
    """Sir oshkor bo'lganmi: .env git'da, kalit naqshlari, xavfli fayl nomlari."""
    problems: list[str] = []
    try:
        proc = run(["git", "ls-files"], timeout=60)
        tracked = [line.strip() for line in (proc.stdout or "").splitlines() if line.strip()]
    except Exception:
        tracked = []

    for rel in tracked:
        if SECRET_NAME_RE.search(rel):
            problems.append(f"git'da kuzatilgan: {rel}")

    targets = [
        p for p in VAULT.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".json", ".jsonc", ".yaml", ".yml", ".md", ".py", ".cmd", ".env"}
        and p.stat().st_size < 200_000
        and not any(part in {".git", ".obsidian", "node_modules", "graphify-out", "__pycache__",
                             ".smart-env", "tmp", "output", "tests"} for part in p.relative_to(VAULT).parts)
        and True  # claude-ads-main ham sirlar uchun to'liq tekshiriladi
    ]
    import importlib
    sh_mod = importlib.import_module("tyrion-shield")
    sh_data = sh_mod.run_all()
    sec_check = next((c for c in sh_data.get("checks", []) if c["check"].startswith("Secrets")), None)
    if sec_check and sec_check["status"] != "ok":
        problems.extend(sec_check.get("items", []))

    if problems:
        report.add("Sirlar (secrets)", FAIL, "; ".join(sorted(set(problems))[:4]))
    else:
        report.add("Sirlar (secrets)", OK, f"{len(targets)} fayl tekshirildi, oshkor sir yo'q")


def check_git(report: Report) -> None:
    try:
        status = run(["git", "status", "--short"], timeout=60)
        branch = run(["git", "branch", "--show-current"], timeout=30)
    except Exception as exc:
        report.add("Git holati", SKIP, f"git yo'q: {exc}")
        return
    dirty = [l for l in (status.stdout or "").splitlines() if l.strip()]
    name = (branch.stdout or "").strip() or "?"
    if not dirty:
        report.add("Git holati", OK, f"{name}: toza")
    else:
        report.add("Git holati", WARN, f"{name}: {len(dirty)} o'zgargan fayl (commit kutilmoqda)")


def check_tests(report: Report, quick: bool) -> None:
    tests_dir = VAULT / "tests"
    if not tests_dir.is_dir() or not list(tests_dir.glob("test_*.py")):
        report.add("Testlar", WARN, "tests/ bo'sh — testlar yo'q")
        return
    if quick:
        report.add("Testlar", SKIP, "--quick")
        return
    try:
        proc = run([sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir),
                    "-t", str(VAULT), "-v"], timeout=300)
    except Exception as exc:
        report.add("Testlar", FAIL, f"ishga tushmadi: {exc}")
        return
    output = (proc.stdout or "") + (proc.stderr or "")
    match = re.search(r"Ran (\d+) test", output)
    ran = match.group(1) if match else "?"
    if proc.returncode == 0:
        report.add("Testlar", OK, f"{ran} test o'tdi")
    else:
        fails = re.search(r"FAILED \(([^)]+)\)", output)
        report.add("Testlar", FAIL, f"{ran} test, xato: {fails.group(1) if fails else 'batafsil'}")


def check_skills(report: Report) -> None:
    """Skill reyestri va agent ulanishlari (skill-search.py check) butunmi.

    Nega: agent ishni boshlashdan oldin o'ziga ulangan skillni topishi kerak —
    uzilgan ulanish (skill `attached_agents:` bor, agentda `skills:` yo'q yoki fayl yo'q)
    bo'lsa agent skillsiz qolib, ish tasodifiy bo'ladi.
    """
    script = TOOLS / "skill-search.py"
    if not script.is_file():
        report.add("Skill reyestri", SKIP, "skill-search.py yo'q")
        return
    try:
        import io, contextlib, importlib
        ss_mod = importlib.import_module("skill-search")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = ss_mod.main(["check"])
        proc = subprocess.CompletedProcess(args=["skill-search.py", "check"], returncode=rc, stdout=buf.getvalue(), stderr="")
    except Exception as exc:  # pragma: no cover
        report.add("Skill reyestri", FAIL, f"ishga tushmadi: {exc}")
        return
    out = (proc.stdout or "") + (proc.stderr or "")
    skills = re.search(r"Skill: (\d+) · agent: (\d+) · ulanish: (\d+)", out)
    warn = re.search(r"ogohlantirish \((\d+)\)", out)
    detail = (f"{skills.group(1)} skill · {skills.group(3)} ulanish"
              + (f" · {warn.group(1)} ulanmagan" if warn else "")) if skills else "hisobotni o'qib bo'lmadi"
    if proc.returncode == 0:
        report.add("Skill reyestri", OK, detail)
    else:
        broken = re.search(r"xato \((\d+)\)", out)
        report.add("Skill reyestri", FAIL,
                   f"{broken.group(1) if broken else '?'} uzilgan ulanish (skill-search.py check)")



def check_instincts(report: Report) -> None:
    """Uzluksiz o'rganish instinktlari reestri (instincts.py check) butunmi."""
    script = TOOLS / "instincts.py"
    if not script.is_file():
        report.add("Instinktlar (/learn)", SKIP, "instincts.py yo'q")
        return
    try:
        import importlib
        inst_mod = importlib.import_module("instincts")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            inst_mod.main(["check", "--json"])
        payload = json.loads(buf.getvalue() or "{}")
        if payload.get("passed"):
            report.add("Instinctlar (/learn)", OK,
                       f"{payload.get('count', 0)} instinkt ({payload.get('high_confidence', 0)} yuqori ishonchli)")
        else:
            report.add("Instinctlar (/learn)", FAIL, "; ".join(payload.get("errors", [])[:2]))
    except Exception as exc:
        report.add("Instinctlar (/learn)", WARN, f"tekshirib bo'lmadi: {exc}")


def check_shield(report: Report) -> None:
    """TyrionShield (ECC AgentShield analogi) 5 qavatli xavfsizlik skaneri."""
    script = TOOLS / "tyrion-shield.py"
    if not script.is_file():
        report.add("TyrionShield (/shield)", SKIP, "tyrion-shield.py yo'q")
        return
    try:
        import importlib
        sh_mod = importlib.import_module("tyrion-shield")
        payload = sh_mod.run_all()
        s = payload.get("summary", {})
        if s.get("errors", 0) > 0:
            report.add("TyrionShield (/shield)", FAIL, f"{s.get('errors')} xavfsizlik xatosi")
        elif s.get("warnings", 0) > 0:
            report.add("TyrionShield (/shield)", WARN, f"{s.get('ok')}/{s.get('checked')} joyida, {s.get('warnings')} ogohlantirish")
        else:
            report.add("TyrionShield (/shield)", OK, f"{s.get('checked')}/{s['checked']} xavfsizlik qatlami toza")
    except Exception as exc:
        report.add("TyrionShield (/shield)", WARN, f"tekshirib bo'lmadi: {exc}")

# Charter `tools:` maydonida ruxsat etilgan yagona MCP naqsh (code.claude.com/docs/en/mcp
# bo'yicha plugin-provided server: `mcp__plugin_<plugin>_<server>__<tool>`).
MCP_TOOL_RE = re.compile(
    r"^mcp__plugin_tyrion_tyrion-core__tyrion_"
    r"(brain_search|breakdown_effect|capi_utm|creative_matrix|media_calculator|"
    r"meta_audience|meta_detailed_targeting|meta_live_insights|spend_guard|universal_router)$"
)

URL_RE = re.compile(r"https?://[^\s\"'`<>)\]]+")

TEXT_SUFFIXES = {".md", ".py", ".json", ".html", ".sh", ".ps1"}


def _iter_repo_text_files(root: Path) -> list[Path]:
    skip_parts = {".git", "node_modules", "graphify-out", "__pycache__"}
    return [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix in TEXT_SUFFIXES and not (skip_parts & set(p.parts))
    ]


def find_broken_md_links(root: Path) -> list[tuple[str, str]]:
    """Nisbiy markdown havolalar ([matn](yo'l)) bo'lmagan faylga ko'rsatsa — qaytaradi."""
    files = [p for p in root.rglob("*.md") if not ({"__pycache__", "graphify-out"} & set(p.parts))]
    md_link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
    broken: list[tuple[str, str]] = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            # inline kod namunalari tekshirilmaydi (masalan CLAUDE.md dagi `[[...]]`)
            for m in md_link_re.finditer(re.sub(r"`[^`]*`", "", line)):
                target = m.group(1).strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_part = target.replace("\\", "/").split("#")[0]
                if not path_part:
                    continue
                if not any((base / path_part).is_file() or (base / path_part).is_dir()
                           for base in (p.parent, root)):
                    broken.append((str(p.relative_to(root)).replace("\\", "/"), target))
    return broken


def find_broken_wikilinks(root: Path) -> list[tuple[str, str]]:
    """Wikilink ([[nishon]]) nomi vault ichida mavjud .md faylga mos kelmasa — qaytaradi.

    `templates/` (Obsidian Templater placeholderlari) tekshiruvdan tashqarida.
    """
    files = [p for p in root.rglob("*.md") if not ({"__pycache__", "graphify-out"} & set(p.parts))]
    names = {p.name.lower() for p in files}
    wikilink_re = re.compile(r"\[\[([^\]#|]+)")
    broken: list[tuple[str, str]] = []
    for p in files:
        if "templates" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            for m in wikilink_re.finditer(re.sub(r"`[^`]*`", "", line)):
                target = m.group(1).strip()
                if not target or target == "..." or target.startswith("<%"):
                    continue
                base = target.split("/")[-1]
                cand = base if base.endswith(".md") else base + ".md"
                if cand.lower() not in names:
                    broken.append((str(p.relative_to(root)).replace("\\", "/"), target))
    return broken


def check_links(report: Report) -> None:
    """3B: buzilgan navigatsiya havolalari (markdown + wikilink) nol bo'lishi shart."""
    broken_md = find_broken_md_links(VAULT)
    broken_wl = find_broken_wikilinks(VAULT)
    total = len(broken_md) + len(broken_wl)
    if total == 0:
        report.add("Buzilgan havolalar", OK, "markdown + wikilink havolalari joyida")
        return
    sample = (broken_md + broken_wl)[:2]
    detail = f"{total} ta buzilgan (md={len(broken_md)}, wikilink={len(broken_wl)}): " + "; ".join(
        f"{f} -> {t}" for f, t in sample)
    report.add("Buzilgan havolalar", FAIL, detail)


def charter_hygiene_issues(root: Path) -> list[str]:
    """3A/3C: charter nomi, MCP nomlanishi va URL ajratuvchi gigiyenasi muammolari."""
    issues: list[str] = []
    fm_re = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
    for p in sorted((root / "agents").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if "Claude Ads conductor" in text:
            issues.append(f"{p.name}: harness-ga bog'liq 'Claude Ads conductor' nomi")
        fm = fm_re.match(text)
        if not fm:
            continue
        tools = re.search(r"^tools:\s*(.+)$", fm.group(1), re.M)
        if not tools:
            continue
        for token in (t.strip() for t in tools.group(1).split(",")):
            if token.startswith("mcp__") and not MCP_TOOL_RE.fullmatch(token):
                issues.append(f"{p.name}: yaroqsiz MCP nom: {token}")
    for p in _iter_repo_text_files(root):
        if "agents" in p.parts:
            continue  # charterlar yuqorida tekshirildi
        if "tests" in p.parts:
            continue  # testlar atayin buzilgan namunalarni olib yuradi
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            continue
        for m in URL_RE.finditer(text):
            url = m.group(0)
            if url.count("?") > 1 or "&?" in url:
                issues.append(f"{p.name}: noto'g'ri '?' ajratuvchi: {url[:80]}")
                break
    return issues


def check_charter_hygiene(report: Report) -> None:
    """3A/3C: charter nomi, MCP nomlanishi va URL '?' ajratuvchi gigiyenasi."""
    issues = charter_hygiene_issues(VAULT)
    if not issues:
        report.add("Charter gigiyenasi", OK, "harness-neytral nom, MCP naqshi va URL ajratuvchilar toza")
    else:
        report.add("Charter gigiyenasi", FAIL, f"{len(issues)} muammo: " + "; ".join(issues[:2]))


# --------------------------------------------------------------------------- #
# Hisobot
# --------------------------------------------------------------------------- #

def render(report: Report, data: dict) -> None:
    counts = data["counts"]
    print("=" * 64)
    print("  TYRION DOCTOR — tizim sog'liq hisoboti")
    print("=" * 64)
    print(f"  vaqt: {datetime.now().astimezone().isoformat(timespec='seconds')}")
    print(f"  vault: {VAULT}\n")

    for row in report.rows:
        print(f"  {ICON[row['status']]} {row['check']:26} {row['detail']}")

    print("\n  Qatlamlar: " + " · ".join(
        f"{k} {counts.get(k, 0)}" for k in
        ("wiki", "playbooks", "contexts", "agents", "skills", "rules", "tools", "commands", "hooks", "tests")
    ))

    ok, warn, fail, skip = (report.count(s) for s in (OK, WARN, FAIL, SKIP))
    print("\n" + "-" * 64)
    verdict = "HAMMASI JOYIDA" if fail == 0 and warn == 0 else (
        "ISHLAYDI, lekin diqqat talab" if fail == 0 else "TUZATISH KERAK")
    print(f"  {ok} joyida · {warn} ogohlantirish · {fail} xato · {skip} o'tkazildi  →  {verdict}")
    print(f"  Summary: checked={len(report.rows)}, ok={ok}, warnings={warn}, errors={fail}")
    print("-" * 64)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(prog="doctor.py", description="Tyrion tizim sog'liq tekshiruvi")
    parser.add_argument("--quick", action="store_true", help="unit-testlarsiz tezkor tekshiruv")
    parser.add_argument("--json", action="store_true", help="mashina o'qiydigan chiqish")
    args = parser.parse_args(argv)

    try:
        data = cat.scan()
    except Exception as exc:
        print(f"✗ skanerlashda xato: {exc}")
        return 2

    report = Report()
    check_required(report)
    check_vault(report, data)
    check_frontmatter(report, data)
    check_catalog(report, data)
    check_drift(report, data)
    check_claims(report, data)
    check_version(report)
    check_wiki_freshness(report)
    check_skills(report)
    check_instincts(report)
    check_shield(report)
    check_links(report)
    check_charter_hygiene(report)
    check_memory(report)
    check_mcp_and_evals(report)
    check_graph(report, data)
    check_secrets(report)
    check_git(report)
    check_tests(report, args.quick)

    if args.json:
        print(json.dumps(
            {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "counts": data["counts"], "checks": report.rows},
            ensure_ascii=False, indent=2))
    else:
        render(report, data)

    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
