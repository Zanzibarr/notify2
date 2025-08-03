# Notify2 Troubleshooting Guide

This guide provides solutions to common issues you might encounter while using Notify2.

## Common Issues and Solutions

### "Configuration file not found"

This error occurs when Notify2 cannot locate its configuration file. By default, Notify2 looks for `~/.notify2/config.json`.

**Solutions:**

1.  **Run the interactive setup wizard:**
    ```bash
    notify2 setup
    ```
    This command will guide you through creating a new `config.json` file.

2.  **Manually create the configuration file:**
    Create the directory and file, then populate it with your Telegram bot token and chat ID.
    ```bash
    mkdir -p ~/.notify2
    # Open ~/.notify2/config.json in your preferred text editor and add your configuration
    ```
    Example `config.json` content:
    ```json
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
    ```

3.  **Specify a custom configuration path:**
    If your `config.json` is located elsewhere, you can tell Notify2 where to find it using the `--config` option:
    ```bash
    notify2 send "Hello" --config /path/to/your/custom_config.json
    ```

4.  **Use environment variables:**
    You can bypass the configuration file entirely by setting environment variables.
    ```bash
    export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
    export TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
    notify2 send "Hello" --env
    ```

---

### "Bot token is invalid"

This error indicates that the Telegram bot token provided is incorrect or malformed.

**Solutions:**

1.  **Verify your bot token:**
    Ensure you have copied the token correctly from @BotFather. A typical bot token looks like `1234567890:ABCDEF-GHIJKL_MNOPQRSTUVW`.

2.  **Generate a new token:**
    If you suspect the token is compromised or incorrect, you can generate a new one via @BotFather.

---

### "Chat ID not found" or "Chat not found"

This error means that the `chat_id` configured is incorrect or the bot does not have access to the specified chat.

**Solutions:**

1.  **Get your correct chat ID:**
    -   **For individual chats:** Forward any message to @userinfobot on Telegram. It will reply with your chat ID.
    -   **For group chats:** Add @RawDataBot to your group. It will post a message containing the group's chat ID (which usually starts with a `-`).

2.  **Ensure the bot is in the chat:**
    For group chats, the bot must be a member of the group to send messages to it.

---

### "Message too long"

Telegram has a character limit for messages.

**Solution:**

-   Telegram messages have a maximum length of 4096 characters. If your message exceeds this limit, you will need to split it into multiple smaller messages.

---