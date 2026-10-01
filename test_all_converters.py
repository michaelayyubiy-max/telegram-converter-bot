import os
import sys
import tempfile
import traceback
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path("/Users/macbook/.gemini/antigravity-ide/scratch/telegram-converter-bot")
sys.path.insert(0, str(BASE_DIR))

import converters
from utils.helpers import get_temp_path, get_temp_dir

def run_tests():
    passed = 0
    failed = 0
    results = []

    def test(name, func, *args, **kwargs):
        nonlocal passed, failed
        try:
            res = func(*args, **kwargs)
            passed += 1
            results.append((name, "SUCCESS", None))
            print(f"✅ {name}: SUCCESS")
            return res
        except Exception as e:
            failed += 1
            results.append((name, "FAILED", str(e)))
            print(f"❌ {name}: FAILED -> {e}")
            traceback.print_exc()
            return None

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        # 1. TEXT CONVERTERS
        sample_text = "Salom Dunyo! Bu test uchun matn.\nIkkinchi qator."
        txt_pdf = str(tmp / "test_text.pdf")
        test("text_to_pdf", converters.text_to_pdf, sample_text, txt_pdf)

        txt_docx = str(tmp / "test_text.docx")
        test("text_to_docx", converters.text_to_docx, sample_text, txt_docx)

        txt_tts = str(tmp / "test_text.mp3")
        test("text_to_speech", converters.text_to_speech, sample_text, txt_tts)

        txt_qr = str(tmp / "test_qr.png")
        test("text_to_qr", converters.text_to_qr, sample_text, txt_qr)

        # JSON / YAML
        json_file = str(tmp / "data.json")
        with open(json_file, "w") as f:
            f.write('[{"ism": "Ali", "yosh": 25}, {"ism": "Vali", "yosh": 30}]')
        
        json_csv = str(tmp / "data.csv")
        test("json_to_csv", converters.json_to_csv, json_file, json_csv)

        json_yaml = str(tmp / "data.yaml")
        test("json_to_yaml", converters.json_to_yaml, json_file, json_yaml)

        test("yaml_to_json", converters.yaml_to_json, json_yaml, str(tmp / "back.json"))

        # 2. PDF CONVERTERS
        # Create a sample PDF with ReportLab or PyMuPDF
        import pymupdf
        pdf_path = str(tmp / "sample.pdf")
        doc = pymupdf.open()
        p = doc.new_page()
        p.insert_text((50, 50), "Salom PDF test!")
        p.insert_text((50, 80), "Bu test qatori.")
        doc.save(pdf_path)
        doc.close()

        test("pdf_to_docx", converters.pdf_to_docx, pdf_path, str(tmp / "pdf_out.docx"))
        test("pdf_to_xlsx", converters.pdf_to_xlsx, pdf_path, str(tmp / "pdf_out.xlsx"))
        test("pdf_to_txt", converters.pdf_to_txt, pdf_path, str(tmp / "pdf_out.txt"))
        test("pdf_to_html", converters.pdf_to_html, pdf_path, str(tmp / "pdf_out.html"))
        test("pdf_compress", converters.pdf_compress, pdf_path, str(tmp / "pdf_compressed.pdf"))
        test("pdf_to_images", converters.pdf_to_images, pdf_path, str(tmp / "pdf_imgs"), "png")

        # 3. DOCX CONVERTERS
        import docx
        docx_path = str(tmp / "sample.docx")
        d = docx.Document()
        d.add_heading("Sarlavha", level=1)
        d.add_paragraph("Bu Word hujjat matni.")
        d.save(docx_path)

        test("docx_to_pdf", converters.docx_to_pdf, docx_path, str(tmp / "docx_out.pdf"))
        test("docx_to_txt", converters.docx_to_txt, docx_path, str(tmp / "docx_out.txt"))
        test("docx_to_html", converters.docx_to_html, docx_path, str(tmp / "docx_out.html"))
        test("docx_to_images", converters.docx_to_images, docx_path, str(tmp / "docx_imgs"))
        test("docx_to_speech", converters.docx_to_speech, docx_path, str(tmp / "docx_out.mp3"))

        # 4. EXCEL / CSV CONVERTERS
        import pandas as pd
        xlsx_path = str(tmp / "sample.xlsx")
        df = pd.DataFrame({"Ism": ["Ali", "Vali"], "Ball": [85, 92]})
        df.to_excel(xlsx_path, index=False)

        test("xlsx_to_pdf", converters.xlsx_to_pdf, xlsx_path, str(tmp / "xlsx_out.pdf"))
        test("xlsx_to_csv", converters.xlsx_to_csv, xlsx_path, str(tmp / "xlsx_out.csv"))
        test("xlsx_to_json", converters.xlsx_to_json, xlsx_path, str(tmp / "xlsx_out.json"))
        test("xlsx_to_html", converters.xlsx_to_html, xlsx_path, str(tmp / "xlsx_out.html"))

        csv_path = str(tmp / "sample.csv")
        df.to_csv(csv_path, index=False)
        test("csv_to_xlsx", converters.csv_to_xlsx, csv_path, str(tmp / "csv_out.xlsx"))
        test("csv_to_pdf", converters.csv_to_pdf, csv_path, str(tmp / "csv_out.pdf"))
        test("csv_to_json", converters.csv_to_json, csv_path, str(tmp / "csv_out.json"))
        test("csv_to_html", converters.csv_to_html, csv_path, str(tmp / "csv_out.html"))

        # 5. PPTX CONVERTERS
        from pptx import Presentation
        prs_path = str(tmp / "sample.pptx")
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = "Taqdimot Test"
        prs.save(prs_path)

        test("pptx_to_pdf", converters.pptx_to_pdf, prs_path, str(tmp / "pptx_out.pdf"))
        test("pptx_to_txt", converters.pptx_to_txt, prs_path, str(tmp / "pptx_out.txt"))
        test("pptx_to_images", converters.pptx_to_images, prs_path, str(tmp / "pptx_imgs"))

        # 6. IMAGE CONVERTERS
        from PIL import Image, ImageDraw
        img_path = str(tmp / "sample.png")
        im = Image.new("RGB", (200, 200), color=(73, 109, 137))
        d = ImageDraw.Draw(im)
        d.text((10, 10), "Test", fill=(255, 255, 0))
        im.save(img_path)

        for fmt in ["jpg", "png", "webp", "bmp", "ico", "tiff", "pdf"]:
            test(f"convert_image_to_{fmt}", converters.convert_image_format, img_path, str(tmp / f"out.{fmt}"), fmt)

        test("convert_to_telegram_sticker", converters.convert_to_telegram_sticker, img_path, str(tmp / "sticker.webp"))
        test("convert_to_grayscale", converters.convert_to_grayscale, img_path, str(tmp / "gray.png"))
        test("invert_image_colors", converters.invert_image_colors, img_path, str(tmp / "invert.png"))
        test("compress_image", converters.compress_image, img_path, str(tmp / "compress.jpg"))
        test("scan_qr_code", converters.scan_qr_code, img_path)
        test("ocr_extract_text", converters.ocr_extract_text, img_path)

        # 7. AUDIO CONVERTERS (Create 1s test sine wave audio via ffmpeg)
        import subprocess
        from config import FFMPEG_PATH
        audio_path = str(tmp / "sample.mp3")
        subprocess.run([
            FFMPEG_PATH, "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
            audio_path
        ], capture_output=True)

        test("convert_audio_wav", converters.convert_audio, audio_path, str(tmp / "out.wav"), "wav")
        test("convert_audio_m4a", converters.convert_audio, audio_path, str(tmp / "out.m4a"), "m4a")
        test("convert_audio_flac", converters.convert_audio, audio_path, str(tmp / "out.flac"), "flac")
        test("audio_to_voice_note", converters.audio_to_voice_note, audio_path, str(tmp / "out.ogg"))
        test("change_audio_speed", converters.change_audio_speed, audio_path, str(tmp / "speed.mp3"), 1.25)
        test("boost_audio_volume", converters.boost_audio_volume, audio_path, str(tmp / "boost.mp3"), 1.5)

        # 8. VIDEO CONVERTERS (Create 2s test video via ffmpeg)
        video_path = str(tmp / "sample.mp4")
        subprocess.run([
            FFMPEG_PATH, "-y", "-f", "lavfi", "-i", "testsrc=size=320x240:rate=10",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
            "-t", "2", "-pix_fmt", "yuv420p",
            video_path
        ], capture_output=True)

        test("video_to_mp3", converters.video_to_mp3, video_path, str(tmp / "vid_out.mp3"))
        test("video_to_voice", converters.video_to_voice, video_path, str(tmp / "vid_out.ogg"))
        test("video_to_gif", converters.video_to_gif, video_path, str(tmp / "vid_out.gif"))
        test("video_to_round_note", converters.video_to_round_note, video_path, str(tmp / "vid_note.mp4"))
        test("compress_video", converters.compress_video, video_path, str(tmp / "vid_comp.mp4"))
        test("convert_video_format_mkv", converters.convert_video_format, video_path, str(tmp / "vid.mkv"), "mkv")
        test("convert_video_format_webm", converters.convert_video_format, video_path, str(tmp / "vid.webm"), "webm")
        test("mute_video", converters.mute_video, video_path, str(tmp / "vid_mute.mp4"))
        test("change_video_speed", converters.change_video_speed, video_path, str(tmp / "vid_fast.mp4"), 1.25)

        # 9. ARCHIVE CONVERTERS
        arc_zip = str(tmp / "test.zip")
        test("create_zip_archive", converters.create_zip_archive, [img_path, audio_path], arc_zip)
        test("extract_archive", converters.extract_archive, arc_zip, str(tmp / "extracted"))

        # 10. SOCIAL MEDIA & URL TESTS
        ig_url = "https://www.instagram.com/reel/Dd6XnDBIksU/"
        test("instagram_metadata", converters.get_url_metadata, ig_url)
        test("instagram_download_video", converters.download_social_media, ig_url, "video", str(tmp / "ig_vid"))
        test("instagram_download_mp3", converters.download_social_media, ig_url, "mp3", str(tmp / "ig_mp3"))

        yt_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        test("youtube_metadata", converters.get_url_metadata, yt_url)
        test("youtube_download_video", converters.download_social_media, yt_url, "video", str(tmp / "yt_vid"))
        test("youtube_download_mp3", converters.download_social_media, yt_url, "mp3", str(tmp / "yt_mp3"))

    print("\n" + "=" * 50)
    print(f"TOTAL TESTS: {passed + failed}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")
    print("=" * 50)

if __name__ == "__main__":
    run_tests()
