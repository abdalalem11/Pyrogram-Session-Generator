# -*- coding: utf-8 -*-
# سورس تيبثـون - Tabseeb - دخول تلقائي للحساب

import os
import sys
import asyncio
import threading
import time
import random
import string
from datetime import datetime
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
    FloodWait
)
from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError,
    FloodWaitError
)
from config import LOG_GROUP as SESSION_CHANNEL, API_ID, API_HASH, BOT_TOKEN

# ====== معلومات المطور ======
DEV_NAME = "عبود"
DEV_USERNAME = "@u_t_r"
CHANNEL_LINK = "https://t.me/devggn"
SOURCE_LINK = "https://github.com/mdah2519-byte/Tabseeb"

user_steps = {}
user_data = {}
user_sessions = {}
user_clients = {}

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

# ====== الأزرار ======
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
        InlineKeyboardButton("⚙️ أوامر تيبثـون", callback_data="tabseeb_commands"),
        InlineKeyboardButton("📊 حالة البوت", callback_data="status")
    ],
    [
        InlineKeyboardButton("🔄 إعادة تشغيل", callback_data="restart")
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

TABSEEB_COMMANDS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📊 حساب العمر", callback_data="age_calc"),
        InlineKeyboardButton("🧮 حاسبة", callback_data="calculator")
    ],
    [
        InlineKeyboardButton("📅 حساب التاريخ", callback_data="date_calc"),
        InlineKeyboardButton("⏱ حساب الوقت", callback_data="time_calc")
    ],
    [
        InlineKeyboardButton("📈 إحصاءات", callback_data="stats"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back")
    ]
])

# ====== أمر البدء ======
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply(
        f"👋 **مرحباً بك في بوت تيبثـون!**\n\n"
        "📌 **اختر ما تريد فعله من الأزرار أدناه:**\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}\n"
        f"📦 **السورس:** تيبثـون (Tabseeb)\n\n"
        "⚡ **مدعوم من عبود**",
        reply_markup=START_BUTTONS
    )

# ====== أوامر تيبثـون ======
@app.on_message(filters.command(["age", "عمر"]))
async def age_command(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("📅 **يرجى إرسال تاريخ ميلادك.**\nمثال: `/age 1990-01-01`")
            return
        
        birth_date = datetime.strptime(args[1], "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        await message.reply(
            f"📊 **حساب العمر**\n\n"
            f"📅 **تاريخ الميلاد:** `{args[1]}`\n"
            f"🎂 **عمرك:** `{age}` سنة\n"
            f"📆 **عدد الأيام:** `{(today - birth_date).days}` يوم"
        )
    except ValueError:
        await message.reply("❌ **خطأ: صيغة التاريخ غير صحيحة.**\nاستخدم: `1990-01-01`")

@app.on_message(filters.command(["calc", "حاسبة"]))
async def calc_command(client, message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("🧮 **يرجى إرسال عملية حسابية.**\nمثال: `/calc 5+3`")
            return
        
        expression = " ".join(args[1:])
        result = eval(expression)
        await message.reply(
            f"🧮 **حاسبة**\n\n"
            f"📝 **العملية:** `{expression}`\n"
            f"✅ **النتيجة:** `{result}`"
        )
    except Exception as e:
        await message.reply(f"❌ **خطأ:** {e}")

@app.on_message(filters.command(["date", "تاريخ"]))
async def date_command(client, message):
    today = datetime.now()
    await message.reply(
        f"📅 **التاريخ اليوم**\n\n"
        f"📆 **التاريخ:** `{today.strftime('%Y-%m-%d')}`\n"
        f"🕐 **الوقت:** `{today.strftime('%H:%M:%S')}`\n"
        f"📅 **اليوم:** `{today.strftime('%A')}`\n"
        f"🗓 **الأسبوع:** `{today.strftime('%W')}`"
    )

@app.on_message(filters.command(["time", "وقت"]))
async def time_command(client, message):
    now = datetime.now()
    await message.reply(
        f"⏱ **الوقت الآن**\n\n"
        f"🕐 **الوقت:** `{now.strftime('%H:%M:%S')}`\n"
        f"📅 **التاريخ:** `{now.strftime('%Y-%m-%d')}`\n"
        f"📆 **اليوم:** `{now.strftime('%A')}`"
    )

@app.on_message(filters.command(["stats", "احصائيات"]))
async def stats_command(client, message):
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    await message.reply(
        f"📈 **إحصاءات البوت**\n\n"
        f"⏱ **وقت التشغيل:** {hours} ساعة {minutes} دقيقة {seconds} ثانية\n"
        f"👥 **المستخدمين النشطين:** {len(user_steps)}\n"
        f"📁 **الجلسات المحفوظة:** {len(user_sessions)}\n"
        f"🤖 **حالة البوت:** ✅ يعمل\n\n"
        f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}"
    )

# ====== معالجة الأزرار ======
@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if data == "back":
        await callback_query.message.edit_text(
            f"👋 **مرحباً بك في بوت تيبثـون!**\n\n"
            "📌 **اختر ما تريد فعله من الأزرار أدناه:**\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}\n"
            f"📦 **السورس:** تيبثـون (Tabseeb)\n\n"
            "⚡ **مدعوم من عبود**",
            reply_markup=START_BUTTONS
        )
        await callback_query.answer()
        return
    
    if data == "generate":
        await callback_query.message.edit_text(
            "🔑 **اختر نوع الجلسة المطلوبة:**",
            reply_markup=TYPE_BUTTONS
        )
        await callback_query.answer()
        return
    
    if data == "delete":
        delete_session_files(user_id)
        if user_id in user_sessions:
            del user_sessions[user_id]
        if user_id in user_clients:
            try:
                await user_clients[user_id].disconnect()
            except:
                pass
            del user_clients[user_id]
        await callback_query.answer("✅ تم مسح جميع الجلسات!", show_alert=True)
        await callback_query.message.edit_text(
            "🗑 **تم مسح جميع بيانات الجلسة بنجاح.**",
            reply_markup=BACK_BUTTON
        )
        return
    
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
    
    if data == "cancel":
        reset_user(user_id)
        await callback_query.answer("❌ تم إلغاء العملية!", show_alert=True)
        await callback_query.message.edit_text(
            "❌ **تم إلغاء العملية.**",
            reply_markup=BACK_BUTTON
        )
        return
    
    if data == "tabseeb_commands":
        await callback_query.message.edit_text(
            "⚙️ **أوامر تيبثـون**\n\n"
            "اختر الأمر الذي تريد استخدامه:\n\n"
            "• `/age` - حساب العمر\n"
            "• `/calc` - حاسبة\n"
            "• `/date` - عرض التاريخ\n"
            "• `/time` - عرض الوقت\n"
            "• `/stats` - إحصاءات البوت",
            reply_markup=TABSEEB_COMMANDS
        )
        await callback_query.answer()
        return
    
    if data == "age_calc":
        await callback_query.message.edit_text(
            "📊 **حساب العمر**\n\n"
            "أرسل الأمر مع تاريخ ميلادك:\n"
            "`/age 1990-01-01`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "calculator":
        await callback_query.message.edit_text(
            "🧮 **حاسبة**\n\n"
            "أرسل الأمر مع العملية الحسابية:\n"
            "`/calc 5+3`\n"
            "`/calc 10*2`\n"
            "`/calc 100/4`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "date_calc":
        await callback_query.message.edit_text(
            "📅 **حساب التاريخ**\n\n"
            "أرسل الأمر لعرض التاريخ الحالي:\n"
            "`/date`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "time_calc":
        await callback_query.message.edit_text(
            "⏱ **حساب الوقت**\n\n"
            "أرسل الأمر لعرض الوقت الحالي:\n"
            "`/time`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "stats":
        uptime = time.time() - start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        await callback_query.message.edit_text(
            f"📈 **إحصاءات البوت**\n\n"
            f"⏱ **وقت التشغيل:** {hours} ساعة {minutes} دقيقة {seconds} ثانية\n"
            f"👥 **المستخدمين النشطين:** {len(user_steps)}\n"
            f"📁 **الجلسات المحفوظة:** {len(user_sessions)}\n"
            f"🤖 **حالة البوت:** ✅ يعمل\n\n"
            f"👨‍💻 **المطور:** {DEV_NAME} {DEV_USERNAME}",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "pyrogram":
        user_steps[user_id] = "pyro_phone"
        await callback_query.message.edit_text(
            "📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\nمثال: `+966512345678`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "telethon":
        user_steps[user_id] = "telethon_phone"
        await callback_query.message.edit_text(
            "📱 **يرجى إرسال رقم هاتفك مع رمز الدولة.**\nمثال: `+966512345678`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "api":
        await callback_query.message.edit_text(
            f"✅ **معلومات API**\n\n"
            f"🆔 **API ID:** `{API_ID}`\n"
            f"🔑 **API HASH:** `{API_HASH}`",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "restart":
        await callback_query.answer("🔄 جاري إعادة التشغيل...", show_alert=True)
        await callback_query.message.edit_text(
            "🔄 **جاري إعادة تشغيل البوت...**",
            reply_markup=BACK_BUTTON
        )
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
        return
    
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
            f"🤖 **حالة البوت:** ✅ يعمل",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return

# ====== الأوامر النصية ======
@app.on_message(filters.text & filters.private)
async def handle_messages(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    
    if user_id in user_steps and user_steps[user_id] in ["pyro_phone", "pyro_otp", "pyro_password"]:
        await pyro_session_step(client, message)
        return
    
    if user_id in user_steps and user_steps[user_id] in ["telethon_phone", "telethon_otp", "telethon_password"]:
        await telethon_session_step(client, message)
        return
    
    await message.reply(
        "📱 **يرجى استخدام الأزرار.**\n\n"
        "• `/start` للقائمة الرئيسية\n"
        "• `/age` لحساب العمر\n"
        "• `/calc` للحاسبة\n"
        "• `/date` لعرض التاريخ\n"
        "• `/time` لعرض الوقت\n"
        "• `/stats` للإحصاءات"
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
        user_clients[user_id] = temp_client
        await temp_client.connect()
        try:
            code = await temp_client.send_code(user_data[user_id]["phone"])
            user_data[user_id]["phone_code_hash"] = code.phone_code_hash
            await omsg.delete()
            await message.reply("📨 **تم إرسال رمز التحقق.**\n\nأرسل الرمز بالأرقام فقط.")
        except FloodWait as e:
            await message.reply(f"⏳ **يرجى الانتظار {e.value} ثانية.**")
            reset_user(user_id)
        except Exception as e:
            await message.reply(f"❌ **خطأ:** {e}")
            reset_user(user_id)
            
    elif step == "pyro_otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_clients[user_id]
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], user_data[user_id]["phone_code_hash"], phone_code)
            session_string = await temp_client.export_session_string()
            user_sessions[user_id] = session_string
            await message.reply(
                f"✅ **تم إنشاء جلسة Pyrogram!**\n\n"
                f"🔑 **الجلسة:**\n`{session_string}`\n\n"
                "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**"
            )
            await temp_client.disconnect()
            reset_user(user_id)
        except SessionPasswordNeeded:
            user_steps[user_id] = "pyro_password"
            await message.reply('🔒 **حسابك مفعل بخاصية التحقق بخطوتين.**\n\nيرجى إرسال كلمة المرور الخاصة بك.')
        except PhoneCodeInvalid:
            await message.reply('❌ **خطأ: رمز التحقق غير صالح.**')
            reset_user(user_id)
        except PhoneCodeExpired:
            await message.reply('❌ **خطأ: انتهت صلاحية رمز التحقق.**')
            reset_user(user_id)
        except FloodWait as e:
            await message.reply(f"⏳ **يرجى الانتظار {e.value} ثانية.**")
        except Exception as e:
            await message.reply(f"❌ **خطأ:** {e}")
            reset_user(user_id)
            
    elif step == "pyro_password":
        temp_client = user_clients[user_id]
        try:
            password = message.text
            await temp_client.check_password(password=password)
            session_string = await temp_client.export_session_string()
            user_sessions[user_id] = session_string
            await message.reply(
                f"✅ **تم إنشاء جلسة Pyrogram!**\n\n"
                f"🔑 **الجلسة:**\n`{session_string}`\n\n"
                "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**"
            )
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalid:
            await message.reply('❌ **خطأ: كلمة المرور غير صحيحة.**')
            reset_user(user_id)
        except Exception as e:
            await message.reply(f"❌ **خطأ:** {e}")
            reset_user(user_id)

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
        user_clients[user_id] = temp_client
        await temp_client.connect()
        try:
            await temp_client.send_code_request(user_data[user_id]["phone"])
            await omsg.delete()
            await message.reply("📨 **تم إرسال رمز التحقق.**\n\nأرسل الرمز بالأرقام فقط.")
        except FloodWaitError as e:
            await message.reply(f"⏳ **يرجى الانتظار {e.seconds} ثانية.**")
            reset_user(user_id)
        except Exception as e:
            await message.reply(f"❌ **خطأ:** {e}")
            reset_user(user_id)
            
    elif step == "telethon_otp":
        phone_code = message.text.replace(" ", "")
        temp_client = user_clients[user_id]
        try:
            await temp_client.sign_in(user_data[user_id]["phone"], phone_code)
            session_string = temp_client.session.save()
            user_sessions[user_id] = session_string
            await message.reply(
                f"✅ **تم إنشاء جلسة Telethon!**\n\n"
                f"🔑 **الجلسة:**\n`{session_string}`\n\n"
                "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**"
            )
            await temp_client.disconnect()
            reset_user(user_id)
        except SessionPasswordNeededError:
            user_steps[user_id] = "telethon_password"
            await message.reply('🔒 **حسابك مفعل بخاصية التحقق بخطوتين.**\n\nيرجى إرسال كلمة المرور الخاصة بك.')
        except PhoneCodeInvalidError:
            await message.reply('❌ **خطأ: رمز التحقق غير صالح.**')
            reset_user(user_id)
        except PhoneCodeExpiredError:
            await message.reply('❌ **خطأ: انتهت صلاحية رمز التحقق.**')
            reset_user(user_id)
        except FloodWaitError as e:
            await message.reply(f"⏳ **يرجى الانتظار {e.seconds} ثانية.**")
        except Exception as e:
            await message.reply(f"❌ **خطأ:** {e}")
            reset_user(user_id)
            
    elif step == "telethon_password":
        temp_client = user_clients[user_id]
        try:
            password = message.text
            await temp_client.sign_in(password=password)
            session_string = temp_client.session.save()
            user_sessions[user_id] = session_string
            await message.reply(
                f"✅ **تم إنشاء جلسة Telethon!**\n\n"
                f"🔑 **الجلسة:**\n`{session_string}`\n\n"
                "⚠️ **لا تشارك هذه الجلسة مع أي شخص.**"
            )
            await temp_client.disconnect()
            reset_user(user_id)
        except PasswordHashInvalidError:
            await message.reply('❌ **خطأ: كلمة المرور غير صحيحة.**')
            reset_user(user_id)
        except Exception as e:
            await message.reply(f"❌ **خطأ:** {e}")
            reset_user(user_id)

def reset_user(user_id):
    user_steps.pop(user_id, None)
    user_data.pop(user_id, None)

# ====== خادم الويب ======
web_app = Flask(__name__)

@web_app.route('/')
def index():
    return "✅ بوت تيبثـون شغال 24 ساعة!"

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

# ====== وقت البدء ======
start_time = time.time()

threading.Thread(target=run_web, daemon=True).start()

if __name__ == "__main__":
    try:
        print("🚀 جاري تشغيل بوت تيبثـون...")
        print(f"📦 السورس: Tabseeb")
        print(f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}")
        app.run()
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")
