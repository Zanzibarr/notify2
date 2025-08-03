"""
Command-line interface for notify2.

This module provides a beautiful, user-friendly command-line interface
for the notify2 package. It uses Click for command parsing
and Rich for beautiful terminal output with colors, progress bars,
and formatted tables.

Features:
    - Beautiful terminal output with colors and formatting
    - Progress bars for long-running operations
    - Interactive prompts for user input
    - Comprehensive error handling and user feedback
    - Support for multiple configuration sources
    - Helpful command descriptions and examples

Available Commands:
    - test: Test Telegram connection and show bot info
    - send: Send text messages with formatting options
    - photo: Send photos with optional captions
    - document: Send documents with optional captions
    - setup: Interactive setup wizard
    - info: Show current configuration

Example Usage:
    $ notify test                    # Test connection
    $ notify send "Hello, World!"   # Send message
    $ notify photo image.jpg        # Send photo
    $ notify setup                  # Interactive setup
"""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

from .config import Config, TelegramConfig
from .core import TelegramNotifier
from .exceptions import ConfigError, NotifyError, TelegramError

# Global console instance for consistent styling
console = Console()


def print_error(message: str) -> None:
    """
    Print an error message with red styling.

    Args:
        message: The error message to display
    """
    console.print(f"[red]Error: {message}[/red]")


def print_success(message: str) -> None:
    """
    Print a success message with green styling.

    Args:
        message: The success message to display
    """
    console.print(f"[green]✓ {message}[/green]")


def print_info(message: str) -> None:
    """
    Print an info message with blue styling.

    Args:
        message: The info message to display
    """
    console.print(f"[blue]ℹ {message}[/blue]")


@click.group()
@click.version_option(version="2.0.0", prog_name="notify2")
def main() -> None:
    """
    Notify2 - Telegram notification system.

    A modern, well-organized Python package for sending Telegram messages
    with improved performance, better error handling, and enhanced features.

    This CLI provides an easy-to-use interface for sending messages,
    testing connections, and managing configuration.

    For more information, visit: https://github.com/Zanzibarr/notify2
    """
    pass


@main.command()
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--env", is_flag=True, help="Use environment variables for configuration")
def test(config: Optional[str], env: bool) -> None:
    """
    Test the Telegram connection and display bot information.

    This command tests the connection to the Telegram Bot API and displays
    detailed information about the configured bot including its capabilities
    and settings.

    Examples:\n
        notify test                   # Use default config\n
        notify test --env             # Use environment variables\n
        notify test -c config.json    # Use custom config file
    """
    try:
        # Load configuration based on options
        if env:
            cfg = Config.from_env()
        elif config:
            cfg = Config.from_file(config)
        else:
            cfg = Config.from_file()

        # Test connection with progress indicator
        with TelegramNotifier(cfg) as notifier:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Testing Telegram connection...", total=None)

                notifier.test_connection()
                progress.update(task, description="Connection successful!")
                print_success("Telegram connection test passed!")

                # Get and display bot information
                bot_info = notifier.get_me()
                bot_data = bot_info["result"]

                # Create formatted table with bot details
                table = Table(title="Bot Information")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Bot ID", str(bot_data["id"]))
                table.add_row("Bot Name", bot_data["first_name"])
                table.add_row("Username", f"@{bot_data['username']}")
                table.add_row(
                    "Can Join Groups", str(bot_data.get("can_join_groups", False))
                )
                table.add_row(
                    "Can Read All Group Messages",
                    str(bot_data.get("can_read_all_group_messages", False)),
                )
                table.add_row(
                    "Supports Inline Queries",
                    str(bot_data.get("supports_inline_queries", False)),
                )

                console.print(table)
    except (ConfigError, TelegramError) as e:
        print_error(str(e))
        sys.exit(1)


@main.command()
@click.argument("message", required=False)
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--env", is_flag=True, help="Use environment variables for configuration")
@click.option(
    "--parse-mode",
    "-p",
    type=click.Choice(["HTML", "Markdown", "MarkdownV2"]),
    help="Parse mode for the message",
)
@click.option("--disable-preview", is_flag=True, help="Disable web page preview")
@click.option("--silent", is_flag=True, help="Send message silently")
def send(
    message: Optional[str],
    config: Optional[str],
    env: bool,
    parse_mode: Optional[str],
    disable_preview: bool,
    silent: bool,
) -> None:
    """
    Send a message to Telegram.

    This command sends a text message to the configured Telegram chat.
    If no message is provided, it will read from stdin or prompt for input.

    The message supports various formatting options and can be sent silently
    or with disabled link previews.

    Examples:\n
        notify send "Hello, World!"                         # Simple message\n
        notify send "**Bold** text" --parse-mode Markdown   # Formatted\n
        echo "Hello" | notify send                          # From stdin\n
        notify send --silent "Secret message"               # Silent message\n
    """
    try:
        # Load configuration based on options
        if env:
            cfg = Config.from_env()
        elif config:
            cfg = Config.from_file(config)
        else:
            cfg = Config.from_file()

        # Get message from argument, stdin, or prompt
        if not message:
            if not sys.stdin.isatty():
                message = sys.stdin.read().strip()
            else:
                message = Prompt.ask("Enter your message")

        if not message:
            print_error("No message provided")
            sys.exit(1)

        # Send message with progress indicator
        with TelegramNotifier(cfg) as notifier:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Sending message...", total=None)

                result = notifier.send_message(
                    message=message,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_preview,
                    disable_notification=silent,
                )

                progress.update(task, description="Message sent!")
                print_success("Message sent successfully!")

                # Display message details in formatted table
                message_data = result["result"]
                table = Table(title="Message Details")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Message ID", str(message_data["message_id"]))
                table.add_row("Chat ID", str(message_data["chat"]["id"]))
                table.add_row("Date", str(message_data["date"]))
                table.add_row(
                    "Text",
                    (
                        message_data["text"][:50] + "..."
                        if len(message_data["text"]) > 50
                        else message_data["text"]
                    ),
                )

                console.print(table)

    except (ConfigError, TelegramError, NotifyError) as e:
        print_error(str(e))
        sys.exit(1)


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--env", is_flag=True, help="Use environment variables for configuration")
@click.option("--caption", help="Caption for the photo")
@click.option(
    "--parse-mode",
    "-p",
    type=click.Choice(["HTML", "Markdown", "MarkdownV2"]),
    help="Parse mode for the caption",
)
def photo(
    file_path: str,
    config: Optional[str],
    env: bool,
    caption: Optional[str],
    parse_mode: Optional[str],
) -> None:
    """
    Send a photo to Telegram.

    This command sends a photo file to the configured Telegram chat
    with an optional caption and formatting.

    Examples:\n
        notify photo image.jpg                          # Simple photo\n
        notify photo sunset.png --caption "Beautiful!"  # With caption\n
        notify photo pic.jpg --parse-mode Markdown      # Formatted caption\n
    """
    try:
        # Load configuration based on options
        if env:
            cfg = Config.from_env()
        elif config:
            cfg = Config.from_file(config)
        else:
            cfg = Config.from_file()

        # Send photo with progress indicator
        with TelegramNotifier(cfg) as notifier:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Sending photo...", total=None)

                result = notifier.send_photo(
                    photo_path=file_path, caption=caption, parse_mode=parse_mode
                )

                progress.update(task, description="Photo sent!")
                print_success("Photo sent successfully!")

    except (ConfigError, TelegramError, NotifyError) as e:
        print_error(str(e))
        sys.exit(1)


@main.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--env", is_flag=True, help="Use environment variables for configuration")
@click.option("--caption", help="Caption for the document")
@click.option(
    "--parse-mode",
    "-p",
    type=click.Choice(["HTML", "Markdown", "MarkdownV2"]),
    help="Parse mode for the caption",
)
def document(
    file_path: str,
    config: Optional[str],
    env: bool,
    caption: Optional[str],
    parse_mode: Optional[str],
) -> None:
    """
    Send a document to Telegram.

    This command sends a document file to the configured Telegram chat
    with an optional caption and formatting.

    Examples:\n
        notify document report.pdf                          # Simple document\n
        notify document data.csv --caption "Monthly data"   # With caption\n
        notify document file.txt --parse-mode Markdown      # Formatted caption\n
    """
    try:
        # Load configuration based on options
        if env:
            cfg = Config.from_env()
        elif config:
            cfg = Config.from_file(config)
        else:
            cfg = Config.from_file()

        # Send document with progress indicator
        with TelegramNotifier(cfg) as notifier:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Sending document...", total=None)

                result = notifier.send_document(
                    document_path=file_path, caption=caption, parse_mode=parse_mode
                )

                progress.update(task, description="Document sent!")
                print_success("Document sent successfully!")

    except (ConfigError, TelegramError, NotifyError) as e:
        print_error(str(e))
        sys.exit(1)


@main.command()
def setup() -> None:
    """
    Interactive setup wizard for configuration.

    This command guides you through setting up your Telegram bot
    configuration interactively. It will prompt for your bot token
    and chat ID, test the connection, and save the configuration.

    You'll need:
    - Bot token from @BotFather
    - Chat ID (your user ID or group ID)

    Example:
        notify setup
    """
    # Display welcome message
    console.print(
        Panel.fit(
            "[bold blue]Notify2 Setup[/bold blue]\n\n"
            "This will help you configure your Telegram bot settings.\n"
            "You'll need your bot token and chat ID.",
            title="Setup Wizard",
        )
    )

    try:
        # Get bot token with validation
        bot_token = Prompt.ask("Enter your Telegram bot token")
        if not bot_token:
            print_error("Bot token is required")
            sys.exit(1)

        # Get chat ID with validation
        chat_id = Prompt.ask("Enter your Telegram chat ID")
        if not chat_id:
            print_error("Chat ID is required")
            sys.exit(1)

        # Create configuration object
        config = Config(telegram=TelegramConfig(bot_token=bot_token, chat_id=chat_id))

        # Test configuration with progress indicator
        with TelegramNotifier(config) as notifier:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Testing configuration...", total=None)

                notifier.test_connection()
                progress.update(task, description="Configuration valid!")
                print_success("Configuration is valid!")

                # Save configuration to file
                config.save_to_file()
                print_success("Configuration saved successfully!")

                # Display success message with next steps
                console.print(
                    "\n[bold green]Setup completed successfully![/bold green]"
                )
                console.print("You can now use the following commands:")
                console.print("  • [cyan]notify test[/cyan] - Test your connection")
                console.print("  • [cyan]notify send <message>[/cyan] - Send a message")
                console.print("  • [cyan]notify photo <file>[/cyan] - Send a photo")
                console.print(
                    "  • [cyan]notify document <file>[/cyan] - Send a document"
                )

    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)


@main.command()
def info() -> None:
    """
    Show information about the current configuration.

    This command displays the current configuration settings in a
    formatted table, including bot token (partially hidden for security),
    chat ID, and network settings.

    Example:
        notify info
    """
    try:
        # Load and display configuration
        config = Config.from_file()

        # Create formatted table with config details
        table = Table(title="Configuration Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        # Display bot token partially hidden for security
        bot_token_display = (
            config.telegram.bot_token[:10] + "..."
            if len(config.telegram.bot_token) > 10
            else config.telegram.bot_token
        )
        table.add_row("Bot Token", bot_token_display)
        table.add_row("Chat ID", config.telegram.chat_id)
        table.add_row("Parse Mode", config.telegram.parse_mode)
        table.add_row("Timeout", str(config.timeout) + "s")
        table.add_row("Retry Attempts", str(config.retry_attempts))
        table.add_row("Retry Delay", str(config.retry_delay) + "s")
        console.print(table)

    except ConfigError as e:
        print_error(str(e))
        console.print(
            "\n[yellow]Run 'notify setup' to configure the application.[/yellow]"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
