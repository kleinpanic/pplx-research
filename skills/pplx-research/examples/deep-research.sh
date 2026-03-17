#!/usr/bin/env bash
# deep-research.sh — deep iterative research with gap analysis
#
# Demonstrates: --mode deep, --depth, --sources academic, --output, --reasoning-effort

set -euo pipefail

# --- Example 1: Deep research with default depth (3 iterations) ---
echo "=== Example 1: Deep research, default depth ==="
pplx-research "transformer architecture advances 2024" \
    --mode deep \
    --quiet

# --- Example 2: Deep research with max depth, academic sources only ---
echo ""
echo "=== Example 2: Deep academic research, depth 5 ==="
pplx-research "attention mechanisms in large language models" \
    --mode deep \
    --depth 5 \
    --sources academic \
    --quiet \
    --output /tmp/attention-mechanisms-report.md
echo "Full report saved to /tmp/attention-mechanisms-report.md"

# --- Example 3: Faster deep run for iteration (depth 2) ---
echo ""
echo "=== Example 3: Fast deep run for drafting (depth 2) ==="
pplx-research "Rust ownership model internals" \
    --mode deep \
    --depth 2 \
    --quiet \
    --format summary

# --- Example 4: Deep research with high reasoning effort ---
echo ""
echo "=== Example 4: Deep research with high reasoning effort ==="
pplx-research "Kubernetes networking: CNI plugins and eBPF" \
    --mode deep \
    --depth 4 \
    --sources docs,academic \
    --reasoning-effort high \
    --quiet \
    --output /tmp/k8s-networking.md
echo "K8s networking report saved to /tmp/k8s-networking.md"

# --- Example 5: Recent news with deep mode + time filter ---
echo ""
echo "=== Example 5: Recent news, deep mode ==="
pplx-research "AI model releases last month" \
    --mode deep \
    --depth 2 \
    --sources news \
    --time-range month \
    --quiet
