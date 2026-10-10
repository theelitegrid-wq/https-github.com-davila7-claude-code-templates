#!/usr/bin/env bash
# Find local businesses on Google Maps, then rank them as leads.
#
# Usage:  tools/find_leads.sh "Austin, TX"            (uses the default niches below)
#         tools/find_leads.sh "Austin, TX" dentist roofer
#
# Needs Docker running. Uses the open-source gosom/google-maps-scraper (MIT).
# Takes ~5-15 minutes. Results: data/results.csv, then data/leads_ranked.csv + data/messages.md
set -euo pipefail

CITY="${1:?Give a city, e.g. tools/find_leads.sh \"Austin, TX\"}"
shift
# Niches that pay well and lose real money when customers can't find or reach them.
NICHES=("$@")
[ ${#NICHES[@]} -eq 0 ] && NICHES=(dentist roofer plumber "hvac contractor" "med spa"
                                   "auto repair" "law firm" "hair salon")

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/data"
QUERIES="$ROOT/data/queries.txt"
: > "$QUERIES"
for n in "${NICHES[@]}"; do echo "$n in $CITY" >> "$QUERIES"; done
echo "Searching Google Maps for:"; sed 's/^/  - /' "$QUERIES"

docker run --rm \
  -v gmaps-playwright-cache:/opt \
  -v "$QUERIES:/queries.txt:ro" \
  -v "$ROOT/data:/out" \
  gosom/google-maps-scraper:v1.18.1 \
  -input /queries.txt \
  -results /out/results.csv \
  -depth 1 \
  -email \
  -exit-on-inactivity 3m

python3 "$ROOT/tools/qualify_leads.py" "$ROOT/data/results.csv" --name "${MY_NAME:-[Your name]}"
