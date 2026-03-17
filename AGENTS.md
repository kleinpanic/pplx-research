# AGENTS.md — Developer Guide for AI Agents

This file describes how to work **on** the `pplx-research` repository itself.
If you want to _use_ the tool to do research, see `skills/pplx-research/SKILL.md`.

## Repo Structure

```
pplx-research/
├── src/pplx_research/
│   ├── __init__.py        # Public exports: ResearchEngine, PerplexitySDK
│   ├── cli.py             # argparse CLI entry point — all flags defined here
│   ├── engine.py          # Research orchestration logic (quick/deep/synthesis modes)
│   └── sdk.py             # Thin Perplexity API wrapper (HTTP calls, auth)
├── tests/                 # pytest test suite
├── docs/
│   └── man/
│       └── pplx-research.1  # troff man page
├── skills/
│   └── pplx-research/
│       └── SKILL.md       # OpenClaw agent skill definition
├── scripts/
│   └── install-skill.sh   # Installs SKILL.md to ~/.openclaw/skills/
├── pyproject.toml         # Build config; entry point defined under [project.scripts]
├── README.md
└── AGENTS.md              # This file
```

## Key Files

| File | Purpose |
|------|---------|
| `src/pplx_research/cli.py` | All CLI argument definitions live here; edit here to add/remove flags |
| `src/pplx_research/engine.py` | Research logic: mode dispatch, gap analysis, synthesis loop |
| `src/pplx_research/sdk.py` | Low-level Perplexity API calls; handles auth and HTTP |
| `src/pplx_research/__init__.py` | Public API surface for Python importers |
| `pyproject.toml` | Package metadata, dependencies, and `[project.scripts]` entry point |

## Running Tests

```bash
cd ~/codeWS/Python/PerplexityDeepResearch
source venv/bin/activate
pytest
```

Run a specific test file:
```bash
pytest tests/test_engine.py -v
```

## Building the Package

```bash
source venv/bin/activate
python -m build
```

Output goes to `dist/`. Produces both a `.tar.gz` sdist and a `.whl` wheel.

## Entry Point

Defined in `pyproject.toml` under `[project.scripts]`:

```toml
[project.scripts]
pplx-research = "pplx_research.cli:main"
```

After `pip install -e .` (editable install), `pplx-research` on PATH calls
`pplx_research.cli.main()`.

## Dependency Notes

- **setuptools is pinned to 69.5.1** — do not upgrade it. A newer version caused
  PyPI compatibility issues in CI. Pin is enforced in `pyproject.toml` build
  requirements.
- All runtime deps are declared in `pyproject.toml` under `[project.dependencies]`.

## Virtual Environment

**Never edit or commit files inside `venv/`.** The virtualenv is local only and
is excluded by `.gitignore`. Recreate it with:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## CI

GitHub Actions workflow at `.github/workflows/ci.yml`. Runs tests on push/PR,
publishes to PyPI and GitHub Packages on version tags.

## Making Changes

1. Modify source under `src/pplx_research/` only.
2. Do not modify `pyproject.toml` build backend pins (especially setuptools).
3. Do not modify test files unless fixing a broken test.
4. Run `pytest` before committing.
5. Version is set in `pyproject.toml` under `[project] version`.
