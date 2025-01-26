from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import asyncio

# Store user credentials temporarily
user_credentials = {}

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


# Function to handle multiple accounts
async def handle_multiple_accounts(account_details, group_links):
    tasks = []
    for account in account_details:
        api_id, api_hash, phone_number = account
        client = TelegramClient(f"{phone_number}_session", api_id, api_hash)

        # Handling login process
        async def login_and_join():
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone_number)
                otp = user_credentials.get(phone_number, {}).get("otp")
                if not otp:
                    print(f"OTP not found for {phone_number}, skipping...")
                    return
                try:
                    await client.sign_in(phone_number, otp)
                except SessionPasswordNeededError:
                    password = user_credentials.get(phone_number, {}).get("password")
                    if password:
                        await client.sign_in(password=password)
                    else:
                        print(f"Password missing for {phone_number}, skipping...")
                        return
            
            # Join groups for this account
            success, failure = await join_groups(client, group_links)
            print(f"Account {phone_number}:\n  Successfully joined: {success}\n  Failed to join: {failure}")
            await client.disconnect()

        tasks.append(login_and_join())

    await asyncio.gather(*tasks)


# Function to handle new messages in DM
async def on_new_message(event):
    # Start or handle messages from the user (bot DM)
    if event.text.lower() == '/start':
        await event.respond("Hi! Please provide the following information to proceed:\n\n"
                            "1. API ID\n"
                            "2. API Hash\n"
                            "3. Phone Number\n")
    elif event.text.startswith("API ID:"):
        # Extract API ID, Hash, and Phone Number
        api_id = int(event.text.split(":")[1].strip())
        await event.respond("Great! Now please provide the API hash:")
        user_credentials[event.sender_id] = {"api_id": api_id}
    elif event.text.startswith("API Hash:"):
        api_hash = event.text.split(":")[1].strip()
        user_credentials[event.sender_id]["api_hash"] = api_hash
        await event.respond("Awesome! Now, please enter your phone number:")
    elif event.text.startswith("Phone Number:"):
        phone_number = event.text.split(":")[1].strip()
        user_credentials[event.sender_id]["phone_number"] = phone_number
        await event.respond(f"Thanks! An OTP will be sent to {phone_number}. Please enter the OTP here.")
    elif event.text.startswith("OTP:"):
        otp = event.text.split(":")[1].strip()
        user_credentials[event.sender_id]["otp"] = otp
        await event.respond("Thanks for providing the OTP! Now, you can send the group links you'd like to join.")
    else:
        # Handle group links
        group_links = event.text.splitlines()
        if group_links:
            # Once all credentials are gathered, proceed to join groups
            account_details = [(user_credentials[event.sender_id]["api_id"],
                                user_credentials[event.sender_id]["api_hash"],
                                user_credentials[event.sender_id]["phone_number"])]
            await handle_multiple_accounts(account_details, group_links)
            await event.respond("Done! Groups joined successfully.")
        else:
            await event.respond("Please send valid group links to join.")


# Main function to run the bot
async def main():
    # Set up the bot
    bot_token = "8075027784:AAHbomx4HBS8GvZGKnOuRwcgDBMzdZTxodw"  # Replace with your bot's token
    bot = TelegramClient("bot_session", api_id=0, api_hash="")  # Dummy API ID and Hash; bot token will handle login

    @bot.on(events.NewMessage)
    async def message_handler(event):
        await on_new_message(event)

    # Start the bot with the token
    await bot.start(bot_token=bot_token)
    print("EonRobot-core-main - database loaded successfully.
           EonRobot-bot-userbot - Eon On The Way 💗
          @EonRobot-Started Successfully!! .")

    # Run bot until manually stopped
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
