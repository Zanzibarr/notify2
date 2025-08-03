"""
This script demonstrates a realistic usage of the notify2 library,
specifically focusing on sending Telegram notifications and using the progress bar feature.

It initializes a TelegramNotifier using configuration loaded from a file,
tests the connection, sends a simple message, and then showcases a progress bar
for a simulated long-running task.

Before running, ensure you have a `config.json` file in `~/.notify2/`
(or the default config path) with your Telegram bot token and chat ID.
Example `config.json`:
{
    "telegram": {
        "bot_token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    },
    "timeout": 10,
    "retry_attempts": 3,
    "retry_delay": 1.0
}
"""

import time
from notify2 import Config, TelegramNotifier, NotifyError, TelegramError, ConfigError, ValidationError


def initialize_notifier() -> TelegramNotifier | None:
    """
    Initializes and returns a TelegramNotifier instance.
    Loads configuration from the default file path.
    """
    print(f"Attempting to load configuration from: {Config.DEFAULT_CONFIG_PATH}")
    try:
        # Initialize TelegramNotifier with the loaded configuration.
        # By default, Config.from_file() looks for ~/.notify2/config.json.
        # It's recommended to use it as a context manager for proper resource cleanup.
        notifier = TelegramNotifier(Config.from_file())
        print("TelegramNotifier initialized.")
        return notifier
    except (NotifyError, Exception) as e:
        print(f"An error occurred during configuration loading or notifier initialization: {e}")
        if isinstance(e, ConfigError):
            print(f"Please ensure your configuration file exists at '{Config.DEFAULT_CONFIG_PATH}' and is correctly formatted.")
            print("Example config.json content:")
            print('''{
    "telegram": {
        "bot_token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
    },
    "timeout": 10,
    "retry_attempts": 3,
    "retry_delay": 1.0
}''')
        elif isinstance(e, ValidationError):
            print("There was a validation error with the loaded configuration.")
        else:
            print(f"An unexpected error occurred: {e}")
        return None


def test_telegram_connection(notifier: TelegramNotifier) -> bool:
    """
    Tests the connection to the Telegram API using the provided notifier.
    Returns True if connection is successful, False otherwise.
    """
    print("Testing connection to Telegram API...")
    try:
        notifier.test_connection()
        print("Connection successful!")
        return True
    except TelegramError as e:
        print(f"Connection failed: {e}. Please check your bot token and internet connection.")
        return False

def send_test_message(notifier: TelegramNotifier):
    """
    Sends a predefined test message using the notifier.
    """
    test_message = "Hello from notify2! This is a test message from a realistic usage script."
    print(f"Sending test message: '{test_message}'")
    try:
        result = notifier.send_message(test_message)
        print("Message sent successfully!")
        print(f"Telegram API response: {result}")
    except NotifyError as e:
        print(f"Failed to send message: {e}")
        if isinstance(e, TelegramError):
            print("This might be due to an invalid chat ID or bot token, or network issues.")
        elif isinstance(e, ValidationError):
            print("This might be due to an invalid message format.")

def demonstrate_progress_bar(notifier: TelegramNotifier):
    """
    Demonstrates the progress bar feature of the notifier.
    Simulates processing a list of items and updates the progress bar in Telegram.
    """
    print("\nDemonstrating progress bar...")
    items_to_process = list(range(20))  # Example: 20 items to simulate work

    try:
        # Send an initial message to get a message_id for the progress bar.
        # This message will be updated as the progress bar advances.
        initial_pb_message = notifier.send_message("Starting progress...")
        pb_message_id = initial_pb_message["result"]["message_id"]

        for i in notifier.progress_bar(items_to_process, prefix="Processing items:", message_id=pb_message_id):
            print(f"Processing item {i}...")
            time.sleep(0.5)  # Simulate work being done for each item
        
        notifier.send_message("Progress bar complete!")
        print("Progress bar demonstration finished.")

    except NotifyError as e:
        print(f"Failed to demonstrate progress bar: {e}")
        if isinstance(e, TelegramError):
            print("This might be due to an invalid chat ID or bot token, or network issues.")

def main():
    """
    Main function to run the realistic usage demonstration.
    """
    notifier = initialize_notifier()
    if notifier:
        with notifier:  # Use notifier as a context manager for proper resource cleanup
            if test_telegram_connection(notifier):
                send_test_message(notifier)
                demonstrate_progress_bar(notifier)


if __name__ == "__main__":
    main()
