# PPLX Research

A monolithic, versatile research CLI powered by Perplexity's Sonar API. Features auto-classification, iterative gap analysis, multi-perspective synthesis, and comprehensive output formats.

[![CI](https://github.com/kleinpanic/pplx-research/actions/workflows/ci.yml/badge.svg)](https://github.com/kleinpanic/pplx-research/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pplx-research.svg)](https://badge.fury.io/py/pplx-research)
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

Or from source:

```bash
git clone https://github.com/kleinpanic/pplx-research.git
cd pplx-research
pip install -e ".[dev]"
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
pplx-research "transformer architecture improvements" --mode deep --sources academic --depth 4

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

Depth & Reasoning:
  -d, --depth 1-5          Iteration depth (default: 3)
  --reasoning-effort {minimal,low,medium,high}
                           Reasoning effort level

Output:
  -f, --format {markdown,json,summary,plain}
                           Output format (default: markdown)
  --return-images          Include image results
  --return-related-questions
                           Include follow-up questions

Automation:
  -a, --auto               Auto-classify query and select optimal settings
  -o, --output PATH        Save output to file
  -w, --webhook URL        POST results to webhook on completion
  -q, --quiet              Suppress progress (for piping)
```

## Examples

### Quick Research

```bash
# Simple fact lookup
pplx-research "what is the latest version of Python"

# With site constraint
pplx-research "campus construction" --site news.vt.edu --time-range month

# JSON output for scripting
pplx-research "OpenAI API pricing" --format json --quiet | jq '.content'
```

### Deep Research

```bash
# Iterative gap analysis
pplx-research "quantum error correction methods" --mode deep --depth 4

# Academic sources with reasoning
pplx-research "transformer attention mechanisms" --mode deep --sources academic --reasoning-effort high

# Save to file
pplx-research "competitive analysis AI tools" --mode deep --output report.md
```

### Synthesis Mode

```bash
# Multi-perspective comparison
pplx-research "React vs Vue vs Angular" --mode synthesis

# Specific source types
pplx-research "best practices for API design" --mode synthesis --sources academic,news,forums

# With webhook notification
pplx-research "microservices patterns" --mode synthesis --webhook https://hooks.slack.com/...
```

### Auto Mode

```bash
# Let AI classify and optimize
pplx-research "compare Kubernetes vs Docker Swarm" --auto

# Auto with quiet output
pplx-research "latest AI breakthroughs 2024" --auto --quiet | head -50
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
print(report)

# Low-level SDK
sdk = PerplexitySDK(api_key="pplx-...")
result = sdk.chat("Hello", model="sonar-pro")
print(result["choices"][0]["message"]["content"])

# Type-safe request
from pplx_research.sdk import ChatCompletionRequest, ReasoningEffort

req = ChatCompletionRequest(
    model="sonar-reasoning-pro",
    messages=[{"role": "user", "content": "Explain quantum entanglement"}],
    reasoning_effort=ReasoningEffort.HIGH,
    search_domain_filter=["arxiv.org", "nature.com"],
)
result = sdk.chat_typed(req)
```

## API Coverage

All Perplexity Sonar API features are supported:

| Feature | CLI Flag | SDK Param |
|---------|----------|-----------|
| Search domain filter | `--site` | `search_domain_filter` |
| Search recency filter | `--time-range` | `search_recency_filter` |
| Search language filter | `--language` | `search_language_filter` |
| Search mode | — | `search_mode` (web/academic/sec) |
| Reasoning effort | `--reasoning-effort` | `reasoning_effort` |
| Return images | `--return-images` | `return_images` |
| Return related questions | `--return-related-questions` | `return_related_questions` |
| Response format | `--format json` | `response_format` |
| Stream mode | — | `stream_mode` |
| Disable search | — | `disable_search` |

## Comparison to Other Tools

| Feature | pplx-research | perplexityai (official) | perplexity-ai-toolkit |
|---------|---------------|------------------------|---------------------|
| Research orchestration | ✅ | ❌ | ❌ |
| Auto-classification | ✅ | ❌ | ❌ |
| Gap analysis | ✅ | ❌ | ❌ |
| Multi-perspective synthesis | ✅ | ❌ | ❌ |
| Full API params | ✅ | ✅ | ❌ |
| CLI included | ✅ | ❌ | ✅ |
| Streaming | ✅ | ✅ | ❌ |
| Type-safe requests | ✅ | ✅ | ❌ |
| OpenRouter fallback | ✅ | ❌ | ❌ |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src/pplx_research

# Lint
ruff check src/ tests/
black --check src/ tests/

# Type check
mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Acknowledgments

- [Perplexity AI](https://perplexity.ai) for the Sonar API
- [OpenRouter](https://openrouter.ai) for fallback support
