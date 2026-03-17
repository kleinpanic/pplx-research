#!/usr/bin/env bash
# agent-workflow.sh — how an agent calls pplx-research and parses JSON output in a loop
#
# Demonstrates: JSON parsing, iterative research loop, building a structured report,
# error handling, and chaining results from one query into the next.

set -euo pipefail

# Helper: run pplx-research and return parsed JSON content field
research_summary() {
    local query="$1"
    shift
    pplx-research "$query" --format json --quiet "$@" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['content'])"
}

# Helper: run pplx-research and return all citations as newline-separated URLs
research_citations() {
    local query="$1"
    shift
    pplx-research "$query" --format json --quiet "$@" \
        | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('citations', []):
    print(c)
"
}

# -----------------------------------------------------------------------
# Example: Agent building a structured technology report in a loop
# -----------------------------------------------------------------------

TOPIC="WebAssembly in production 2024"
OUTPUT_FILE="/tmp/agent-wasm-report.md"

echo "Agent: Starting research loop for topic: $TOPIC"
echo ""

# Step 1: Overview — quick mode for broad context
echo "## Agent Step 1: Quick overview"
overview=$(research_summary "$TOPIC" --mode quick)
echo "$overview"
echo ""

# Step 2: Deep dive — gather detailed information
echo "## Agent Step 2: Deep research"
deep_content=$(research_summary "$TOPIC" --mode deep --depth 3 --sources academic,docs)
echo "$deep_content"
echo ""

# Step 3: Community perspective — what practitioners say
echo "## Agent Step 3: Community perspective"
community=$(research_summary "WebAssembly production use cases developer experience" \
    --mode quick --sources forums)
echo "$community"
echo ""

# Step 4: Collect all citations from multiple angles
echo "## Agent Step 4: Gathering citations"
declare -a ALL_CITATIONS=()
while IFS= read -r url; do
    ALL_CITATIONS+=("$url")
done < <(research_citations "$TOPIC" --mode deep --depth 2)

echo "Found ${#ALL_CITATIONS[@]} citations"
printf '%s\n' "${ALL_CITATIONS[@]}"
echo ""

# Step 5: Assemble the final report
echo "## Agent Step 5: Assembling report"
{
    echo "# Research Report: $TOPIC"
    echo ""
    echo "## Overview"
    echo "$overview"
    echo ""
    echo "## Deep Analysis"
    echo "$deep_content"
    echo ""
    echo "## Community Perspective"
    echo "$community"
    echo ""
    echo "## Sources"
    for url in "${ALL_CITATIONS[@]}"; do
        echo "- $url"
    done
} > "$OUTPUT_FILE"

echo "Report written to $OUTPUT_FILE"
echo "Lines: $(wc -l < "$OUTPUT_FILE")"

# -----------------------------------------------------------------------
# Example: Iterative research — refine query based on initial answer
# -----------------------------------------------------------------------

echo ""
echo "=== Iterative refinement example ==="

# Initial broad query
initial=$(pplx-research "Wasm WASI status" --format json --quiet)
initial_content=$(echo "$initial" | python3 -c "import sys,json; print(json.load(sys.stdin)['content'])")

echo "Initial answer:"
echo "$initial_content" | head -5
echo "..."

# Extract a follow-up topic from the answer (simulate agent reasoning)
# In a real agent, an LLM would derive the follow-up from the content
followup_query="WASI preview2 component model specification"
echo ""
echo "Follow-up query: $followup_query"

followup=$(research_summary "$followup_query" --mode deep --depth 2 --sources docs)
echo "Follow-up result:"
echo "$followup" | head -10
echo "..."

echo ""
echo "Agent workflow complete."
