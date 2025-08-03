# Notify2 Configuration

Notify2 offers flexible configuration options to suit various deployment scenarios. You can configure Notify2 using environment variables, a JSON configuration file, or directly within your Python code.

## Configuration Priority

When multiple configuration sources are present, Notify2 follows a specific priority order:

1.  **Command-line arguments**: Values provided directly to CLI commands (e.g., `--config-path`).
2.  **Environment variables**: Values loaded from the system's environment.
3.  **Configuration file**: Values loaded from `~/.notify2/config.json` (or a custom path).
4.  **Default values**: Hardcoded default values for optional parameters.

## 1. Environment Variables

You can set the following environment variables to configure Notify2:

| Environment Variable | Description                                  | Example Value                               |
| :------------------- | :------------------------------------------- | :------------------------------------------ |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather.     | `1234567890:ABCDEF-GHIJKL_MNOPQRSTUVW`      |
| `TELEGRAM_CHAT_ID`   | The target chat ID for sending messages.     | `-123456789` (for a group) or `123456789`   |

### Example

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
export TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
notify2 send "Hello from environment variables!"
```

## 2. Configuration File

Notify2 can load configuration from a JSON file. By default, it looks for `~/.notify2/config.json`. You can also specify a custom path using the `--config` option in the CLI or the `config_path` parameter in the `Config.from_file()` method.

### Default Configuration File Location

`~/.notify2/config.json`

### Example `config.json`

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

### Configuration Options

| Option           | Type     | Default | Description                                                              |
| :--------------- | :------- | :------ | :----------------------------------------------------------------------- |
| `telegram`       | object   | required | Contains Telegram-specific settings.                                     |
| `telegram.bot_token` | string   | required | Your Telegram bot token from @BotFather.                                 |
| `telegram.chat_id`   | string   | required | The target chat ID for messages.                                         |
| `telegram.parse_mode` | string   | `"HTML"` | Default parse mode for messages (`HTML`, `Markdown`, or `MarkdownV2`). |
| `timeout`        | integer  | `10`    | Request timeout in seconds (1-300).                                      |
| `retry_attempts` | integer  | `3`     | Number of retry attempts for failed requests (0-10).                     |
| `retry_delay`    | float    | `1.0`   | Delay in seconds between retries (0.1-60.0).                             |

### Interactive Setup

The `notify2 setup` command provides an interactive wizard to help you create and save your `config.json` file.

```bash
notify2 setup
```

## 3. In-Code Configuration

For programmatic usage, you can create and manage `Config` objects directly within your Python code. This is useful for applications that need dynamic configuration or do not rely on external files or environment variables.

### Example

```python
from notify2 import Config, TelegramConfig

# Create Telegram-specific configuration
telegram_config = TelegramConfig(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID",
    parse_mode="Markdown"
)

# Create main Notify2 configuration
config = Config(
    telegram=telegram_config,
    timeout=30,          # 30 second timeout
    retry_attempts=5,    # 5 retry attempts
    retry_delay=2.0      # 2 second delay between retries
)

# You can then use this config object with TelegramNotifier
from notify2 import TelegramNotifier

with TelegramNotifier(config) as notifier:
    notifier.send_message("Hello from in-code config!")
```

For more details on the `Config` and `TelegramConfig` classes, refer to the [API Documentation](api.md).
