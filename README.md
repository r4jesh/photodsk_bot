# Passport Photo Bot

A Telegram bot that removes background using Cutout Pro and creates a 4x6 inch sheet with 12 passport-size photos (30x35 mm).

## 🔧 How to Deploy on Render

1. Upload this folder to GitHub
2. Go to https://render.com
3. Click "New" → "Web Service"
4. Select your GitHub repo
5. Set Environment Variables:
   - `BOT_TOKEN` = your Telegram bot token
   - `CUTOUT_PRO_API_KEY` = your Cutout Pro API key
6. Set Start Command:
   ```
   python passport_bot.py
   ```

✅ Your bot will now run 24×7!
