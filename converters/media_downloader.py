import os
import re
import html
import shutil
import urllib.request
import urllib.parse
from pathlib import Path
import yt_dlp
from curl_cffi import requests as cffi_requests

from config import FFMPEG_PATH, TEMP_DIR, MAX_UPLOAD_SIZE_BYTES
from converters.video_converter import video_to_mp3, video_to_voice, video_to_gif, video_to_round_note, compress_video

def extract_platform(url: str) -> tuple[str, str]:
    """Detects platform name and icon from URL"""
    u = url.lower()
    if "instagram.com" in u or "instagr.am" in u:
        return "Instagram", "📸"
    elif "tiktok.com" in u:
        return "TikTok", "🎵"
    elif "youtube.com" in u or "youtu.be" in u:
        return "YouTube", "🔴"
    elif "twitter.com" in u or "x.com" in u:
        return "Twitter / X", "🐦"
    elif "facebook.com" in u or "fb.watch" in u or "fb.com" in u:
        return "Facebook", "📘"
    elif "pinterest.com" in u or "pin.it" in u:
        return "Pinterest", "📌"
    elif "threads.net" in u:
        return "Threads", "🧵"
    elif "reddit.com" in u or "redd.it" in u:
        return "Reddit", "👽"
    elif "vk.com" in u:
        return "VKontakte", "🔷"
    elif "soundcloud.com" in u:
        return "SoundCloud", "🎧"
    else:
        return "Veb-havola", "🌐"

def is_direct_file_url(url: str) -> tuple[bool, str]:
    """Checks if URL directly points to a media/document file"""
    try:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        ext = Path(path).suffix.lower()
        known_exts = [
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".pptx", ".ppt",
            ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".ico", ".heic",
            ".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac",
            ".mp4", ".mkv", ".avi", ".mov", ".webm",
            ".zip", ".tar", ".gz", ".7z",
            ".txt", ".json", ".yaml", ".yml"
        ]
        if ext in known_exts:
            return True, ext.lstrip(".")
    except Exception:
        pass
    return False, ""

def _get_instagram_metadata(url: str) -> dict | None:
    """Fast Instagram metadata extraction via embed page and curl_cffi"""
    try:
        m_code = re.search(r'/(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
        if not m_code:
            return None
        code = m_code.group(1)
        embed_url = f"https://www.instagram.com/p/{code}/embed/captioned/"
        res = cffi_requests.get(embed_url, impersonate="chrome124", timeout=8)
        if res.status_code == 200:
            caption_m = re.search(r'class=\"Caption\"[^>]*>(.*?)</div>', res.text, re.DOTALL)
            title = f"Instagram Post ({code})"
            if caption_m:
                raw_cap = re.sub(r'<[^>]+>', ' ', caption_m.group(1))
                title = re.sub(r'[\r\n\t]+', ' ', raw_cap).strip()[:70] or title

            return {
                "platform": "Instagram",
                "icon": "📸",
                "title": title,
                "duration": None,
                "thumbnail": None,
                "is_direct_file": False,
                "direct_ext": ""
            }
    except Exception as e:
        print(f"Instagram fast metadata error: {e}")
    return None

def _get_tiktok_metadata(url: str) -> dict | None:
    """Fast TikTok metadata extraction via TikWM API"""
    try:
        import json
        api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
        resp = cffi_requests.get(api_url, impersonate="chrome124", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0 and "data" in data:
                tdata = data["data"]
                title = tdata.get("title") or "TikTok video"
                return {
                    "platform": "TikTok",
                    "icon": "🎵",
                    "title": title[:75],
                    "duration": tdata.get("duration"),
                    "thumbnail": tdata.get("cover"),
                    "is_direct_file": False,
                    "direct_ext": ""
                }
    except Exception:
        pass
    return None

def _get_youtube_metadata(url: str) -> dict | None:
    """Fast YouTube metadata extraction via oEmbed API in <0.2s"""
    try:
        import json
        clean_url = url.split("&")[0].split("?si=")[0]
        oembed_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(clean_url)}&format=json"
        req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data.get("title", "YouTube video")
            author = data.get("author_name")
            display_title = f"{title} ({author})" if author and author not in title else title
            return {
                "platform": "YouTube",
                "icon": "🔴",
                "title": display_title[:75],
                "duration": None,
                "thumbnail": data.get("thumbnail_url"),
                "is_direct_file": False,
                "direct_ext": ""
            }
    except Exception:
        pass
    return None

def get_url_metadata(url: str) -> dict:
    """Fetches title, platform, and basic info for URL"""
    platform, icon = extract_platform(url)
    is_direct, direct_ext = is_direct_file_url(url)
    
    if is_direct:
        stem = Path(urllib.parse.urlparse(url).path).name or "fayl"
        return {
            "platform": platform,
            "icon": icon,
            "title": stem,
            "duration": None,
            "is_direct_file": True,
            "direct_ext": direct_ext
        }

    # 1. Instagram fast bypass
    if platform == "Instagram":
        ig_meta = _get_instagram_metadata(url)
        if ig_meta:
            return ig_meta

    # 2. TikTok fast bypass
    if platform == "TikTok":
        tik_meta = _get_tiktok_metadata(url)
        if tik_meta:
            return tik_meta

    # 3. YouTube fast oEmbed bypass
    if platform == "YouTube":
        yt_meta = _get_youtube_metadata(url)
        if yt_meta:
            return yt_meta

    title = f"{platform} fayli"
    duration = None
    thumbnail = None

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': False,
        'noplaylist': True,
        'extractor_args': {
            'youtube': {'player_client': ['android', 'web', 'ios']},
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                title = info.get("title") or title
                duration = info.get("duration")
                thumbnail = info.get("thumbnail")
    except Exception as e:
        print(f"Info extract error: {e}")

    # Clean title
    title = re.sub(r'[\r\n\t]+', ' ', title).strip()
    if len(title) > 80:
        title = title[:77] + "..."

    return {
        "platform": platform,
        "icon": icon,
        "title": title,
        "duration": duration,
        "thumbnail": thumbnail,
        "is_direct_file": False,
        "direct_ext": ""
    }

def _download_instagram_curl_cffi(url: str, target: str, out_dir_path: Path) -> tuple[str, str, str] | None:
    """Downloads Instagram video or photo using Chrome impersonation"""
    try:
        m_code = re.search(r'/(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
        if not m_code:
            return None
        code = m_code.group(1)
        embed_url = f"https://www.instagram.com/p/{code}/embed/captioned/"
        res = cffi_requests.get(embed_url, impersonate="chrome124", timeout=12)
        if res.status_code != 200:
            return None

        video_m = re.search(r'video_url\\?\":\\?\"([^\"]+)', res.text)
        display_m = re.search(r'display_url\\?\":\\?\"([^\"]+)', res.text)
        
        caption_m = re.search(r'class=\"Caption\"[^>]*>(.*?)</div>', res.text, re.DOTALL)
        caption_text = ""
        if caption_m:
            raw_cap = re.sub(r'<[^>]+>', ' ', caption_m.group(1))
            caption_text = re.sub(r'[\r\n\t]+', ' ', raw_cap).strip()
        title = (caption_text[:40] if caption_text else f"instagram_{code}").strip()
        title = re.sub(r'[\\/*?:"<>|]', "", title) or f"instagram_{code}"

        if video_m and target != "thumb":
            raw_v_url = video_m.group(1).rstrip('\\\"')
            clean_v_url = raw_v_url.replace(chr(92) + "/", "/").replace(chr(92), "")
            v_res = cffi_requests.get(clean_v_url, impersonate="chrome124", timeout=30)
            if v_res.status_code == 200 and len(v_res.content) > 1000:
                raw_video = str(out_dir_path / f"{title}.mp4")
                with open(raw_video, "wb") as f:
                    f.write(v_res.content)

                if target == "mp3":
                    out_mp3 = str(out_dir_path / f"{title}.mp3")
                    video_to_mp3(raw_video, out_mp3)
                    return out_mp3, "audio", f"{title}.mp3"
                elif target == "voice":
                    out_voice = str(out_dir_path / f"{title}.ogg")
                    video_to_voice(raw_video, out_voice)
                    return out_voice, "voice", f"{title}.ogg"
                elif target == "note":
                    out_note = str(out_dir_path / f"{title}_note.mp4")
                    video_to_round_note(raw_video, out_note)
                    return out_note, "video_note", f"{title}_note.mp4"
                elif target == "gif":
                    out_gif = str(out_dir_path / f"{title}.gif")
                    video_to_gif(raw_video, out_gif)
                    return out_gif, "animation", f"{title}.gif"
                else:
                    return raw_video, "video", f"{title}.mp4"

        elif display_m:
            raw_i_url = display_m.group(1).rstrip('\\\"')
            clean_i_url = raw_i_url.replace(chr(92) + "/", "/").replace(chr(92), "")
            i_res = cffi_requests.get(clean_i_url, impersonate="chrome124", timeout=20)
            if i_res.status_code == 200:
                raw_img = str(out_dir_path / f"{title}.jpg")
                with open(raw_img, "wb") as f:
                    f.write(i_res.content)
                return raw_img, "photo", f"{title}.jpg"
    except Exception as e:
        print(f"Instagram cffi error: {e}")
    return None

def _download_youtube_fast(url: str, target: str, out_dir_path: Path) -> tuple[str, str, str] | None:
    """Fast YouTube downloader via streaming proxy bypassing bot detection"""
    import requests, time
    fmt = "mp3" if target == "mp3" else "720"
    api_url = f"https://loader.to/ajax/download.php?button=1&start=1&end=1&format={fmt}&url={urllib.parse.quote(url)}"
    try:
        r = requests.get(api_url, timeout=6)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data.get("success"):
            return None
            
        title = data.get("title") or "youtube_video"
        title = re.sub(r'[\\/*?:"<>|]', "", title).strip() or "video"
        
        prog_url = data.get("progress_url") or f"https://p.oceansaver.in/ajax/progress.php?id={data.get('id')}"
        
        download_url = None
        for _ in range(12):
            time.sleep(1)
            pr = requests.get(prog_url, timeout=6)
            if pr.status_code == 200:
                pdata = pr.json()
                if pdata.get("download_url"):
                    download_url = pdata["download_url"]
                    if pdata.get("title"):
                        title = re.sub(r'[\\/*?:"<>|]', "", pdata["title"]).strip() or title
                    break
                if pdata.get("progress") == 1000 and not pdata.get("download_url"):
                    return None
                    
        if download_url:
            ext = "mp3" if target == "mp3" else "mp4"
            out_file = str(out_dir_path / f"{title[:40]}.{ext}")
            with requests.get(download_url, stream=True, timeout=30) as dl_resp:
                if dl_resp.status_code == 200:
                    with open(out_file, "wb") as f:
                        for chunk in dl_resp.iter_content(chunk_size=65536):
                            f.write(chunk)
                    
                    if target == "mp3":
                        return out_file, "audio", f"{title[:40]}.mp3"
                    elif target == "voice":
                        out_voice = str(out_dir_path / f"{title[:40]}.ogg")
                        video_to_voice(out_file, out_voice)
                        return out_voice, "voice", f"{title[:40]}.ogg"
                    elif target == "note":
                        out_note = str(out_dir_path / f"{title[:40]}_note.mp4")
                        video_to_round_note(out_file, out_note)
                        return out_note, "video_note", f"{title[:40]}_note.mp4"
                    elif target == "gif":
                        out_gif = str(out_dir_path / f"{title[:40]}.gif")
                        video_to_gif(out_file, out_gif)
                        return out_gif, "animation", f"{title[:40]}.gif"
                    else:
                        return out_file, "video", f"{title[:40]}.mp4"
    except Exception as e:
        print(f"Fast youtube download error: {e}")
    return None

def download_social_media(url: str, target: str, out_dir: str) -> tuple[str, str, str]:
    """
    Downloads media from social media or web url and converts to target format.
    Targets: 'video' (MP4), 'mp3' (Audio), 'voice' (Voice note), 'note' (Round video), 'gif' (GIF), 'thumb' (Image)
    Returns: (output_file_path, send_type, display_title)
    """
    platform, icon = extract_platform(url)
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    # 1. Direct file download fallback
    is_direct, direct_ext = is_direct_file_url(url)
    if is_direct:
        parsed_name = Path(urllib.parse.urlparse(url).path).name or f"download.{direct_ext}"
        out_file = str(out_dir_path / parsed_name)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp, open(out_file, 'wb') as f:
            shutil.copyfileobj(resp, f)
        return out_file, "document", parsed_name

    # 2. Instagram bypass via Chrome impersonation
    if platform == "Instagram":
        ig_res = _download_instagram_curl_cffi(url, target, out_dir_path)
        if ig_res:
            return ig_res

    # 3. TikTok special handling
    if platform == "TikTok":
        try:
            tik_res = _download_tiktok_tikwm(url, target, out_dir_path)
            if tik_res:
                return tik_res
        except Exception as e:
            print(f"TikWM error: {e}")

    # 4. YouTube fast streaming bypass
    if platform == "YouTube":
        try:
            yt_res = _download_youtube_fast(url, target, out_dir_path)
            if yt_res:
                return yt_res
        except Exception as e:
            print(f"Fast YouTube loader error: {e}")

    # 4. Universal yt-dlp download
    base_template = str(out_dir_path / "%(id)s.%(ext)s")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'outtmpl': base_template,
        'ffmpeg_location': FFMPEG_PATH,
        'extractor_args': {
            'youtube': {'player_client': ['android', 'web', 'ios']},
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
    }

    if target == "mp3":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif target == "thumb":
        ydl_opts['skip_download'] = True
        ydl_opts['writethumbnail'] = True
    else:
        # Best video compatible with mp4
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        ydl_opts['merge_output_format'] = 'mp4'

    title = f"{platform}_media"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info:
                title = info.get("title") or title
    except Exception as e:
        err_str = str(e)
        if "Sign in to confirm you" in err_str or ("bot" in err_str.lower() and "youtube" in err_str.lower()) or "unavailable" in err_str.lower() or "private video" in err_str.lower():
            raise RuntimeError("Ushbu video YouTube tomonidan cheklangan, yopiq (private) yoki o'chirib tashlangan.")
        raise

    title = re.sub(r'[\\/*?:"<>|]', "", title).strip() or "media"
    if len(title) > 60:
        title = title[:60]

    # Find the downloaded file in out_dir_path
    downloaded_files = list(out_dir_path.glob("*"))
    if not downloaded_files:
        raise RuntimeError("Fayl yuklab olinmadi yoki havola mavjud emas.")

    # Select latest / primary media file
    primary_file = None
    for f in downloaded_files:
        if f.suffix.lower() in [".mp4", ".mp3", ".webm", ".mkv", ".m4a", ".jpg", ".png", ".webp"]:
            primary_file = f
            break
    if not primary_file:
        primary_file = downloaded_files[0]

    input_file_str = str(primary_file)

    # 5. Post-process according to target
    if target == "mp3":
        if primary_file.suffix.lower() == ".mp3":
            return input_file_str, "audio", f"{title}.mp3"
        out_mp3 = str(out_dir_path / f"{title}.mp3")
        video_to_mp3(input_file_str, out_mp3)
        return out_mp3, "audio", f"{title}.mp3"

    elif target == "voice":
        out_voice = str(out_dir_path / f"{title}.ogg")
        video_to_voice(input_file_str, out_voice)
        return out_voice, "voice", f"{title}.ogg"

    elif target == "note":
        out_note = str(out_dir_path / f"{title}_note.mp4")
        video_to_round_note(input_file_str, out_note)
        return out_note, "video_note", f"{title}_note.mp4"

    elif target == "gif":
        out_gif = str(out_dir_path / f"{title}.gif")
        video_to_gif(input_file_str, out_gif)
        return out_gif, "animation", f"{title}.gif"

    elif target == "thumb":
        out_thumb = str(out_dir_path / f"{title}.jpg")
        if primary_file.suffix.lower() in [".jpg", ".png", ".webp"]:
            return input_file_str, "photo", f"{title}.jpg"
        # Extract 1st frame from video
        cmd = [
            FFMPEG_PATH, "-y", "-i", input_file_str,
            "-ss", "00:00:01",
            "-vframes", "1",
            out_thumb
        ]
        import subprocess
        subprocess.run(cmd, capture_output=True)
        if os.path.exists(out_thumb):
            return out_thumb, "photo", f"{title}.jpg"
        return input_file_str, "document", f"{title}.jpg"

    else:
        # Default: Video (MP4)
        out_mp4 = input_file_str
        if primary_file.suffix.lower() != ".mp4":
            out_mp4 = str(out_dir_path / f"{title}.mp4")
            from converters.video_converter import convert_video_format
            convert_video_format(input_file_str, out_mp4, "mp4")

        # Check file size (Telegram limit: 50MB)
        file_size = os.path.getsize(out_mp4)
        if file_size > (48 * 1024 * 1024):
            print(f"Video size {file_size} exceeds Telegram limit, compressing...")
            compressed_mp4 = str(out_dir_path / f"{title}_compressed.mp4")
            compress_video(out_mp4, compressed_mp4, crf=30)
            if os.path.exists(compressed_mp4):
                out_mp4 = compressed_mp4

        return out_mp4, "video", f"{title}.mp4"

def _download_tiktok_tikwm(url: str, target: str, out_dir_path: Path) -> tuple[str, str, str] | None:
    """Helper for downloading TikTok without watermark via TikWM API"""
    import json
    api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(url)}"
    resp = cffi_requests.get(api_url, impersonate="chrome124", timeout=12)
    if resp.status_code != 200:
        return None
    data = resp.json()
    
    if data.get("code") == 0 and "data" in data:
        tdata = data["data"]
        title = re.sub(r'[\\/*?:"<>|]', "", tdata.get("title", "tiktok")).strip() or "tiktok"
        if len(title) > 50:
            title = title[:50]

        if target == "mp3":
            music_url = tdata.get("music") or tdata.get("play")
            if music_url:
                out_file = str(out_dir_path / f"{title}.mp3")
                m_resp = cffi_requests.get(music_url, impersonate="chrome124", timeout=20)
                if m_resp.status_code == 200:
                    with open(out_file, "wb") as f:
                        f.write(m_resp.content)
                    return out_file, "audio", f"{title}.mp3"
        else:
            # Download watermark-free video
            video_url = tdata.get("play") or tdata.get("wmplay")
            if video_url:
                raw_video = str(out_dir_path / f"{title}_raw.mp4")
                v_resp = cffi_requests.get(video_url, impersonate="chrome124", timeout=30)
                if v_resp.status_code == 200:
                    with open(raw_video, "wb") as f:
                        f.write(v_resp.content)

                    if target == "voice":
                        out_voice = str(out_dir_path / f"{title}.ogg")
                        video_to_voice(raw_video, out_voice)
                        return out_voice, "voice", f"{title}.ogg"
                    elif target == "note":
                        out_note = str(out_dir_path / f"{title}_note.mp4")
                        video_to_round_note(raw_video, out_note)
                        return out_note, "video_note", f"{title}_note.mp4"
                    elif target == "gif":
                        out_gif = str(out_dir_path / f"{title}.gif")
                        video_to_gif(raw_video, out_gif)
                        return out_gif, "animation", f"{title}.gif"
                    else:
                        return raw_video, "video", f"{title}.mp4"
    return None
