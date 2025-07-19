import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
STORAGE_CHANNEL = int(os.environ.get("STORAGE_CHANNEL"))
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL")
OWNER_ID = int(os.environ.get("OWNER_ID"))

app = Client("filestorebot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def is_subscribed(user_id):
    try:
        member = await app.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@app.on_message(filters.document | filters.video | filters.audio & filters.private)
async def save_file(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("🚫 Only admins can upload files.")

    sent_msg = await message.copy(STORAGE_CHANNEL)
    file_id = sent_msg.message_id

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Download File", url=f"https://t.me/{(await app.get_me()).username}?start=file_{file_id}")]
    ])

    await message.reply("✅ File saved. Available for 50 minutes.", reply_markup=btn)
    await asyncio.sleep(50 * 60)
    try:
        await app.delete_messages(STORAGE_CHANNEL, file_id)
    except:
        pass

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id
    if not await is_subscribed(user_id):
        return await message.reply(
            "🚫 You must join our channel to access files.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("✅ I Joined", callback_data="refresh")]
            ])
        )

    if len(message.command) > 1 and message.command[1].startswith("file_"):
        file_id = int(message.command[1].split("_")[1])
        try:
            await app.forward_messages(chat_id=message.chat.id, from_chat_id=STORAGE_CHANNEL,
                                       message_ids=file_id, protect_content=True)
        except:
            await message.reply("⚠️ File not found or expired.")
    else:
        await message.reply("👋 Welcome! This bot saves files for 50 minutes.\n\nOnly admins can upload.")

@app.on_callback_query(filters.regex("refresh"))
async def refresh(client, cb):
    if await is_subscribed(cb.from_user.id):
        await cb.message.delete()
        await cb.message.reply("✅ Subscribed. Now send /start again.")
    else:
        await cb.answer("❌ You still haven't joined.", show_alert=True)

app.run()
