from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InviteHashInvalid, UserAlreadyParticipant
import asyncio

# Dictionary to store user data temporarily
user_data = {}

# Start a simple Pyrogram app
bot = Client(
    "telegram_bot",
    api_id=26416419,  # Replace with your Bot API ID
    api_hash= "c109c77f5823c847b1aeb7fbd4990cc4",  # Replace with your Bot API Hash
    bot_token= "8075027784:AAHbomx4HBS8GvZGKnOuRwcgDBMzdZTxodw" ,  # Replace with your Bot Token
)

@bot.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await message.reply("Welcome! Please provide your phone number to log in (format: +1234567890).")

@bot.on_message(filters.private & ~filters.command("start"))
async def handle_message(client, message):
    user_id = message.from_user.id
    text = message.text

    # Check if the user has sent the phone number
    if user_id not in user_data:
        user_data[user_id] = {"phone_number": text}
        await message.reply("Phone number saved! Now provide your API ID.")
    elif "api_id" not in user_data[user_id]:
        user_data[user_id]["api_id"] = text
        await message.reply("API ID saved! Now provide your API Hash.")
    elif "api_hash" not in user_data[user_id]:
        user_data[user_id]["api_hash"] = text
        await message.reply("API Hash saved! You can now send me the group links (separated by spaces or new lines).")
    elif "links" not in user_data[user_id]:
        user_data[user_id]["links"] = text.split()
        await message.reply("Links received! Attempting to join groups...")

        # Start joining groups
        phone_number = user_data[user_id]["phone_number"]
        api_id = int(user_data[user_id]["api_id"])
        api_hash = user_data[user_id]["api_hash"]
        links = user_data[user_id]["links"]

        await join_groups(user_id, phone_number, api_id, api_hash, links, message)

async def join_groups(user_id, phone_number, api_id, api_hash, links, message):
    # Create a new Pyrogram client for the user
    async with Client(f"session_{user_id}", api_id=api_id, api_hash=api_hash) as user_client:
        joined_count = 0
        total_links = len(links)

        for link in links:
            try:
                if link.startswith("@"):
                    await user_client.join_chat(link)
                elif "t.me/" in link:
                    chat_username = link.split("t.me/")[-1]
                    await user_client.join_chat(chat_username)
                else:
                    await message.reply(f"Invalid link format: {link}")
                    continue

                joined_count += 1
                await message.reply(f"Successfully joined: {link}")
            except UserAlreadyParticipant:
                await message.reply(f"Already a member of: {link}")
            except InviteHashInvalid:
                await message.reply(f"Invalid invite link: {link}")
            except FloodWait as e:
                await message.reply(f"Rate limit reached. Waiting for {e.value} seconds...")
                await asyncio.sleep(e.value)
            except Exception as e:
                await message.reply(f"Failed to join {link}: {e}")

        await message.reply(f"Joined {joined_count}/{total_links} groups successfully!")

# Run the bot
bot.run()
