import os
import asyncio
from fastapi import FastAPI
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from datetime import datetime, timezone, timedelta

# قراءة المتغيرات من Render
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER", "")
TARGET_CHAT = os.environ.get("TARGET_CHAT", "")
MY_TELEGRAM_ID = int(os.environ.get("MY_TELEGRAM_ID", 0))
STICKER_ID = os.environ.get("STICKER_ID", "")

if TARGET_CHAT and TARGET_CHAT.lstrip("-").isdigit():
    TARGET_CHAT = int(TARGET_CHAT)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Mahdi Terminal Bot is running!"}

bot = TelegramClient('bot_session', API_ID, API_HASH)
user = TelegramClient('user_session', API_ID, API_HASH)

waiting_for_code = False
waiting_for_password = False
phone_code_hash_global = None

# ==========================================
# دالة إرسال اللايك وانتظار النتيجة من القروب
# ==========================================
async def execute_like_and_fetch_result():
    if not await user.is_user_authorized():
        return "⚠️ الحساب الشخصي غير مسجل دخول حالياً!"
    
    # إرسال الأمر للقروب وحفظ بيانات الرسالة المرسلة
    sent_msg = await user.send_message(TARGET_CHAT, "/like me 11877711994")
    
    # الانتظار لمدة 15 ثانية كحد أقصى لالتقاط رد البوت في القروب
    for _ in range(15):
        await asyncio.sleep(1)
        # جلب أحدث الرسائل في القروب التي أتت بعد رسالتنا
        messages = await user.get_messages(TARGET_CHAT, limit=6, min_id=sent_msg.id)
        for msg in messages:
            if msg.text and ("UID" in msg.text or "NickName" in msg.text or "Added" in msg.text):
                return f"📊 **نتيجة اللايك من القروب:**\n\n{msg.text}"
                
    return "✅ تم إرسال أمر اللايك للقروب، ولكن لم يرد بوت اللايكات خلال 15 ثانية."

# ==========================================
# تسجيل الدخول التفاعلي عبر البوت كـ Terminal
# ==========================================
async def interactive_login():
    global waiting_for_code, waiting_for_password, phone_code_hash_global
    await user.connect()
    
    if await user.is_user_authorized():
        print("حسابك الشخصي مسجل دخول بالفعل وجاهز!")
        if MY_TELEGRAM_ID:
            await bot.send_message(MY_TELEGRAM_ID, "✅ الحساب الشخصي متصل ومسجل دخول بنجاح تام!")
        return

    try:
        sent = await user.send_code_request(PHONE_NUMBER)
        phone_code_hash_global = sent.phone_code_hash
        waiting_for_code = True
        if MY_TELEGRAM_ID:
            await bot.send_message(
                MY_TELEGRAM_ID, 
                "🔑 **طلب تسجيل دخول جديد!**\nأرسل لي الآن **كود التحقق** الذي وصلك على تيليجرام:"
            )
    except Exception as e:
        if MY_TELEGRAM_ID:
            await bot.send_message(MY_TELEGRAM_ID, f"❌ حدث خطأ أثناء طلب الكود: {e}")

# استقبال الأوامر والأكواد من محادثتك مع البوت
@bot.on(events.NewMessage(from_users=MY_TELEGRAM_ID, incoming=True))
async def handle_terminal_input(event):
    global waiting_for_code, waiting_for_password, phone_code_hash_global
    text = event.raw_text.strip()

    if waiting_for_code:
        waiting_for_code = False
        try:
            await user.sign_in(PHONE_NUMBER, text, phone_code_hash=phone_code_hash_global)
            await event.respond("✅ تم تسجيل الدخول بحسابك الشخصي بنجاح تام!")
        except SessionPasswordNeededError:
            waiting_for_password = True
            await event.respond("🔒 الحساب محمي بكلمة سر (التحقق بخطوتين).\nأرسل **كلمة السر** الآن:")
        except Exception as e:
            waiting_for_code = True
            await event.respond(f"❌ الكود غير صحيح أو منتهي. حاول مجدداً:\n{e}")
        return

    if waiting_for_password:
        waiting_for_password = False
        try:
            await user.sign_in(password=text)
            await event.respond("✅ تم إدخال كلمة السر وتسجيل الدخول بنجاح تام!")
        except Exception as e:
            waiting_for_password = True
            await event.respond(f"❌ كلمة السر خطأ. أعد إرسالها:\n{e}")
        return

    if text == "/mahdi":
        menu_text = (
            "👑 **لوحة تحكم ترمينال مهدي:**\n\n"
            "▫️ `/like` - إرسال أمر اللايك وجلب النتيجة فوراً.\n"
            "▫️ `/status` - التحقق من حالة الاتصال.\n"
            "▫️ `/login` - إعادة طلب كود تسجيل الدخول.\n"
            "▫️ `/mahdi` - إظهار هذه القائمة."
        )
        await event.respond(menu_text)
    
    elif text == "/like":
        wait_msg = await event.respond("⏳ جاري إرسال أمر اللايك وانتظار النتيجة من القروب...")
        try:
            result_text = await execute_like_and_fetch_result()
            await wait_msg.edit(result_text)
        except Exception as e:
            await wait_msg.edit(f"❌ حدث خطأ أثناء العملية: {e}")
            
    elif text == "/status":
        auth = "متصل ✅" if await user.is_user_authorized() else "غير مسجل دخول ❌ (أرسل /login)"
        await event.respond(f"ℹ️ حالة الحساب الشخصي: {auth}")
        
    elif text == "/login":
        await event.respond("🔄 جاري طلب كود تسجيل الدخول...")
        await interactive_login()

# ==========================================
# الرد التلقائي على الخاص (AFK)
# ==========================================
@user.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    if event.sender_id == MY_TELEGRAM_ID or event.out:
        return
    reply_text = "أهلاً يا حلو 🤍\nأنا الحين ماني متصل، اترك رسالتك وإن شاء الله برد عليك ياقلبي 🫀"
    try:
        if STICKER_ID:
            await event.respond(reply_text, file=STICKER_ID)
        else:
            await event.respond(reply_text)
    except Exception as e:
        print(f"خطأ في الرد التلقائي: {e}")

# ==========================================
# الجدولة اليومية الساعة 5:00 فجراً
# ==========================================
async def daily_task():
    await asyncio.sleep(20)
    print("بدء مراقبة الموعد اليومي لإرسال اللايك...")
    while True:
        local_now = datetime.now(timezone(timedelta(hours=3)))
        if local_now.hour == 5 and local_now.minute == 0:
            try:
                result_text = await execute_like_and_fetch_result()
                if MY_TELEGRAM_ID:
                    await bot.send_message(MY_TELEGRAM_ID, f"🔔 **تقرير اللايك اليومي (5:00 فجراً):**\n\n{result_text}")
                await asyncio.sleep(61)
            except Exception as e:
                print(f"خطأ في التنفيذ التلقائي: {e}")
                if MY_TELEGRAM_ID:
                    await bot.send_message(MY_TELEGRAM_ID, f"⚠️ خطأ في تنفيذ أمر الساعة 5:00: {e}")
        await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    await bot.start(bot_token=BOT_TOKEN)
    print("تم تشغيل البوت الوسيط بنجاح!")
    asyncio.create_task(interactive_login())
    asyncio.create_task(daily_task())
