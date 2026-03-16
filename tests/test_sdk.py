"""Tests for PPLX Research SDK."""

from unittest.mock import Mock, patch

from pplx_research.sdk import (
    ChatCompletionRequest,
    PerplexitySDK,
    ReasoningEffort,
    SearchMode,
    WebSearchOptions,
)


class TestChatCompletionRequest:
    """Tests for ChatCompletionRequest dataclass."""

    def test_basic_request(self):
        """Test basic request creation."""
        req = ChatCompletionRequest(model="sonar", messages=[{"role": "user", "content": "Hello"}])
        payload = req.to_dict()

        assert payload["model"] == "sonar"
        assert payload["messages"] == [{"role": "user", "content": "Hello"}]
        assert not payload["stream"]

    def test_request_with_filters(self):
        """Test request with search filters."""
        req = ChatCompletionRequest(
            model="sonar",
            messages=[{"role": "user", "content": "Test"}],
            search_domain_filter=["github.com", "stackoverflow.com"],
            search_recency_filter="week",
            search_language_filter=["en"],
            reasoning_effort=ReasoningEffort.HIGH,
        )
        payload = req.to_dict()

        assert payload["search_domain_filter"] == ["github.com", "stackoverflow.com"]
        assert payload["search_recency_filter"] == "week"
        assert payload["search_language_filter"] == ["en"]
        assert payload["reasoning_effort"] == "high"

    def test_request_with_web_search_options(self):
        """Test request with web_search_options."""
        wso = WebSearchOptions(
            search_context_size="high",
            use_autoprompt=True,
            search_after_date="01/01/2024",
        )
        req = ChatCompletionRequest(
            model="sonar",
            messages=[{"role": "user", "content": "Test"}],
            web_search_options=wso,
        )
        payload = req.to_dict()

        assert "web_search_options" in payload
        assert payload["web_search_options"]["search_context_size"] == "high"
        assert payload["web_search_options"]["search_after_date"] == "01/01/2024"


class TestPerplexitySDK:
    """Tests for PerplexitySDK class."""

    @patch.dict("os.environ", {"PERPLEXITY_API_KEY": "test-key"})
    def test_init_with_env(self):
        """Test SDK initialization from environment."""
        sdk = PerplexitySDK()
        assert sdk.pplx_key == "test-key"
        assert not sdk.use_openrouter

    def test_model_resolution(self):
        """Test model name resolution."""
        sdk = PerplexitySDK(api_key="test")

        # Perplexity mode
        assert sdk._resolve_model("sonar") == "sonar"
        assert sdk._resolve_model("sonar-pro") == "sonar-pro"

        # OpenRouter mode
        sdk.use_openrouter = True
        assert sdk._resolve_model("sonar") == "perplexity/sonar"
        assert sdk._resolve_model("sonar-reasoning") == "perplexity/sonar-reasoning-pro"

    @patch("pplx_research.sdk.requests.post")
    def test_chat_success(self, mock_post):
        """Test successful chat completion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "choices": [{"message": {"content": "Test response"}}],
            "citations": ["https://example.com"],
            "usage": {"total_tokens": 100},
        }
        mock_post.return_value = mock_response

        sdk = PerplexitySDK(api_key="test-key")
        result = sdk.chat("Hello", model="sonar")

        assert "error" not in result
        assert result["choices"][0]["message"]["content"] == "Test response"
        assert len(result["citations"]) == 1

    @patch("pplx_research.sdk.requests.post")
    def test_chat_with_quota_fallback(self, mock_post):
        """Test fallback to OpenRouter on quota exceeded."""
        # First call: 401 quota error
        error_response = Mock()
        error_response.status_code = 401
        error_response.text = '{"error": "quota exceeded"}'

        # Second call (fallback): success
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "id": "test-id",
            "choices": [{"message": {"content": "Fallback response"}}],
        }

        mock_post.side_effect = [error_response, success_response]

        sdk = PerplexitySDK(api_key="test-pplx", openrouter_key="test-or")
        result = sdk.chat("Hello")

        # Should have fallen back to OpenRouter
        assert sdk.use_openrouter
        assert "error" not in result


class TestSearchModes:
    """Tests for search mode configurations."""

    def test_search_mode_values(self):
        """Test SearchMode enum values."""
        assert SearchMode.WEB.value == "web"
        assert SearchMode.ACADEMIC.value == "academic"
        assert SearchMode.SEC.value == "sec"

    def test_reasoning_effort_values(self):
        """Test ReasoningEffort enum values."""
        assert ReasoningEffort.MINIMAL.value == "minimal"
        assert ReasoningEffort.LOW.value == "low"
        assert ReasoningEffort.MEDIUM.value == "medium"
        assert ReasoningEffort.HIGH.value == "high"


class TestWebSearchOptions:
    """Tests for WebSearchOptions."""

    def test_default_options(self):
        """Test default web search options."""
        wso = WebSearchOptions()
        assert wso.search_context_size == "medium"
        assert wso.use_autoprompt

    def test_custom_options(self):
        """Test custom web search options."""
        wso = WebSearchOptions(
            search_context_size="high",
            use_autoprompt=False,
            search_after_date="01/01/2024",
            search_before_date="12/31/2024",
        )
        assert wso.search_context_size == "high"
        assert not wso.use_autoprompt
        assert wso.search_after_date == "01/01/2024"
