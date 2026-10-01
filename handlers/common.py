from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from utils.keyboards import get_main_reply_keyboard

router = Router()

START_TEXT = """
👋 <b>Assalomu alaykum! Barcha turdagi fayllar va havolalarni aylantiruvchi universal botga xush kelibsiz!</b>

🚀 <b>Men sizga istalgan fayl yoki havolani kerakli formatga o'tkazib beraman:</b>

🌐 <b>Ijtimoiy tarmoqlar va Havolalar:</b>
• Instagram, TikTok, YouTube, Twitter/X, Pinterest, Facebook, Threads, Reddit va h.k.
• Havola yuboring ➔ <b>Video (MP4), Musiqa (MP3), Ovozli xabar, Dumaloq video (Note), GIF, Rasm</b>

📄 <b>Hujjatlar:</b>
• PDF ➔ Word (DOCX), Excel (XLSX), Rasmlar (PNG/JPG ZIP), Matn (TXT), HTML, Siqish
• Word (DOCX) ➔ PDF, Ovoz (Audio/TTS), Matn (TXT), HTML, Rasmlar
• Excel (XLSX, CSV) ➔ PDF, CSV, JSON, HTML
• PowerPoint (PPTX) ➔ PDF, Slaydlar rasmi (ZIP), Matn (TXT)

🖼 <b>Rasmlar (JPG, PNG, WEBP, BMP, ICO, TIFF, HEIC, HEIF, SVG):</b>
• Formatlarni o'zgartirish (PNG, JPG, WEBP, ICO, PDF, TIFF)
• iPhone rasmlarini ochish va aylantirish (HEIC / HEIF)
• Telegram Stiker qilish (512x512)
• Rasm ichidagi matnni o'qib olish (OCR)
• Rasm ichidagi QR-kodni o'qish (Scan QR)
• Oq-qora qilish va hajmini siqish

🎬 <b>Video (MP4, MKV, AVI, MOV, WEBM):</b>
• Videodan musiqani ajratish (MP3)
• Ovozli xabar qilish (Voice message - OGG)
• GIF animatsiya yaratish
• Telegram dumaloq video (Video Note)
• Videoni siqish (hajmini kamaytirish)
• Ovozini o'chirish (Mute) va tezlashtirish (1.25x)

🎵 <b>Musiqa va Ovoz:</b>
• MP3, WAV, OGG, M4A, FLAC formatlar
• Musiqani Telegram ovozli xabariga aylantirish
• Ovozli xabarni MP3 qilish
• Tezlikni oshirish (1.25x, 1.5x) va kuchaytirish

📦 <b>Arxivlar va Ma'lumotlar:</b>
• ZIP / TAR arxivlarni ochish
• JSON ➔ CSV, YAML
• Matn ➔ PDF, DOCX, Ovoz (Audio/TTS), QR-kod, HTML

👇 <b>Boshlash uchun istalgan fayl, rasm, video, ovoz, matn yoki havola yuboring!</b>
"""

HELP_TEXT = """
💡 <b>Botdan qanday foydalanish kerak?</b>

1️⃣ <b>Fayl yoki havola yuboring:</b>
• Istalgan hujjat, rasm, audio, video yoki matn
• Yoki <b>Instagram, TikTok, YouTube, Twitter</b> va boshqa sayt havolasini yuboring.

2️⃣ <b>Formatni tanlang:</b>
• Bot sizga fayl yoki havola turiga mos formatlar ro'yxatini chiqaradi.

3️⃣ <b>Natijani oling:</b>
• Bot tezkorlik bilan aylantirib, sizga tayyor faylni qaytarib beradi.

📌 <b>Fayl hajmi cheklovi:</b> Telegram orqali 50 MB gacha bo'lgan natijaviy fayllar yuboriladi. Katta videolar avtomatik siqib moslashtiriladi.

👨‍💻 <b>Admin / Qo'llab-quvvatlash:</b> <a href="https://t.me/Vibecdruz">@Vibecdruz</a>
Savol, taklif va yordam uchun adminga murojaat qilishingiz mumkin.
"""

FORMATS_TEXT = """
📋 <b>Qo'llab-quvvatlanadigan formatlar ro'yxati:</b>

🔹 <b>Ijtimoiy tarmoqlar va Veb:</b>
• Instagram (Reels, Post, Story)
• TikTok (Suv belgisiz video va musiqa)
• YouTube & YouTube Shorts
• Twitter / X
• Facebook & Reels
• Pinterest
• Threads, Reddit, SoundCloud va barcha internet havolalari

🔹 <b>Hujjatlar:</b>
• PDF (.pdf)
• Microsoft Word (.docx, .doc, .odt, .rtf)
• Microsoft Excel (.xlsx, .xls)
• CSV va TSV jadvallari (.csv, .tsv)
• PowerPoint (.pptx, .ppt)
• Matnli fayllar (.txt, .md, .log, .html)

🔹 <b>Rasmlar:</b>
• JPG, JPEG, PNG, WEBP, BMP, ICO, TIFF, GIF
• iPhone fotolari: HEIC, HEIF
• Vektor grafika: SVG

🔹 <b>Audio va Musiqa:</b>
• MP3, WAV, OGG, M4A, AAC, FLAC, OPUS, WMA, AIFF

🔹 <b>Video:</b>
• MP4, MKV, AVI, MOV, WEBM, FLV, 3GP, M4V, WMV, TS

🔹 <b>Ma'lumotlar va Kod:</b>
• JSON, YAML, XML, CSV

🔹 <b>Arxivlar:</b>
• ZIP, TAR, GZ, TGZ, BZ2, 7Z, RAR
"""

ABOUT_TEXT = """
🤖 <b>Universal File & Media Converter Bot</b>
Versiya: 3.0 Ultimate
Tezkor, xavfsiz va barcha turdagi fayllarni hamda ijtimoiy tarmoq videolarini o'zaro sifatli aylantirish tizimi.

👨‍💻 <b>Admin / Bog'lanish:</b> <a href="https://t.me/Vibecdruz">@Vibecdruz</a>

⚡ Bot Python, FFmpeg, yt-dlp, PyMuPDF, OpenCV, RapidOCR va ReportLab texnologiyalari asosida ishlaydi.
"""

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(START_TEXT, parse_mode=ParseMode.HTML, reply_markup=get_main_reply_keyboard())

@router.message(Command("help"))
@router.message(F.text == "💡 Yordam")
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode=ParseMode.HTML)

@router.message(Command("formats"))
@router.message(F.text == "📋 Qo'llab-quvvatlanadigan formatlar")
async def cmd_formats(message: Message):
    await message.answer(FORMATS_TEXT, parse_mode=ParseMode.HTML)

@router.message(F.text == "ℹ️ Bot haqida")
async def cmd_about(message: Message):
    await message.answer(ABOUT_TEXT, parse_mode=ParseMode.HTML)

@router.message(F.text == "⚡ Tezkor QR-kod")
async def cmd_quick_qr(message: Message):
    await message.answer("📱 QR-kod yaratish uchun istalgan matn yoki havolani yozib yuboring!")
