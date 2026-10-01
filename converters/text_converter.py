import os
import json
import yaml
import html
from pathlib import Path
import docx
import qrcode
from gtts import gTTS
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Font configuration
FONT_NAME = "Helvetica"
try:
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            pdfmetrics.registerFont(TTFont("CustomTextFont", fp))
            FONT_NAME = "CustomTextFont"
            break
except Exception:
    pass

def text_to_pdf(text: str, output_path: str, title: str = "Hujjat") -> str:
    """Converts raw text to styled A4 PDF"""
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'TxtNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#1f2937')
    )
    title_style = ParagraphStyle(
        'TxtTitle',
        parent=styles['Title'],
        fontName=FONT_NAME,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=15
    )
    
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = [Paragraph(html.escape(title), title_style)]
    for line in text.split("\n"):
        line = line.strip()
        if line:
            story.append(Paragraph(html.escape(line), normal_style))
            story.append(Spacer(1, 6))
        else:
            story.append(Spacer(1, 8))
            
    pdf.build(story)
    return output_path

def text_to_docx(text: str, output_path: str, title: str = "Hujjat") -> str:
    """Converts raw text to Word (.docx) document"""
    doc = docx.Document()
    if title:
        doc.add_heading(title, level=0)
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(output_path)
    return output_path

def text_to_speech(text: str, output_path: str, lang: str = "tr") -> str:
    """Converts text to speech MP3 audio"""
    # Supported languages in gTTS: 'tr', 'ru', 'en'
    tts = gTTS(text=text[:3000], lang=lang, slow=False)
    tts.save(output_path)
    return output_path

def text_to_qr(text: str, output_path: str) -> str:
    """Generates high quality QR code image from text or URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1e293b", back_color="white")
    img.save(output_path)
    return output_path

def json_to_csv(input_path: str, output_path: str) -> str:
    """Converts JSON array/object to CSV"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.json_normalize(data)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path

def json_to_yaml(input_path: str, output_path: str) -> str:
    """Converts JSON to YAML"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return output_path

def yaml_to_json(input_path: str, output_path: str) -> str:
    """Converts YAML to JSON"""
    with open(input_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output_path
