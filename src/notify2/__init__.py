"""
Notify2 - Enhanced Telegram notification system.

A modern, well-organized Python package for sending Telegram messages
with improved performance, better error handling, and enhanced features.

This package provides:
- High-performance Telegram message sending with connection pooling
- Type-safe configuration management with Pydantic validation
- Beautiful command-line interface with Rich formatting
- Support for sending text messages, photos, and documents
- Comprehensive error handling and retry strategies
- Easy setup and configuration management

Example usage:
    >>> from notify2 import TelegramNotifier, Config
    >>> config = Config.from_file()
    >>> with TelegramNotifier(config) as notifier:
    ...     notifier.send_message("Hello, World!")

CLI usage:
    $ notify2 send "Hello, World!"
    $ notify2 photo image.jpg --caption "Check this out!"
    $ notify2 test
"""

__version__ = "2.0.0"
__author__ = "Zanella Matteo"
__email__ = "matteozanella2@gmail.com"
__description__ = "Enhanced Telegram notification system with modern Python features"
__url__ = "https://github.com/Zanzibarr/notify2"

from .config import Config, TelegramConfig

# Core functionality
from .core import TelegramNotifier
from .exceptions import ConfigError, NotifyError, TelegramError, ValidationError

# Public API
__all__ = [
    # Core classes
    "TelegramNotifier",
    "Config",
    "TelegramConfig",
    # Exceptions
    "NotifyError",
    "ConfigError",
    "TelegramError",
    "ValidationError",
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
]
