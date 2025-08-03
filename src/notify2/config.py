"""
Configuration management for notify2.

This module provides type-safe configuration management using Pydantic models.
It supports loading configuration from environment variables, JSON files,
and provides validation for all configuration values.

The configuration system includes:
- TelegramConfig: Bot-specific settings with validation
- Config: Main configuration class with all settings
- Environment variable support
- JSON file configuration
- Automatic validation and error handling

Example:
    >>> from notify2.config import Config
    >>> config = Config.from_env()  # Load from environment
    >>> config = Config.from_file()  # Load from default file
    >>> config = Config.from_file("/path/to/config.json")  # Custom file
"""

import json
import os
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from .exceptions import ConfigError

# Load environment variables from .env file if present
load_dotenv()


class TelegramConfig(BaseModel):
    """
    Configuration for Telegram bot settings.

    This class validates and stores all Telegram-specific configuration
    including bot token, chat ID, and parse mode settings.

    Attributes:
        bot_token: The Telegram bot token from @BotFather
        chat_id: The target chat ID for messages
        parse_mode: Message parsing mode (HTML, Markdown, MarkdownV2)

    Example:
        >>> config = TelegramConfig(
        ...     bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
        ...     chat_id="123456789",
        ...     parse_mode="HTML"
        ... )
    """

    bot_token: str = Field(
        ...,
        description="Telegram bot token from @BotFather",
        min_length=10,
        pattern=r"^\d+:[A-Za-z0-9_-]+$",
    )
    chat_id: str = Field(..., description="Telegram chat ID for sending messages")
    parse_mode: str = Field(
        default="HTML",
        description="Message parse mode for formatting",
        pattern=r"^(HTML|Markdown|MarkdownV2)$",
    )

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """
        Validate bot token format and length.

        Args:
            v: The bot token to validate

        Returns:
            The validated bot token

        Raises:
            ValueError: If token is invalid
        """
        if not v or len(v) < 10:
            raise ValueError("Bot token must be at least 10 characters long")
        if ":" not in v:
            raise ValueError("Bot token must contain a colon separator")
        return v

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, v: str) -> str:
        """
        Validate chat ID is not empty.

        Args:
            v: The chat ID to validate

        Returns:
            The validated chat ID

        Raises:
            ValueError: If chat ID is empty
        """
        if not v:
            raise ValueError("Chat ID cannot be empty")
        return v


class Config(BaseModel):
    """
    Main configuration class for notify2.

    This class manages all configuration settings including Telegram settings,
    network timeouts, retry strategies, and provides methods for loading
    configuration from different sources.

    Attributes:
        telegram: Telegram-specific configuration
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts for failed requests
        retry_delay: Delay between retries in seconds

    Example:
        >>> from notify2.config import Config, TelegramConfig
        >>> telegram_config = TelegramConfig(
        ...     bot_token="your_token",
        ...     chat_id="your_chat_id"
        ... )
        >>> config = Config(
        ...     telegram=telegram_config,
        ...     timeout=30,
        ...     retry_attempts=5
        ... )
    """

    telegram: TelegramConfig
    timeout: int = Field(
        default=10, description="Request timeout in seconds", ge=1, le=300
    )
    retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for failed requests",
        ge=0,
        le=10,
    )
    retry_delay: float = Field(
        default=1.0, description="Delay between retries in seconds", ge=0.1, le=60.0
    )

    # Default configuration file path
    DEFAULT_CONFIG_PATH: ClassVar[str] = "~/.notify2/config.json"

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.

        Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from environment.

        Returns:
            Config instance with environment variables

        Raises:
            ConfigError: If required environment variables are missing
        """
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not bot_token:
            raise ConfigError("TELEGRAM_BOT_TOKEN environment variable is required")
        if not chat_id:
            raise ConfigError("TELEGRAM_CHAT_ID environment variable is required")

        return cls(telegram=TelegramConfig(bot_token=bot_token, chat_id=chat_id))

    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> "Config":
        """
        Create configuration from JSON file.

        Args:
            config_path: Path to configuration file. If None, uses default path.

        Returns:
            Config instance loaded from file

        Raises:
            ConfigError: If file doesn't exist or has invalid JSON
        """
        if config_path is None:
            config_path = os.path.expanduser(cls.DEFAULT_CONFIG_PATH)

        config_file = Path(config_path)
        if not config_file.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        try:
            with open(config_file, "r") as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, KeyError) as e:
            raise ConfigError(f"Invalid configuration file: {e}")
        except Exception as e:
            raise ConfigError(f"Invalid configuration file: {e}")

    def save_to_file(self, config_path: Optional[str] = None) -> None:
        """
        Save configuration to JSON file.

        Args:
            config_path: Path to save configuration. If None, uses default path.

        Raises:
            ConfigError: If file cannot be written
        """
        if config_path is None:
            config_path = os.path.expanduser(self.DEFAULT_CONFIG_PATH)

        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_file, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to save configuration: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return self.model_dump()
