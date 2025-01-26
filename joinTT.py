from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import asyncio

# === Option 1: Use a bot token ===
BOT_TOKEN = "8075027784:AAHbomx4HBS8GvZGKnOuRwcgDBMzdZTxodw"  # Replace with your bot token from BotFather
USE_BOT_TOKEN = True  # Set to True if you want to use the bot token

# === Option 2: Use your user account ===
API_ID = 26416419  # Replace with your API ID from my.telegram.org
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"  # Replace with your API Hash
PHONE_NUMBER = "+1234567890"  # Replace with your phone number if using a user account


# Function to join groups
async def join_groups(client, group_links):
    for link in group_links:
        try:
            await client.join_chat(link.strip())
            print(f"Successfully joined: {link}")
        except Exception as e:
            print(f"Failed to join {link}: {e}")


async def main():
    # Initialize client based on the chosen method
    if USE_BOT_TOKEN:
        print("Starting bot with bot token...")
        client = TelegramClient("bot_session", api_id=26416419, api_hash="c109c77f5823c847b1aeb7fbd4990cc4").start(bot_token=BOT_TOKEN)
    else:
        print("Starting bot with user account...")
        client = TelegramClient("user_session", API_ID, API_HASH)

        await client.connect()

        # If not logged in, perform login process
        if not await client.is_user_authorized():
            await client.send_code_request(PHONE_NUMBER)
            otp = input("Enter the OTP sent to your Telegram account: ")
            try:
                await client.sign_in(PHONE_NUMBER, otp)
            except SessionPasswordNeededError:
                password = input("Your account has 2FA enabled. Enter your password: ")
                await client.sign_in(password=password)

    print("Bot is ready!")

    # Start handling commands
    @client.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        await event.respond(
            "Welcome! Please send group links (one per line), and I'll join them for you."
        )

    @client.on(events.NewMessage)
    async def message_handler(event):
        if event.text.startswith("http"):
            group_links = event.text.splitlines()
            await join_groups(client, group_links)
            await event.respond("I have successfully processed the links.")

    # Run until disconnected
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
