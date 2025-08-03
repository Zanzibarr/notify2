"""
Tests for configuration management.

This module contains comprehensive tests for the configuration system,
including validation, loading from different sources, and error handling.

Test Coverage:
    - TelegramConfig validation
    - Config class functionality
    - Environment variable loading
    - File-based configuration
    - Error handling for invalid configurations
    - Configuration serialization and deserialization
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from notify2.config import Config, TelegramConfig
from notify2.exceptions import ConfigError


class TestTelegramConfig:
    """
    Test cases for TelegramConfig class.

    These tests verify that the TelegramConfig class properly validates
    bot tokens and chat IDs, and handles various edge cases correctly.
    """

    def test_valid_config(self):
        """Test creating a valid TelegramConfig with all required fields."""
        config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )

        assert config.bot_token == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        assert config.chat_id == "123456789"
        assert config.parse_mode == "HTML"

    def test_invalid_bot_token(self):
        """Test that invalid bot token raises appropriate error."""
        with pytest.raises(ValueError):
            TelegramConfig(bot_token="short", chat_id="123456789")

    def test_empty_chat_id(self):
        """Test that empty chat ID raises appropriate error."""
        with pytest.raises(ValueError):
            TelegramConfig(
                bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id=""
            )

    def test_bot_token_without_colon(self):
        """Test that bot token without colon separator raises error."""
        with pytest.raises(ValueError):
            TelegramConfig(
                bot_token="1234567890ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
            )

    def test_custom_parse_mode(self):
        """Test that custom parse mode is properly set."""
        config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            chat_id="123456789",
            parse_mode="Markdown",
        )
        assert config.parse_mode == "Markdown"


class TestConfig:
    """
    Test cases for Config class.

    These tests verify that the Config class properly manages configuration
    settings, loads from different sources, and handles errors correctly.
    """

    def test_valid_config(self):
        """Test creating a valid Config with default settings."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )

        config = Config(telegram=telegram_config)

        assert config.telegram == telegram_config
        assert config.timeout == 10
        assert config.retry_attempts == 3
        assert config.retry_delay == 1.0

    def test_custom_settings(self):
        """Test creating Config with custom network settings."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )

        config = Config(
            telegram=telegram_config, timeout=30, retry_attempts=5, retry_delay=2.0
        )

        assert config.timeout == 30
        assert config.retry_attempts == 5
        assert config.retry_delay == 2.0

    def test_timeout_validation(self):
        """Test that timeout values are properly validated."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )

        # Test minimum value
        config = Config(telegram=telegram_config, timeout=1)
        assert config.timeout == 1

        # Test maximum value
        config = Config(telegram=telegram_config, timeout=300)
        assert config.timeout == 300

    def test_retry_validation(self):
        """Test that retry settings are properly validated."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )

        # Test minimum values
        config = Config(telegram=telegram_config, retry_attempts=0, retry_delay=0.1)
        assert config.retry_attempts == 0
        assert config.retry_delay == 0.1

        # Test maximum values
        config = Config(telegram=telegram_config, retry_attempts=10, retry_delay=60.0)
        assert config.retry_attempts == 10
        assert config.retry_delay == 60.0

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_save_to_file_io_error(self, mock_open):
        """Test that IOError during file writing raises ConfigError."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )
        config = Config(telegram=telegram_config)

        with pytest.raises(ConfigError, match="Failed to save configuration"):
            config.save_to_file("dummy_path.json")

    @patch.dict(
        os.environ,
        {
            "TELEGRAM_BOT_TOKEN": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
            "TELEGRAM_CHAT_ID": "123456789",
        },
    )
    def test_from_env_success(self):
        """Test creating Config from environment variables successfully."""
        config = Config.from_env()

        assert config.telegram.bot_token == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        assert config.telegram.chat_id == "123456789"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_bot_token(self):
        """Test that missing bot token raises appropriate error."""
        with pytest.raises(
            ConfigError, match="TELEGRAM_BOT_TOKEN environment variable is required"
        ):
            Config.from_env()

    @patch.dict(
        os.environ, {"TELEGRAM_BOT_TOKEN": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"}
    )
    def test_from_env_missing_chat_id(self):
        """Test that missing chat ID raises appropriate error."""
        with pytest.raises(
            ConfigError, match="TELEGRAM_CHAT_ID environment variable is required"
        ):
            Config.from_env()

    def test_from_file_success(self):
        """Test creating Config from JSON file successfully."""
        config_data = {
            "telegram": {
                "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
                "chat_id": "123456789",
                "parse_mode": "Markdown",
            },
            "timeout": 15,
            "retry_attempts": 4,
            "retry_delay": 1.5,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config.from_file(config_path)

            assert config.telegram.bot_token == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
            assert config.telegram.chat_id == "123456789"
            assert config.telegram.parse_mode == "Markdown"
            assert config.timeout == 15
            assert config.retry_attempts == 4
            assert config.retry_delay == 1.5
        finally:
            os.unlink(config_path)

    def test_from_file_not_found(self):
        """Test that non-existent file raises appropriate error."""
        with pytest.raises(ConfigError, match="Configuration file not found"):
            Config.from_file("/nonexistent/path/config.json")

    def test_from_file_invalid_json(self):
        """Test that invalid JSON raises appropriate error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            config_path = f.name

        try:
            with pytest.raises(ConfigError, match="Invalid configuration file"):
                Config.from_file(config_path)
        finally:
            os.unlink(config_path)

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_from_file_io_error(self, mock_open):
        """Test that IOError during file reading raises ConfigError."""
        with pytest.raises(ConfigError, match="Configuration file not found"):
            Config.from_file("dummy_path.json")

    def test_from_file_missing_required_fields(self):
        """Test that missing required fields raises appropriate error."""
        config_data = {
            "timeout": 15,
            "retry_attempts": 4,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            with pytest.raises(ConfigError):
                Config.from_file(config_path)
        finally:
            os.unlink(config_path)

    def test_save_to_file(self):
        """Test saving Config to JSON file successfully."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )

        config = Config(telegram=telegram_config)

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            config.save_to_file(config_path)

            # Verify file was created and contains correct data
            assert os.path.exists(config_path)

            with open(config_path, "r") as f:
                saved_data = json.load(f)

            assert (
                saved_data["telegram"]["bot_token"]
                == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
            )
            assert saved_data["telegram"]["chat_id"] == "123456789"
            assert saved_data["timeout"] == 10

    def test_to_dict(self):
        """Test converting Config to dictionary representation."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )

        config = Config(telegram=telegram_config, timeout=20, retry_attempts=5)

        config_dict = config.to_dict()

        assert (
            config_dict["telegram"]["bot_token"]
            == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        )
        assert config_dict["telegram"]["chat_id"] == "123456789"
        assert config_dict["timeout"] == 20
        assert config_dict["retry_attempts"] == 5
        assert config_dict["retry_delay"] == 1.0
