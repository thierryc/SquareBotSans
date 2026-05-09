#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GS_BIN="${GS_BIN:-gs}"

DEFAULT_RGB_PROFILE="${DEFAULT_RGB_PROFILE:-/System/Library/ColorSync/Profiles/sRGB Profile.icc}"
OUTPUT_PROFILE="${OUTPUT_PROFILE:-/System/Library/ColorSync/Profiles/Generic CMYK Profile.icc}"

if ! command -v "$GS_BIN" >/dev/null 2>&1; then
  cat >&2 <<'MSG'
Ghostscript was not found.

Install it with:
  brew install ghostscript

Then run:
  tools/convert_specimen_cmyk.sh

For press delivery, pass the printer's CMYK ICC profile:
  OUTPUT_PROFILE="/path/to/GRACoL_or_FOGRA.icc" tools/convert_specimen_cmyk.sh
MSG
  exit 127
fi

if [[ ! -f "$DEFAULT_RGB_PROFILE" ]]; then
  echo "Missing DEFAULT_RGB_PROFILE: $DEFAULT_RGB_PROFILE" >&2
  exit 1
fi

if [[ ! -f "$OUTPUT_PROFILE" ]]; then
  echo "Missing OUTPUT_PROFILE: $OUTPUT_PROFILE" >&2
  exit 1
fi

convert_pdf() {
  local input="$1"
  local output="$2"

  if [[ ! -f "$input" ]]; then
    echo "Missing input PDF: $input" >&2
    exit 1
  fi

  rm -f "$output"

  "$GS_BIN" \
    --permit-file-read="$input:$DEFAULT_RGB_PROFILE:$OUTPUT_PROFILE" \
    --permit-file-write="$output" \
    -dSAFER \
    -dBATCH \
    -dNOPAUSE \
    -sDEVICE=pdfwrite \
    -dCompatibilityLevel=1.7 \
    -dPDFSETTINGS=/prepress \
    -dAutoRotatePages=/None \
    -dEmbedAllFonts=true \
    -dSubsetFonts=true \
    -dCompressFonts=true \
    -dBlackText=true \
    -dProcessColorModel=/DeviceCMYK \
    -sColorConversionStrategy=CMYK \
    -sBlendConversionStrategy=Managed \
    -dOverrideICC \
    -sDefaultRGBProfile="$DEFAULT_RGB_PROFILE" \
    -sOutputICCProfile="$OUTPUT_PROFILE" \
    -sOutputFile="$output" \
    "$input"

  echo "wrote ${output#$ROOT/}"
}

convert_pdf "$ROOT/specimen-squarebot-sans.pdf" "$ROOT/specimen-squarebot-sans-cmyk.pdf"
convert_pdf "$ROOT/specimen-squarebot-sans-letter.pdf" "$ROOT/specimen-squarebot-sans-letter-cmyk.pdf"
