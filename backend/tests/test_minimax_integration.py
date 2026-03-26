"""Integration tests for MiniMax LLM provider.

These tests verify end-to-end behavior with the MiniMax API.
They require a valid MINIMAX_API_KEY environment variable.
Run with: pytest backend/tests/test_minimax_integration.py -v
"""
import os

import pytest

# Skip all tests in this module if no API key is available
pytestmark = pytest.mark.skipif(
    not os.environ.get("MINIMAX_API_KEY"),
    reason="MINIMAX_API_KEY not set"
)


class TestMiniMaxIntegration:
    """Integration tests that call the real MiniMax API."""

    def _create_minimax_llm(self, model="MiniMax-M2.7", temperature=0.5, streaming=False):
        """Helper to create a MiniMax LLM instance."""
        from unittest.mock import patch
        from app.services.llm.llm_factory import LLMFactory

        mock_settings = type("MockSettings", (), {
            "CHAT_PROVIDER": "minimax",
            "MINIMAX_API_KEY": os.environ["MINIMAX_API_KEY"],
            "MINIMAX_API_BASE": "https://api.minimax.io/v1",
            "MINIMAX_MODEL": model,
        })()

        with patch("app.services.llm.llm_factory.settings", mock_settings):
            return LLMFactory.create(
                provider="minimax",
                temperature=temperature,
                streaming=streaming,
            )

    def test_minimax_simple_completion(self):
        """MiniMax can generate a simple text completion."""
        llm = self._create_minimax_llm()
        response = llm.invoke("What is 2 + 2? Answer with just the number.")
        assert response.content
        assert "4" in response.content

    def test_minimax_highspeed_model(self):
        """MiniMax-M2.7-highspeed model works correctly."""
        llm = self._create_minimax_llm(model="MiniMax-M2.7-highspeed")
        response = llm.invoke("Say 'hello' in one word.")
        assert response.content
        assert len(response.content) > 0

    def test_minimax_streaming_response(self):
        """MiniMax streaming mode produces chunks."""
        llm = self._create_minimax_llm(streaming=True)
        chunks = list(llm.stream("Count from 1 to 3."))
        assert len(chunks) > 0
        full_text = "".join(c.content for c in chunks)
        assert len(full_text) > 0
