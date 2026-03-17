---
name: pplx-research
description: "Use pplx-research CLI for web research via Perplexity Sonar API. Supports quick lookups, deep iterative analysis with gap filling, and multi-perspective synthesis. Use when: agent needs to research a topic with web search. NOT for: questions answerable from memory or local files."
metadata:
  {"openclaw": {"emoji": "🔍", "requires": {"bins": ["pplx-research"]}}}
---

# pplx-research Skill

## Quick Start

```bash
# Minimal: fast lookup
pplx-research "what is QUIC protocol" --quiet

# Auto mode: let the tool pick mode/depth/sources
pplx-research "compare gRPC vs REST" --auto --quiet

# Deep research, pipe to file
pplx-research "transformer architecture advances 2024" --mode deep --sources academic --quiet > report.md

# Multi-perspective synthesis, JSON output
pplx-research "Rust vs Go for systems programming" --mode synthesis --format json --quiet
```

## When to Use This Tool

**Use pplx-research when:**
- The query requires current information (post training cutoff)
- The topic benefits from multiple web sources
- You need a structured research report, not a quick answer
- The user asks you to "research", "look up", "find out about", or "compare" something
- You need academic papers, news, documentation, or forum discussions

**Do NOT use when:**
- The answer is in local files (read them instead)
- The question is answerable from training data with high confidence
- You need to search within a specific repository or codebase

## Modes

| Mode | When to use | API calls |
|------|-------------|-----------|
| `quick` | Facts, definitions, single-question lookups | 1 |
| `deep` | Complex topics, research reports, gap analysis | depth × N |
| `synthesis` | Comparisons, debates, multi-perspective topics | 1 per source type |

Default mode is `quick`. Use `--auto` to let the classifier decide.

## All Flags

| Flag | Short | Values | Default | Notes |
|------|-------|--------|---------|-------|
| `--mode` | `-m` | `quick` `deep` `synthesis` | `quick` | Research strategy |
| `--format` | `-f` | `markdown` `json` `summary` `plain` | `markdown` | Output format |
| `--site` | `-s` | domain string | — | Restrict to one domain |
| `--exclude` | `-e` | domain string | — | Exclude domain; repeatable |
| `--time-range` | `-t` | `hour` `day` `week` `month` `year` | — | Recency filter |
| `--region` | `-r` | ISO country code | — | e.g. `US`, `UK`, `JP` |
| `--language` | `-l` | ISO 639-1 code | — | e.g. `en`, `de`, `ja` |
| `--depth` | `-d` | integer 1–5 | `3` | Iterations for deep mode only (ignored in quick/synthesis) |
| `--sources` | — | `academic,news,docs,forums,code,all` | `all` | Comma-separated list |
| `--reasoning-effort` | — | `minimal` `low` `medium` `high` | — | Passed to sonar-reasoning; only effective in deep mode |
| `--return-images` | — | flag | off | Include image URLs in response |
| `--return-related-questions` | — | flag | off | Include follow-up questions |
| `--output` | `-o` | file path | — | Also write result to file |
| `--webhook` | `-w` | URL | — | POST result to URL on completion |
| `--quiet` | `-q` | flag | off | Suppress progress; only final output to stdout |
| `--auto` | `-a` | flag | off | Auto-classify query; overrides mode/depth/sources |

## Output Formats

| Format | Structure | Best for |
|--------|-----------|----------|
| `markdown` | Headers, sections, bullet lists | Human reading, documents |
| `json` | `{"content": "...", "citations": [...], ...}` | Programmatic parsing |
| `summary` | Single concise paragraph | Quick agent consumption |
| `plain` | Unformatted text | Simple piping |

**Parsing JSON output:**
```bash
result=$(pplx-research "topic" --format json --quiet)
content=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin)['content'])")
```

## Running Quietly for Piping

Always pass `--quiet` / `-q` when capturing output programmatically. Without it,
progress spinners and status lines pollute stdout.

```bash
# Capture result into variable
output=$(pplx-research "latest Rust features" --quiet)

# Pipe directly to another command
pplx-research "Python packaging best practices" --quiet --format summary | grep -i "wheel"

# Save to file silently
pplx-research "kubernetes networking" --mode deep --quiet --output k8s-net.md
```

## Environment

`PERPLEXITY_API_KEY` must be set in the environment or in `~/.env`. The tool will
fail with an error if the key is absent.

```bash
export PERPLEXITY_API_KEY="pplx-..."
pplx-research "my query" --quiet
```

## Integration Tips

- Prefer `--auto` for general research tasks when you are unsure which mode fits.
- Use `--format summary` when you only need a brief answer to pass to the next step.
- Use `--format json` when you need to extract structured data (sources, sections).
- Set `--depth 2` for faster deep runs during iteration; raise to `5` for final reports.
- Combine `--site` with `--mode quick` to do targeted lookups within a known domain.
- Use `--time-range day` or `week` for breaking-news or recent-release queries.
- Multiple `--exclude` flags help avoid low-quality domains: `-e reddit.com -e quora.com`.
- `--webhook` is useful for long synthesis runs where you want async notification.
