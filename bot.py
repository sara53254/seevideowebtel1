import os
import uuid
from flask import Flask, send_from_directory
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
UPLOAD_FOLDER = "/app/data/videos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def index():
    return "Video server is running!"

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    video = message.video or message.document
    if not video:
        await message.reply_text("لطفاً یک فایل ویدیویی ارسال کنید.")
        return
    file_id = video.file_id
    file_name = getattr(video, 'file_name', None) or f"{uuid.uuid4().hex}.mp4"
    unique_name = f"{uuid.uuid4().hex}_{file_name}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    await message.reply_text("⏳ در حال دانلود و ذخیره ویدیو...")
    try:
        new_file = await context.bot.get_file(file_id)
        await new_file.download_to_drive(file_path)
    except Exception as e:
        await message.reply_text(f"❌ خطا در دانلود فایل: {e}")
        return
    video_url = f"{BASE_URL}/video/{unique_name}"
    await message.reply_text(
        f"✅ ویدیو با موفقیت آپلود شد!\n\n🔗 لینک پخش: {video_url}"
    )

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 یک ویدیو برام بفرست تا آپلودش کنم و لینک پخشش رو بدم. 🎬"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Document.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/start$"), handle_start))
    print("🤖 ربات در حال اجراست...")
    application.run_polling()

if __name__ == "__main__":
    main()
