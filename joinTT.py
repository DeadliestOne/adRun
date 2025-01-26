from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import asyncio

# === User Account Configuration ===
API_ID = 26416419  # Replace with your API ID from my.telegram.org
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"  # Replace with your API Hash
PHONE_NUMBER = "+8801634532670"  # Replace with your phone number if using a user account


# Function to join groups
async def join_groups(client, group_links):
    success_count = 0
    failure_count = 0

    for link in group_links:
        try:
            # Attempt to join the group
            await client.join_chat(link.strip())
            print(f"Successfully joined: {link}")
            success_count += 1
        except FloodWaitError as e:
            print(f"Rate limited! Need to wait for {e.seconds} seconds before the next attempt.")
            await asyncio.sleep(e.seconds)  # Wait for the specified time
        except Exception as e:
            print(f"Failed to join {link}: {e}")
            failure_count += 1

    # Provide a summary
    print(f"\nSummary:\n  Successfully joined: {success_count}\n  Failed to join: {failure_count}")
    return success_count, failure_count


async def main():
    print("Starting bot with user account...")

    # Initialize client
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

    print("Logged in successfully!")

    # Register event handlers
    @client.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        await event.respond(
            "Welcome! Please send group links (one per line), and I'll join them for you."
        )

    @client.on(events.NewMessage)
    async def message_handler(event):
        if event.text.startswith("http"):
            group_links = event.text.splitlines()
            success, failure = await join_groups(client, group_links)
            await event.respond(f"Task complete!\nSuccessfully joined: {success}\nFailed to join: {failure}")

    # Run until disconnected
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
