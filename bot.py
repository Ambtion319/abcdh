from telethon import TelegramClient, events
import asyncio

api_id = 21339876  # استبدل بـ API ID الخاص بك
api_hash = '5dcddba0ec86b0c9a71785401d9bb605'  # استبدل بـ API Hash الخاص بك

client = TelegramClient('user_session', api_id, api_hash)

@client.on(events.NewMessage)
async def handle_message(event):
    if 'https://t.me/c/' in event.raw_text:
        try:
            await event.reply("جارٍ تحميل الملف...")

            link = event.raw_text
            parts = link.split('/')
            channel_id = int(parts[-2])  # معرف القناة
            message_id = int(parts[-1])  # رقم الرسالة

            if channel_id > 0:
                channel_id = int(f"-100{channel_id}")

            message = await client.get_messages(entity=channel_id, ids=message_id)

            if message.media:
                # إرسال الملف مباشرة إلى المستخدم دون تحميله محليًا
                await client.send_file(event.chat_id, message.media, caption="ها هو الملف الذي طلبته!")
            else:
                await event.reply("الرسالة لا تحتوي على ملف.")

        except Exception as e:
            await event.reply(f"حدث خطأ: {e}")

async def main():
    await client.start(phone='+201203482344')  # استبدل برقم هاتفك الفعلي
    print("Bot is running...")
    await client.run_until_disconnected()

asyncio.run(main())
