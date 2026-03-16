# Contributing to PPLX Research

Thanks for your interest in contributing!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/kleinpanic/pplx-research.git
cd pplx-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -e ".[dev]"

# Set up API key for testing
export PERPLEXITY_API_KEY="pplx-..."
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/pplx_research --cov-report=term-missing

# Run specific test file
pytest tests/test_sdk.py -v
```

## Code Style

- We use [Black](https://black.readthedocs.io/) for formatting (line length: 100)
- We use [Ruff](https://docs.astral.sh/ruff/) for linting
- We use [mypy](https://mypy.readthedocs.io/) for type checking

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Pull Request Process

1. Fork the repo and create your branch from `main`
2. Make your changes with tests
3. Run the test suite and linting
4. Update documentation if needed
5. Submit a pull request

## Adding New Features

### New Search Filters

Add to `sdk.py`:
1. Add to `ChatCompletionRequest` dataclass
2. Add to `to_dict()` method
3. Add CLI argument in `cli.py`
4. Add engine support in `engine.py`

### New Output Formats

Add to `engine.py`:
1. Add to `_format_output()` method
2. Add CLI argument
3. Update README

## Reporting Issues

Please include:
- Python version
- Operating system
- Command that failed
- Full error message
- Steps to reproduce
