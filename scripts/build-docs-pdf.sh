#!/bin/bash
# 生成运营/业务用的 PDF（中文 + 截图，无页眉页脚）。
# 依赖：pandoc + Google Chrome（macOS）。
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS_DIR="$ROOT/docs/operations"
CSS="$ROOT/scripts/docs-pdf.css"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p "$DOCS_DIR/pdf"

build() {
  local md="$1"
  local out="$2"
  local html
  html="$(mktemp -t agent-hunt-pdf).html"
  ( cd "$DOCS_DIR" && pandoc "$(basename "$md")" \
      --standalone --metadata title="" \
      --css "$CSS" --embed-resources -o "$html" )
  "$CHROME" --headless --disable-gpu --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf="$out" "file://$html" 2>/dev/null
  rm "$html"
  printf "  → %s (%s)\n" "$out" "$(du -h "$out" | cut -f1)"
}

build "$DOCS_DIR/产品手册-运营版.md" "$DOCS_DIR/pdf/产品手册-运营版.pdf"
build "$DOCS_DIR/网站使用-图文版.md" "$DOCS_DIR/pdf/网站使用-图文版.pdf"
