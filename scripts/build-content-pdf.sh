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

cn_name() {
  case "$1" in
    01-35-crisis)                    echo "01-35岁危机不成立" ;;
    02-genai-gap)                    echo "02-国内外AI说两种语言" ;;
    03-traditional-industry-ai)      echo "03-传统行业AI更值钱" ;;
    04-traditional-salary-premium)   echo "04-银行40k互联网20k" ;;
    05-bridge-engineer)              echo "05-OpenAI桥梁工程师" ;;
    06-cross-market-arbitrage)       echo "06-海外AI真实2.78倍" ;;
    07-ghost-listings)               echo "07-Deloitte幽灵岗" ;;
    *)                               echo "$1" ;;
  esac
}

for md in "$CONTENT_DIR"/0*/wechat.md; do
  slug="$(basename "$(dirname "$md")")"
  out_name="$(cn_name "$slug")"
  build "$md" "$OUT_DIR/${out_name}.pdf"
done

echo ""
echo "Done. $(ls "$OUT_DIR"/*.pdf | wc -l | tr -d ' ') PDFs in $OUT_DIR"
