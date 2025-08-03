from notify2 import TelegramNotifier, Config, TelegramConfig

# Create configuration manually (replace with your actual bot token and chat ID)
telegram_config = TelegramConfig(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID",
    parse_mode="HTML"
)
config = Config(
    telegram=telegram_config,
    timeout=10,
    retry_attempts=3,
    retry_delay=1.0
)

# Send a simple message
with TelegramNotifier(config) as notifier:
    result = notifier.send_message("Hello from basic_usage.py!")
    print(f"Message sent with ID: {result['result']['message_id']}")
