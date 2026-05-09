#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 tools/build_specimen.py
node tools/export_specimen_pdf.mjs
tools/convert_specimen_cmyk.sh
