#!/bin/bash
# Agent Hunt — weekly data refresh (collect + export + commit + deploy).
#
# Triggered by launchd (~/Library/LaunchAgents/com.llm-x-factorer.agent-hunt.weekly.plist)
# every Sunday at 02:00 local time. Designed to be idempotent — if collectors
# fail (rate-limited / OpenRouter quota / etc.) the script keeps going and
# refreshes whatever else it can.
#
# Manual run:
#   /Users/liu/Projects/agent-hunt/ops/weekly_refresh.sh
#
# Logs: ~/Library/Logs/agent-hunt/weekly-YYYYMMDD-HHMMSS.log

set -uo pipefail

REPO_DIR="/Users/liu/Projects/agent-hunt"
LOG_DIR="$HOME/Library/Logs/agent-hunt"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/weekly-$(date +%Y%m%d-%H%M%S).log"

exec > >(tee -a "$LOG_FILE") 2>&1

# Bring in user PATH (npm / docker / wrangler) — launchd's PATH is minimal.
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.npm-global/bin:$PATH"
source "$HOME/.zshrc" 2>/dev/null || true

echo "=== Agent Hunt weekly refresh — $(date) ==="
cd "$REPO_DIR"

# ---------------------------------------------------------------------------
# 1. Make sure DB + Redis are up
# ---------------------------------------------------------------------------
echo "--- ensuring docker compose services up ---"
docker compose up -d
# Best-effort wait for db healthy (max 30s)
for i in $(seq 1 15); do
    if docker compose ps db --format json 2>/dev/null | grep -q '"healthy"'; then
        break
    fi
    sleep 2
done

# ---------------------------------------------------------------------------
# 2. Incremental collect — only the cheap, no-anti-scrape sources
# ---------------------------------------------------------------------------
cd "$REPO_DIR/backend"

echo "--- collecting incremental data ---"
.venv/bin/python scripts/collect_hn_wih.py 2>&1 || echo "[warn] HN WIH collect failed (non-critical)"
.venv/bin/python scripts/collect_github_hiring.py 2>&1 || echo "[warn] GitHub hiring collect failed (non-critical)"

# ---------------------------------------------------------------------------
# 3. Backfill role_type for any new entries (rule-based, no LLM cost)
# ---------------------------------------------------------------------------
echo "--- rule-based role_type backfill ---"
.venv/bin/python scripts/backfill_role_type_rules.py --apply 2>&1 || echo "[warn] backfill failed (non-critical)"

# ---------------------------------------------------------------------------
# 4. Re-export every dependent JSON
# ---------------------------------------------------------------------------
echo "--- regenerating frontend/public/data/*.json ---"
EXPORT_SCRIPTS=(
    export_api_snapshots
    export_market_data
    analyze_roles
    export_real_salary
    export_roles_by_industry
    export_roles_by_city
    export_augmented_by_profession
    export_industry_salary
    export_graduate_friendly
    export_quality_signals
    export_applicant_profiles
    export_vendor_title_breakdown
    export_narrative_stats
    export_narrative_examples
    export_trends
)
for s in "${EXPORT_SCRIPTS[@]}"; do
    echo "  > $s"
    .venv/bin/python "scripts/$s.py" 2>&1 | tail -3 || echo "    [warn] $s failed"
done

# ---------------------------------------------------------------------------
# 5. Commit + push if any data JSON changed
# ---------------------------------------------------------------------------
cd "$REPO_DIR"
echo "--- checking for data changes ---"
if [[ -n "$(git status --porcelain frontend/public/data/)" ]]; then
    git add frontend/public/data/
    git commit -m "data: weekly refresh ($(date +%Y-%m-%d))" 2>&1 || echo "[warn] commit skipped"
    git push 2>&1 || echo "[warn] git push failed"
else
    echo "no data changes"
fi

# ---------------------------------------------------------------------------
# 6. Frontend rebuild + Cloudflare Pages deploy
# ---------------------------------------------------------------------------
echo "--- frontend build + deploy ---"
cd "$REPO_DIR/frontend"
npm run build 2>&1 | tail -5
npx wrangler pages deploy out --project-name agent-hunt --commit-dirty=true 2>&1 | tail -5 || echo "[warn] wrangler deploy failed"

echo "=== Done — $(date) ==="
