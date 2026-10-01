import os
import shutil
import uuid
from pathlib import Path
from config import TEMP_DIR

def format_size(size_bytes: int) -> str:
    """Formats file size into human-readable string (KB, MB, GB)"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def get_temp_path(prefix: str = "file", suffix: str = "") -> Path:
    """Generates unique file path in TEMP_DIR"""
    uid = uuid.uuid4().hex[:10]
    if suffix and not suffix.startswith("."):
        suffix = f".{suffix}"
    return TEMP_DIR / f"{prefix}_{uid}{suffix}"

def get_temp_dir(prefix: str = "task") -> Path:
    """Creates a unique temporary folder"""
    uid = uuid.uuid4().hex[:10]
    folder = TEMP_DIR / f"{prefix}_{uid}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def safe_remove(*paths):
    """Safely deletes files or folders"""
    for p in paths:
        try:
            if not p:
                continue
            path = Path(p)
            if path.is_file() or path.is_symlink():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
        except Exception as e:
            print(f"Error removing {p}: {e}")

def detect_file_category(filename: str, mime_type: str = "") -> str:
    """Detects file category based on filename extension and mime type"""
    ext = Path(filename).suffix.lower()
    
    if ext in [".pdf"]:
        return "pdf"
    elif ext in [".docx", ".doc", ".odt", ".rtf"]:
        return "docx"
    elif ext in [".xlsx", ".xls"]:
        return "xlsx"
    elif ext in [".csv", ".tsv"]:
        return "csv"
    elif ext in [".pptx", ".ppt"]:
        return "pptx"
    elif ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".ico", ".tiff", ".tif", ".gif", ".heic", ".heif", ".svg"]:
        return "image"
    elif ext in [".mp3", ".wav", ".ogg", ".oga", ".m4a", ".aac", ".flac", ".opus", ".wma", ".aiff"]:
        return "audio"
    elif ext in [".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".3gp", ".m4v", ".wmv", ".ts"]:
        return "video"
    elif ext in [".zip", ".tar", ".gz", ".tgz", ".bz2", ".7z", ".rar"]:
        return "archive"
    elif ext in [".json"]:
        return "json"
    elif ext in [".yaml", ".yml"]:
        return "yaml"
    elif ext in [".xml"]:
        return "xml"
    elif ext in [".txt", ".log", ".md", ".html", ".htm"]:
        return "text"

def is_url_text(text: str) -> bool:
    """Checks if text contains or is a web URL"""
    import re
    url_pattern = re.compile(
        r'(https?://[^\s]+|www\.[^\s]+|instagram\.com/[^\s]+|tiktok\.com/[^\s]+|vt\.tiktok\.com/[^\s]+|youtu\.be/[^\s]+|youtube\.com/[^\s]+|pin\.it/[^\s]+|x\.com/[^\s]+|twitter\.com/[^\s]+)',
        re.IGNORECASE
    )
    return bool(url_pattern.search(text))

def extract_first_url(text: str) -> str:
    """Extracts the first valid URL from text"""
    import re
    url_pattern = re.compile(
        r'(https?://[^\s]+|www\.[^\s]+|instagram\.com/[^\s]+|tiktok\.com/[^\s]+|vt\.tiktok\.com/[^\s]+|youtu\.be/[^\s]+|youtube\.com/[^\s]+|pin\.it/[^\s]+|x\.com/[^\s]+|twitter\.com/[^\s]+)',
        re.IGNORECASE
    )
    m = url_pattern.search(text)
    if m:
        url = m.group(0).rstrip('.,!?)"\'')
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        return url
    return ""
        
    # Check mime type
    if mime_type:
        if "image/" in mime_type:
            return "image"
        elif "audio/" in mime_type:
            return "audio"
        elif "video/" in mime_type:
            return "video"
        elif "pdf" in mime_type:
            return "pdf"
            
    return "unknown"
