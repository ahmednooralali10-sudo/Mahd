import os
import asyncio
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from fastapi import FastAPI

# قراءة المتغيرات من إعدادات Render البيئية
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TARGET_CHAT = os.environ.get("TARGET_CHAT", "")
MY_TELEGRAM_ID = int(os.environ.get("MY_TELEGRAM_ID", 0))
STICKER_ID = os.environ.get("STICKER_ID", "")

# ضبط معرف القروب إن كان رقماً
if TARGET_CHAT and TARGET_CHAT.lstrip("-").isdigit():
    TARGET_CHAT = int(TARGET_CHAT)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "XxMAHDI.py Telegram Advanced Userbot is running!"}

# تهيئة البوت الوسيط واليوزر بوت
bot_client = TelegramClient('bot_session', API_ID, API_HASH)
user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==========================================
# قائمة الأوامر الشاملة (عند إرسال /mahdi)
# ==========================================
@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/mahdi$'))
async def mahdi_menu(event):
    menu_text = (
        "👑 **قائمة أوامر يوزر بوت XxMAHDI.py الشاملة:**\n\n"
        "⚡ **أوامر التشغيل واللايك:**\n"
        "▫️ `/like` - إرسال أمر اللايك اليدوي (`/like me 11877711994`).\n"
        "▫️ `/ping` - فحص سرعة وبنغ السيرفر.\n"
        "▫️ `/speed` - فحص سرعة استجابة التيليجرام.\n\n"
        "💤 **أوامر الرد التلقائي (AFK):**\n"
        "▫️ `/afk_on` - تفعيل الرد التلقائي للملصق والرسالة.\n"
        "▫️ `/afk_off` - إيقاف الرد التلقائي مؤقتاً.\n"
        "▫️ `/afk_status` - معرفة حالة الرد التلقائي الحالية.\n\n"
        "🛠 **أوامر الأدوات والمساعدة:**\n"
        "▫️ `/id` - جلب آيدي الشخص أو القروب مع تفاصيل الحساب.\n"
        "▫️ `/info` - عرض معلومات حسابك الشخصي.\n"
        "▫️ `/time` - معرفة الوقت والتاريخ الحالي بتوقيت السيرفر.\n"
        "▫️ `/calc [عملية]` - حساب عمليات رياضية (مثال: `/calc 50*2`).\n\n"
        "🌀 **أوامر الترفيه والتحكم:**\n"
        "▫️ `/spam [عدد] [نص]` - إرسال رسالة عدة مرات للتجربة.\n"
        "▫️ `/restart` - إعادة تشغيل السيرفر البرمجي.\n"
        "▫️ `/mahdi` - إظهار هذه القائمة المحدثة."
    )
    await event.edit(menu_text)

# ==========================================
# تنفيذ الأوامر الجديدة
# ==========================================

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/ping$'))
async def ping_cmd(event):
    await event.edit("🏓 **Pong!**\n⚡ السيرفر يعمل بكفاءة تامة على Render بدون أي تأخير.")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/speed$'))
async def speed_cmd(event):
    start = datetime.now()
    tx = await event.edit("⏳ جاري قياس السرعة...")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await tx.edit(f"🚀 **سرعة الاستجابة:** `{ms}ms`")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/like$'))
async def manual_like(event):
    try:
        await user_client.send_message(TARGET_CHAT, "/like me 11877711994")
        await event.edit("✅ تم إرسال أمر اللايك يدوياً للقروب بنجاح!")
    except Exception as e:
        await event.edit(f"❌ حدث خطأ: {e}")

# إدارة الرد التلقائي (AFK)
AFK_MODE = True

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/afk_off$'))
async def afk_off(event):
    global AFK_MODE
    AFK_MODE = False
    await event.edit("🔕 **تم إيقاف الرد التلقائي (AFK).**")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/afk_on$'))
async def afk_on(event):
    global AFK_MODE
    AFK_MODE = True
    await event.edit("🔔 **تم تفعيل الرد التلقائي (AFK) بنجاح.**")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/afk_status$'))
async def afk_status(event):
    status = "مفعل ✅" if AFK_MODE else "معطل ❌"
    await event.edit(f"ℹ️ حالة الرد التلقائي حالياً: **{status}**")

# جلب الآيدي والمعلومات
@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/id$'))
async def get_id(event):
    replied = await event.get_reply_message()
    if replied:
        user = await replied.get_sender()
        await event.edit(f"👤 **معلومات المستخدم:**\n- الآيدي: `{user.id}`\n- الاسم: `{user.first_name}`\n- المعرف: `@{user.username}`")
    else:
        chat = await event.get_chat()
        await event.edit(f"📍 **معلومات المحادثة/القروب:**\n- الآيدي: `{chat.id}`\n- الاسم: `{chat.title if hasattr(chat, 'title') else chat.first_name}`")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/info$'))
async def get_my_info(event):
    me = await user_client.get_me()
    await event.edit(f"👑 **معلومات حسابك يا مهدي:**\n- الآيدي: `{me.id}`\n- الاسم: `{me.first_name}`\n- المعرف: `@{me.username}`\n- الهاتف: `{me.phone}`")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/time$'))
async def show_time(event):
    now_utc3 = datetime.now(timezone(timedelta(hours=3)))
    current_time = now_utc3.strftime("%Y-%m-%d | %I:%M:%S %p")
    await event.edit(f"⏰ **التوقيت الحالي (توقيت مكة):**\n`{current_time}`")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/calc (.+)$'))
async def calculator(event):
    expr = event.pattern_match.group(1)
    try:
        # حساب أمن للعمليات البسيطة
        result = eval(expr, {"__builtins__": {}}, {})
        await event.edit(f"🧮 **النتيجة:**\n`{expr} = {result}`")
    except Exception:
        await event.edit("❌ خطأ في عملية الحساب، تأكد من كتابة الأرقام بشكل صحيح.")

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/spam (\d+) (.+)$'))
async def spam_msg(event):
    count = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    if count > 10:
        count = 10 # حماية لتجنب الحظر
    await event.delete()
    for _ in range(count):
        await event.respond(text)
        await asyncio.sleep(0.3)

@user_client.on(events.NewMessage(outgoing=True, pattern=r'^/restart$'))
async def restart_bot(event):
    await event.edit("🔄 جاري إعادة تشغيل السيرفر...")
    os._exit(0) # راندر سيقوم بإعادة تشغيل السيرفر تلقائياً


# ==========================================
# الرد التلقائي على الخاص (مع الملصق والرسالة)
# ==========================================
@user_client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply_handler(event):
    global AFK_MODE
    if not AFK_MODE:
        return
    
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
# مهمة الجدولة اليومية الدقيقة (الساعة 5:00 فجراً)
# ==========================================
async def daily_task():
    await asyncio.sleep(15)
    print("بدء نظام المراقبة الزمنية لإرسال أمر اللايك يومياً الساعة 5:00 فجراً...")
    
    while True:
        local_now = datetime.now(timezone(timedelta(hours=3)))
        
        if local_now.hour == 5 and local_now.minute == 0:
            try:
                message = "/like me 11877711994"
                await user_client.send_message(TARGET_CHAT, message)
                print(f"تم إرسال أمر اللايك تلقائياً بنجاح الساعة 5:00 فجراً: {message}")
                
                if MY_TELEGRAM_ID:
                    await bot_client.send_message(MY_TELEGRAM_ID, "🔔 تم تنفيذ أمر اللايك تلقائياً في القروب بنجاح (الساعة 5:00 فجراً).")
                
                await asyncio.sleep(61)
            except Exception as e:
                print(f"خطأ في التنفيذ التلقائي: {e}")
                if MY_TELEGRAM_ID:
                    await bot_client.send_message(MY_TELEGRAM_ID, f"⚠️ خطأ في تنفيذ أمر الساعة 5:00: {e}")
        
        await asyncio.sleep(30)

async def start_services():
    await bot_client.start(bot_token=BOT_TOKEN)
    await user_client.start()
    print("تم تشغيل اليوزر بوت والبوت الوسيط بنجاح مع الأوامر الجديدة!")
    asyncio.create_task(daily_task())

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_services())
