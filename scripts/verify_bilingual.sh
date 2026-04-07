#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/3] Auditing bilingual completeness..."
python3 scripts/audit_bilingual_completeness.py --summary "$@"

echo "[2/3] Checking bilingual paragraph pairing..."
python3 scripts/check_bilingual_format.py --summary "$@"

echo "[3/3] Building bilingual PDF..."
latexmk -xelatex -interaction=nonstopmode main_bilingual.tex
