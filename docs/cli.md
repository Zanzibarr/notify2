# Notify2 CLI Documentation

This document provides detailed information on how to use the Notify2 Command Line Interface (CLI).

## Commands Overview

- [`notify2 test`](#notify2-test): Test the Telegram connection.
- [`notify2 send`](#notify2-send): Send text messages.
- [`notify2 photo`](#notify2-photo): Send photos.
- [`notify2 document`](#notify2-document): Send documents.
- [`notify2 setup`](#notify2-setup): Interactive setup wizard.
- [`notify2 info`](#notify2-info): Show current configuration.

---

## `notify2 test`

Test the Telegram connection and display bot information.

### Usage

```bash
notify2 test                    # Use default config
notify2 test --env             # Use environment variables
notify2 test -c config.json    # Use custom config file
```

### Options

- `-c, --config TEXT`: Path to a custom configuration file.
- `--env`: Use environment variables for configuration.

---

## `notify2 send`

Send text messages with various formatting options.

### Usage

```bash
notify2 send "Hello, World!"                    # Simple message
notify2 send "*Bold* text" --parse-mode Markdown  # Formatted
echo "Hello" | notify2 send                     # From stdin
notify2 send --silent "Secret message"          # Silent message
```

### Options

- `--parse-mode [HTML|Markdown|MarkdownV2]`: Parse mode for message text. Defaults to `HTML`.
- `--disable-preview`: Disables web page preview for links in the message.
- `--silent`: Sends the message silently. Users will receive a notification with no sound.
- `-c, --config TEXT`: Path to a custom configuration file.
- `--env`: Use environment variables for configuration.

---

## `notify2 photo`

Send photos with optional captions.

### Usage

```bash
notify2 photo image.jpg                           # Simple photo
notify2 photo sunset.png --caption "Beautiful!"  # With caption
notify2 photo pic.jpg --parse-mode Markdown      # Formatted caption
```

### Options

- `--caption TEXT`: Caption for the photo.
- `--parse-mode [HTML|Markdown|MarkdownV2]`: Parse mode for caption text. Defaults to `HTML`.
- `-c, --config TEXT`: Path to a custom configuration file.
- `--env`: Use environment variables for configuration.

---

## `notify2 document`

Send documents with optional captions.

### Usage

```bash
notify2 document report.pdf                           # Simple document
notify2 document data.csv --caption "Monthly data"   # With caption
notify2 document file.txt --parse-mode Markdown      # Formatted caption
```

### Options

- `--caption TEXT`: Caption for the document.
- `--parse-mode [HTML|Markdown|MarkdownV2]`: Parse mode for caption text. Defaults to `HTML`.
- `-c, --config TEXT`: Path to a custom configuration file.
- `--env`: Use environment variables for configuration.

---

## `notify2 setup`

Interactive setup wizard for configuration. This command guides you through entering your bot token, chat ID, testing the connection, and saving the configuration.

### Usage

```bash
notify2 setup
```

---

## `notify2 info`

Show current configuration information.

### Usage

```bash
notify2 info
```
