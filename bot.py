import os
import time
import asyncio
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from rembg import remove
from PIL import Image
import io

# --- CONFIGURATION ---
BOT_TOKEN = "8565139961:AAGhHB46oIbsuDvfPzfxhqgpZzmghOOLRUI"
ADMIN_ID = 8381570120
ADMIN_USERNAME = "@ShimulXD"
START_TIME = time.time()
RESTART_INTERVAL = 4 * 60 * 60  # 4 hours in seconds

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        f"Hi {update.effective_user.first_name}!\n"
        "I am a High-Quality Background Remover Bot.\n\n"
        "✨ Send me any image, and I will remove the background for you.\n"
        f"👤 Admin: {ADMIN_USERNAME}"
    )
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just send me a photo or an image as a document!")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Determine if it's a photo or a document
    if update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
    elif update.message.document and update.message.document.mime_type.startswith("image/"):
        file = await context.bot.get_file(update.message.document.file_id)
    else:
        return

    status_msg = await update.message.reply_text("⏳ Processing your image... Please wait.")

    try:
        # Download image to memory
        image_bytes = await file.download_as_bytearray()
        
        # Background removal
        print(f"Processing image from {update.effective_user.id}")
        input_image = image_bytes
        output_image = remove(input_image)

        # Send result back
        with io.BytesIO(output_image) as bio:
            bio.name = "no_bg.png"
            await update.message.reply_document(
                document=bio,
                caption="✅ Background Removed Successfully!\nBy @ShimulXD",
                reply_to_message_id=update.message.message_id
            )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def auto_restart_task():
    """Check if 4 hours have passed and exit to trigger GitHub Action restart"""
    while True:
        await asyncio.sleep(60) # check every minute
        elapsed = time.time() - START_TIME
        if elapsed >= RESTART_INTERVAL:
            print("4 Hours reached. Restarting...")
            os._exit(0) # Force exit to let GitHub Action loop restart it

if __name__ == "__main__":
    print("Bot is starting...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image))
    
    # Auto restart logic
    loop = asyncio.get_event_loop()
    loop.create_task(auto_restart_task())
    
    application.run_polling()
