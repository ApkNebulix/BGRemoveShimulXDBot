import os
import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from rembg import remove
import io

# --- CONFIGURATION ---
BOT_TOKEN = "8565139961:AAGhHB46oIbsuDvfPzfxhqgpZzmghOOLRUI"
ADMIN_ID = 8381570120
ADMIN_USERNAME = "@ShimulXD"
START_TIME = time.time()
RESTART_INTERVAL = 4 * 60 * 60  # 4 hours

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        f"Hi {update.effective_user.first_name} [🇧🇩]!\n"
        "I am a High-Quality Background Remover Bot.\n\n"
        "✨ Send me any image, and I will remove the background for you.\n"
        f"👤 Admin: {ADMIN_USERNAME}"
    )
    await update.message.reply_text(welcome_msg)

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Determine the file (Photo or Document)
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document and update.message.document.mime_type.startswith("image/"):
        file_id = update.message.document.file_id
    else:
        return

    status_msg = await update.message.reply_text("⏳ Processing your image... Please wait.")

    try:
        # Get file from telegram
        tg_file = await context.bot.get_file(file_id)
        
        # Download as bytearray and CONVERT TO BYTES (Fixing the error)
        image_byte_array = await tg_file.download_as_bytearray()
        input_image = bytes(image_byte_array) # This fixes the 'bytearray' error

        # Processing with rembg (High Quality Settings)
        # alpha_matting adds better edge detection for hair/details
        output_image = remove(input_image, alpha_matting=True)

        # Create output stream
        output_io = io.BytesIO(output_image)
        output_io.name = "shimul_xd_bg_removed.png"

        # Send as document to keep 100% quality
        await update.message.reply_document(
            document=output_io,
            caption="✅ Background Removed Successfully!\nProcessed by @ShimulXD",
            reply_to_message_id=update.message.message_id
        )
        
        await status_msg.delete()

    except Exception as e:
        print(f"Error: {e}")
        await status_msg.edit_text(f"❌ Error occurred while processing. Please try again.")

async def auto_restart_task():
    while True:
        await asyncio.sleep(60)
        elapsed = time.time() - START_TIME
        if elapsed >= RESTART_INTERVAL:
            os._exit(0)

if __name__ == "__main__":
    print("Bot is starting...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image))
    
    # Run auto-restart task in background
    asyncio.get_event_loop().create_task(auto_restart_task())
    
    application.run_polling()
