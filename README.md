# PPLX Research

A monolithic, versatile research CLI powered by Perplexity's Sonar API. Features auto-classification, iterative gap analysis, multi-perspective synthesis, and comprehensive output formats.

[![CI](https://github.com/kleinpanic/pplx-research/actions/workflows/ci.yml/badge.svg)](https://github.com/kleinpanic/pplx-research/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why This Exists

Other Perplexity wrappers are simple API clients. **PPLX Research is a research orchestration layer** that adds:

- **Auto-classification**: Analyzes your query and picks the optimal mode/depth/sources
- **Gap analysis**: Iteratively identifies and fills knowledge gaps (deep mode)
- **Multi-perspective synthesis**: Gathers insights from academic, news, forums, docs, and code sources
- **Full API coverage**: All Perplexity features including `search_domain_filter`, `reasoning_effort`, `return_images`, etc.

## Installation

```bash
pip install pplx-research
```

## Quick Start

```bash
# Set your API key
export PERPLEXITY_API_KEY="pplx-..."

# Basic research
pplx-research "what is quantum computing"

# Let AI pick the best approach
pplx-research "React vs Vue performance" --auto

# Deep academic research
pplx-research "transformer architecture" --mode deep --sources academic --depth 4

# Multi-perspective analysis
pplx-research "microservices pros and cons" --mode synthesis
```

## Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `quick` | Single query, fast response | Facts, definitions, current events |
| `deep` | Iterative gap analysis | Complex topics, research reports |
| `synthesis` | Multi-source perspectives | Comparisons, debates, pros/cons |

## Options

```
pplx-research <query> [options]

Modes:
  -m, --mode {quick,deep,synthesis}  Research mode (default: quick)

Scope:
  -s, --site DOMAIN         Constrain to specific domain
  -e, --exclude DOMAIN      Exclude domain (can use multiple times)
  -t, --time-range {hour,day,week,month,year}
                           Time range for results
  -r, --region CODE        Country/region code (US, UK, JP, etc.)
  -l, --language CODE      Language filter (en, de, ja, etc.)
  --sources TYPES          Comma-separated: academic,news,docs,forums,code,all

Output:
  -f, --format {markdown,json,summary,plain}
                           Output format (default: markdown)
  -d, --depth 1-5          Iteration depth (default: 3)

Automation:
  -a, --auto               Auto-classify query and select optimal settings
  -o, --output PATH        Save output to file
  -w, --webhook URL        POST results to webhook on completion
  -q, --quiet              Suppress progress (for piping)
```

## Python API

```python
from pplx_research import ResearchEngine, PerplexitySDK

# High-level research
engine = ResearchEngine(
    query="quantum computing applications",
    mode="deep",
    sources=["academic"],
    depth=4
)
report = engine.run()

# Low-level SDK
sdk = PerplexitySDK(api_key="pplx-...")
result = sdk.chat("Hello", model="sonar-pro")
```

## License

MIT License - see [LICENSE](LICENSE) for details.
