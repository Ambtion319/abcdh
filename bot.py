from telethon import TelegramClient, events
import asyncio
import os

# استبدل هذه القيم بـ API ID و API Hash الخاص بك
api_id = 21339876
api_hash = '5dcddba0ec86b0c9a71785401d9bb605'

# إنشاء العميل باستخدام حساب مستخدم
client = TelegramClient('user_session', api_id, api_hash)

# دالة لتتبع تقدم التحميل
async def track_progress(current, total, event, progress_message, link):
    percentage = (current / total) * 100
    await client.edit_message(progress_message, f"جارٍ تحميل الملف من الرابط: {link}\nالنسبة: {percentage:.2f}%")

# حدث عند استقبال رسالة
@client.on(events.NewMessage)
async def handle_message(event):
    # التحقق من أن الرسالة تحتوي على روابط
    if 'https://t.me/c/' in event.raw_text:
        try:
            # إرسال رسالة تفيد بأنه يتم تحميل الملفات
            progress_message = await event.reply("جارٍ تحميل الملفات...")

            # فصل الروابط عن بعضها (يدعم الروابط في سطر واحد أو عدة أسطر)
            links = [link.strip() for link in event.raw_text.split() if 'https://t.me/c/' in link]

            success_count = 0  # عدد الملفات التي تم تحميلها بنجاح

            # معالجة كل رابط على حدة
            for link in links:
                try:
                    # استخراج معرف القناة ورقم الرسالة من الرابط
                    parts = link.split('/')
                    channel_id = int(parts[-2])  # معرف القناة
                    message_ids = parts[-1].split('-')  # أرقام الرسائل

                    # تحويل معرف القناة إلى صيغة صحيحة
                    if channel_id > 0:  # إذا كان المعرف موجبًا، أضف -100
                        channel_id = int(f"-100{channel_id}")

                    # إذا كان الرابط يحتوي على نطاق رسائل (مثل firstmsgid-lastmsgid)
                    if len(message_ids) == 2:
                        first_msg_id = int(message_ids[0])
                        last_msg_id = int(message_ids[1])

                        # جلب جميع الرسائل في النطاق
                        messages = await client.get_messages(entity=channel_id, ids=range(first_msg_id, last_msg_id + 1))

                        # تحميل الملفات من كل رسالة
                        for message in messages:
                            if message.media:
                                file = await message.download_media(
                                    progress_callback=lambda current, total: track_progress(current, total, event, progress_message, link)
                                )
                                await client.send_file(event.chat_id, file, caption=f"تم تحميل الملف من الرابط: {link}")
                                success_count += 1
                                os.remove(file)  # حذف الملف المؤقت
                            else:
                                await event.reply(f"الرسالة من الرابط {link} لا تحتوي على ملف.")
                    else:
                        # إذا كان الرابط يحتوي على رسالة واحدة فقط
                        message_id = int(message_ids[0])
                        message = await client.get_messages(entity=channel_id, ids=message_id)

                        # تحميل الملف إذا كان موجودًا
                        if message.media:
                            file = await message.download_media(
                                progress_callback=lambda current, total: track_progress(current, total, event, progress_message, link)
                            )
                            await client.send_file(event.chat_id, file, caption=f"تم تحميل الملف من الرابط: {link}")
                            success_count += 1
                            os.remove(file)  # حذف الملف المؤقت
                        else:
                            await event.reply(f"الرسالة من الرابط {link} لا تحتوي على ملف.")
                except Exception as e:
                    await event.reply(f"حدث خطأ أثناء جلب الرسالة: {e}")

            # إرسال ملخص بعد الانتهاء
            await client.edit_message(progress_message, f"تم تحميل {success_count} ملف(ات) بنجاح من أصل {len(links)}.")

        except Exception as e:
            await event.reply(f"حدث خطأ: {e}")

# تسجيل الدخول باستخدام رقم الهاتف
async def main():
    await client.start(phone='+201203482344')
    print("Bot is running...")
    await client.run_until_disconnected()

# تشغيل العميل
asyncio.run(main())
