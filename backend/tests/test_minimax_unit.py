"""Unit tests for MiniMax LLM provider integration."""
import os
from unittest.mock import patch, MagicMock

import pytest


class TestMiniMaxConfig:
    """Tests for MiniMax configuration settings."""

    def test_minimax_settings_defaults(self):
        """Verify default values for MiniMax settings."""
        env_clean = {k: v for k, v in os.environ.items()
                     if k not in ("MINIMAX_API_KEY", "MINIMAX_API_BASE", "MINIMAX_MODEL")}
        with patch.dict(os.environ, env_clean, clear=True):
            from app.core.config import Settings
            s = Settings()
            assert s.MINIMAX_API_BASE == "https://api.minimax.io/v1"
            assert s.MINIMAX_MODEL == "MiniMax-M2.7"
            assert s.MINIMAX_API_KEY == ""

    def test_minimax_settings_from_env(self):
        """Verify MiniMax settings loaded from environment variables."""
        env = {
            "MINIMAX_API_KEY": "test-key-123",
            "MINIMAX_API_BASE": "https://custom.minimax.io/v1",
            "MINIMAX_MODEL": "MiniMax-M2.7-highspeed",
        }
        with patch.dict(os.environ, env, clear=False):
            from app.core.config import Settings
            s = Settings()
            assert s.MINIMAX_API_KEY == "test-key-123"
            assert s.MINIMAX_API_BASE == "https://custom.minimax.io/v1"
            assert s.MINIMAX_MODEL == "MiniMax-M2.7-highspeed"

    def test_chat_provider_minimax(self):
        """Verify CHAT_PROVIDER can be set to minimax."""
        with patch.dict(os.environ, {"CHAT_PROVIDER": "minimax"}, clear=False):
            from app.core.config import Settings
            s = Settings()
            assert s.CHAT_PROVIDER == "minimax"


class TestMiniMaxLLMFactory:
    """Tests for MiniMax provider in LLMFactory."""

    @patch("app.services.llm.llm_factory.settings")
    def test_create_minimax_provider(self, mock_settings):
        """LLMFactory.create() returns ChatOpenAI for minimax provider."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax", temperature=0.5)

        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "MiniMax-M2.7"
        assert llm.openai_api_base == "https://api.minimax.io/v1"

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_temperature_clamping_zero(self, mock_settings):
        """Temperature 0 is clamped to 0.01 for MiniMax API."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax", temperature=0)

        assert llm.temperature == 0.01

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_temperature_clamping_high(self, mock_settings):
        """Temperature > 1.0 is clamped to 1.0 for MiniMax API."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax", temperature=2.0)

        assert llm.temperature == 1.0

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_temperature_valid(self, mock_settings):
        """Valid temperature passes through unchanged."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax", temperature=0.7)

        assert llm.temperature == 0.7

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_streaming_enabled(self, mock_settings):
        """MiniMax provider supports streaming by default."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax", streaming=True)

        assert llm.streaming is True

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_streaming_disabled(self, mock_settings):
        """MiniMax provider can disable streaming."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax", streaming=False)

        assert llm.streaming is False

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_highspeed_model(self, mock_settings):
        """MiniMax highspeed model variant works correctly."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7-highspeed"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax")

        assert llm.model_name == "MiniMax-M2.7-highspeed"

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_via_default_provider(self, mock_settings):
        """MiniMax selected via CHAT_PROVIDER setting when no provider arg given."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create()

        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "MiniMax-M2.7"

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_case_insensitive(self, mock_settings):
        """Provider name matching is case-insensitive."""
        mock_settings.CHAT_PROVIDER = "MiniMax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="MiniMax")

        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_custom_base_url(self, mock_settings):
        """MiniMax provider works with custom API base URL."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "test-key"
        mock_settings.MINIMAX_API_BASE = "https://custom-proxy.example.com/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax")

        assert llm.openai_api_base == "https://custom-proxy.example.com/v1"

    def test_unsupported_provider_raises(self):
        """Unsupported provider raises ValueError."""
        from app.services.llm.llm_factory import LLMFactory
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMFactory.create(provider="nonexistent")

    @patch("app.services.llm.llm_factory.settings")
    def test_minimax_api_key_passed(self, mock_settings):
        """MiniMax API key is correctly passed to ChatOpenAI."""
        mock_settings.CHAT_PROVIDER = "minimax"
        mock_settings.MINIMAX_API_KEY = "sk-minimax-secret"
        mock_settings.MINIMAX_API_BASE = "https://api.minimax.io/v1"
        mock_settings.MINIMAX_MODEL = "MiniMax-M2.7"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="minimax")

        assert llm.openai_api_key.get_secret_value() == "sk-minimax-secret"


class TestExistingProviders:
    """Verify existing providers still work after adding MiniMax."""

    @patch("app.services.llm.llm_factory.settings")
    def test_openai_provider_unchanged(self, mock_settings):
        """OpenAI provider still works correctly."""
        mock_settings.CHAT_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_API_BASE = "https://api.openai.com/v1"
        mock_settings.OPENAI_MODEL = "gpt-4"

        from app.services.llm.llm_factory import LLMFactory
        llm = LLMFactory.create(provider="openai")

        from langchain_openai import ChatOpenAI
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "gpt-4"

    @patch("app.services.llm.llm_factory.settings")
    def test_deepseek_provider_unchanged(self, mock_settings):
        """DeepSeek provider still works correctly."""
        mock_settings.CHAT_PROVIDER = "deepseek"
        mock_settings.DEEPSEEK_API_KEY = "test-key"
        mock_settings.DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
        mock_settings.DEEPSEEK_MODEL = "deepseek-chat"

        from app.services.llm.llm_factory import LLMFactory
        from langchain_deepseek import ChatDeepSeek
        llm = LLMFactory.create(provider="deepseek")
        assert isinstance(llm, ChatDeepSeek)
