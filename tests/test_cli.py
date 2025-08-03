"""
Tests for the command-line interface (CLI).

This module contains tests for the CLI commands in the `cli.py` module.
It uses the Click testing framework to invoke the CLI commands and check
their output and exit codes.

Test Coverage:
    - `test` command
    - `send` command
    - `photo` command
    - `document` command
    - `setup` command
    - `info` command
"""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from notify2.cli import main
from notify2.exceptions import ConfigError, NotifyError, TelegramError


@pytest.fixture
def runner():
    """Fixture for invoking command-line calls."""
    return CliRunner()


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_test_success(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'test' command with a successful connection."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.test_connection.return_value = None
        mock_instance.get_me.return_value = {
            "ok": True,
            "result": {
                "id": 123,
                "first_name": "TestBot",
                "username": "test_bot",
                "can_join_groups": True,
                "can_read_all_group_messages": False,
                "supports_inline_queries": False,
            },
        }
        mock_notifier.return_value.__enter__.return_value = mock_instance

        result = runner.invoke(main, ["test"])
        assert result.exit_code == 0
        assert "Telegram connection test passed!" in result.output
        assert "Bot Information" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_test_config_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'test' command with a ConfigError."""
    mock_from_file.side_effect = ConfigError("Config file not found")
    mock_from_env.side_effect = ConfigError("Config file not found")

    result = runner.invoke(main, ["test"])
    assert result.exit_code == 1
    assert "Error: Config file not found" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_test_telegram_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'test' command with a TelegramError."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.test_connection.side_effect = TelegramError("Invalid token")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        result = runner.invoke(main, ["test"])
        assert result.exit_code == 1
        assert "Error: Invalid token" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_send_success(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'send' command with a successful message."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_message.return_value = {
            "ok": True,
            "result": {
                "message_id": 123,
                "chat": {"id": 123456789},
                "date": 1234567890,
                "text": "Hello, World!",
            },
        }
        mock_notifier.return_value.__enter__.return_value = mock_instance

        result = runner.invoke(main, ["send", "Hello, World!"])
        assert result.exit_code == 0
        assert "Message sent successfully!" in result.output
        assert "Message Details" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_send_no_message_provided(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'send' command when no message is provided."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    result = runner.invoke(main, ["send"], input="\n")  # Simulate empty input
    assert result.exit_code == 1
    assert "Error: No message provided" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_send_config_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'send' command with a ConfigError."""
    mock_from_file.side_effect = ConfigError("Config file not found")
    mock_from_env.side_effect = ConfigError("Config file not found")

    result = runner.invoke(main, ["send", "test message"])
    assert result.exit_code == 1
    assert "Error: Config file not found" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_send_telegram_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'send' command with a TelegramError."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_message.side_effect = TelegramError("Invalid chat ID")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        result = runner.invoke(main, ["send", "test message"])
        assert result.exit_code == 1
        assert "Error: Invalid chat ID" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_send_notify_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'send' command with a NotifyError."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_message.side_effect = NotifyError("Unknown error")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        result = runner.invoke(main, ["send", "test message"])
        assert result.exit_code == 1
        assert "Error: Unknown error" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_photo_success(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'photo' command with a successful message."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_photo.return_value = {
            "ok": True,
            "result": {
                "message_id": 123,
                "chat": {"id": 123456789},
                "date": 1234567890,
                "caption": "A beautiful photo",
            },
        }
        mock_notifier.return_value.__enter__.return_value = mock_instance

        with runner.isolated_filesystem():
            with open("test.jpg", "w") as f:
                f.write("test")
            result = runner.invoke(
                main, ["photo", "test.jpg", "--caption", "A beautiful photo"]
            )
            assert result.exit_code == 0
            assert "Photo sent successfully!" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_photo_config_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'photo' command with a ConfigError."""
    mock_from_file.side_effect = ConfigError("Config file not found")
    mock_from_env.side_effect = ConfigError("Config file not found")

    with runner.isolated_filesystem():
        with open("test.jpg", "w") as f:
            f.write("test")
        result = runner.invoke(main, ["photo", "test.jpg"])
        assert result.exit_code == 1
        assert "Error: Config file not found" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_photo_telegram_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'photo' command with a TelegramError."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_photo.side_effect = TelegramError("File too large")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        with runner.isolated_filesystem():
            with open("test.jpg", "w") as f:
                f.write("test")
            result = runner.invoke(main, ["photo", "test.jpg"])
            assert result.exit_code == 1
            assert "Error: File too large" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_photo_notify_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'photo' command with a NotifyError."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_photo.side_effect = NotifyError("Invalid photo format")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        with runner.isolated_filesystem():
            with open("test.jpg", "w") as f:
                f.write("test")
            result = runner.invoke(main, ["photo", "test.jpg"])
            assert result.exit_code == 1
            assert "Error: Invalid photo format" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_document_success(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'document' command with a successful message."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_document.return_value = {
            "ok": True,
            "result": {
                "message_id": 123,
                "chat": {"id": 123456789},
                "date": 1234567890,
                "caption": "A beautiful document",
            },
        }
        mock_notifier.return_value.__enter__.return_value = mock_instance

        with runner.isolated_filesystem():
            with open("test.txt", "w") as f:
                f.write("test")
            result = runner.invoke(
                main, ["document", "test.txt", "--caption", "A beautiful document"]
            )
            assert result.exit_code == 0
            assert "Document sent successfully!" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_document_config_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'document' command with a ConfigError."""
    mock_from_file.side_effect = ConfigError("Config file not found")
    mock_from_env.side_effect = ConfigError("Config file not found")

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("test")
        result = runner.invoke(main, ["document", "test.txt"])
        assert result.exit_code == 1
        assert "Error: Config file not found" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_document_telegram_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'document' command with a TelegramError."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_document.side_effect = TelegramError("File too large")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        with runner.isolated_filesystem():
            with open("test.txt", "w") as f:
                f.write("test")
            result = runner.invoke(main, ["document", "test.txt"])
            assert result.exit_code == 1
            assert "Error: File too large" in result.output


@patch("notify2.cli.Config.from_file")
@patch("notify2.cli.Config.from_env")
def test_cli_document_notify_error(
    mock_from_env: MagicMock, mock_from_file: MagicMock, runner: CliRunner
):
    """Test the 'document' command with a NotifyError."""
    mock_config = MagicMock()
    mock_from_file.return_value = mock_config
    mock_from_env.return_value = mock_config

    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.send_document.side_effect = NotifyError("Invalid document format")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        with runner.isolated_filesystem():
            with open("test.txt", "w") as f:
                f.write("test")
            result = runner.invoke(main, ["document", "test.txt"])
            assert result.exit_code == 1
            assert "Error: Invalid document format" in result.output


def test_cli_setup_success(runner: CliRunner):
    """Test the 'setup' command with a successful connection."""
    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.test_connection.return_value = None
        mock_notifier.return_value.__enter__.return_value = mock_instance

        result = runner.invoke(
            main, ["setup"], input="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n123456789\n"
        )
        assert result.exit_code == 0
        assert "Configuration saved successfully!" in result.output


def test_cli_setup_no_bot_token(runner: CliRunner):
    """Test the 'setup' command when no bot token is provided."""
    result = runner.invoke(main, ["setup"], input="\n123456789\n")
    assert result.exit_code == 1
    assert "Error: Bot token is required" in result.output


def test_cli_setup_no_chat_id(runner: CliRunner):
    """Test the 'setup' command when no chat ID is provided."""
    result = runner.invoke(main, ["setup"], input="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n\n")
    assert result.exit_code == 1
    assert "Error: Chat ID is required" in result.output


def test_cli_setup_telegram_error(runner: CliRunner):
    """Test the 'setup' command with a TelegramError during connection test."""
    with patch("notify2.cli.TelegramNotifier") as mock_notifier:
        mock_instance = MagicMock()
        mock_instance.test_connection.side_effect = TelegramError("Invalid token")
        mock_notifier.return_value.__enter__.return_value = mock_instance

        result = runner.invoke(
            main, ["setup"], input="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz\n123456789\n"
        )
        assert result.exit_code == 1
        assert "Setup failed: Invalid token" in result.output


def test_cli_setup_keyboard_interrupt(runner: CliRunner):
    """Test the 'setup' command when interrupted by the user."""
    with patch("notify2.cli.Prompt.ask", side_effect=KeyboardInterrupt):
        result = runner.invoke(main, ["setup"])
        assert result.exit_code == 1
        assert "Setup cancelled by user" in result.output


def test_cli_info_success(runner: CliRunner):
    """Test the 'info' command with a successful connection."""
    with patch("notify2.cli.Config.from_file") as mock_from_file:
        mock_config = MagicMock()
        mock_config.telegram.bot_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
        mock_config.telegram.chat_id = "123456789"
        mock_config.telegram.parse_mode = "HTML"
        mock_config.timeout = 10
        mock_config.retry_attempts = 3
        mock_config.retry_delay = 1.0
        mock_from_file.return_value = mock_config

        result = runner.invoke(main, ["info"])
        assert result.exit_code == 0
        assert "Configuration Information" in result.output
