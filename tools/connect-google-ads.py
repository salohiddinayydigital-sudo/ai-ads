#!/usr/bin/env python3
"""Tyrion Google Ads (faqat o'qish) — bir qadamli ulash.

Rasmiy `googleads/google-ads-mcp` serveri `search`, `customers`, `metadata` asboblaridan tashqari
reklama hisobiga YOZADIGAN asboblarni ham beradi (`labels`, `assets`). Tyrion hisobga yozmaydi, shuning
uchun bu ulagich serverni doim faqat o'qish rejimida sozlaydi: `tools_config.yaml` da `labels` va `assets`
o'chiriladi va `GOOGLE_ADS_MCP_TOOLS_CONFIG` shu faylga yo'naltiriladi.

Ishlatish:
  python3 tools/connect-google-ads.py            # tekshiradi va rejani ko'rsatadi (hech narsa o'zgarmaydi)
  python3 tools/connect-google-ads.py --apply    # `claude mcp add` ni bajaradi (foydalanuvchi darajasida)
  python3 tools/connect-google-ads.py --remove   # ulanishni olib tashlaydi

Kirish (birinchi topilgani olinadi): bayroq > muhit o'zgaruvchisi > standart joy.
  --developer-token   GOOGLE_ADS_DEVELOPER_TOKEN
  --credentials       GOOGLE_APPLICATION_CREDENTIALS | ~/.config/gcloud/application_default_credentials.json
  --project           GOOGLE_PROJECT_ID | GOOGLE_CLOUD_PROJECT
  --login-customer-id GOOGLE_ADS_LOGIN_CUSTOMER_ID (MCC ostida ishlasangiz)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

SERVER_NAME = "google-ads"
SPEC = "git+https://github.com/googleads/google-ads-mcp.git"
READ_ONLY_CONFIG = (
    "# Tyrion: Google Ads faqat o'qish. Bu faylni o'zgartirmang — ulagich qayta yozadi.\n"
    "namespaces:\n"
    "  customers: true\n"
    "  search: true\n"
    "  metadata: true\n"
    "  labels: false\n"
    "  assets: false\n"
)
DEFAULT_ADC = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
_ID_RE = re.compile(r"^\d{10}$")
WRITE_NAMESPACES = ("labels", "assets")


def config_path() -> Path:
    # Doim foydalanuvchi papkasida: checkout'ni ham, plugin keshini ham (yangilanishda almashadi) ifloslantirmaydi.
    base = os.environ.get(tcore.STATE_DIR_ENV, "").strip()
    return (Path(base).expanduser() if base else Path.home() / ".tyrion") / "google-ads" / "tools_config.yaml"


def read_only_violations(text: str) -> list[str]:
    """Namespaces that still allow writing in a tools_config.yaml (empty list = read-only)."""
    bad = []
    for name in WRITE_NAMESPACES:
        match = re.search(rf"^\s*{name}\s*:\s*(.*?)\s*$", text, re.M)
        if not match or match.group(1).lower() != "false":
            bad.append(name)
    return bad


def normalize_customer_id(value: str) -> str:
    digits = re.sub(r"[\s-]", "", str(value or ""))
    return digits if _ID_RE.match(digits) else ""


def gather(args: argparse.Namespace) -> dict[str, str]:
    env = os.environ
    token = args.developer_token or env.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    creds = args.credentials or env.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not creds and DEFAULT_ADC.is_file():
        creds = str(DEFAULT_ADC)
    return {
        "developer_token": tcore.usable_setting(token),
        "credentials": str(Path(creds).expanduser()) if creds else "",
        "project": args.project or env.get("GOOGLE_PROJECT_ID", "") or env.get("GOOGLE_CLOUD_PROJECT", ""),
        "login_customer_id": normalize_customer_id(args.login_customer_id or env.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")),
    }


def missing_steps(values: dict[str, str], have_pipx: bool, have_claude: bool) -> list[str]:
    steps = []
    if not have_pipx:
        steps.append("pipx o'rnating: https://pipx.pypa.io/stable/#install-pipx")
    if not have_claude:
        steps.append("`claude` buyrug'i topilmadi — Claude Code o'rnatilganini tekshiring")
    if not values["developer_token"]:
        steps.append("Developer token yo'q: Google Ads → Tools → API Center; so'ng `export GOOGLE_ADS_DEVELOPER_TOKEN=...`")
    if not values["credentials"] or not Path(values["credentials"]).is_file():
        steps.append(
            "Kirish ma'lumoti topilmadi: `gcloud auth application-default login --scopes "
            "https://www.googleapis.com/auth/adwords,https://www.googleapis.com/auth/cloud-platform`"
        )
    if not values["project"]:
        steps.append("Google Cloud loyiha ID si yo'q: `--project <id>` yoki `GOOGLE_PROJECT_ID` (Google Ads API shu loyihada yoqilgan bo'lsin)")
    return steps


def server_env(values: dict[str, str], cfg: Path) -> dict[str, str]:
    env = {
        "GOOGLE_APPLICATION_CREDENTIALS": values["credentials"],
        "GOOGLE_PROJECT_ID": values["project"],
        "GOOGLE_ADS_DEVELOPER_TOKEN": values["developer_token"],
        "GOOGLE_ADS_MCP_TOOLS_CONFIG": str(cfg),
    }
    if values["login_customer_id"]:
        env["GOOGLE_ADS_LOGIN_CUSTOMER_ID"] = values["login_customer_id"]
    return env


def build_command(env: dict[str, str]) -> list[str]:
    cmd = ["claude", "mcp", "add", "--scope", "user", SERVER_NAME]
    for key, value in env.items():
        cmd += ["-e", f"{key}={value}"]
    return cmd + ["--", "pipx", "run", "--spec", SPEC, "google-ads-mcp"]


def masked(cmd: list[str]) -> str:
    out = []
    for part in cmd:
        if part.startswith("GOOGLE_ADS_DEVELOPER_TOKEN="):
            part = "GOOGLE_ADS_DEVELOPER_TOKEN=***"
        out.append(part)
    return " ".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="connect-google-ads.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="ulanishni haqiqatan qo'shadi")
    parser.add_argument("--remove", action="store_true", help="ulanishni olib tashlaydi")
    parser.add_argument("--developer-token", default="")
    parser.add_argument("--credentials", default="")
    parser.add_argument("--project", default="")
    parser.add_argument("--login-customer-id", default="")
    args = parser.parse_args(argv)

    have_claude = shutil.which("claude") is not None
    if args.remove:
        if not have_claude:
            print("Xato: `claude` buyrug'i topilmadi.", file=sys.stderr)
            return 2
        return subprocess.run(["claude", "mcp", "remove", "--scope", "user", SERVER_NAME]).returncode

    values = gather(args)
    todo = missing_steps(values, shutil.which("pipx") is not None, have_claude)
    cfg = config_path()
    print("Google Ads (faqat o'qish) ulanishi")
    print(f"  Kirish ma'lumoti : {values['credentials'] or '—'}")
    print(f"  Loyiha           : {values['project'] or '—'}")
    print(f"  Developer token  : {'bor' if values['developer_token'] else 'yo‘q'}")
    print(f"  MCC (login)      : {values['login_customer_id'] or '—'}")
    print(f"  Sozlama fayli    : {cfg}  (labels va assets o'chirilgan)")
    if todo:
        print("\nHali yetishmaydi:")
        for step in todo:
            print(f"  - {step}")
        return 2

    cmd = build_command(server_env(values, cfg))
    if not args.apply:
        print("\nReja (hech narsa o'zgarmadi):\n  " + masked(cmd))
        print("\nBajarish uchun: python3 tools/connect-google-ads.py --apply")
        return 0

    tcore.atomic_write_text(cfg, READ_ONLY_CONFIG)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Xato: `claude mcp add` muvaffaqiyatsiz tugadi.", file=sys.stderr)
        return result.returncode
    print("\n✓ Ulandi. Claude Code'ni qayta ishga tushiring va `/mcp` da google-ads ni ko'ring.")
    print("  Faqat o'qish: customers, search, metadata. Yozuvchi asboblar (labels, assets) o'chirilgan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
