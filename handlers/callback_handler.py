import os
import html
import asyncio
import traceback
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, FSInputFile
from config import TEMP_DIR
from utils.helpers import get_temp_path, get_temp_dir, safe_remove, format_size
from utils.task_store import task_store
from converters import (
    pdf_to_docx, pdf_to_images, pdf_to_txt, pdf_to_html, pdf_compress, pdf_to_xlsx,
    docx_to_pdf, docx_to_txt, docx_to_html, docx_to_images, docx_to_speech,
    xlsx_to_pdf, xlsx_to_csv, xlsx_to_json, xlsx_to_html,
    csv_to_xlsx, csv_to_pdf, csv_to_json, csv_to_html,
    pptx_to_pdf, pptx_to_txt, pptx_to_images,
    convert_image_format, convert_to_telegram_sticker,
    convert_to_grayscale, invert_image_colors, compress_image,
    scan_qr_code, ocr_extract_text,
    convert_audio, audio_to_voice_note, change_audio_speed, boost_audio_volume,
    video_to_mp3, video_to_voice, video_to_gif, video_to_round_note,
    compress_video, convert_video_format, mute_video, change_video_speed,
    text_to_pdf, text_to_docx, text_to_speech, text_to_qr,
    json_to_csv, json_to_yaml, yaml_to_json,
    extract_archive, create_zip_archive,
    download_social_media
)

router = Router()

@router.callback_query(F.data.startswith("cancel:"))
async def cb_cancel(callback: CallbackQuery):
    task_id = callback.data.split(":")[1]
    task_store.remove_task(task_id)
    try:
        await callback.message.edit_text("❌ <b>Amal bekor qilindi.</b>", parse_mode=ParseMode.HTML)
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data.startswith("c:"))
async def cb_convert(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Noto'g'ri so'rov.", show_alert=True)
        return
        
    task_id = parts[1]
    target = parts[2]
    
    task = task_store.get_task(task_id)
    if not task:
        await callback.answer("⚠️ Ushbu fayl muddati tugagan. Iltimos, qaytadan yuboring.", show_alert=True)
        try:
            await callback.message.edit_text("⚠️ <b>Amal muddati tugagan.</b> Iltimos, qaytadan yuboring.", parse_mode=ParseMode.HTML)
        except Exception:
            pass
        return

    await callback.answer()
    progress_msg = await callback.message.edit_text(
        "⏳ <b>Yuklab olinmoqda va aylantirilmoqda...</b>\n<i>Iltimos, biroz kuting...</i>",
        parse_mode=ParseMode.HTML
    )

    clean_paths = []
    try:
        category = task.get("category", "")
        file_name = task.get("file_name", "file")
        base_stem = Path(file_name).stem
        
        out_path = None
        text_result = None
        target_ext = ""
        send_type = "document"
        custom_display_name = ""

        # --- A. SPECIAL CATEGORY: SOCIAL MEDIA / WEB URL ---
        if category == "url":
            url = task["url"]
            out_dir = str(get_temp_dir("url_media"))
            clean_paths.append(out_dir)
            
            sub_target = target.replace("url_", "")
            out_path, send_type, custom_display_name = await asyncio.to_thread(
                download_social_media, url, sub_target, out_dir
            )
            base_stem = Path(custom_display_name).stem
            target_ext = Path(custom_display_name).suffix.lstrip(".")

        # --- B. STANDARD FILE & TEXT CONVERSIONS ---
        else:
            # 1. Download file or write text
            if "raw_text" in task:
                in_path = str(get_temp_path("raw_text", ".txt"))
                with open(in_path, "w", encoding="utf-8") as f:
                    f.write(task["raw_text"])
                clean_paths.append(in_path)
            else:
                ext = Path(file_name).suffix or ".bin"
                in_path = str(get_temp_path("input", ext))
                clean_paths.append(in_path)
                file_obj = await bot.get_file(task["file_id"])
                await bot.download_file(file_obj.file_path, destination=in_path)

            # 2. Category logic
            if category == "pdf":
                if target == "docx":
                    target_ext = "docx"
                    out_path = str(get_temp_path(f"{base_stem}", ".docx"))
                    await asyncio.to_thread(pdf_to_docx, in_path, out_path)
                elif target == "xlsx":
                    target_ext = "xlsx"
                    out_path = str(get_temp_path(f"{base_stem}", ".xlsx"))
                    await asyncio.to_thread(pdf_to_xlsx, in_path, out_path)
                elif target == "images":
                    target_ext = "zip"
                    out_dir = str(get_temp_dir("pdf_imgs"))
                    clean_paths.append(out_dir)
                    out_path = await asyncio.to_thread(pdf_to_images, in_path, out_dir, "png")
                    if out_path.endswith(".png"):
                        target_ext = "png"
                elif target == "txt":
                    target_ext = "txt"
                    out_path = str(get_temp_path(f"{base_stem}", ".txt"))
                    await asyncio.to_thread(pdf_to_txt, in_path, out_path)
                elif target == "html":
                    target_ext = "html"
                    out_path = str(get_temp_path(f"{base_stem}", ".html"))
                    await asyncio.to_thread(pdf_to_html, in_path, out_path)
                elif target == "compress_pdf":
                    target_ext = "pdf"
                    out_path = str(get_temp_path(f"{base_stem}_compressed", ".pdf"))
                    await asyncio.to_thread(pdf_compress, in_path, out_path)

            elif category == "docx":
                if target == "pdf":
                    target_ext = "pdf"
                    out_path = str(get_temp_path(f"{base_stem}", ".pdf"))
                    await asyncio.to_thread(docx_to_pdf, in_path, out_path)
                elif target == "txt":
                    target_ext = "txt"
                    out_path = str(get_temp_path(f"{base_stem}", ".txt"))
                    await asyncio.to_thread(docx_to_txt, in_path, out_path)
                elif target == "tts":
                    target_ext = "mp3"
                    out_path = str(get_temp_path(f"{base_stem}_audio", ".mp3"))
                    await asyncio.to_thread(docx_to_speech, in_path, out_path)
                    send_type = "audio"
                elif target == "html":
                    target_ext = "html"
                    out_path = str(get_temp_path(f"{base_stem}", ".html"))
                    await asyncio.to_thread(docx_to_html, in_path, out_path)
                elif target == "images":
                    target_ext = "zip"
                    out_dir = str(get_temp_dir("docx_imgs"))
                    clean_paths.append(out_dir)
                    out_path = await asyncio.to_thread(docx_to_images, in_path, out_dir)
                    if out_path.endswith(".png"):
                        target_ext = "png"

            elif category == "image":
                if target == "ocr":
                    text_result = await asyncio.to_thread(ocr_extract_text, in_path)
                elif target == "qrscan":
                    text_result = await asyncio.to_thread(scan_qr_code, in_path)
                elif target == "sticker":
                    target_ext = "webp"
                    out_path = str(get_temp_path(f"{base_stem}_sticker", ".webp"))
                    await asyncio.to_thread(convert_to_telegram_sticker, in_path, out_path)
                    send_type = "sticker"
                elif target == "gray":
                    target_ext = "png"
                    out_path = str(get_temp_path(f"{base_stem}_gray", ".png"))
                    await asyncio.to_thread(convert_to_grayscale, in_path, out_path)
                    send_type = "photo"
                elif target == "compress_img":
                    target_ext = "jpg"
                    out_path = str(get_temp_path(f"{base_stem}_compressed", ".jpg"))
                    await asyncio.to_thread(compress_image, in_path, out_path)
                    send_type = "photo"
                elif target in ["png", "jpg", "webp", "bmp", "ico", "pdf", "tiff"]:
                    target_ext = target
                    out_path = str(get_temp_path(f"{base_stem}", f".{target}"))
                    await asyncio.to_thread(convert_image_format, in_path, out_path, target)
                    if target in ["png", "jpg", "webp"]:
                        send_type = "photo"
                    else:
                        send_type = "document"

            elif category in ["video", "video_note"]:
                if target == "mp3":
                    target_ext = "mp3"
                    out_path = str(get_temp_path(f"{base_stem}", ".mp3"))
                    await asyncio.to_thread(video_to_mp3, in_path, out_path)
                    send_type = "audio"
                elif target == "voice":
                    target_ext = "ogg"
                    out_path = str(get_temp_path(f"{base_stem}", ".ogg"))
                    await asyncio.to_thread(video_to_voice, in_path, out_path)
                    send_type = "voice"
                elif target == "gif":
                    target_ext = "gif"
                    out_path = str(get_temp_path(f"{base_stem}", ".gif"))
                    await asyncio.to_thread(video_to_gif, in_path, out_path)
                    send_type = "animation"
                elif target == "note":
                    target_ext = "mp4"
                    out_path = str(get_temp_path(f"{base_stem}_note", ".mp4"))
                    await asyncio.to_thread(video_to_round_note, in_path, out_path)
                    send_type = "video_note"
                elif target == "compress_vid":
                    target_ext = "mp4"
                    out_path = str(get_temp_path(f"{base_stem}_compressed", ".mp4"))
                    await asyncio.to_thread(compress_video, in_path, out_path)
                    send_type = "video"
                elif target == "mute":
                    target_ext = "mp4"
                    out_path = str(get_temp_path(f"{base_stem}_muted", ".mp4"))
                    await asyncio.to_thread(mute_video, in_path, out_path)
                    send_type = "video"
                elif target == "vspeed_125":
                    target_ext = "mp4"
                    out_path = str(get_temp_path(f"{base_stem}_1.25x", ".mp4"))
                    await asyncio.to_thread(change_video_speed, in_path, out_path, 1.25)
                    send_type = "video"
                elif target in ["mp4", "mkv", "avi", "mov", "webm"]:
                    target_ext = target
                    out_path = str(get_temp_path(f"{base_stem}_conv", f".{target}"))
                    await asyncio.to_thread(convert_video_format, in_path, out_path, target)
                    send_type = "video"

            elif category in ["audio", "voice"]:
                if target == "voice":
                    target_ext = "ogg"
                    out_path = str(get_temp_path(f"{base_stem}", ".ogg"))
                    await asyncio.to_thread(audio_to_voice_note, in_path, out_path)
                    send_type = "voice"
                elif target == "speed_125":
                    ext_a = Path(file_name).suffix or ".mp3"
                    target_ext = ext_a.lstrip(".")
                    out_path = str(get_temp_path(f"{base_stem}_1.25x", ext_a))
                    await asyncio.to_thread(change_audio_speed, in_path, out_path, 1.25)
                    send_type = "audio" if category == "audio" else "voice"
                elif target == "speed_150":
                    ext_a = Path(file_name).suffix or ".mp3"
                    target_ext = ext_a.lstrip(".")
                    out_path = str(get_temp_path(f"{base_stem}_1.5x", ext_a))
                    await asyncio.to_thread(change_audio_speed, in_path, out_path, 1.50)
                    send_type = "audio" if category == "audio" else "voice"
                elif target == "boost":
                    ext_a = Path(file_name).suffix or ".mp3"
                    target_ext = ext_a.lstrip(".")
                    out_path = str(get_temp_path(f"{base_stem}_boosted", ext_a))
                    await asyncio.to_thread(boost_audio_volume, in_path, out_path, 1.5)
                    send_type = "audio"
                elif target in ["mp3", "wav", "m4a", "flac"]:
                    target_ext = target
                    out_path = str(get_temp_path(f"{base_stem}", f".{target}"))
                    await asyncio.to_thread(convert_audio, in_path, out_path, target)
                    send_type = "audio"

            elif category == "xlsx":
                if target == "pdf":
                    target_ext = "pdf"
                    out_path = str(get_temp_path(f"{base_stem}", ".pdf"))
                    await asyncio.to_thread(xlsx_to_pdf, in_path, out_path)
                elif target == "csv":
                    target_ext = "csv"
                    out_path = str(get_temp_path(f"{base_stem}", ".csv"))
                    await asyncio.to_thread(xlsx_to_csv, in_path, out_path)
                elif target == "json":
                    target_ext = "json"
                    out_path = str(get_temp_path(f"{base_stem}", ".json"))
                    await asyncio.to_thread(xlsx_to_json, in_path, out_path)
                elif target == "html":
                    target_ext = "html"
                    out_path = str(get_temp_path(f"{base_stem}", ".html"))
                    await asyncio.to_thread(xlsx_to_html, in_path, out_path)

            elif category == "csv":
                if target == "xlsx":
                    target_ext = "xlsx"
                    out_path = str(get_temp_path(f"{base_stem}", ".xlsx"))
                    await asyncio.to_thread(csv_to_xlsx, in_path, out_path)
                elif target == "pdf":
                    target_ext = "pdf"
                    out_path = str(get_temp_path(f"{base_stem}", ".pdf"))
                    await asyncio.to_thread(csv_to_pdf, in_path, out_path)
                elif target == "json":
                    target_ext = "json"
                    out_path = str(get_temp_path(f"{base_stem}", ".json"))
                    await asyncio.to_thread(csv_to_json, in_path, out_path)
                elif target == "html":
                    target_ext = "html"
                    out_path = str(get_temp_path(f"{base_stem}", ".html"))
                    await asyncio.to_thread(csv_to_html, in_path, out_path)

            elif category == "pptx":
                if target == "pdf":
                    target_ext = "pdf"
                    out_path = str(get_temp_path(f"{base_stem}", ".pdf"))
                    await asyncio.to_thread(pptx_to_pdf, in_path, out_path)
                elif target == "images":
                    target_ext = "zip"
                    out_dir = str(get_temp_dir("pptx_imgs"))
                    clean_paths.append(out_dir)
                    out_path = await asyncio.to_thread(pptx_to_images, in_path, out_dir)
                elif target == "txt":
                    target_ext = "txt"
                    out_path = str(get_temp_path(f"{base_stem}", ".txt"))
                    await asyncio.to_thread(pptx_to_txt, in_path, out_path)

            elif category == "archive":
                if target == "extract":
                    out_dir = str(get_temp_dir("extracted"))
                    clean_paths.append(out_dir)
                    files, summary = await asyncio.to_thread(extract_archive, in_path, out_dir)
                    if len(files) == 1:
                        out_path = files[0]
                        target_ext = Path(out_path).suffix.lstrip(".")
                    elif len(files) > 1:
                        target_ext = "zip"
                        out_path = str(get_temp_path(f"{base_stem}_extracted", ".zip"))
                        await asyncio.to_thread(create_zip_archive, files, out_path)
                    else:
                        text_result = "⚠️ Arxiv ichida fayllar topilmadi."

            elif category in ["json", "yaml", "xml"]:
                if target == "csv":
                    target_ext = "csv"
                    out_path = str(get_temp_path(f"{base_stem}", ".csv"))
                    await asyncio.to_thread(json_to_csv, in_path, out_path)
                elif target == "yaml":
                    target_ext = "yaml"
                    out_path = str(get_temp_path(f"{base_stem}", ".yaml"))
                    await asyncio.to_thread(json_to_yaml, in_path, out_path)
                elif target == "json":
                    target_ext = "json"
                    out_path = str(get_temp_path(f"{base_stem}", ".json"))
                    await asyncio.to_thread(yaml_to_json, in_path, out_path)
                elif target == "txt":
                    target_ext = "txt"
                    out_path = in_path

            elif category == "text":
                raw_text = task.get("raw_text", "")
                if target == "pdf":
                    target_ext = "pdf"
                    out_path = str(get_temp_path(f"hujjat_{task_id}", ".pdf"))
                    await asyncio.to_thread(text_to_pdf, raw_text, out_path)
                elif target == "docx":
                    target_ext = "docx"
                    out_path = str(get_temp_path(f"hujjat_{task_id}", ".docx"))
                    await asyncio.to_thread(text_to_docx, raw_text, out_path)
                elif target == "tts":
                    target_ext = "mp3"
                    out_path = str(get_temp_path(f"ovoz_{task_id}", ".mp3"))
                    await asyncio.to_thread(text_to_speech, raw_text, out_path)
                    send_type = "audio"
                elif target == "qr":
                    target_ext = "png"
                    out_path = str(get_temp_path(f"qr_{task_id}", ".png"))
                    await asyncio.to_thread(text_to_qr, raw_text, out_path)
                    send_type = "photo"
                elif target == "html":
                    target_ext = "html"
                    out_path = str(get_temp_path(f"sahifa_{task_id}", ".html"))
                    html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body><pre style='font-size:14px;white-space:pre-wrap;'>{html.escape(raw_text)}</pre></body></html>"
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

        chat_id = callback.message.chat.id
        
        # 3. Handle pure text result (OCR or QR Scan)
        if text_result:
            safe_text = html.escape(text_result)
            await progress_msg.edit_text(
                f"✅ <b>Natija:</b>\n\n<pre>{safe_text}</pre>\n\n⚡ @aylantirpdf_bot",
                parse_mode=ParseMode.HTML
            )
            return

        # 4. Handle file delivery
        if out_path and os.path.exists(out_path):
            clean_paths.append(out_path)
            
            final_ext = target_ext or Path(out_path).suffix.lstrip(".")
            display_filename = custom_display_name or f"{base_stem}.{final_ext}"
            
            out_file = FSInputFile(out_path, filename=display_filename)
            out_size = os.path.getsize(out_path)
            
            caption_html = (
                f"✅ <b>Tayyor!</b>\n"
                f"📄 <code>{html.escape(display_filename)}</code>\n"
                f"📊 Hajmi: <b>{html.escape(format_size(out_size))}</b>\n\n"
                f"⚡ @aylantirpdf_bot"
            )
            plain_caption = f"✅ Tayyor!\n📄 {display_filename}\n📊 Hajmi: {format_size(out_size)}\n\n⚡ @aylantirpdf_bot"

            async def safe_send(send_func, *args, **kwargs):
                try:
                    await send_func(*args, **kwargs, caption=caption_html, parse_mode=ParseMode.HTML)
                except Exception:
                    await send_func(*args, **kwargs, caption=plain_caption)

            if send_type == "audio":
                await safe_send(bot.send_audio, chat_id, out_file)
            elif send_type == "voice":
                await safe_send(bot.send_voice, chat_id, out_file)
            elif send_type == "video_note":
                await bot.send_video_note(chat_id, out_file)
                await callback.message.answer(caption_html, parse_mode=ParseMode.HTML)
            elif send_type == "video":
                await safe_send(bot.send_video, chat_id, out_file)
            elif send_type == "animation":
                await safe_send(bot.send_animation, chat_id, out_file)
            elif send_type == "photo":
                await safe_send(bot.send_photo, chat_id, out_file)
            elif send_type == "sticker":
                await safe_send(bot.send_document, chat_id, out_file)
            else:
                await safe_send(bot.send_document, chat_id, out_file)

            await progress_msg.edit_text("✅ <b>Muvaffaqiyatli aylantirildi va yuborildi!</b>", parse_mode=ParseMode.HTML)
        else:
            await progress_msg.edit_text("❌ <b>Aylantirishda xatolik yuz berdi.</b> Iltimos qaytadan urinib ko'ring.", parse_mode=ParseMode.HTML)

    except Exception as e:
        traceback.print_exc()
        err_msg = html.escape(str(e)[:250])
        await progress_msg.edit_text(
            f"❌ <b>Xatolik yuz berdi:</b>\n<code>{err_msg}</code>\n\nIltimos boshqa formatni tanlab ko'ring yoki havolani tekshiring.",
            parse_mode=ParseMode.HTML
        )
    finally:
        safe_remove(*clean_paths)
        task_store.remove_task(task_id)
