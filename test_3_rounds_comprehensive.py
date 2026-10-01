#!/usr/bin/env python3
"""
Comprehensive 3-Round Test Suite for Telegram Converter Bot
Tests YouTube, TikTok, Instagram, Documents, HTML/Tables, Audio, and Video across 3 full rounds.
"""
import sys, os, time, tempfile, traceback
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

import converters
from converters.media_downloader import get_url_metadata, download_social_media
from config import FFMPEG_PATH

def run_round(round_num: int) -> bool:
    print(f"\n=======================================================")
    print(f"             STARTING TEST ROUND {round_num} / 3")
    print(f"=======================================================")
    
    passed = 0
    failed = 0

    def check(name, fn, *args, **kwargs):
        nonlocal passed, failed
        try:
            t0 = time.time()
            res = fn(*args, **kwargs)
            dt = time.time() - t0
            passed += 1
            print(f"  ✅ [Round {round_num}] {name} ({dt:.2f}s): SUCCESS")
            return res
        except Exception as e:
            failed += 1
            print(f"  ❌ [Round {round_num}] {name}: FAILED -> {e}")
            traceback.print_exc()
            return None

    # -------------------------------------------------------------
    # 1. Social Media Links & Downloads
    # -------------------------------------------------------------
    print(f"\n--- [Round {round_num}] 1. Social Media URLs & Downloads ---")
    
    # YouTube Link 1: The user's exact failing video
    yt1 = "https://youtu.be/Azkx7GUtbyc?si=-JMk0DuN7r1DHqWm"
    check("YouTube (Azkx7GUtbyc) Metadata", get_url_metadata, yt1)
    
    # YouTube Link 2: Short classic video
    yt2 = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    check("YouTube (jNQXAC9IVRw) Metadata", get_url_metadata, yt2)
    
    # YouTube Link 3: Shorts
    yt3 = "https://youtube.com/shorts/dQw4w9WgXcQ"
    check("YouTube Shorts Metadata", get_url_metadata, yt3)

    # TikTok URL
    tt_url = "https://www.tiktok.com/@tiktok/video/7106594312292453678"
    check("TikTok Metadata", get_url_metadata, tt_url)

    # YouTube Media Download (Fast short video MP3 & Video)
    with tempfile.TemporaryDirectory() as td:
        check("YouTube MP3 Download", download_social_media, yt2, "mp3", td)
        check("YouTube Video Download", download_social_media, yt2, "video", td)

    # -------------------------------------------------------------
    # 2. File & Document Converters
    # -------------------------------------------------------------
    print(f"\n--- [Round {round_num}] 2. Document & Text Converters ---")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        
        # Text converters
        txt_sample = "Salom Dunyo! O'zbekiston kelajagi buyuk davlat.\nIkkinchi qator."
        check("text_to_pdf", converters.text_to_pdf, txt_sample, str(tmp / "t.pdf"))
        check("text_to_docx", converters.text_to_docx, txt_sample, str(tmp / "t.docx"))
        check("text_to_qr", converters.text_to_qr, txt_sample, str(tmp / "t_qr.png"))

        # HTML with Tables & Rich formatting
        html_sample = (
            "<!DOCTYPE html><html><head><title>Jadval</title></head><body>"
            "<h1>Test Sarlavha</h1><p>Paragraf matni</p>"
            "<table border='1'><tr><th>№</th><th>Nomi</th><th>Narxi</th></tr>"
            "<tr><td>1</td><td>Osh</td><td>40000</td></tr>"
            "<tr><td>2</td><td>Somsa</td><td>10000</td></tr></table>"
            "</body></html>"
        )
        check("html_to_docx", converters.html_to_docx, html_sample, str(tmp / "h.docx"), "Jadval")
        check("html_to_pdf", converters.html_to_pdf, html_sample, str(tmp / "h.pdf"), "Jadval")
        check("html_to_clean_text", converters.html_to_clean_text, html_sample)

        # PDF Conversions
        import fitz
        pdf_path = str(tmp / "sample.pdf")
        doc = fitz.open()
        p = doc.new_page()
        p.insert_text((50, 80), "Salom PDF test!")
        doc.save(pdf_path)
        doc.close()

        check("pdf_to_docx", converters.pdf_to_docx, pdf_path, str(tmp / "p.docx"))
        check("pdf_to_xlsx", converters.pdf_to_xlsx, pdf_path, str(tmp / "p.xlsx"))
        check("pdf_to_txt", converters.pdf_to_txt, pdf_path, str(tmp / "p.txt"))
        check("pdf_to_html", converters.pdf_to_html, pdf_path, str(tmp / "p.html"))
        check("pdf_compress", converters.pdf_compress, pdf_path, str(tmp / "p_comp.pdf"))
        check("pdf_to_images", converters.pdf_to_images, pdf_path, str(tmp / "p_imgs"), "png")

        # Word DOCX Conversions
        import docx
        docx_path = str(tmp / "sample.docx")
        d = docx.Document()
        d.add_heading("Word Sarlavha", level=1)
        d.add_paragraph("Word matn qatori.")
        d.save(docx_path)

        check("docx_to_pdf", converters.docx_to_pdf, docx_path, str(tmp / "d.pdf"))
        check("docx_to_txt", converters.docx_to_txt, docx_path, str(tmp / "d.txt"))
        check("docx_to_html", converters.docx_to_html, docx_path, str(tmp / "d.html"))

        # Excel & CSV
        import pandas as pd
        xlsx_path = str(tmp / "sample.xlsx")
        df = pd.DataFrame({"Nomi": ["A", "B"], "Son": [10, 20]})
        df.to_excel(xlsx_path, index=False)

        check("xlsx_to_pdf", converters.xlsx_to_pdf, xlsx_path, str(tmp / "x.pdf"))
        check("xlsx_to_csv", converters.xlsx_to_csv, xlsx_path, str(tmp / "x.csv"))
        check("xlsx_to_json", converters.xlsx_to_json, xlsx_path, str(tmp / "x.json"))

        csv_path = str(tmp / "sample.csv")
        df.to_csv(csv_path, index=False)
        check("csv_to_xlsx", converters.csv_to_xlsx, csv_path, str(tmp / "c.xlsx"))
        check("csv_to_pdf", converters.csv_to_pdf, csv_path, str(tmp / "c.pdf"))

        # JSON & YAML
        json_path = str(tmp / "sample.json")
        with open(json_path, "w") as jf:
            jf.write('[{"id": 1, "val": "ok"}]')
        check("json_to_csv", converters.json_to_csv, json_path, str(tmp / "j.csv"))
        check("json_to_yaml", converters.json_to_yaml, json_path, str(tmp / "j.yaml"))

    # -------------------------------------------------------------
    # 3. Image, Audio, Video Converters
    # -------------------------------------------------------------
    print(f"\n--- [Round {round_num}] 3. Image, Audio & Video Converters ---")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        
        # Image
        from PIL import Image
        img_path = str(tmp / "sample.png")
        im = Image.new("RGB", (100, 100), color=(10, 150, 80))
        im.save(img_path)

        for fmt in ["jpg", "webp", "pdf", "ico"]:
            check(f"convert_image_{fmt}", converters.convert_image_format, img_path, str(tmp / f"out.{fmt}"), fmt)
        check("convert_to_telegram_sticker", converters.convert_to_telegram_sticker, img_path, str(tmp / "stk.webp"))

        # Audio
        import subprocess
        aud_path = str(tmp / "sample.mp3")
        subprocess.run([
            FFMPEG_PATH, "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=1", aud_path
        ], capture_output=True)

        check("convert_audio_wav", converters.convert_audio, aud_path, str(tmp / "out.wav"), "wav")
        check("audio_to_voice_note", converters.audio_to_voice_note, aud_path, str(tmp / "out.ogg"))
        check("change_audio_speed", converters.change_audio_speed, aud_path, str(tmp / "spd.mp3"), 1.2)

        # Video
        vid_path = str(tmp / "sample.mp4")
        subprocess.run([
            FFMPEG_PATH, "-y", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=10",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-t", "1", "-pix_fmt", "yuv420p", vid_path
        ], capture_output=True)

        check("video_to_mp3", converters.video_to_mp3, vid_path, str(tmp / "v.mp3"))
        check("video_to_voice", converters.video_to_voice, vid_path, str(tmp / "v.ogg"))
        check("video_to_gif", converters.video_to_gif, vid_path, str(tmp / "v.gif"))
        check("video_to_round_note", converters.video_to_round_note, vid_path, str(tmp / "v_note.mp4"))
        check("compress_video", converters.compress_video, vid_path, str(tmp / "v_comp.mp4"), target_mb=1.0)

    print(f"\n>>> ROUND {round_num} RESULT: {passed} passed, {failed} failed (Total: {passed+failed})")
    return failed == 0

def main():
    print("=" * 65)
    print("  AUTOMATED 3-ROUND COMPREHENSIVE CONVERTER & URL TEST SUITE")
    print("=" * 65)
    
    all_ok = True
    for r in range(1, 4):
        ok = run_round(r)
        if not ok:
            all_ok = False
            print(f"❌ ROUND {r} ENCOUNTERED FAILURES! Halting.")
            break
        print(f"🎉 ROUND {r} COMPLETED WITH ZERO ERRORS!\n")
        time.sleep(1)

    if all_ok:
        print("=" * 65)
        print("🏆 100% TEST PASS RATE! ALL 3 ROUNDS SUCCEEDED COMPLETELY!")
        print("=" * 65)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
