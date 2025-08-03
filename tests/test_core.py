"""
Tests for core TelegramNotifier functionality.

This module contains comprehensive tests for the TelegramNotifier class,
including message sending, file uploads, error handling, and connection
management.

Test Coverage:
    - TelegramNotifier initialization and configuration
    - Message sending with various options
    - Photo and document uploads
    - Error handling for network and API issues
    - Connection testing and bot information retrieval
    - Context manager functionality
    - Input validation and error cases
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
import requests

from notify2.config import Config, TelegramConfig
from notify2.core import TelegramNotifier
from notify2.exceptions import TelegramError, ValidationError


class TestTelegramNotifier:
    """
    Test cases for TelegramNotifier class.

    These tests verify that the TelegramNotifier class properly handles
    all Telegram API interactions, including message sending, file uploads,
    error handling, and resource management.
    """

    @pytest.fixture
    def config(self):
        """Create a test configuration fixture."""
        telegram_config = TelegramConfig(
            bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", chat_id="123456789"
        )
        return Config(telegram=telegram_config)

    @pytest.fixture
    def notifier(self, config):
        """Create a test notifier fixture."""
        return TelegramNotifier(config)

    def test_init(self, config):
        """Test notifier initialization with valid configuration."""
        notifier = TelegramNotifier(config)

        assert notifier.config == config
        assert (
            notifier.base_url
            == f"https://api.telegram.org/bot{config.telegram.bot_token}"
        )
        assert notifier.session is not None

    def test_create_session(self, config):
        """Test session creation with proper retry strategy."""
        notifier = TelegramNotifier(config)

        # Check that session has retry adapter configured correctly
        adapter = notifier.session.get_adapter("https://")
        assert adapter.max_retries.total == config.retry_attempts
        assert adapter.max_retries.backoff_factor == config.retry_delay

    @patch("requests.Session.post")
    def test_send_message_success(self, mock_post, notifier):
        """Test successful message sending with proper API response."""
        # Mock successful response from Telegram API
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "message_id": 123,
                "chat": {"id": 123456789},
                "date": 1234567890,
                "text": "Test message",
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = notifier.send_message("Test message")

        assert result["ok"] is True
        assert result["result"]["message_id"] == 123

        # Verify the request was made with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == f"{notifier.base_url}/sendMessage"
        assert call_args[1]["json"]["text"] == "Test message"
        assert call_args[1]["json"]["chat_id"] == "123456789"

    @patch("requests.Session.post")
    def test_send_message_with_options(self, mock_post, notifier):
        """Test sending message with various formatting and behavior options."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "result": {}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test with all options enabled
        notifier.send_message(
            message="Test message",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            disable_notification=True,
            reply_to_message_id=123,
        )

        # Verify all options were passed correctly
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        assert payload["parse_mode"] == "Markdown"
        assert payload["disable_web_page_preview"] is True
        assert payload["disable_notification"] is True
        assert payload["reply_to_message_id"] == 123

    def test_send_message_empty(self, notifier):
        """Test that empty or whitespace-only messages raise validation error."""
        with pytest.raises(ValidationError, match="Message cannot be empty"):
            notifier.send_message("")

        with pytest.raises(ValidationError, match="Message cannot be empty"):
            notifier.send_message("   ")

        with pytest.raises(ValidationError, match="Message cannot be empty"):
            notifier.send_message("\n\t")

    def test_send_message_too_long(self, notifier):
        """Test that messages exceeding Telegram's limit raise validation error."""
        long_message = "x" * 4097  # Telegram limit is 4096 characters
        with pytest.raises(ValidationError, match="Message too long"):
            notifier.send_message(long_message)

        # Test that exactly 4096 characters is allowed
        exact_message = "x" * 4096
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"ok": True, "result": {}}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Should not raise an error
            notifier.send_message(exact_message)

    @patch("requests.Session.post")
    def test_send_message_api_error(self, mock_post, notifier):
        """Test handling of Telegram API errors."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": False,
            "description": "Bad Request: chat not found",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(
            TelegramError, match="Telegram API error: Bad Request: chat not found"
        ):
            notifier.send_message("Test message")

    @patch("requests.Session.post")
    def test_send_message_network_error(self, mock_post, notifier):
        """Test handling of network connection errors."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        with pytest.raises(TelegramError, match="Failed to send message"):
            notifier.send_message("Test message")

    @patch("requests.Session.post")
    def test_send_photo_success(self, mock_post, notifier):
        """Test successful photo sending with proper file handling."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake image data")
            photo_path = f.name

        try:
            mock_response = Mock()
            mock_response.json.return_value = {"ok": True, "result": {}}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = notifier.send_photo(photo_path, caption="Test caption")

            assert result["ok"] is True

            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == f"{notifier.base_url}/sendPhoto"
            assert call_args[1]["data"]["chat_id"] == "123456789"
            assert call_args[1]["data"]["caption"] == "Test caption"
        finally:
            os.unlink(photo_path)

    @patch("requests.Session.post")
    def test_send_photo_api_error(self, mock_post, notifier):
        """Test handling of Telegram API errors during photo sending."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake image data")
            photo_path = f.name

        try:
            mock_response = Mock()
            mock_response.json.return_value = {
                "ok": False,
                "description": "Bad Request: photo too large",
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            with pytest.raises(
                TelegramError, match="Telegram API error: Bad Request: photo too large"
            ):
                notifier.send_photo(photo_path)
        finally:
            os.unlink(photo_path)

    @patch("requests.Session.post")
    def test_send_photo_network_error(self, mock_post, notifier):
        """Test handling of network connection errors during photo sending."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"fake image data")
            photo_path = f.name

        try:
            mock_post.side_effect = requests.exceptions.RequestException("Network error")

            with pytest.raises(TelegramError, match="Failed to send photo"):
                notifier.send_photo(photo_path)
        finally:
            os.unlink(photo_path)

    def test_send_photo_file_not_found(self, notifier):
        """Test that non-existent photo file raises validation error."""
        with pytest.raises(ValidationError, match="Photo file not found"):
            notifier.send_photo("/nonexistent/photo.jpg")

    @patch("requests.Session.post")
    def test_send_document_success(self, mock_post, notifier):
        """Test successful document sending with proper file handling."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test document content")
            doc_path = f.name

        try:
            mock_response = Mock()
            mock_response.json.return_value = {"ok": True, "result": {}}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = notifier.send_document(doc_path, caption="Test document")

            assert result["ok"] is True

            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == f"{notifier.base_url}/sendDocument"
            assert call_args[1]["data"]["chat_id"] == "123456789"
            assert call_args[1]["data"]["caption"] == "Test document"
        finally:
            os.unlink(doc_path)

    @patch("requests.Session.post")
    def test_send_document_api_error(self, mock_post, notifier):
        """Test handling of Telegram API errors during document sending."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test document content")
            doc_path = f.name

        try:
            mock_response = Mock()
            mock_response.json.return_value = {
                "ok": False,
                "description": "Bad Request: document too large",
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            with pytest.raises(
                TelegramError, match="Telegram API error: Bad Request: document too large"
            ):
                notifier.send_document(doc_path)
        finally:
            os.unlink(doc_path)

    @patch("requests.Session.post")
    def test_send_document_network_error(self, mock_post, notifier):
        """Test handling of network connection errors during document sending."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test document content")
            doc_path = f.name

        try:
            mock_post.side_effect = requests.exceptions.RequestException("Network error")

            with pytest.raises(TelegramError, match="Failed to send document"):
                notifier.send_document(doc_path)
        finally:
            os.unlink(doc_path)

    def test_send_document_file_not_found(self, notifier):
        """Test that non-existent document file raises validation error."""
        with pytest.raises(ValidationError, match="Document file not found"):
            notifier.send_document("/nonexistent/document.txt")

    @patch("requests.Session.get")
    def test_get_me_success(self, mock_get, notifier):
        """Test successful bot information retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "id": 123456789,
                "first_name": "TestBot",
                "username": "test_bot",
                "can_join_groups": True,
                "can_read_all_group_messages": False,
                "supports_inline_queries": False,
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = notifier.get_me()

        assert result["ok"] is True
        assert result["result"]["first_name"] == "TestBot"
        assert result["result"]["username"] == "test_bot"

    @patch("requests.Session.get")
    def test_get_me_network_error(self, mock_get, notifier):
        """Test handling of network connection errors in get_me method."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        with pytest.raises(TelegramError, match="Failed to get bot info"):
            notifier.get_me()

    @patch("requests.Session.get")
    def test_get_me_api_error(self, mock_get, notifier):
        """Test handling of API errors in get_me method."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": False, "description": "Unauthorized"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(TelegramError, match="Telegram API error: Unauthorized"):
            notifier.get_me()

    @patch("requests.Session.get")
    def test_test_connection_success(self, mock_get, notifier):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "result": {}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        notifier.test_connection()

    @patch("requests.Session.get")
    def test_test_connection_failure(self, mock_get, notifier):
        """Test failed connection test."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": False, "description": "Unauthorized"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(TelegramError):
            notifier.test_connection()

    @patch("requests.Session.post")
    def test_edit_message_text_success(self, mock_post, notifier):
        """Test successful message editing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "message_id": 123,
                "chat": {"id": 123456789},
                "date": 1234567890,
                "text": "Edited message",
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = notifier.edit_message_text(123, "Edited message")

        assert result["ok"] is True
        assert result["result"]["text"] == "Edited message"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == f"{notifier.base_url}/editMessageText"
        assert call_args[1]["json"]["message_id"] == 123
        assert call_args[1]["json"]["text"] == "Edited message"

    @patch("requests.Session.post")
    def test_edit_message_text_with_options(self, mock_post, notifier):
        """Test editing message with various formatting and behavior options."""
        mock_response = Mock()
        mock_response.json.return_value = {"ok": True, "result": {}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        notifier.edit_message_text(
            123,
            "Edited message",
            parse_mode="MarkdownV2",
            disable_web_page_preview=True,
        )

        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        assert payload["parse_mode"] == "MarkdownV2"
        assert payload["disable_web_page_preview"] is True

    def test_edit_message_text_empty(self, notifier):
        """Test that empty or whitespace-only edited messages raise validation error."""
        with pytest.raises(ValidationError, match="Message text cannot be empty"):
            notifier.edit_message_text(123, "")

        with pytest.raises(ValidationError, match="Message text cannot be empty"):
            notifier.edit_message_text(123, "   ")

    def test_edit_message_text_too_long(self, notifier):
        """Test that edited messages exceeding Telegram's limit raise validation error."""
        long_message = "x" * 4097
        with pytest.raises(ValidationError, match="Message text too long"):
            notifier.edit_message_text(123, long_message)

    @patch("requests.Session.post")
    def test_edit_message_text_api_error(self, mock_post, notifier):
        """Test handling of Telegram API errors during message editing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": False,
            "description": "Bad Request: message not found",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(
            TelegramError, match="Telegram API error: Bad Request: message not found"
        ):
            notifier.edit_message_text(123, "Test message")

    @patch("requests.Session.post")
    def test_edit_message_text_network_error(self, mock_post, notifier):
        """Test handling of network connection errors during message editing."""
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        with pytest.raises(TelegramError, match="Failed to edit message"):
            notifier.edit_message_text(123, "Test message")

    @patch("requests.Session.post")
    def test_progress_bar_new_message(self, mock_post, notifier):
        """Test progress bar with a new message being sent."""
        mock_response_send = Mock()
        mock_response_send.json.return_value = {"ok": True, "result": {"message_id": 1}}
        mock_response_send.raise_for_status.return_value = None

        mock_response_edit = Mock()
        mock_response_edit.json.return_value = {"ok": True, "result": {}}
        mock_response_edit.raise_for_status.return_value = None

        mock_post.side_effect = [mock_response_send, mock_response_edit, mock_response_edit, mock_response_edit]

        items = [1, 2, 3]
        processed_items = []
        for item in notifier.progress_bar(items):
            processed_items.append(item)

        assert processed_items == items
        assert mock_post.call_count == len(items) + 1 # Initial send + 3 edits
        # Verify initial message
        initial_text = mock_post.call_args_list[0][1]["json"]["text"]
        assert "Progress:" in initial_text
        assert "[" in initial_text
        assert "]" in initial_text
        assert "0.0%" in initial_text
        # Verify final message
        assert "100.0%" in mock_post.call_args_list[-1][1]["json"]["text"]

    @patch("requests.Session.post")
    def test_progress_bar_existing_message(self, mock_post, notifier):
        """Test progress bar by editing an existing message."""
        mock_response_edit = Mock()
        mock_response_edit.json.return_value = {"ok": True, "result": {}}
        mock_response_edit.raise_for_status.return_value = None

        mock_post.side_effect = [mock_response_edit, mock_response_edit, mock_response_edit, mock_response_edit]

        items = [1, 2, 3]
        processed_items = []
        for item in notifier.progress_bar(items, message_id=123):
            processed_items.append(item)

        assert processed_items == items
        assert mock_post.call_count == len(items) + 1 # 1 initial edit + 3 updates
        # Verify initial message
        assert mock_post.call_args_list[0][1]["json"]["message_id"] == 123
        initial_text = mock_post.call_args_list[0][1]["json"]["text"]
        assert "Progress:" in initial_text
        assert "[" in initial_text
        assert "]" in initial_text
        assert "0.0%" in initial_text
        # Verify final message
        assert "100.0%" in mock_post.call_args_list[-1][1]["json"]["text"]

    def test_progress_bar_no_len_iterable(self, notifier):
        """Test progress bar with an iterable that doesn't have __len__."""
        def gen_items():
            yield 1
            yield 2
        with pytest.raises(ValueError, match="Iterable must have a __len__ method for progress bar."):
            for _ in notifier.progress_bar(gen_items()):
                pass

    @patch("requests.Session.post")
    def test_progress_bar_api_error(self, mock_post, notifier):
        """Test handling of API errors during progress bar updates."""
        mock_response_send = Mock()
        mock_response_send.json.return_value = {"ok": True, "result": {"message_id": 1}}
        mock_response_send.raise_for_status.return_value = None

        mock_response_error = Mock()
        mock_response_error.json.return_value = {"ok": False, "description": "API error"}
        mock_response_error.raise_for_status.return_value = None

        mock_post.side_effect = [mock_response_send, mock_response_error]

        items = [1, 2, 3]
        with pytest.raises(TelegramError, match="Failed to update progress bar"):
            for _ in notifier.progress_bar(items):
                pass

    def test_context_manager(self, config):
        """Test that notifier works properly as a context manager."""
        with TelegramNotifier(config) as notifier:
            assert notifier.session is not None

        # Session should be properly managed by context manager
        assert notifier.session is not None

    def test_close(self, notifier):
        """Test that close method works without errors."""
        notifier.close()
        # Note: requests.Session doesn't have a 'closed' attribute
        # The close method is called but we can't easily verify it
        assert notifier.session is not None

    def test_path_object_support(self, notifier):
        """Test that Path objects are supported for file operations."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            file_path = Path(f.name)

        try:
            with patch("requests.Session.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {"ok": True, "result": {}}
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                # Should work with Path object
                notifier.send_document(file_path)
                mock_post.assert_called_once()
        finally:
            os.unlink(file_path)
