import logging
import requests
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import os

BOT_TOKEN = os.getenv('7767749828:AAHB-D8atqEoGWz5nzUx387AGz9Jd2oL0UQ')
CUTOUT_PRO_API_KEY = os.getenv('5d8477b9d3f04a518de5bd5c8cb5ad0')

logging.basicConfig(level=logging.INFO)

def remove_bg_cutoutpro(image_bytes):
    response = requests.post(
        'https://www.cutout.pro/api/v1/matting?mattingType=1',
        headers={'APIKEY': 5d8477b9d3f04a518de5bd5c8cb5ad0},
        files={'file': ('photo.jpg', image_bytes, 'image/jpeg')}
    )
    if response.status_code == 200:
        return response.content
    else:
        print("❌ Cutout Pro error:", response.text)
        return None

def make_passport_sheet(image_bytes):
    passport_img = Image.open(BytesIO(image_bytes)).convert("RGB")
    passport_img = passport_img.resize((354, 413))
    sheet = Image.new("RGB", (1200, 1800), "white")
    for row in range(4):
        for col in range(3):
            x = col * 400
            y = row * 440
            sheet.paste(passport_img, (x, y))
    output = BytesIO()
    output.name = "passport_4x6_30x35mm.jpg"
    sheet.save(output, format="JPEG", quality=95, dpi=(300, 300))
    output.seek(0)
    return output

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send a photo and I’ll return a 4x6 inch passport sheet (12 photos, 30×35 mm).")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    await update.message.reply_text("🧠 Removing background using Cutout Pro...")
    processed = remove_bg_cutoutpro(photo_bytes)
    if not processed:
        await update.message.reply_text("❌ Background removal failed. Try again.")
        return
    await update.message.reply_text("📐 Generating your 4x6 passport sheet...")
    sheet = make_passport_sheet(processed)
    await update.message.reply_photo(photo=sheet, caption="✅ Ready to print (4x6 inch, 30x35 mm × 12 photos)")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
