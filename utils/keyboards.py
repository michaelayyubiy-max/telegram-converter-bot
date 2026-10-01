from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Returns main menu reply keyboard"""
    kb = [
        [KeyboardButton(text="ℹ️ Bot haqida"), KeyboardButton(text="📋 Qo'llab-quvvatlanadigan formatlar")],
        [KeyboardButton(text="💡 Yordam"), KeyboardButton(text="⚡ Tezkor QR-kod")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_conversion_keyboard(category: str, task_id: str, original_ext: str = "") -> InlineKeyboardMarkup:
    """Generates inline keyboard with conversion options based on file category"""
    buttons = []
    
    if category == "url":
        buttons = [
            [
                InlineKeyboardButton(text="🎬 Video (MP4)", callback_data=f"c:{task_id}:url_video"),
                InlineKeyboardButton(text="🎵 Musiqa (MP3)", callback_data=f"c:{task_id}:url_mp3")
            ],
            [
                InlineKeyboardButton(text="🎙 Ovozli xabar (Voice)", callback_data=f"c:{task_id}:url_voice"),
                InlineKeyboardButton(text="⚪ Dumaloq video (Note)", callback_data=f"c:{task_id}:url_note")
            ],
            [
                InlineKeyboardButton(text="🎬 GIF animatsiya", callback_data=f"c:{task_id}:url_gif"),
                InlineKeyboardButton(text="📸 Muqova / Rasm", callback_data=f"c:{task_id}:url_thumb")
            ]
        ]

    elif category == "pdf":
        buttons = [
            [
                InlineKeyboardButton(text="📝 Word (DOCX)", callback_data=f"c:{task_id}:docx"),
                InlineKeyboardButton(text="🖼 Rasm (PNG ZIP)", callback_data=f"c:{task_id}:images")
            ],
            [
                InlineKeyboardButton(text="📑 Excel (XLSX)", callback_data=f"c:{task_id}:xlsx"),
                InlineKeyboardButton(text="📄 Matn (TXT)", callback_data=f"c:{task_id}:txt")
            ],
            [
                InlineKeyboardButton(text="🌐 HTML sahifa", callback_data=f"c:{task_id}:html"),
                InlineKeyboardButton(text="🗜 Hajmini siqish", callback_data=f"c:{task_id}:compress_pdf")
            ]
        ]
        
    elif category == "docx":
        buttons = [
            [
                InlineKeyboardButton(text="📕 PDF format", callback_data=f"c:{task_id}:pdf"),
                InlineKeyboardButton(text="📄 Matn (TXT)", callback_data=f"c:{task_id}:txt")
            ],
            [
                InlineKeyboardButton(text="🔊 Ovoz (Audio/TTS)", callback_data=f"c:{task_id}:tts"),
                InlineKeyboardButton(text="🌐 HTML sahifa", callback_data=f"c:{task_id}:html")
            ],
            [
                InlineKeyboardButton(text="🖼 Rasm (PNG ZIP)", callback_data=f"c:{task_id}:images")
            ]
        ]
        
    elif category == "image":
        buttons = [
            [
                InlineKeyboardButton(text="📕 PDF ga", callback_data=f"c:{task_id}:pdf"),
                InlineKeyboardButton(text="🖼 PNG ga", callback_data=f"c:{task_id}:png"),
                InlineKeyboardButton(text="🖼 JPG ga", callback_data=f"c:{task_id}:jpg")
            ],
            [
                InlineKeyboardButton(text="🎨 WEBP ga", callback_data=f"c:{task_id}:webp"),
                InlineKeyboardButton(text="🎭 Stiker (512x512)", callback_data=f"c:{task_id}:sticker"),
                InlineKeyboardButton(text="🔲 Favicon (ICO)", callback_data=f"c:{task_id}:ico")
            ],
            [
                InlineKeyboardButton(text="⚫ Oq-qora (B&W)", callback_data=f"c:{task_id}:gray"),
                InlineKeyboardButton(text="🗜 Hajmini siqish", callback_data=f"c:{task_id}:compress_img")
            ],
            [
                InlineKeyboardButton(text="🔍 Matnni o'qish (OCR)", callback_data=f"c:{task_id}:ocr"),
                InlineKeyboardButton(text="📱 QR-kodni o'qish", callback_data=f"c:{task_id}:qrscan")
            ]
        ]
        
    elif category == "video":
        buttons = [
            [
                InlineKeyboardButton(text="🎵 Musiqasi (MP3)", callback_data=f"c:{task_id}:mp3"),
                InlineKeyboardButton(text="🎙 Ovozli xabar (Voice)", callback_data=f"c:{task_id}:voice")
            ],
            [
                InlineKeyboardButton(text="🎬 GIF animatsiya", callback_data=f"c:{task_id}:gif"),
                InlineKeyboardButton(text="⚪ Dumaloq video (Note)", callback_data=f"c:{task_id}:note")
            ],
            [
                InlineKeyboardButton(text="🗜 Hajmini siqish", callback_data=f"c:{task_id}:compress_vid"),
                InlineKeyboardButton(text="🔇 Ovozini o'chirish", callback_data=f"c:{task_id}:mute")
            ],
            [
                InlineKeyboardButton(text="⚡ 1.25x tezlik", callback_data=f"c:{task_id}:vspeed_125"),
                InlineKeyboardButton(text="🎞 Standart MP4", callback_data=f"c:{task_id}:mp4")
            ]
        ]
        
    elif category == "video_note":
        buttons = [
            [
                InlineKeyboardButton(text="🎞 Oddiy video (MP4)", callback_data=f"c:{task_id}:mp4"),
                InlineKeyboardButton(text="🎵 Ovozini olish (MP3)", callback_data=f"c:{task_id}:mp3")
            ],
            [
                InlineKeyboardButton(text="🎬 GIF animatsiya", callback_data=f"c:{task_id}:gif")
            ]
        ]
        
    elif category == "audio":
        buttons = [
            [
                InlineKeyboardButton(text="🎵 MP3 ga", callback_data=f"c:{task_id}:mp3"),
                InlineKeyboardButton(text="🎙 Ovozli xabar (Voice)", callback_data=f"c:{task_id}:voice")
            ],
            [
                InlineKeyboardButton(text="🔊 WAV ga", callback_data=f"c:{task_id}:wav"),
                InlineKeyboardButton(text="🎧 M4A / AAC ga", callback_data=f"c:{task_id}:m4a"),
                InlineKeyboardButton(text="🎼 FLAC ga", callback_data=f"c:{task_id}:flac")
            ],
            [
                InlineKeyboardButton(text="⚡ 1.25x tezlik", callback_data=f"c:{task_id}:speed_125"),
                InlineKeyboardButton(text="🚀 1.5x tezlik", callback_data=f"c:{task_id}:speed_150"),
                InlineKeyboardButton(text="📢 Ovozni kuchaytirish", callback_data=f"c:{task_id}:boost")
            ]
        ]
        
    elif category == "voice":
        buttons = [
            [
                InlineKeyboardButton(text="🎵 MP3 musiqaga", callback_data=f"c:{task_id}:mp3"),
                InlineKeyboardButton(text="🔊 WAV formatga", callback_data=f"c:{task_id}:wav")
            ],
            [
                InlineKeyboardButton(text="⚡ 1.25x tezlashtirish", callback_data=f"c:{task_id}:speed_125"),
                InlineKeyboardButton(text="🚀 1.5x tezlashtirish", callback_data=f"c:{task_id}:speed_150")
            ]
        ]
        
    elif category == "xlsx":
        buttons = [
            [
                InlineKeyboardButton(text="📕 PDF jadval", callback_data=f"c:{task_id}:pdf"),
                InlineKeyboardButton(text="📊 CSV format", callback_data=f"c:{task_id}:csv")
            ],
            [
                InlineKeyboardButton(text="💻 JSON format", callback_data=f"c:{task_id}:json"),
                InlineKeyboardButton(text="🌐 HTML jadval", callback_data=f"c:{task_id}:html")
            ]
        ]
        
    elif category == "csv":
        buttons = [
            [
                InlineKeyboardButton(text="📑 Excel (XLSX)", callback_data=f"c:{task_id}:xlsx"),
                InlineKeyboardButton(text="📕 PDF jadval", callback_data=f"c:{task_id}:pdf")
            ],
            [
                InlineKeyboardButton(text="💻 JSON format", callback_data=f"c:{task_id}:json"),
                InlineKeyboardButton(text="🌐 HTML jadval", callback_data=f"c:{task_id}:html")
            ]
        ]
        
    elif category == "pptx":
        buttons = [
            [
                InlineKeyboardButton(text="📕 PDF slaydlar", callback_data=f"c:{task_id}:pdf"),
                InlineKeyboardButton(text="🖼 Slaydlar rasmi (ZIP)", callback_data=f"c:{task_id}:images")
            ],
            [
                InlineKeyboardButton(text="📄 Matn (TXT)", callback_data=f"c:{task_id}:txt")
            ]
        ]
        
    elif category == "archive":
        buttons = [
            [
                InlineKeyboardButton(text="📂 Arxivni ochish (Extract)", callback_data=f"c:{task_id}:extract")
            ]
        ]
        
    elif category == "json":
        buttons = [
            [
                InlineKeyboardButton(text="📊 CSV ga", callback_data=f"c:{task_id}:csv"),
                InlineKeyboardButton(text="📑 YAML ga", callback_data=f"c:{task_id}:yaml")
            ]
        ]
        
    elif category == "yaml":
        buttons = [
            [
                InlineKeyboardButton(text="💻 JSON ga", callback_data=f"c:{task_id}:json")
            ]
        ]

    elif category == "xml":
        buttons = [
            [
                InlineKeyboardButton(text="💻 JSON ga", callback_data=f"c:{task_id}:json"),
                InlineKeyboardButton(text="📄 Matn (TXT)", callback_data=f"c:{task_id}:txt")
            ]
        ]
        
    elif category == "text":
        buttons = [
            [
                InlineKeyboardButton(text="📕 PDF hujjat", callback_data=f"c:{task_id}:pdf"),
                InlineKeyboardButton(text="📝 Word (DOCX)", callback_data=f"c:{task_id}:docx")
            ],
            [
                InlineKeyboardButton(text="🔊 Ovozga aylantirish (TTS)", callback_data=f"c:{task_id}:tts"),
                InlineKeyboardButton(text="📱 QR-kod yaratish", callback_data=f"c:{task_id}:qr")
            ],
            [
                InlineKeyboardButton(text="🌐 HTML sahifa", callback_data=f"c:{task_id}:html")
            ]
        ]
        
    # Cancel button at bottom
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel:{task_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
