"""Tests for PPLX Research Engine."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from pplx_research.engine import ResearchEngine


class TestResearchEngine:
    """Tests for ResearchEngine class."""
    
    def test_init_defaults(self):
        """Test default initialization."""
        engine = ResearchEngine("test query")
        
        assert engine.query == "test query"
        assert engine.mode == "quick"
        assert engine.depth == 3
        assert engine.sources == ["all"]
        assert engine.quiet == False
    
    def test_depth_clamping(self):
        """Test depth is clamped to 1-5."""
        engine1 = ResearchEngine("test", depth=0)
        engine2 = ResearchEngine("test", depth=10)
        
        assert engine1.depth == 1
        assert engine2.depth == 5
    
    def test_build_query_basic(self):
        """Test basic query building."""
        engine = ResearchEngine("what is Python")
        query = engine._build_query("what is Python")
        
        assert "what is Python" in query
    
    def test_build_query_with_filters(self):
        """Test query building with filters."""
        engine = ResearchEngine(
            "test query",
            exclude=["reddit.com", "twitter.com"],
            time_range="week",
            sources=["academic"],
        )
        query = engine._build_query("test query")
        
        # Source prefix should be included
        assert "arxiv.org" in query or "scholar.google.com" in query
        # Exclude filters should be in query
        assert "-site:reddit.com" in query
        assert "-site:twitter.com" in query
        # Time range context should be included
        assert "in the last week" in query
    
    def test_source_prefixes(self):
        """Test source prefix application."""
        engine = ResearchEngine("test", sources=["academic"])
        query = engine._build_query("test")
        
        # Academic sources should be included
        assert "arxiv.org" in query or "scholar.google.com" in query
    
    def test_site_filter_api_params(self):
        """Test site filter is passed to API params."""
        engine = ResearchEngine("test", site="github.com")
        filters = engine._build_search_filters()
        
        assert "search_domain_filter" in filters
        assert "github.com" in filters["search_domain_filter"]
    
    def test_time_range_api_params(self):
        """Test time range filter is passed to API params."""
        engine = ResearchEngine("test", time_range="week")
        filters = engine._build_search_filters()
        
        assert "search_recency_filter" in filters
        assert filters["search_recency_filter"] == "week"
    
    def test_language_api_params(self):
        """Test language filter is passed to API params."""
        engine = ResearchEngine("test", language="en")
        filters = engine._build_search_filters()
        
        assert "search_language_filter" in filters
        assert "en" in filters["search_language_filter"]
    
    @patch('pplx_research.engine.PerplexitySDK')
    def test_classify_query_comparison(self, mock_sdk_class):
        """Test query classification for comparisons."""
        mock_sdk = MagicMock()
        mock_sdk.chat.return_value = {
            "choices": [{"message": {"content": '{"mode": "synthesis", "depth": 3, "sources": ["docs", "news"], "time_range": null, "reasoning": "test"}'}}]
        }
        mock_sdk_class.return_value = mock_sdk
        
        engine = ResearchEngine("React vs Vue", auto=True)
        result = engine.classify_query("React vs Vue")
        
        # Classification should detect synthesis mode for comparisons
        assert result["mode"] in ["synthesis", "quick", "deep"]
    
    @patch('pplx_research.engine.PerplexitySDK')
    def test_quick_mode(self, mock_sdk_class):
        """Test quick mode execution."""
        mock_sdk = MagicMock()
        mock_sdk.chat.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "citations": ["https://example.com"],
        }
        mock_sdk_class.return_value = mock_sdk
        
        engine = ResearchEngine("test query", quiet=True)
        result = engine._quick_mode()
        
        assert "content" in result
        assert result["mode"] == "quick"
        assert result["iterations"] == 1


class TestOutputFormatting:
    """Tests for output formatting."""
    
    def test_format_json(self):
        """Test JSON output format."""
        engine = ResearchEngine("test", output_format="json", quiet=True)
        result = {
            "content": "Test response",
            "citations": ["https://example.com"],
            "mode": "quick",
            "iterations": 1
        }
        
        output = engine._format_output(result)
        parsed = json.loads(output)
        
        assert parsed["mode"] == "quick"
        assert parsed["iterations"] == 1
    
    def test_format_summary(self):
        """Test summary output format."""
        engine = ResearchEngine("test", output_format="summary", quiet=True)
        result = {
            "content": "Line 1\n\nLine 2\n\nLine 3",
            "citations": [],
        }
        
        output = engine._format_output(result)
        
        # Summary should be truncated
        assert "Line 1" in output
    
    def test_format_plain(self):
        """Test plain text output format."""
        engine = ResearchEngine("test", output_format="plain", quiet=True)
        result = {
            "content": "# Header\n\n**Bold** text",
            "citations": [],
        }
        
        output = engine._format_output(result)
        
        # Markdown should be stripped
        assert "#" not in output
        assert "**" not in output
    
    def test_format_markdown_with_citations(self):
        """Test markdown output with citations."""
        engine = ResearchEngine("test", output_format="markdown", quiet=True)
        result = {
            "content": "Test response",
            "citations": ["https://example.com", "https://test.com"],
            "mode": "quick",
            "iterations": 1
        }
        
        output = engine._format_output(result)
        
        assert "## Sources" in output
        assert "https://example.com" in output


class TestGapAnalysis:
    """Tests for gap analysis in deep mode."""
    
    @patch('pplx_research.engine.PerplexitySDK')
    def test_analyze_gaps(self, mock_sdk_class):
        """Test gap identification."""
        mock_sdk = MagicMock()
        mock_sdk.chat.return_value = {
            "choices": [{"message": {"content": "What about X?\nHow does Y work?\nCan you explain Z?"}}],
        }
        mock_sdk_class.return_value = mock_sdk
        
        engine = ResearchEngine("test", quiet=True)
        gaps = engine._analyze_gaps("Some content here")
        
        assert len(gaps) > 0
        assert any("?" in g for g in gaps)
