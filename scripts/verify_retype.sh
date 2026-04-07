#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/2] Building English PDF..."
latexmk -xelatex -interaction=nonstopmode main.tex

echo "[2/2] Auditing English retype completeness..."
python3 scripts/audit_retype_completeness.py --summary
