"""
PPLX Research - Monolithic research CLI powered by Perplexity Sonar API.

A versatile research tool supporting multiple modes (quick, deep, synthesis),
auto-classification, iterative gap analysis, and comprehensive output formats.
"""

__version__ = "1.0.0"
__author__ = "kleinpanic"

from pplx_research.sdk import PerplexitySDK
from pplx_research.engine import ResearchEngine

__all__ = ["PerplexitySDK", "ResearchEngine"]
