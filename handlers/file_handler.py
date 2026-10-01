import uuid
import html
import asyncio
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from config import MAX_DOWNLOAD_SIZE_BYTES
from utils.helpers import format_size, detect_file_category, is_url_text, extract_first_url
from utils.keyboards import get_conversion_keyboard
from utils.task_store import task_store
from converters.media_downloader import get_url_metadata

router = Router()

CATEGORY_TITLES = {
    "pdf": "📕 PDF Hujjati",
    "docx": "📝 Microsoft Word",
    "xlsx": "📑 Excel Jadvali",
    "csv": "📊 CSV Jadvali",
    "pptx": "📽 PowerPoint Taqdimoti",
    "image": "🖼 Rasm",
    "video": "🎬 Video",
    "video_note": "⚪ Dumaloq Video (Note)",
    "audio": "🎵 Audio / Musiqa",
    "voice": "🎙 Ovozli Xabar",
    "archive": "📦 Arxiv (ZIP/TAR)",
    "json": "💻 JSON Fayli",
    "yaml": "💻 YAML Fayli",
    "xml": "💻 XML Fayli",
    "text": "📄 Matn / Ma'lumot",
    "url": "🌐 Ijtimoiy tarmoq / Havola",
    "unknown": "📁 Noma'lum Fayl"
}

# 1. Handle Document
@router.message(F.document)
async def handle_document(message: Message):
    doc = message.document
    if doc.file_size and doc.file_size > MAX_DOWNLOAD_SIZE_BYTES:
        await message.reply(
            f"⚠️ <b>Fayl hajmi juda katta!</b>\n\n"
            f"Telegram botlari cheklovi sababli 20 MB dan katta fayllarni yuklab bo'lmaydi.\n"
            f"Sizning faylingiz hajmi: <b>{html.escape(format_size(doc.file_size))}</b>\n\n"
            f"Iltimos, 20 MB dan kichik fayl yuboring.",
            parse_mode=ParseMode.HTML
        )
        return

    cat = detect_file_category(doc.file_name or "file.bin", doc.mime_type or "")
    task_id = uuid.uuid4().hex[:8]
    
    file_name = doc.file_name or "fayl.bin"
    task_store.add_task(task_id, {
        "task_id": task_id,
        "file_id": doc.file_id,
        "file_name": file_name,
        "file_size": doc.file_size or 0,
        "category": cat,
        "mime_type": doc.mime_type,
        "user_id": message.from_user.id
    })

    cat_name = CATEGORY_TITLES.get(cat, "📁 Fayl")
    kb = get_conversion_keyboard(cat, task_id, original_ext=file_name)
    
    await message.reply(
        f"📁 <b>Fayl qabul qilindi!</b>\n\n"
        f"📄 <b>Nomi:</b> <code>{html.escape(file_name)}</code>\n"
        f"📊 <b>Hajmi:</b> <b>{html.escape(format_size(doc.file_size or 0))}</b>\n"
        f"📂 <b>Turi:</b> {html.escape(cat_name)}\n\n"
        f"👇 <i>Qaysi formatga aylantirmoqchisiz? Quyidagi variantlardan birini tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

# 2. Handle Photo
@router.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1] # Highest resolution
    if photo.file_size and photo.file_size > MAX_DOWNLOAD_SIZE_BYTES:
        await message.reply("⚠️ Rasm hajmi 20 MB dan katta!")
        return

    task_id = uuid.uuid4().hex[:8]
    task_store.add_task(task_id, {
        "task_id": task_id,
        "file_id": photo.file_id,
        "file_name": f"image_{task_id}.jpg",
        "file_size": photo.file_size or 0,
        "category": "image",
        "user_id": message.from_user.id
    })

    kb = get_conversion_keyboard("image", task_id, original_ext="jpg")
    await message.reply(
        f"🖼 <b>Rasm qabul qilindi!</b>\n\n"
        f"📊 <b>Hajmi:</b> <b>{html.escape(format_size(photo.file_size or 0))}</b>\n"
        f"📐 <b>O'lchami:</b> <code>{photo.width}x{photo.height}</code> px\n\n"
        f"👇 <i>Qaysi formatga aylantirmoqchisiz? Tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

# 3. Handle Video
@router.message(F.video)
async def handle_video(message: Message):
    video = message.video
    if video.file_size and video.file_size > MAX_DOWNLOAD_SIZE_BYTES:
        await message.reply(
            f"⚠️ <b>Video hajmi juda katta!</b> (<code>{html.escape(format_size(video.file_size))}</code>)\n"
            f"Telegram botlari uchun 20 MB cheklovi mavjud.",
            parse_mode=ParseMode.HTML
        )
        return

    task_id = uuid.uuid4().hex[:8]
    file_name = video.file_name or f"video_{task_id}.mp4"
    task_store.add_task(task_id, {
        "task_id": task_id,
        "file_id": video.file_id,
        "file_name": file_name,
        "file_size": video.file_size or 0,
        "category": "video",
        "duration": video.duration,
        "user_id": message.from_user.id
    })

    kb = get_conversion_keyboard("video", task_id, original_ext="mp4")
    await message.reply(
        f"🎬 <b>Video qabul qilindi!</b>\n\n"
        f"📄 <b>Nomi:</b> <code>{html.escape(file_name)}</code>\n"
        f"📊 <b>Hajmi:</b> <b>{html.escape(format_size(video.file_size or 0))}</b>\n"
        f"⏱ <b>Davomiyligi:</b> <code>{video.duration}</code> soniya\n\n"
        f"👇 <i>Qaysi formatga aylantirmoqchisiz? Tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

# 4. Handle Video Note (Circle video)
@router.message(F.video_note)
async def handle_video_note(message: Message):
    vn = message.video_note
    task_id = uuid.uuid4().hex[:8]
    task_store.add_task(task_id, {
        "task_id": task_id,
        "file_id": vn.file_id,
        "file_name": f"round_video_{task_id}.mp4",
        "file_size": vn.file_size or 0,
        "category": "video_note",
        "duration": vn.duration,
        "user_id": message.from_user.id
    })

    kb = get_conversion_keyboard("video_note", task_id, original_ext="mp4")
    await message.reply(
        f"⚪ <b>Dumaloq video qabul qilindi!</b>\n\n"
        f"📊 <b>Hajmi:</b> <b>{html.escape(format_size(vn.file_size or 0))}</b>\n"
        f"⏱ <b>Davomiyligi:</b> <code>{vn.duration}</code> soniya\n\n"
        f"👇 <i>Quyidagi variantlardan birini tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

# 5. Handle Audio
@router.message(F.audio)
async def handle_audio(message: Message):
    audio = message.audio
    if audio.file_size and audio.file_size > MAX_DOWNLOAD_SIZE_BYTES:
        await message.reply(
            f"⚠️ Audio hajmi 20 MB dan katta (<code>{html.escape(format_size(audio.file_size))}</code>)!",
            parse_mode=ParseMode.HTML
        )
        return

    task_id = uuid.uuid4().hex[:8]
    file_name = audio.file_name or f"audio_{task_id}.mp3"
    task_store.add_task(task_id, {
        "task_id": task_id,
        "file_id": audio.file_id,
        "file_name": file_name,
        "file_size": audio.file_size or 0,
        "category": "audio",
        "duration": audio.duration,
        "performer": audio.performer,
        "title": audio.title,
        "user_id": message.from_user.id
    })

    kb = get_conversion_keyboard("audio", task_id, original_ext="mp3")
    title_text = f"{audio.performer} - {audio.title}" if audio.performer and audio.title else file_name
    await message.reply(
        f"🎵 <b>Audio qabul qilindi!</b>\n\n"
        f"🎶 <b>Nomi:</b> <code>{html.escape(title_text)}</code>\n"
        f"📊 <b>Hajmi:</b> <b>{html.escape(format_size(audio.file_size or 0))}</b>\n"
        f"⏱ <b>Davomiyligi:</b> <code>{audio.duration}</code> soniya\n\n"
        f"👇 <i>Qaysi formatga aylantirmoqchisiz? Tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

# 6. Handle Voice Note
@router.message(F.voice)
async def handle_voice(message: Message):
    voice = message.voice
    task_id = uuid.uuid4().hex[:8]
    task_store.add_task(task_id, {
        "task_id": task_id,
        "file_id": voice.file_id,
        "file_name": f"voice_{task_id}.ogg",
        "file_size": voice.file_size or 0,
        "category": "voice",
        "duration": voice.duration,
        "user_id": message.from_user.id
    })

    kb = get_conversion_keyboard("voice", task_id, original_ext="ogg")
    await message.reply(
        f"🎙 <b>Ovozli xabar qabul qilindi!</b>\n\n"
        f"📊 <b>Hajmi:</b> <b>{html.escape(format_size(voice.file_size or 0))}</b>\n"
        f"⏱ <b>Davomiyligi:</b> <code>{voice.duration}</code> soniya\n\n"
        f"👇 <i>Qaysi formatga o'tkazmoqchisiz? Tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

# 7. Handle Sticker
@router.message(F.sticker)
async def handle_sticker(message: Message):
    sticker = message.sticker
    if sticker.is_animated or sticker.is_video:
        ext = "webm" if sticker.is_video else "tgs"
    else:
        ext = "webp"

    task_id = uuid.uuid4().hex[:8]
    task_store.add_task(task_id, {
        "task_id": task_id,
        "file_id": sticker.file_id,
        "file_name": f"sticker_{task_id}.{ext}",
        "file_size": sticker.file_size or 0,
        "category": "image",
        "is_sticker": True,
        "user_id": message.from_user.id
    })

    kb = get_conversion_keyboard("image", task_id, original_ext=ext)
    await message.reply(
        f"🎭 <b>Stiker qabul qilindi!</b>\n\n"
        f"Emoji: {html.escape(sticker.emoji or '⭐️')}\n"
        f"Hajmi: <b>{html.escape(format_size(sticker.file_size or 0))}</b>\n\n"
        f"👇 <i>Qaysi formatga aylantirmoqchisiz? Tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )

# 8. Handle Raw Text or URL (non-command)
@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
    if message.text in ["ℹ️ Bot haqida", "📋 Qo'llab-quvvatlanadigan formatlar", "💡 Yordam", "⚡ Tezkor QR-kod"]:
        return

    text = message.text.strip()
    if not text:
        return

    # Check if message contains a social media or web URL
    if is_url_text(text):
        url = extract_first_url(text)
        wait_msg = await message.reply("🔍 <b>Havola tekshirilmoqda...</b>", parse_mode=ParseMode.HTML)
        try:
            meta = await asyncio.to_thread(get_url_metadata, url)
            task_id = uuid.uuid4().hex[:8]
            task_store.add_task(task_id, {
                "task_id": task_id,
                "url": url,
                "platform": meta["platform"],
                "icon": meta["icon"],
                "title": meta["title"],
                "is_direct_file": meta.get("is_direct_file", False),
                "direct_ext": meta.get("direct_ext", ""),
                "category": "url",
                "user_id": message.from_user.id
            })

            kb = get_conversion_keyboard("url", task_id)
            duration_info = ""
            if meta.get("duration"):
                m, s = divmod(int(meta["duration"]), 60)
                duration_info = f"\n⏱ <b>Davomiyligi:</b> <code>{m:02d}:{s:02d}</code>"

            await wait_msg.edit_text(
                f"{meta['icon']} <b>{meta['platform']} havolasi qabul qilindi!</b>\n\n"
                f"🏷 <b>Nomi:</b> <code>{html.escape(meta['title'])}</code>{duration_info}\n\n"
                f"👇 <i>Qaysi formatga aylantirmoqchisiz? Quyidagi variantlardan birini tanlang:</i>",
                reply_markup=kb,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await wait_msg.edit_text(
                f"⚠️ <b>Havolani tekshirishda xatolik:</b>\n<code>{html.escape(str(e)[:150])}</code>",
                parse_mode=ParseMode.HTML
            )
        return

    # Normal text conversion
    task_id = uuid.uuid4().hex[:8]
    task_store.add_task(task_id, {
        "task_id": task_id,
        "raw_text": text,
        "file_name": "matn.txt",
        "file_size": len(text.encode("utf-8")),
        "category": "text",
        "user_id": message.from_user.id
    })

    kb = get_conversion_keyboard("text", task_id)
    preview = (text[:100] + "...") if len(text) > 100 else text
    await message.reply(
        f"📝 <b>Matn qabul qilindi!</b>\n\n"
        f"💬 <i>«{html.escape(preview)}»</i>\n"
        f"📊 Belgilar soni: <code>{len(text)} ta</code>\n\n"
        f"👇 <i>Qaysi formatga aylantirmoqchisiz? Tanlang:</i>",
        reply_markup=kb,
        parse_mode=ParseMode.HTML
    )
