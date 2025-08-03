# Notify2 API Documentation

This document provides comprehensive API documentation for the `notify2` Python package.

## Table of Contents

- [Overview](#overview)
- [Configuration Classes](#configuration-classes)
  - [TelegramConfig](#telegramconfig)
  - [Config](#config)
- [Core Class](#core-class)
  - [TelegramNotifier](#telegramnotifier)
- [Exceptions](#exceptions)

---

## Overview

The `notify2` package provides a modern, type-safe interface for sending Telegram messages. It's built with performance, reliability, and ease of use in mind.

### Key Design Principles

- **Type Safety**: Full Pydantic validation for all configurations
- **Resource Management**: Context managers for proper cleanup
- **Error Handling**: Comprehensive exception hierarchy
- **Performance**: Connection pooling and retry strategies
- **Usability**: Simple API with sensible defaults

---

## Configuration Classes

### `TelegramConfig`

Configuration class for Telegram-specific settings.

```python
from notify2 import TelegramConfig

# Create with required fields
config = TelegramConfig(
    bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    chat_id="123456789"
)

# Create with custom parse mode
config = TelegramConfig(
    bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    chat_id="123456789",
    parse_mode="Markdown"
)
```

#### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `bot_token` | `str` | Yes | - | Telegram bot token from @BotFather |
| `chat_id` | `str` | Yes | - | Target chat ID for messages |
| `parse_mode` | `str` | No | `"HTML"` | Message parsing mode (HTML, Markdown, or MarkdownV2) |

#### Validation Rules

- **`bot_token`**: Must be at least 10 characters and contain a colon separator.
- **`chat_id`**: Cannot be empty.
- **`parse_mode`**: Must be one of `"HTML"`, `"Markdown"`, or `"MarkdownV2"`.

#### Methods

##### `validate_bot_token(cls, v: str) -> str`

Validates bot token format and length.

**Raises:**
- `ValueError`: If token is invalid.

##### `validate_chat_id(cls, v: str) -> str`

Validates chat ID is not empty.

**Raises:**
- `ValueError`: If chat ID is empty.

---

### `Config`

Main configuration class that manages all settings for Notify2.

```python
from notify2 import Config, TelegramConfig

# Create from components
telegram_config = TelegramConfig(
    bot_token="your_token",
    chat_id="your_chat_id"
)
config = Config(
    telegram=telegram_config,
    timeout=30,
    retry_attempts=5,
    retry_delay=2.0
)
```

#### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `telegram` | `TelegramConfig` | Yes | - | Telegram-specific configuration |
| `timeout` | `int` | No | `10` | Request timeout in seconds (1-300) |
| `retry_attempts` | `int` | No | `3` | Number of retry attempts (0-10) |
| `retry_delay` | `float` | No | `1.0` | Delay between retries in seconds (0.1-60.0) |

#### Class Methods

##### `from_env() -> Config`

Create configuration from environment variables.

**Environment Variables:**
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather
- `TELEGRAM_CHAT_ID`: Target chat ID

**Returns:**
- `Config`: Configuration instance.

**Raises:**
- `ConfigError`: If required environment variables are missing.

**Example:**
```python
import os
os.environ["TELEGRAM_BOT_TOKEN"] = "your_token"
os.environ["TELEGRAM_CHAT_ID"] = "your_chat_id"

config = Config.from_env()
```

##### `from_file(config_path: Optional[str] = None) -> Config`

Create configuration from JSON file.

**Parameters:**
- `config_path`: Path to configuration file (default: `~/.notify2/config.json`)

**Returns:**
- `Config`: Configuration instance.

**Raises:**
- `ConfigError`: If file doesn't exist or has invalid JSON.

**Example:**
```python
# Use default path
config = Config.from_file()

# Use custom path
config = Config.from_file("/path/to/config.json")
```

#### Instance Methods

##### `save_to_file(config_path: Optional[str] = None) -> None`

Save configuration to JSON file.

**Parameters:**
- `config_path`: Path to save configuration (default: `~/.notify2/config.json`)

**Raises:**
- `ConfigError`: If file cannot be written.

**Example:**
```python
config.save_to_file()
config.save_to_file("/path/to/config.json")
```

##### `to_dict() -> Dict[str, Any]`

Convert configuration to dictionary.

**Returns:**
- `Dict[str, Any]`: Dictionary representation.

**Example:**
```python
config_dict = config.to_dict()
print(config_dict["telegram"]["bot_token"])
```

---

## Core Class

### `TelegramNotifier`

Main class for sending Telegram messages with high performance and reliability.

```python
from notify2 import TelegramNotifier, Config

# Use as context manager (recommended)
with TelegramNotifier(config) as notifier:
    result = notifier.send_message("Hello, World!")
```

#### Constructor

##### `__init__(config: Config)`

Initialize the notifier with configuration.

**Parameters:**
- `config`: Configuration object.

**Raises:**
- `ValidationError`: If configuration is invalid.

#### Methods

##### `send_message(message: str, parse_mode: Optional[str] = None, disable_web_page_preview: bool = False, disable_notification: bool = False, reply_to_message_id: Optional[int] = None) -> Dict[str, Any]`

Send a text message to Telegram.

**Parameters:**
- `message`: Message text (max 4096 characters).
- `parse_mode`: Parse mode for formatting (HTML, Markdown, MarkdownV2).
- `disable_web_page_preview`: Whether to disable link previews.
- `disable_notification`: Whether to send silently.
- `reply_to_message_id`: ID of message to reply to.

**Returns:**
- `Dict[str, Any]`: Telegram API response.

**Raises:**
- `ValidationError`: If message is empty or too long.
- `TelegramError`: If the message fails to send.

**Example:**
```python
# Simple message
result = notifier.send_message("Hello, World!")

# Formatted message
result = notifier.send_message(
    "**Bold text** and *italic text*",
    parse_mode="Markdown"
)

# Silent message with options
result = notifier.send_message(
    message="Secret message",
    disable_notification=True,
    disable_web_page_preview=True
)
```

##### `send_photo(photo_path: Union[str, Path], caption: Optional[str] = None, parse_mode: Optional[str] = None) -> Dict[str, Any]`

Send a photo to Telegram.

**Parameters:**
- `photo_path`: Path to photo file.
- `caption`: Optional caption for the photo.
- `parse_mode`: Parse mode for caption formatting.

**Returns:**
- `Dict[str, Any]`: Telegram API response.

**Raises:**
- `ValidationError`: If photo file doesn't exist.
- `TelegramError`: If the photo fails to send.

**Example:**
```python
# Simple photo
result = notifier.send_photo("image.jpg")

# Photo with caption
result = notifier.send_photo(
    "sunset.png",
    caption="Beautiful sunset!",
    parse_mode="Markdown"
)
```

##### `send_document(document_path: Union[str, Path], caption: Optional[str] = None, parse_mode: Optional[str] = None) -> Dict[str, Any]`

Send a document to Telegram.

**Parameters:**
- `document_path`: Path to document file.
- `caption`: Optional caption for the document.
- `parse_mode`: Parse mode for caption formatting.

**Returns:**
- `Dict[str, Any]`: Telegram API response.

**Raises:**
- `ValidationError`: If document file doesn't exist.
- `TelegramError`: If the document fails to send.

**Example:**
```python
# Simple document
result = notifier.send_document("report.pdf")

# Document with caption
result = notifier.send_document(
    "data.csv",
    caption="Monthly data report",
    parse_mode="Markdown"
)
```

##### `get_me() -> Dict[str, Any]`

Get information about the bot.

**Returns:**
- `Dict[str, Any]`: Bot information from Telegram API.

**Raises:**
- `TelegramError`: If the API call fails.

**Example:**
```python
bot_info = notifier.get_me()
print(f"Bot name: {bot_info['result']['first_name']}")
print(f"Username: @{bot_info['result']['username']}")
```

##### `edit_message_text(message_id: int, text: str, parse_mode: Optional[str] = None, disable_web_page_preview: bool = False) -> Dict[str, Any]`

Edit an existing text message in Telegram.

**Parameters:**
- `message_id`: Identifier of the message to edit.
- `text`: New text of the message (max 4096 characters).
- `parse_mode`: Optional parse mode for formatting (HTML, Markdown, MarkdownV2).
- `disable_web_page_preview`: Optional, whether to disable link previews.

**Returns:**
- `Dict[str, Any]`: Telegram API response containing the edited message details.

**Raises:**
- `ValidationError`: If message text is empty or too long.
- `TelegramError`: If the message fails to edit.

**Example:**
```python
# Assuming 'notifier' is an initialized TelegramNotifier instance
sent_message = notifier.send_message("Initial message")
message_id = sent_message["result"]["message_id"]
notifier.edit_message_text(message_id, "Updated message!")
```

##### `test_connection() -> None`

Test the connection to Telegram API.

**Raises:**
- `TelegramError`: If the connection fails.

**Example:**
```python
try:
    notifier.test_connection()
    print("Connection successful!")
except TelegramError:
    print("Connection failed!")
```

##### `progress_bar(iterable: Any, prefix: str = "Progress:", message_id: Optional[int] = None, bar_length: int = 20) -> Any`

Display a dynamic progress bar in Telegram for an iterable.

**Parameters:**
- `iterable`: The iterable (e.g., list, range) to track progress for. Must have a `__len__` method.
- `prefix`: Optional. Text to prepend to the progress bar message.
- `message_id`: Optional. The message ID of an existing message to edit. If None, a new message will be sent.
- `bar_length`: Optional. The length of the progress bar in characters.

**Yields:**
- Each item from the input `iterable`.

**Raises:**
- `ValueError`: If the `iterable` does not have a `__len__` method.
- `TelegramError`: If sending or editing the message fails.

**Example:**
```python
import time
# Assuming 'notifier' is an initialized TelegramNotifier instance
items_to_process = list(range(1, 11))
# Send an initial message to get a message_id for the progress bar
initial_pb_message = notifier.send_message("Starting long task...")
pb_message_id = initial_pb_message["result"]["message_id"]
for item in notifier.progress_bar(items_to_process, prefix="Task progress:", message_id=pb_message_id):
    print(f"Processing item {item}...")
    time.sleep(0.5) # Simulate work
notifier.send_message("Task complete!")
```

##### `close() -> None`

Close the HTTP session.

This method is automatically called when using the notifier as a context manager.

**Example:**
```python
notifier = TelegramNotifier(config)
try:
    notifier.send_message("Hello")
finally:
    notifier.close()
```

#### Context Manager Support

The `TelegramNotifier` class supports context manager protocol for automatic resource cleanup.

```python
# Recommended usage
with TelegramNotifier(config) as notifier:
    notifier.send_message("Hello")
    notifier.send_photo("image.jpg")
# Session is automatically closed
```

---

## Exceptions

### Exception Hierarchy

```
NotifyError (base)
├── ConfigError
├── TelegramError
└── ValidationError
```

### `NotifyError`

Base exception for all notify2 errors.

```python
try:
    notifier.send_message("Hello")
except NotifyError as e:
    print(f"Notification error: {e}")
```

### `ConfigError`

Raised when there's an issue with configuration.

```python
try:
    config = Config.from_file()
except ConfigError as e:
    print(f"Configuration error: {e}")
```

### `TelegramError`

Raised when there's an issue with Telegram API communication.

```python
try:
    notifier.send_message("Hello")
except TelegramError as e:
    print(f"Telegram API error: {e}")
```

### `ValidationError`

Raised when input validation fails.

```python
try:
    notifier.send_message("")  # Empty message
except ValidationError as e:
    print(f"Validation error: {e}")
```