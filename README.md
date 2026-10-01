# 🚀 Universal Telegram Converter & Downloader Bot (@aylantirpdf_bot)

Barcha turdagi fayllarni (hujjatlar, rasmlar, videolar, audio, jadvallar, arxivlar va matnlarni) sifatli va tezkorlik bilan o'zaro bir-biriga aylantirib beruvchi hamda **Instagram, TikTok, YouTube, Twitter, Pinterest va istalgan ilovalardan** video va audiolarni yuklab, kerakli formatga o'tkazib beruvchi universal Telegram boti.

---

## 🌟 Imkoniyatlar va Qo'llab-quvvatlanadigan Formatlar

### 1. 🌐 Ijtimoiy Tarmoqlar va Veb-havolalar (NEW!)
Botga istalgan ijtimoiy tarmoq yoki sayt havolasini yuborishingiz mumkin:
- **Instagram:** Reels, Postlar, Storylar
- **TikTok:** Suv belgisiz (no-watermark) video va musiqa
- **YouTube:** Shorts, uzun videolar, musiqa
- **Twitter / X:** Video va GIF lar
- **Facebook:** Reels va videolar
- **Pinterest, Threads, Reddit, SoundCloud** va barcha internet havolalari
- **Aylantirish imkoniyatlari:**
  - 🎬 **Video (MP4)** — Yuqori sifatli video
  - 🎵 **Musiqa (MP3)** — Videodan ovozni ajratib MP3 qilish
  - 🎙 **Ovozli xabar (Voice note)** — Telegram voice xabari ko'rinishida
  - ⚪ **Dumaloq video (Video Note)** — Telegram dumaloq xabari (1:1)
  - 🎬 **GIF animatsiya** — GIF formatga o'tkazish
  - 📸 **Muqova / Rasm** — Rasm / thumbnail ni yuklash

### 2. 📄 Hujjatlar (Documents)
- **PDF (.pdf)** ➔ Word (.docx), Excel jadval (.xlsx), Rasmlar (.png / .zip), Matn (.txt), HTML, Hajmini siqish (Compress)
- **Word (.docx, .doc, .odt, .rtf)** ➔ PDF (.pdf), Ovoz (Audio/TTS), Matn (.txt), HTML, Rasmlar (.png)
- **Excel (.xlsx, .xls)** ➔ PDF jadval, CSV, JSON, HTML jadval
- **CSV va TSV (.csv, .tsv)** ➔ Excel (.xlsx), PDF, JSON, HTML
- **PowerPoint (.pptx, .ppt)** ➔ PDF slaydlar, Slaydlar rasmi (.zip), Matn (.txt)
- **HTML (.html, .htm)** ➔ PDF, Word (.docx), Matn (.txt)

### 3. 🖼 Rasmlar (Images)
- **Formatlar:** JPG, PNG, WEBP, BMP, ICO, TIFF, GIF, HEIC, HEIF, SVG
- **iPhone rasmlari:** HEIC va HEIF fotolarni to'g'ridan-to'g'ri ochish va aylantirish
- **Vektor grafika:** SVG ni yuqori aniqlikdagi PNG, JPG, PDF ga aylantirish
- **Aylantirish:**
  - Istalgan rasm ➔ PNG, JPG, WEBP, BMP, ICO (Favicon), TIFF, PDF
  - **Telegram Stiker:** Avtomatik 512x512 shaffof fonga ega WEBP stiker formati
  - **Oq-qora (Grayscale):** Rasm rangini oq-qora qilish
  - **Hajmini siqish (Compress):** Fayl hajmini sifatni saqlagan holda kamaytirish
  - **OCR (Matnni ajratish):** Rasm ichidagi so'zlarni o'qib matn ko'rinishida chiqarish (RapidOCR)
  - **QR-kod skaner:** Rasm ichidagi QR-kodni o'qib berish

### 4. 🎬 Video
- **Formatlar:** MP4, MKV, AVI, MOV, WEBM, FLV, 3GP, M4V, WMV, TS
- **Aylantirish:**
  - Videodan musiqani ajratish (.mp3)
  - Telegram ovozli xabariga aylantirish (Voice message - OGG Opus)
  - GIF animatsiya yaratish (12 fps rang palitrasi bilan)
  - **Dumaloq video (Telegram Video Note):** 1:1 kvadrat markazlashtirilgan dumaloq video
  - Videoni siqish (hajmini 50-70% gacha kamaytirish)
  - Ovozini o'chirish (Mute video)
  - Tezlashtirish (1.25x)
  - Standart MP4, MKV, AVI, MOV, WEBM formatlariga o'tkazish

### 5. 🎵 Audio va Musiqa
- **Formatlar:** MP3, WAV, OGG, M4A, AAC, FLAC, OPUS, WMA, AIFF
- **Aylantirish:**
  - Istalgan musiqani boshqa audio formatga o'tkazish (MP3, WAV, M4A, FLAC)
  - Musiqani Telegram ovozli xabariga (Voice Message) aylantirish
  - Ovozli xabarni (.ogg) toza MP3 musiqaga aylantirish
  - Ovoz tezligini o'zgartirish: `1.25x`, `1.5x`
  - Ovoz balandligini kuchaytirish (Volume boost)

### 6. 📦 Arxivlar va Ma'lumotlar
- **Arxivlar (.zip, .tar, .gz, .tgz, .bz2, .7z, .rar):** Arxivni ochish va ichidagi fayllarni chiqarib berish
- **JSON (.json):** CSV va YAML formatlarga o'tkazish
- **YAML (.yaml):** JSON formatga o'tkazish
- **XML (.xml):** JSON va Matnga o'tkazish
- **Oddiy Matn:** Matndan PDF yaratish, Word (.docx) qilish, Ovozga aylantirish (TTS audio), QR-kod yaratish, HTML ga o'tkazish

---

## 🛠 Texnologiyalar
- **Python 3.11**
- **Aiogram 3.x** (Asinxron Telegram Bot Framework)
- **yt-dlp** (Instagram, TikTok, YouTube va barcha ijtimoiy tarmoqlar integratsiyasi)
- **FFmpeg 7.0** (Video, audio va multimediani qayta ishlash)
- **PyMuPDF (Fitz)** (PDF rendering, SVG parsing, jadvallarni ajratish)
- **pdf2docx** (PDF dan Word ga o'tkazish)
- **Pillow & pillow-heif** (JPG, PNG, WEBP, ICO va iPhone HEIC rasmlari)
- **OpenCV & RapidOCR** (QR-kod o'qish va rasm ichidagi matnni aniqlash)
- **gTTS** (Text to Speech - matnni ovozga aylantirish)

---

## 🚀 Ishga tushirish (Run)

```bash
cd /Users/macbook/.gemini/antigravity-ide/scratch/telegram-converter-bot
./run.sh
```

Fonda doimiy ishlab turishi uchun:
```bash
nohup python3 bot.py > bot.log 2>&1 &
```
