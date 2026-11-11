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


def check_version(report: Report) -> None:
    """Versiya bitta joyda yoziladi; manifest nusxalari va matndagi eslatmalar unga mosmi."""
    import tyrion_core as tcore
    current = tcore.plugin_version(VAULT)
    stale = [c for c in cat.version_claims() if not c["ok"]]
    if stale:
        sample = "; ".join(f"{c['file']}: {c['written']}" for c in stale[:4])
        more = f" +{len(stale) - 4}" if len(stale) > 4 else ""
        report.add("Versiya", WARN, f"joriy {current}, eskirgan yozuvlar: {sample}{more} (catalog.py sync-claims)")
    else:
        report.add("Versiya", OK, f"{current} — manifestlar va matn mos")


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


# Claude Code plugin manifest rules (code.claude.com/docs/en/plugins-reference, checked 2026-11-11).
MANIFEST_KEYS = {
    "$schema", "name", "displayName", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "metadata", "icon", "documentationUrl", "supportUrl",
    "privacyPolicyUrl", "termsOfServiceUrl", "defaultEnabled", "dependencies", "settings",
    "userConfig", "types", "channels", "skills", "commands", "agents", "hooks", "mcpServers",
    "lspServers", "outputStyles", "workflows", "experimental",
}
USERCONFIG_KEYS = {"type", "title", "description", "required", "default", "options",
                   "multiple", "sensitive", "min", "max"}
USERCONFIG_TYPES = {"string", "number", "boolean", "directory", "file"}
BARE_PLUGIN_ROOT_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}")


def _as_list(value: object) -> list:
    return value if isinstance(value, list) else [value]


def lint_plugin_manifest(vault: Path = VAULT) -> tuple[list[str], list[str]]:
    """Plugin manifesti va loyiha `.mcp.json` ni rasmiy qoidalarga solishtiradi.

    Qaytaradi: (xatolar, ogohlantirishlar). Xato — plugin yuklanmaydi yoki komponent
    tushib qoladi; ogohlantirish — maydon jim tashlab yuboriladi.
    """
    errors: list[str] = []
    notes: list[str] = []
    manifest = vault / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return [".claude-plugin/plugin.json yo'q"], notes
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"plugin.json buzilgan: {exc}"], notes
    if not isinstance(data, dict):
        return ["plugin.json obyekt emas"], notes

    name = data.get("name")
    if not isinstance(name, str) or not name or re.search(r"[\s@:/\\]", name):
        errors.append("name: bo'sh yoki yaroqsiz belgi bor")
    for key in sorted(set(data) - MANIFEST_KEYS):
        notes.append(f"{key}: noma'lum maydon (yuklashda tashlab yuboriladi)")

    # Komponent yo'llari: `./` bilan boshlanadi, plugin ichida va mavjud bo'lishi shart.
    for key in ("skills", "commands", "agents", "outputStyles", "workflows"):
        if key not in data or isinstance(data[key], dict):
            continue
        for entry in _as_list(data[key]):
            if not isinstance(entry, str):
                errors.append(f"{key}: yo'l satr bo'lishi kerak")
                continue
            if entry != "." and not entry.startswith("./"):
                errors.append(f"{key}: '{entry}' — yo'l './' bilan boshlanishi shart")
                continue
            target = (vault / entry).resolve()
            if vault.resolve() not in (target, *target.parents):
                errors.append(f"{key}: '{entry}' plugin papkasidan tashqarida")
            elif not target.exists():
                errors.append(f"{key}: '{entry}' topilmadi")
            elif key == "agents" and not entry.endswith(".md"):
                errors.append(f"agents: '{entry}' — faqat .md fayllar qabul qilinadi (papka emas)")
            elif key == "skills" and not target.is_dir():
                errors.append(f"skills: '{entry}' papka bo'lishi shart")

    options = data.get("userConfig", {})
    if not isinstance(options, dict):
        errors.append("userConfig: obyekt bo'lishi shart")
        options = {}
    for opt, spec in options.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(opt)):
            errors.append(f"userConfig.{opt}: kalit faqat harf, raqam va _ dan iborat bo'ladi")
        if not isinstance(spec, dict):
            errors.append(f"userConfig.{opt}: obyekt bo'lishi shart")
            continue
        for extra in sorted(set(spec) - USERCONFIG_KEYS):
            errors.append(f"userConfig.{opt}.{extra}: noma'lum kalit (plugin yuklanmaydi)")
        if spec.get("type") not in USERCONFIG_TYPES:
            errors.append(f"userConfig.{opt}.type: {sorted(USERCONFIG_TYPES)} dan biri bo'lishi shart")
        for required in ("title", "description"):
            if not spec.get(required):
                errors.append(f"userConfig.{opt}.{required}: majburiy")
        choices = spec.get("options")
        if choices is not None:
            if spec.get("type") != "string" or spec.get("multiple") or spec.get("sensitive"):
                errors.append(f"userConfig.{opt}.options: faqat oddiy string maydonda ishlaydi")
            elif spec.get("default") not in choices and not spec.get("required"):
                errors.append(f"userConfig.{opt}.default: options ro'yxatidan bo'lishi shart")

    servers = data.get("mcpServers")
    if isinstance(servers, dict):
        for sname, cfg in servers.items():
            if not isinstance(cfg, dict) or not (cfg.get("command") or cfg.get("url")):
                errors.append(f"mcpServers.{sname}: command yoki url kerak")

    # Loyiha rejimi: repo to'g'ridan-to'g'ri ochilganda `${CLAUDE_PLUGIN_ROOT}` bo'sh qoladi,
    # shuning uchun `.mcp.json` da faqat `${CLAUDE_PLUGIN_ROOT:-.}` shakli ishlaydi.
    project_mcp = vault / ".mcp.json"
    if project_mcp.is_file():
        try:
            pcfg = json.loads(project_mcp.read_text(encoding="utf-8"))
            for sname, cfg in (pcfg.get("mcpServers") or {}).items():
                fields = [str(cfg.get("command", "")), *map(str, cfg.get("args") or [])]
                if any(BARE_PLUGIN_ROOT_RE.search(field) for field in fields):
                    errors.append(f".mcp.json {sname}: '${{CLAUDE_PLUGIN_ROOT}}' loyiha rejimida ochilmaydi "
                                  "— '${CLAUDE_PLUGIN_ROOT:-.}' ishlating")
                if isinstance(servers, dict) and sname not in servers:
                    notes.append(f".mcp.json {sname}: plugin.json mcpServers da yo'q (plugin rejimida nisbiy yo'l)")
        except json.JSONDecodeError as exc:
            errors.append(f".mcp.json buzilgan: {exc}")

    hooks_file = vault / "hooks" / "hooks.json"
    if hooks_file.is_file():
        try:
            if "hooks" not in json.loads(hooks_file.read_text(encoding="utf-8")):
                errors.append("hooks/hooks.json: yuqori darajadagi 'hooks' kaliti yo'q")
        except json.JSONDecodeError as exc:
            errors.append(f"hooks/hooks.json buzilgan: {exc}")
    return errors, notes


def official_plugin_validate(vault: Path = VAULT) -> tuple[str, str]:
    """`claude plugin validate` natijasi: (holat, izoh). CLI yo'q bo'lsa — ('skip', ...)."""
    import shutil
    cli = shutil.which("claude")
    if not cli:
        return SKIP, "claude CLI yo'q"
    try:
        proc = run([cli, "plugin", "validate", str(vault)], timeout=90)
    except Exception as exc:  # timeout, ishga tushmadi
        return SKIP, f"validator ishlamadi: {exc}"
    text = (proc.stdout or "") + (proc.stderr or "")
    if "Validation failed" in text:
        found = re.findall(r"^\s*>\s*(.+)$", text, re.M)
        return FAIL, "; ".join(dict.fromkeys(found[:3])) or "Validation failed"
    if "Validation passed" in text:
        return OK, "rasmiy validator o'tdi"
    return SKIP, "validator natijasi noaniq"


def check_plugin_manifest(report: Report, quick: bool = False) -> None:
    errors, notes = lint_plugin_manifest()
    label = "Plugin manifesti"
    if errors:
        report.add(label, FAIL, "; ".join(errors[:4]) + (f" +{len(errors) - 4}" if len(errors) > 4 else ""))
        return
    status, detail = (SKIP, "tezkor rejim") if quick else official_plugin_validate()
    if status == FAIL:
        report.add(label, FAIL, f"claude plugin validate: {detail}")
    elif notes:
        report.add(label, WARN, "; ".join(notes[:3]))
    else:
        suffix = f" · {detail}" if status == OK else f" · {detail} (faqat lokal qoidalar)"
        report.add(label, OK, "qoidalarga mos" + suffix)


RELATIVE_TOOL_RE = re.compile(r"(?:python3?|py -3)\s+(?:tools|hooks)[\\/][A-Za-z0-9_\-]+\.py")
SHELL_CALL_RE = re.compile(r"(?:python3?|py -3)\s+\"?\$\{CLAUDE_PLUGIN_ROOT\}")
PLUGIN_ROOT_TOKEN = "${CLAUDE_PLUGIN_ROOT}"
# Claude Code faqat o'zi yuklagan skill/buyruq/agent matnida `${CLAUDE_PLUGIN_ROOT}` ni almashtiradi.
SUBSTITUTED_GLOBS = ("commands/*.md", "skills/*/SKILL.md", "agents/*.md")
# Bularni model Read orqali o'qiydi yoki loyiha rejimida ishlatadi — almashtirish yo'q.
PLAIN_GLOBS = ("rules/*.md", "wiki/*.md", "playbooks/*.md", "contexts/*.md", "templates/*.md",
               "markets/**/*.md", "skills/*/references/**/*.md", ".claude/commands/*.md")


def lint_tool_paths(vault: Path = VAULT) -> list[str]:
    """Asbob chaqiruvlari plugin o'rnatilgan har qanday papkadan ishlaydimi.

    Plugin o'rnatilganda cwd — foydalanuvchi loyihasi, shuning uchun `python3 tools/x.py`
    topilmaydi. Qoidalar:
      1. skill/buyruq/agent matnida chaqiruv `"${CLAUDE_PLUGIN_ROOT}/tools/x.py"` shaklida bo'ladi;
      2. Bash'i yo'q agentga buyruq bajarish topshirilmaydi;
      3. almashtirilmaydigan fayllarda `${CLAUDE_PLUGIN_ROOT}` uchramaydi (Bash'da u bo'sh).
    """
    problems: list[str] = []
    for pattern in SUBSTITUTED_GLOBS:
        for path in sorted(vault.glob(pattern)):
            text = path.read_text(encoding="utf-8", errors="replace")
            rel = path.relative_to(vault).as_posix()
            hits = RELATIVE_TOOL_RE.findall(text)
            if hits:
                problems.append(f"{rel}: {len(hits)} nisbiy chaqiruv ({hits[0]}) — \"${{CLAUDE_PLUGIN_ROOT}}/...\" kerak")
            if pattern.startswith("agents/"):
                tools_line = re.search(r"^tools:\s*(.*)$", text, re.M)
                has_shell = bool(tools_line) and "Bash" in [t.strip() for t in tools_line.group(1).split(",")]
                if not has_shell and SHELL_CALL_RE.search(text):
                    problems.append(f"{rel}: Bash'i yo'q agentga buyruq bajarish topshirilgan")
    for pattern in PLAIN_GLOBS:
        for path in sorted(vault.glob(pattern)):
            if PLUGIN_ROOT_TOKEN in path.read_text(encoding="utf-8", errors="replace"):
                problems.append(f"{path.relative_to(vault).as_posix()}: ${{CLAUDE_PLUGIN_ROOT}} bu faylda almashtirilmaydi")
    return problems


def check_tool_paths(report: Report) -> None:
    problems = lint_tool_paths()
    if problems:
        report.add("Asbob yo'llari", FAIL, "; ".join(problems[:3]) + (f" +{len(problems) - 3}" if len(problems) > 3 else ""))
    else:
        report.add("Asbob yo'llari", OK, "barcha chaqiruvlar istalgan papkadan ishlaydi")


def mcp_handshake(timeout: int = 20) -> dict:
    """tyrion-core ni `.mcp.json` dagidek ishga tushirib, initialize → ping → tools/list yuboradi.

    Tashqi papkadan va `CLAUDE_PLUGIN_ROOT` siz ishlaydi — ya'ni server o'z ildizini o'zi
    topa olishi tekshiriladi. Qaytaradi: {ok, tools, protocol, error}.
    """
    import os
    import shutil
    import tempfile

    launcher = VAULT / "hooks" / "run-hook.cjs"
    node = shutil.which("node")
    if node and launcher.is_file():
        cmd = [node, str(launcher), "--mcp"]
    else:
        cmd = [sys.executable, str(TOOLS / "tyrion-mcp-server.py")]
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "tyrion-doctor", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "ping"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_ROOT"}
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        with tempfile.TemporaryDirectory() as outside:
            proc = subprocess.run(
                cmd, input="".join(json.dumps(r) + "\n" for r in requests), cwd=outside, env=env,
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
            )
    except Exception as exc:
        return {"ok": False, "error": f"ishga tushmadi: {exc}"}
    replies: dict = {}
    for line in (proc.stdout or "").splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            return {"ok": False, "error": "stdout da JSON bo'lmagan qator (protokol buziladi)"}
        replies[msg.get("id")] = msg
    init, ping, listing = replies.get(1, {}), replies.get(2, {}), replies.get(3, {})
    if "result" not in init:
        return {"ok": False, "error": f"initialize javobsiz (rc={proc.returncode}) {(proc.stderr or '')[:120]}".strip()}
    if "result" not in ping:
        return {"ok": False, "error": "ping javobsiz — klient serverni uzib qo'yadi"}
    tools = (listing.get("result") or {}).get("tools") or []
    if not tools:
        return {"ok": False, "error": "tools/list bo'sh"}
    return {"ok": True, "tools": len(tools), "protocol": init["result"].get("protocolVersion"), "error": ""}


def check_mcp_and_evals(report: Report) -> None:
    """MCP Server (jonli handshake) va Behavioral Evals (skill-eval.py) tekshiruvi."""
    import importlib
    mcp_cfg = VAULT / ".mcp.json"
    mcp_srv = TOOLS / "tyrion-mcp-server.py"
    if not mcp_cfg.is_file() or not mcp_srv.is_file():
        report.add("MCP Server (.mcp.json)", FAIL, ".mcp.json yoki tyrion-mcp-server.py yo'q")
    else:
        result = mcp_handshake()
        if result["ok"]:
            report.add("MCP Server (.mcp.json)", OK,
                       f"tyrion-core javob berdi ({result['tools']} MCP tool, ping ✓, {result['protocol']})")
        else:
            report.add("MCP Server (.mcp.json)", FAIL, f"ulanmadi: {result['error']}")

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
    """Graf qaydlar to'plamiga mosmi. Tarkib bo'yicha solishtiriladi: yangi klonda barcha
    fayllarning mtime'i deyarli bir xil bo'ladi, shuning uchun vaqt farqi yolg'on signal berardi."""
    graph = VAULT / "graphify-out" / "graph.json"
    if not graph.is_file():
        report.add("Bilim grafi", SKIP, "graf ixtiyoriy (graphify-out/graph.json yo'q)")
        return
    try:
        nodes = json.loads(graph.read_text(encoding="utf-8")).get("nodes", [])
    except (json.JSONDecodeError, OSError) as exc:
        report.add("Bilim grafi", WARN, f"o'qib bo'lmadi: {exc} (python3 tools/brain-graph.py build)")
        return
    in_graph = {str(n.get("source_file", "")).replace("\\", "/") for n in nodes}
    notes = {i["path"] for i in data["items"].get("wiki", [])}
    missing = sorted(notes - in_graph)
    gone = sorted(src for src in in_graph if src and not (VAULT / src).is_file())
    if missing or gone:
        parts = []
        if missing:
            parts.append(f"{len(missing)} qayd grafda yo'q")
        if gone:
            parts.append(f"{len(gone)} tugun manbasi o'chirilgan")
        report.add("Bilim grafi", WARN, "eskirgan — " + ", ".join(parts) + " (python3 tools/brain-graph.py build)")
    else:
        size_kb = graph.stat().st_size / 1024
        report.add("Bilim grafi", OK, f"qaydlarga mos ({len(nodes)} tugun, {size_kb:.0f} KB)")


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


SKILL_MAX_LINES = 500


def oversized_skills(vault: Path = VAULT) -> list[tuple[str, int]]:
    """SKILL.md yuklangach butun suhbat davomida kontekstda qoladi, shuning uchun u ixcham
    bo'lishi kerak (rasmiy tavsiya: 500 qatordan kam; tafsilot `references/` da)."""
    result = []
    for path in sorted(vault.glob("skills/*/SKILL.md")):
        lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        if lines > SKILL_MAX_LINES:
            result.append((path.parent.name, lines))
    return result


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
    long_skills = oversized_skills()
    if proc.returncode == 0 and long_skills:
        names = ", ".join(f"{name} ({lines})" for name, lines in long_skills[:4])
        report.add("Skill reyestri", WARN, f"{detail} · {SKILL_MAX_LINES} qatordan uzun: {names} — tafsilotni references/ ga ko'chiring")
    elif proc.returncode == 0:
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
    check_skills(report)
    check_instincts(report)
    check_shield(report)
    check_memory(report)
    check_plugin_manifest(report, args.quick)
    check_tool_paths(report)
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
