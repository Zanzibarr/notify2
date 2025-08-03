"""
Custom exceptions for the notify2 package.

This module defines a hierarchy of custom exceptions that provide
clear, specific error messages for different types of failures
that can occur when using the notify2 package.

Exception Hierarchy:
    NotifyError (base)
    ├── ConfigError
    ├── TelegramError
    └── ValidationError

Each exception includes descriptive error messages and can be caught
individually or as a group using the base NotifyError class.
"""


class NotifyError(Exception):
    """
    Base exception for all notify2 errors.

    This is the parent class for all custom exceptions in this package.
    You can catch this exception to handle any error from notify2.

    Example:
        try:
            notifier.send_message("Hello")
        except NotifyError as e:
            print(f"Notification error: {e}")
    """

    pass


class ConfigError(NotifyError):
    """
    Raised when there's an issue with configuration.

    This exception is raised when:
    - Configuration file is not found
    - Configuration file has invalid JSON
    - Required environment variables are missing
    - Configuration values are invalid

    Example:
        try:
            config = Config.from_file()
        except ConfigError as e:
            print(f"Configuration error: {e}")
    """

    pass


class TelegramError(NotifyError):
    """
    Raised when there's an issue with Telegram API communication.

    This exception is raised when:
    - Telegram API returns an error response
    - Network connection fails
    - Request times out
    - Bot token is invalid
    - Chat ID is invalid

    Example:
        try:
            notifier.send_message("Hello")
        except TelegramError as e:
            print(f"Telegram API error: {e}")
    """

    pass


class ValidationError(NotifyError):
    """
    Raised when input validation fails.

    This exception is raised when:
    - Message is empty or too long
    - File path doesn't exist
    - Invalid parse mode is specified
    - Invalid configuration values are provided

    Example:
        try:
            notifier.send_message("")  # Empty message
        except ValidationError as e:
            print(f"Validation error: {e}")
    """

    pass
