import subprocess
from pathlib import Path
from config import FFMPEG_PATH

def convert_audio(input_path: str, output_path: str, target_format: str, bitrate: str = "192k") -> str:
    """Converts audio to target format (mp3, wav, ogg, aac, m4a, flac, opus)"""
    fmt = target_format.lower()
    
    cmd = [FFMPEG_PATH, "-y", "-i", input_path]
    
    if fmt == "mp3":
        cmd.extend(["-c:a", "libmp3lame", "-b:a", bitrate])
    elif fmt == "wav":
        cmd.extend(["-c:a", "pcm_s16le"])
    elif fmt == "ogg":
        cmd.extend(["-c:a", "libvorbis", "-q:a", "5"])
    elif fmt == "opus":
        cmd.extend(["-c:a", "libopus", "-b:a", "96k"])
    elif fmt in ["m4a", "aac"]:
        cmd.extend(["-c:a", "aac", "-b:a", bitrate])
    elif fmt == "flac":
        cmd.extend(["-c:a", "flac"])
        
    cmd.append(output_path)
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Audio conversion failed: {res.stderr}")
    return output_path

def audio_to_voice_note(input_path: str, output_path: str) -> str:
    """Converts audio/music to Telegram compatible voice message (.ogg with opus codec)"""
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-c:a", "libopus",
        "-b:a", "48k",
        "-vbr", "on",
        "-compression_level", "10",
        "-ar", "48000",
        "-ac", "1",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Voice note conversion failed: {res.stderr}")
    return output_path

def change_audio_speed(input_path: str, output_path: str, speed: float = 1.25) -> str:
    """Changes audio playback speed (0.5 to 2.0)"""
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-filter:a", f"atempo={speed}",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Speed change failed: {res.stderr}")
    return output_path

def boost_audio_volume(input_path: str, output_path: str, volume_factor: float = 1.5) -> str:
    """Boosts or lowers audio volume"""
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-filter:a", f"volume={volume_factor}",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Volume adjustment failed: {res.stderr}")
    return output_path
