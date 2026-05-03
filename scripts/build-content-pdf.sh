#!/bin/bash
# 把 content/0X-*/wechat.md 批量导出成 PDF，给业务方做公众号发布交付包用。
# 依赖：pandoc + Google Chrome（macOS）。复用 scripts/docs-pdf.css。
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTENT_DIR="$ROOT/content"
CSS="$ROOT/scripts/docs-pdf.css"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT_DIR="$CONTENT_DIR/pdf"
mkdir -p "$OUT_DIR"

build() {
  local md="$1"
  local out="$2"
  local src_dir
  src_dir="$(dirname "$md")"
  local html
  html="$(mktemp -t agent-hunt-content-pdf).html"
  ( cd "$src_dir" && pandoc "$(basename "$md")" \
      --standalone --metadata title="" \
      --css "$CSS" --embed-resources -o "$html" )
  "$CHROME" --headless --disable-gpu --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf="$out" "file://$html" 2>/dev/null
  rm "$html"
  printf "  → %s (%s)\n" "$out" "$(du -h "$out" | cut -f1)"
}

for md in "$CONTENT_DIR"/0*/wechat.md; do
  slug="$(basename "$(dirname "$md")")"
  build "$md" "$OUT_DIR/${slug}.pdf"
done

echo ""
echo "Done. $(ls "$OUT_DIR"/*.pdf | wc -l | tr -d ' ') PDFs in $OUT_DIR"
