#!/usr/bin/env bash
# synthesis-compare.sh — multi-perspective synthesis for comparisons
#
# Demonstrates: --mode synthesis, --format json, parsing JSON output, X vs Y queries

set -euo pipefail

# --- Example 1: Classic X vs Y comparison, markdown output ---
echo "=== Example 1: Rust vs Go comparison ==="
pplx-research "Rust vs Go for systems programming" \
    --mode synthesis \
    --quiet

# --- Example 2: Comparison with JSON output for programmatic parsing ---
echo ""
echo "=== Example 2: PostgreSQL vs MySQL, JSON output ==="
result=$(pplx-research "PostgreSQL vs MySQL for production web apps 2024" \
    --mode synthesis \
    --format json \
    --quiet)

# Parse content from JSON
content=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['content'])")
citations=$(echo "$result" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for i, c in enumerate(data.get('citations', []), 1):
    print(f'{i}. {c}')
")

echo "--- Content ---"
echo "$content"
echo ""
echo "--- Citations ---"
echo "$citations"

# --- Example 3: Architecture debate with specific sources ---
echo ""
echo "=== Example 3: Microservices vs monolith (academic + forums) ==="
pplx-research "microservices vs monolith architecture tradeoffs" \
    --mode synthesis \
    --sources academic,forums \
    --quiet

# --- Example 4: Save synthesis report to file ---
echo ""
echo "=== Example 4: Save comparison report to file ==="
pplx-research "React vs Vue vs Svelte frontend framework comparison" \
    --mode synthesis \
    --quiet \
    --output /tmp/frontend-frameworks.md
echo "Report saved to /tmp/frontend-frameworks.md"

# --- Example 5: Quick synthesis for pros/cons ---
echo ""
echo "=== Example 5: Pros and cons synthesis ==="
pplx-research "pros and cons of GraphQL vs REST for mobile apps" \
    --mode synthesis \
    --depth 2 \
    --format summary \
    --quiet
