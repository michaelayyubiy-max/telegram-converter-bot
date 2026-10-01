import subprocess
from pathlib import Path
from config import FFMPEG_PATH

def video_to_mp3(input_path: str, output_path: str, bitrate: str = "192k") -> str:
    """Extracts MP3 audio track from video"""
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-vn",
        "-c:a", "libmp3lame",
        "-b:a", bitrate,
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Video to MP3 failed: {res.stderr}")
    return output_path

def video_to_voice(input_path: str, output_path: str) -> str:
    """Extracts voice note (OGG Opus) from video"""
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-vn",
        "-c:a", "libopus",
        "-b:a", "48k",
        "-vbr", "on",
        "-ar", "48000",
        "-ac", "1",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Video to Voice failed: {res.stderr}")
    return output_path

def video_to_gif(input_path: str, output_path: str, fps: int = 12, width: int = 380) -> str:
    """Converts video to high quality animated GIF using palette optimization"""
    filter_complex = f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-t", "30", # max 30 seconds for GIF
        "-vf", filter_complex,
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # Fallback to simple gif conversion if palette fails
        fallback_cmd = [
            FFMPEG_PATH, "-y", "-i", input_path,
            "-t", "30",
            "-vf", f"fps={fps},scale={width}:-1",
            output_path
        ]
        fallback_res = subprocess.run(fallback_cmd, capture_output=True, text=True)
        if fallback_res.returncode != 0:
            raise RuntimeError(f"Video to GIF failed: {res.stderr}")
    return output_path

def video_to_round_note(input_path: str, output_path: str) -> str:
    """Converts video into Telegram Video Note (circle/round video: 1:1 aspect ratio, max 60s)"""
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-t", "60",
        "-vf", "crop='min(iw,ih)':'min(iw,ih)',scale=384:384",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "24",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "64k",
        "-ar", "44100",
        "-ac", "1",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Video Note conversion failed: {res.stderr}")
    return output_path

def get_video_duration(input_path: str) -> float:
    """Gets duration of video file in seconds using ffprobe"""
    import json
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            input_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(res.stdout)
        return float(data.get("format", {}).get("duration", 0))
    except Exception:
        return 0.0

def compress_video(input_path: str, output_path: str, crf: int = 28, target_mb: float = 44.0) -> str:
    """
    Compresses video for easier sharing on Telegram (must be <= 50MB limit).
    If duration is known, calculates exact bitrate to guarantee size under target_mb with fast preset.
    """
    duration = get_video_duration(input_path)
    if duration > 0:
        target_bits = target_mb * 8 * 1024 * 1024
        total_kbps = int((target_bits / duration) / 1000)
        audio_kbps = 48 if total_kbps < 350 else 64
        video_kbps = max(80, total_kbps - audio_kbps)
        cmd = [
            FFMPEG_PATH, "-y", "-i", input_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-b:v", f"{video_kbps}k",
            "-maxrate", f"{int(video_kbps * 1.3)}k",
            "-bufsize", f"{int(video_kbps * 2)}k",
            "-vf", "scale=min(640\,iw):-2",
            "-c:a", "aac",
            "-b:a", f"{audio_kbps}k",
            "-pix_fmt", "yuv420p",
            output_path
        ]
    else:
        cmd = [
            FFMPEG_PATH, "-y", "-i", input_path,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", str(crf),
            "-vf", "scale=min(640\,iw):-2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "64k",
            output_path
        ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Video compression failed: {res.stderr}")
    return output_path

def convert_video_format(input_path: str, output_path: str, target_format: str = "mp4") -> str:
    """Converts video between formats (MP4, MKV, AVI, MOV, WEBM)"""
    fmt = target_format.lower()
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        output_path
    ]
    if fmt == "webm":
        cmd = [
            FFMPEG_PATH, "-y", "-i", input_path,
            "-c:v", "libvpx-vp9",
            "-crf", "30",
            "-b:v", "0",
            "-c:a", "libopus",
            output_path
        ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Video format conversion failed: {res.stderr}")
    return output_path

def mute_video(input_path: str, output_path: str) -> str:
    """Removes audio from video (mutes video)"""
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-c:v", "copy",
        "-an",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Mute video failed: {res.stderr}")
    return output_path

def change_video_speed(input_path: str, output_path: str, speed: float = 1.25) -> str:
    """Changes video playback speed with synced audio"""
    # pts multiplier is 1/speed
    pts = 1.0 / speed
    atempo = speed
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-filter_complex", f"[0:v]setpts={pts}*PTS[v];[0:a]atempo={atempo}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "aac",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Change video speed failed: {res.stderr}")
    return output_path

