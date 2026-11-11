#!/usr/bin/env bash
# push.sh — Tyrion Automated Pre-Flight Verification & GitHub Push Script
set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$VAULT_ROOT"

PY_CMD="python3"
command -v python3 >/dev/null 2>&1 || PY_CMD="python"

echo "===================================================================="
echo "  🚀 TYRION — GITHUB PRE-PUSH VERIFICATION & DEPLOY"
echo "===================================================================="

echo "[1/5] Running TyrionShield Security Scan (Zero Secrets Gate)..."
"$PY_CMD" tools/tyrion-shield.py scan

echo "[2/5] Running Vault Audit & Catalog Sync Gate..."
"$PY_CMD" tools/vault-audit.py . --gate
"$PY_CMD" tools/catalog.py check
"$PY_CMD" tools/catalog.py drift

echo "[3/5] Running Behavioral Eval Suite (24/24)..."
"$PY_CMD" tools/skill-eval.py

echo "[4/5] Running System Doctor..."
"$PY_CMD" tools/doctor.py --quick

echo "[5/6] Unit testlar..."
"$PY_CMD" -m unittest discover -s tests -q

# Mavjud remote'ga tegilmaydi; faqat remote umuman yo'q bo'lsa va URL berilgan bo'lsa qo'shiladi.
if ! git remote get-url origin >/dev/null 2>&1; then
    if [ -n "${1:-}" ]; then
        git remote add origin "$1"
    else
        echo "Xato: 'origin' remote yo'q. Ishlatish: ./push.sh <remote-url>" >&2
        exit 1
    fi
fi

BRANCH="$(git branch --show-current)"
if [ -z "$BRANCH" ]; then
    echo "Xato: detached HEAD — branch tanlang." >&2
    exit 1
fi
echo "[6/6] Pushing branch '$BRANCH' and tags to $(git remote get-url origin) ..."
git push -u origin "$BRANCH" --tags
echo "✅ Successfully pushed '$BRANCH' to GitHub!"
