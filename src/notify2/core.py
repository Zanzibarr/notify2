"""
Core functionality for sending Telegram notifications.

This module provides the main TelegramNotifier class which handles all
communication with the Telegram Bot API. It includes features like:

- Connection pooling for better performance
- Automatic retry with exponential backoff
- Comprehensive error handling
- Support for text messages, photos, and documents
- Context manager support for resource cleanup
- Type-safe API with proper validation

The TelegramNotifier class is the main interface for sending messages
and should be used as a context manager to ensure proper resource cleanup.

Example:
    >>> from notify2 import TelegramNotifier, Config
    >>> config = Config.from_file()
    >>> with TelegramNotifier(config) as notifier:
    ...     result = notifier.send_message("Hello, World!")
    ...     print(f"Message sent with ID: {result['result']['message_id']}")
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .exceptions import TelegramError, ValidationError


class TelegramNotifier:
    """
    Enhanced Telegram notification sender with improved performance and features.

    This class provides a high-performance interface for sending Telegram messages
    with features like connection pooling, automatic retries, and comprehensive
    error handling. It should be used as a context manager to ensure proper
    resource cleanup.

    Features:
        - Connection pooling for better performance
        - Automatic retry with exponential backoff
        - Support for text messages, photos, and documents
        - Type-safe API with validation
        - Context manager support
        - Comprehensive error handling

    Attributes:
        config: The configuration object containing all settings
        session: The requests session with retry strategy
        base_url: The Telegram Bot API base URL

    Example:
        >>> from notify2 import TelegramNotifier, Config
        >>> config = Config.from_file()
        >>> with TelegramNotifier(config) as notifier:
        ...     # Send a simple message
        ...     result = notifier.send_message("Hello, World!")
        ...
        ...     # Send a photo
        ...     result = notifier.send_photo("image.jpg", "Check this out!")
        ...
        ...     # Send a document
        ...     result = notifier.send_document("report.pdf", "Monthly report")
    """

    def __init__(self, config: Config):
        """
        Initialize the Telegram notifier.

        Args:
            config: Configuration object containing Telegram settings and
                   network configuration (timeout, retries, etc.)

        Raises:
            ValidationError: If configuration is invalid
        """
        self.config = config
        self.session = self._create_session()
        self.base_url = f"https://api.telegram.org/bot{config.telegram.bot_token}"

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy.

        Returns:
            Configured requests session with retry adapter
        """
        session = requests.Session()

        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=self.config.retry_delay,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def send_message(
        self,
        message: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = False,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Send a text message to Telegram.

        This method sends a text message to the configured chat with optional
        formatting, preview settings, and reply functionality.

        Args:
            message: The message text to send (max 4096 characters)
            parse_mode: Parse mode for formatting (HTML, Markdown, MarkdownV2)
            disable_web_page_preview: Whether to disable link previews
            disable_notification: Whether to send silently (no notification)
            reply_to_message_id: ID of message to reply to

        Returns:
            Telegram API response dictionary containing message details

        Raises:
            ValidationError: If message is empty or too long
            TelegramError: If the message fails to send

        Example:
            >>> result = notifier.send_message("Hello, World!")
            >>> print(f"Message ID: {result['result']['message_id']}")

            >>> # Send with formatting
            >>> result = notifier.send_message(
            ...     "**Bold text** and *italic text*",
            ...     parse_mode="Markdown"
            ... )
        """
        if not message or not message.strip():
            raise ValidationError("Message cannot be empty")

        if len(message) > 4096:
            raise ValidationError("Message too long (max 4096 characters)")

        payload = {
            "chat_id": self.config.telegram.chat_id,
            "text": message,
            "parse_mode": parse_mode or self.config.telegram.parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
        }

        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id

        try:
            response = self.session.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            result = response.json()
            if not result.get("ok"):
                raise TelegramError(
                    f"Telegram API error: {result.get('description', 'Unknown error')}"
                )

            return result  # type: ignore

        except requests.exceptions.RequestException as e:
            raise TelegramError(f"Failed to send message: {e}")

    def send_photo(
        self,
        photo_path: Union[str, Path],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a photo to Telegram.

        This method sends a photo file to the configured chat with optional
        caption and formatting.

        Args:
            photo_path: Path to the photo file
            caption: Optional caption for the photo
            parse_mode: Parse mode for caption formatting

        Returns:
            Telegram API response dictionary containing photo details

        Raises:
            ValidationError: If photo file doesn't exist
            TelegramError: If the photo fails to send

        Example:
            >>> result = notifier.send_photo("image.jpg", "Beautiful sunset!")
            >>> print(f"Photo sent with ID: {result['result']['message_id']}")
        """
        photo_file = Path(photo_path)
        if not photo_file.exists():
            raise ValidationError(f"Photo file not found: {photo_path}")

        files = {"photo": open(photo_file, "rb")}
        payload = {
            "chat_id": self.config.telegram.chat_id,
            "parse_mode": parse_mode or self.config.telegram.parse_mode,
        }

        if caption:
            payload["caption"] = caption

        try:
            response = self.session.post(
                f"{self.base_url}/sendPhoto",
                data=payload,
                files=files,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            result = response.json()
            if not result.get("ok"):
                raise TelegramError(
                    f"Telegram API error: {result.get('description', 'Unknown error')}"
                )

            return result  # type: ignore

        except requests.exceptions.RequestException as e:
            raise TelegramError(f"Failed to send photo: {e}")
        finally:
            files["photo"].close()

    def send_document(
        self,
        document_path: Union[str, Path],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a document to Telegram.

        This method sends a document file to the configured chat with optional
        caption and formatting.

        Args:
            document_path: Path to the document file
            caption: Optional caption for the document
            parse_mode: Parse mode for caption formatting

        Returns:
            Telegram API response dictionary containing document details

        Raises:
            ValidationError: If document file doesn't exist
            TelegramError: If the document fails to send

        Example:
            >>> result = notifier.send_document("report.pdf", "Monthly report")
            >>> print(f"Document sent with ID: {result['result']['message_id']}")
        """
        document_file = Path(document_path)
        if not document_file.exists():
            raise ValidationError(f"Document file not found: {document_path}")

        files = {"document": open(document_file, "rb")}
        payload = {
            "chat_id": self.config.telegram.chat_id,
            "parse_mode": parse_mode or self.config.telegram.parse_mode,
        }

        if caption:
            payload["caption"] = caption

        try:
            response = self.session.post(
                f"{self.base_url}/sendDocument",
                data=payload,
                files=files,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            result = response.json()
            if not result.get("ok"):
                raise TelegramError(
                    f"Telegram API error: {result.get('description', 'Unknown error')}"
                )

            return result  # type: ignore

        except requests.exceptions.RequestException as e:
            raise TelegramError(f"Failed to send document: {e}")
        finally:
            files["document"].close()

    def get_me(self) -> Dict[str, Any]:
        """
        Get information about the bot.

        This method retrieves information about the configured bot including
        bot ID, name, username, and capabilities.

        Returns:
            Telegram API response dictionary containing bot information

        Raises:
            TelegramError: If the API call fails

        Example:
            >>> bot_info = notifier.get_me()
            >>> print(f"Bot name: {bot_info['result']['first_name']}")
            >>> print(f"Bot username: @{bot_info['result']['username']}")
        """
        try:
            response = self.session.get(
                f"{self.base_url}/getMe", timeout=self.config.timeout
            )
            response.raise_for_status()

            result = response.json()
            if not result.get("ok"):
                raise TelegramError(
                    f"Telegram API error: {result.get('description', 'Unknown error')}"
                )

            return result  # type: ignore

        except requests.exceptions.RequestException as e:
            raise TelegramError(f"Failed to get bot info: {e}")

    def edit_message_text(
        self,
        message_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = False,
    ) -> Dict[str, Any]:
        """
        Edit an existing text message in Telegram.

        This method allows you to modify the text of a previously sent message.
        It's particularly useful for updating status messages or creating dynamic content.

        Args:
            message_id: Identifier of the message to edit.
            text: New text of the message (max 4096 characters).
            parse_mode: Optional. Parse mode for formatting (HTML, Markdown, MarkdownV2).
                        If None, the default parse mode from the configuration will be used.
            disable_web_page_preview: Optional. Whether to disable link previews for the message.

        Returns:
            Telegram API response dictionary containing the edited message details.

        Raises:
            ValidationError: If message text is empty or too long.
            TelegramError: If the message fails to edit due to API errors or network issues.

        Example:
            >>> # Assuming 'notifier' is an initialized TelegramNotifier instance
            >>> sent_message = notifier.send_message("Initial message")
            >>> message_id = sent_message["result"]["message_id"]
            >>> notifier.edit_message_text(message_id, "Updated message!")
        """
        if not text or not text.strip():
            raise ValidationError("Message text cannot be empty")

        if len(text) > 4096:
            raise ValidationError("Message text too long (max 4096 characters)")

        payload = {
            "chat_id": self.config.telegram.chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode or self.config.telegram.parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/editMessageText",
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            result = response.json()
            if not result.get("ok"):
                raise TelegramError(
                    f"Telegram API error: {result.get('description', 'Unknown error')}"
                )

            return result  # type: ignore

        except requests.exceptions.RequestException as e:
            raise TelegramError(f"Failed to edit message: {e}")

    def test_connection(self) -> None:
        """
        Test the connection to Telegram API.

        This method tests whether the bot token is valid and the bot
        can communicate with the Telegram API.

        Raises:
            TelegramError: If the connection fails

        Example:
            >>> try:
            ...     notifier.test_connection()
            ...     print("Connection successful!")
            ... except TelegramError:
            ...     print("Connection failed!")
        """
        self.get_me()

    def progress_bar(
        self,
        iterable: Any,
        prefix: str = "Progress:",
        message_id: Optional[int] = None,
        bar_length: int = 20,
    ) -> Any:
        """
        Display a dynamic progress bar in Telegram for an iterable.

        This method wraps an iterable and sends/edits a Telegram message
        to display the progress of iterating through the items. It's useful
        for long-running operations where you want to provide real-time feedback.

        Args:
            iterable: The iterable (e.g., list, range) to track progress for.
                      It must have a `__len__` method to determine the total number of items.
            prefix: Optional. Text to prepend to the progress bar message (e.g., "Processing:").
            message_id: Optional. The message ID of an existing message to edit.
                        If provided, the progress bar will update this message.
                        If None, a new message will be sent for the progress bar.
            bar_length: Optional. The length of the progress bar in characters (excluding prefix and percentage).

        Yields:
            Each item from the input `iterable`.

        Raises:
            ValueError: If the `iterable` does not have a `__len__` method.
            TelegramError: If sending or editing the message fails due to API errors or network issues.

        Example:
            >>> import time
            >>> # Assuming 'notifier' is an initialized TelegramNotifier instance
            >>> items_to_process = list(range(1, 11))
            >>> # Send an initial message to get a message_id for the progress bar
            >>> initial_pb_message = notifier.send_message("Starting long task...")
            >>> pb_message_id = initial_pb_message["result"]["message_id"]
            >>> for item in notifier.progress_bar(items_to_process, prefix="Task progress:", message_id=pb_message_id):
            ...     print(f"Processing item {item}...")
            ...     time.sleep(0.5) # Simulate work
            >>> notifier.send_message("Task complete!")
        """
        total = len(iterable) if hasattr(iterable, "__len__") else None
        if total is None:
            raise ValueError("Iterable must have a __len__ method for progress bar.")

        def _get_progress_message(iteration: int) -> str:
            percent = (iteration / total) * 100
            filled_length = int(bar_length * iteration // total)
            bar = "[" + "=" * filled_length + " " * (bar_length - filled_length) + "]"
            # Pad prefix and percentage to ensure consistent length
            padded_prefix = f"{prefix:<15}"  # Adjust width as needed
            padded_percent = f"{percent:6.1f}%"  # Adjust width as needed
            # Wrap the message in MarkdownV2 code block for monospaced font
            return f"```\n{padded_prefix} |{bar}| {padded_percent}\n```"

        try:
            initial_message = _get_progress_message(0)
            if message_id is None:
                response = self.send_message(initial_message, parse_mode="MarkdownV2")
                message_id = response["result"]["message_id"]
            else:
                self.edit_message_text(message_id, initial_message, parse_mode="MarkdownV2")

            for i, item in enumerate(iterable):
                yield item
                progress_message = _get_progress_message(i + 1)
                self.edit_message_text(message_id, progress_message, parse_mode="MarkdownV2")

        except Exception as e:
            raise TelegramError(f"Failed to update progress bar: {e}")

    def close(self) -> None:
        """
        Close the HTTP session.

        This method closes the requests session and frees up resources.
        It's automatically called when using the notifier as a context manager.
        """
        self.session.close()

    def __enter__(self) -> "TelegramNotifier":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - ensures session is closed."""
        self.close()
