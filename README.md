# Notify2 🚀

A modern, well-organized Python package for sending Telegram notifications with enhanced performance, better error handling, and beautiful user interfaces.

## ✨ Features

- **🚀 High Performance**: Connection pooling and automatic retry strategies
- **🎨 Beautiful CLI**: Rich terminal output with colors, progress bars, and tables
- **🔒 Type Safety**: Full Pydantic validation for all configurations
- **📱 Multi-format Support**: Send text messages, photos, and documents
- **⚙️ Flexible Configuration**: Environment variables, JSON files, or interactive setup
- **🛡️ Robust Error Handling**: Comprehensive error handling with clear messages
- **🧪 Comprehensive Testing**: Full test suite with 90%+ coverage
- **📚 Modern Python**: Type hints, async support, and context managers

## 🚀 Quick Start

### Installation

```bash
# Install from source
python3 setup.py install
```

### First Time Setup

```bash
# Interactive setup wizard
notify2 setup

# Or manually create config file
mkdir -p ~/.notify2
cat > ~/.notify2/config.json << EOF
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "parse_mode": "HTML"
  },
  "timeout": 10,
  "retry_attempts": 3,
  "retry_delay": 1.0
}
EOF
```

### Basic Usage

```bash
# Test your connection
notify2 test

# Send a simple message
notify2 send "Hello, World! 🚀"

# Send with formatting
notify2 send "*Bold text* and _italic text_" --parse-mode Markdown

# Send a photo
notify2 photo image.jpg --caption "Check this out!"

# Send a document
notify2 document report.pdf --caption "Monthly report"

# Show current configuration
notify2 info
```

## 📖 Documentation

For full documentation, including CLI usage, API reference, configuration, and troubleshooting, please refer to our [documentation site](docs/index.md).

### Command Line Interface

#### `notify2 test`
Test the Telegram connection and display bot information.

```bash
notify2 test                   # Use default config
notify2 test --env             # Use environment variables
notify2 test -c config.json    # Use custom config file
```

#### `notify2 send`
Send text messages with various formatting options.

```bash
notify2 send "Hello, World!"                      # Simple message
notify2 send "*Bold* text" --parse-mode Markdown  # Formatted
echo "Hello" | notify2 send                       # From stdin
notify2 send --silent "Secret message"            # Silent message
```

**Options:**
- `--parse-mode`: HTML, Markdown, or MarkdownV2
- `--disable-preview`: Disable web page previews
- `--silent`: Send without notification sound

#### `notify2 photo`
Send photos with optional captions.

```bash
notify2 photo image.jpg                          # Simple photo
notify2 photo sunset.png --caption "Beautiful!"  # With caption
notify2 photo pic.jpg --parse-mode Markdown      # Formatted caption
```

#### `notify2 document`
Send documents with optional captions.

```bash
notify2 document report.pdf                          # Simple document
notify2 document data.csv --caption "Monthly data"   # With caption
notify2 document file.txt --parse-mode Markdown      # Formatted caption
```

#### `notify2 setup`
Interactive setup wizard for configuration.

```bash
notify2 setup
```

This guides you through:
- Entering your bot token from @BotFather
- Entering your chat ID
- Testing the connection
- Saving the configuration

#### `notify2 info`
Show current configuration information.

```bash
notify2 info
```

### Python API

#### Basic Usage

```python
from notify2 import TelegramNotifier, Config

# Load configuration
config = Config.from_file()

# Send messages
with TelegramNotifier(config) as notifier:
    # Simple message
    result = notifier.send_message("Hello, World!")
    print(f"Message sent with ID: {result['result']['message_id']}")
    
    # Formatted message
    result = notifier.send_message(
        "**Bold text** and *italic text*",
        parse_mode="Markdown"
    )
    
    # Photo with caption
    result = notifier.send_photo("image.jpg", "Beautiful sunset!")
    
    # Document
    result = notifier.send_document("report.pdf", "Monthly report")
```

#### Configuration Management

```python
from notify2 import Config, TelegramConfig

# Create configuration from environment variables
config = Config.from_env()

# Create configuration from file
config = Config.from_file()

# Create configuration manually
telegram_config = TelegramConfig(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID",
    parse_mode="HTML"
)
config = Config(
    telegram=telegram_config,
    timeout=30,
    retry_attempts=5,
    retry_delay=2.0
)

# Save configuration
config.save_to_file()
```

#### Advanced Usage

```python
from notify2 import TelegramNotifier, Config

config = Config.from_file()

with TelegramNotifier(config) as notifier:
    # Test connection
    if notifier.test_connection():
        print("Connection successful!")
    
    # Get bot information
    bot_info = notifier.get_me()
    print(f"Bot name: {bot_info['result']['first_name']}")
    
    # Send message with all options
    result = notifier.send_message(
        message="Hello with options!",
        parse_mode="Markdown",
        disable_web_page_preview=True,
        disable_notification=True,
        reply_to_message_id=123
    )
```

### Configuration

#### Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

#### Configuration File

Default location: `~/.notify2/config.json`

```json
{
  "telegram": {
    "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "123456789",
    "parse_mode": "HTML"
  },
  "timeout": 10,
  "retry_attempts": 3,
  "retry_delay": 1.0
}
```

#### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bot_token` | string | required | Telegram bot token from @BotFather |
| `chat_id` | string | required | Target chat ID for messages |
| `parse_mode` | string | "HTML" | Message parsing mode (HTML, Markdown, MarkdownV2) |
| `timeout` | int | 10 | Request timeout in seconds (1-300) |
| `retry_attempts` | int | 3 | Number of retry attempts (0-10) |
| `retry_delay` | float | 1.0 | Delay between retries in seconds (0.1-60.0) |

## 📊 Performance

- **Connection Pooling**: Reuses HTTP connections for better performance
- **Automatic Retries**: Exponential backoff for failed requests
- **Resource Management**: Proper cleanup with context managers
- **Type Safety**: Pydantic validation prevents runtime errors

## 🔧 Troubleshooting

### Common Issues

#### "Configuration file not found"
```bash
# Run setup wizard
notify2 setup

# Or create config manually
mkdir -p ~/.notify2
# Edit ~/.notify2/config.json
```

#### "Bot token is invalid"
- Get a new bot token from @BotFather
- Ensure the token format is correct: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

#### "Chat ID not found"
- Use @userinfobot to get your chat ID
- For groups, use @RawDataBot in the group

#### "Message too long"
- Telegram has a 4096 character limit for messages
- Split long messages into multiple parts

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Telegram Bot API](https://core.telegram.org/bots/api) for the excellent API
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Click](https://click.palletsprojects.com/) for CLI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Zanzibarr/notify2/issues)
- **Documentation**: [Documentation](docs/index.md)
- **Examples**: [Basic Usage](examples/basic_usage.py)

---

**Made with ❤️ and ☕ by the Notify2 team** 