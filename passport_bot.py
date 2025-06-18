import logging
import requests
from io import BytesIO
from PIL import Image
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import os

BOT_TOKEN = '7767749828:AAHB-D8atqEoGWz5nzUx387AGz9Jd2oL0UQ'
CUTOUT_PRO_API_KEY = '5d8477b9d3f04a518de5bd5c8cb5ad0e'



logging.basicConfig(level=logging.INFO)

def remove_bg_cutoutpro(image_bytes):
    response = requests.post(
        'https://www.cutout.pro/api/v1/matting?mattingType=1',
        headers={'APIKEY': CUTOUT_PRO_API_KEY},
        files={'file': ('photo.jpg', image_bytes, 'image/jpeg')}
    )
    if response.status_code == 200:
        return response.content
    else:
        print("❌ Cutout Pro error:", response.text)
        return None

def make_passport_sheet(image_bytes):
    passport_img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    passport_img = passport_img.resize((354, 413))
    sheet = Image.new("RGBA", (1200, 1800), "white")
    for row in range(4):
        for col in range(3):
            x = col * 400
            y = row * 440
            sheet.paste(passport_img, (x, y), passport_img)
    sheet = sheet.convert("RGB")
    output = BytesIO()
    output.name = "passport_4x6_sheet.jpg"
    sheet.save(output, format="JPEG", quality=95, dpi=(300, 300))
    output.seek(0)
    return output

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Print Guidelines", callback_data="print_help")],
        [InlineKeyboardButton("🌐 Visit CutoutPro", url="https://www.cutout.pro")],
    ]
    await update.message.reply_text(
        "👋 Welcome to *Passport Photo Bot!*

"
        "📸 Just send me a clear photo with your face.
"
        "I'll remove the background and return a 4x6 inch sheet with 12 passport-size photos (30×35 mm).",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "print_help":
        await query.edit_message_text(
            "📏 *Print Tips:*

"
            "- Use 4x6 inch glossy photo paper
"
            "- Print at 300 DPI resolution
"
            "- Each photo will be 30×35 mm
"
            "- Cut them accurately after printing.",
            parse_mode="Markdown"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action=ChatAction.UPLOAD_PHOTO)
    await update.message.reply_text("🧠 Removing background using Cutout Pro...")

    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    processed = remove_bg_cutoutpro(photo_bytes)

    if not processed:
        await update.message.reply_text("❌ Background removal failed. Try again.")
        return

    await update.message.chat.send_action(action=ChatAction.UPLOAD_PHOTO)
    await update.message.reply_text("📐 Generating your 4x6 inch passport photo sheet...")

    sheet = make_passport_sheet(processed)
    await update.message.reply_photo(photo=sheet, caption="✅ Ready to print! 4x6 inch, 12 photos (30x35 mm each)")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
    
