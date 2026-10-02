import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Directories
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# FFmpeg path
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "")
if not FFMPEG_PATH or not os.path.exists(FFMPEG_PATH):
    local_ffmpeg = Path("/Users/macbook/.local/bin/ffmpeg")
    if local_ffmpeg.exists():
        FFMPEG_PATH = str(local_ffmpeg)
    else:
        import shutil
        FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"

# Limits
MAX_DOWNLOAD_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB Telegram bot API limit
MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024    # 50 MB Telegram bot API limit
