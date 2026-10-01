import os
import html
import zipfile
import uuid
from pathlib import Path
import docx
from docx.shared import Inches
import pymupdf  # PyMuPDF
import pandas as pd
from pptx import Presentation
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register fonts for proper Unicode (Uzbek, Cyrillic, etc.) support
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
            pdfmetrics.registerFont(TTFont("CustomUnicodeFont", fp))
            FONT_NAME = "CustomUnicodeFont"
            break
except Exception as e:
    print(f"Font registration warning: {e}")

def get_base_styles():
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1f2937')
    )
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontName=FONT_NAME,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#111827'),
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=10,
        spaceAfter=6
    )
    return normal_style, title_style, heading_style

# ----------------- PDF CONVERSIONS -----------------

def pdf_to_docx(input_path: str, output_path: str) -> str:
    """Converts PDF to DOCX with high speed and memory safety, with image recovery if not standard PDF"""
    import gc
    success = False
    pdf_doc = None
    
    try:
        pdf_doc = pymupdf.open(input_path)
        page_count = len(pdf_doc)
    except Exception as e:
        print(f"PyMuPDF open error: {e}. Checking if file is an image disguised as PDF...")
        try:
            from PIL import Image
            img = Image.open(input_path)
            w_doc = docx.Document()
            t_img = f"/tmp/p_{uuid.uuid4().hex[:8]}.jpg"
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            img.save(t_img, "JPEG")
            w_doc.add_picture(t_img, width=Inches(6.2))
            w_doc.save(output_path)
            if os.path.exists(t_img):
                os.remove(t_img)
            return output_path
        except Exception:
            raise ValueError("Ushbu fayl haqiqiy PDF formati emas yoki fayl shikastlangan.")

    # Check if PDF contains extractable text
    total_text_len = 0
    sample_pages = min(page_count, 10)
    for p in range(sample_pages):
        total_text_len += len(pdf_doc[p].get_text().strip())
    has_text = total_text_len > 30

    # 1. For small documents with text (<= 15 pages), try pdf2docx for exact layout
    if has_text and page_count <= 15:
        try:
            from pdf2docx import Converter
            cv = Converter(input_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                success = True
        except Exception as e:
            print(f"pdf2docx primary engine error: {e}")

    # 2. For multi-page books (>15 pages) or if pdf2docx failed: fast PyMuPDF text & block extraction
    if not success and has_text:
        try:
            print(f"Using fast PyMuPDF block extraction for {page_count}-page PDF...")
            w_doc = docx.Document()
            
            for page_idx in range(page_count):
                page = pdf_doc[page_idx]
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))
                
                for b in blocks:
                    if len(b) > 4 and b[4].strip():
                        txt = b[4].strip()
                        if len(txt) < 80 and "\n" not in txt and (txt.isupper() or txt.istitle()):
                            w_doc.add_heading(txt, level=2)
                        else:
                            w_doc.add_paragraph(txt)
                            
                if page_idx < page_count - 1:
                    w_doc.add_page_break()
                    
            w_doc.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                success = True
        except Exception as e:
            print(f"PyMuPDF block extraction error: {e}")

    # 3. Fallback for scanned PDFs (no text at all): embed downscaled page images
    if not success:
        print("Using downscaled image-based DOCX fallback for scanned PDF...")
        try:
            w_doc = docx.Document()
            max_scanned_pages = min(page_count, 35)
            temp_imgs = []
            
            for i in range(max_scanned_pages):
                page = pdf_doc[i]
                pix = page.get_pixmap(dpi=96)
                t_img = f"/tmp/p_{uuid.uuid4().hex[:8]}_{i}.jpg"
                pix.save(t_img)
                temp_imgs.append(t_img)
                if i > 0:
                    w_doc.add_page_break()
                w_doc.add_picture(t_img, width=Inches(6.2))
                
                if (i + 1) % 5 == 0:
                    gc.collect()
                    
            if page_count > max_scanned_pages:
                w_doc.add_paragraph(f"\n[Eslatma: PDF {page_count} sahifali scanned hujjat bo'lgani sababli dastlabki {max_scanned_pages} sahifasi kiritildi]")
                
            w_doc.save(output_path)
            for ti in temp_imgs:
                if os.path.exists(ti):
                    try:
                        os.remove(ti)
                    except Exception:
                        pass
            success = True
        except Exception as e:
            print(f"Scanned fallback error: {e}")

    if pdf_doc:
        pdf_doc.close()
    gc.collect()
    return output_path

def pdf_to_txt(input_path: str, output_path: str) -> str:
    """Extracts text from PDF quickly. If scanned or disguised image, falls back to RapidOCR."""
    doc = None
    try:
        doc = pymupdf.open(input_path)
        full_text = []
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                full_text.append(f"--- [Sahifa {page_num}] ---\n" + text.strip())
        
        if not full_text:
            try:
                from rapidocr_onnxruntime import RapidOCR
                import numpy as np
                ocr = RapidOCR()
                max_ocr_pages = min(len(doc), 10)
                for page_num in range(1, max_ocr_pages + 1):
                    page = doc[page_num - 1]
                    pix = page.get_pixmap(dpi=120)
                    img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, pix.n))
                    if pix.n == 4:
                        img_data = img_data[:, :, :3]
                    result, _ = ocr(img_data)
                    if result:
                        lines = [item[1] for item in result if len(item) > 1 and item[1].strip()]
                        if lines:
                            full_text.append(f"--- [Sahifa {page_num} (OCR)] ---\n" + "\n".join(lines))
            except Exception as ocr_err:
                print(f"PDF OCR fallback error: {ocr_err}")
                
        doc.close()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(full_text) if full_text else "Faylda matn topilmadi.")
        return output_path
    except Exception as e:
        # Check if it's an image
        try:
            from PIL import Image
            from rapidocr_onnxruntime import RapidOCR
            import numpy as np
            img = Image.open(input_path)
            ocr = RapidOCR()
            result, _ = ocr(np.array(img.convert("RGB")))
            lines = [item[1] for item in result] if result else ["Rasmda matn topilmadi."]
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return output_path
        except Exception:
            raise ValueError("Ushbu fayl haqiqiy PDF formati emas yoki fayl shikastlangan.")

def pdf_to_images(input_path: str, output_dir: str, fmt: str = "png") -> str:
    """Converts PDF pages to PNG/JPG. If image disguised as PDF, extracts directly."""
    import gc
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        doc = pymupdf.open(input_path)
    except Exception as e:
        print(f"PyMuPDF open error: {e}. Attempting direct image recovery...")
        try:
            from PIL import Image
            img = Image.open(input_path)
            out_img = output_dir_path / f"image_1.{fmt}"
            if fmt.lower() in ["jpg", "jpeg"] and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            img.save(str(out_img))
            return str(out_img)
        except Exception:
            raise ValueError("Ushbu fayl haqiqiy PDF formati emas yoki fayl shikastlangan.")

    img_paths = []
    page_count = len(doc)
    max_pages = min(page_count, 40)
    zoom = 1.5 if page_count > 10 else 2.0
    mat = pymupdf.Matrix(zoom, zoom)
    
    for i in range(max_pages):
        page = doc[i]
        pix = page.get_pixmap(matrix=mat)
        out_img = output_dir_path / f"page_{i + 1:03d}.{fmt}"
        pix.save(str(out_img))
        img_paths.append(str(out_img))
        if (i + 1) % 10 == 0:
            gc.collect()
            
    doc.close()
    gc.collect()

    if len(img_paths) == 1:
        return img_paths[0]
    
    zip_path = output_dir_path / "pdf_sahifalari.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in img_paths:
            zf.write(p, arcname=Path(p).name)
    return str(zip_path)

def pdf_to_html(input_path: str, output_path: str) -> str:
    """Converts PDF pages to readable HTML structure, supports image-based PDFs"""
    try:
        doc = pymupdf.open(input_path)
        html_parts = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>PDF Hujjati</title>",
            "<style>body{font-family:sans-serif;max-width:800px;margin:2rem auto;padding:1rem;line-height:1.6;color:#333;}",
            ".page{border-bottom:2px dashed #ccc;padding:1.5rem 0;margin-bottom:1rem;}",
            ".page-num{font-weight:bold;color:#2563eb;margin-bottom:0.5rem;}</style></head><body>"
        ]
        for i, page in enumerate(doc, 1):
            text = page.get_text("html")
            html_parts.append(f"<div class='page'><div class='page-num'>Sahifa {i}</div>{text}</div>")
        html_parts.append("</body></html>")
        doc.close()
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_parts))
        return output_path
    except Exception:
        try:
            import base64
            from PIL import Image
            img = Image.open(input_path)
            with open(input_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            content = f"<!DOCTYPE html><html><body style='text-align:center;padding:2rem;'><img src='data:image/jpeg;base64,{b64}' style='max-width:100%;border-radius:8px;'/></body></html>"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return output_path
        except Exception:
            raise ValueError("Ushbu fayl haqiqiy PDF formati emas yoki fayl shikastlangan.")

def pdf_compress(input_path: str, output_path: str) -> str:
    """Compresses PDF document or image-based PDF"""
    try:
        doc = pymupdf.open(input_path)
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        return output_path
    except Exception:
        try:
            from PIL import Image
            img = Image.open(input_path)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            img.save(output_path, "JPEG", quality=65)
            return output_path
        except Exception:
            raise ValueError("Ushbu fayl haqiqiy PDF formati emas yoki fayl shikastlangan.")

# ----------------- DOCX CONVERSIONS -----------------

def docx_to_pdf(input_path: str, output_path: str) -> str:
    """Converts DOCX to PDF preserving styling, headings, and tables"""
    normal_style, title_style, heading_style = get_base_styles()
    
    try:
        in_doc = docx.Document(input_path)
        pdf = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        story = []
        
        for element in in_doc.element.body:
            if element.tag.endswith('p'):
                p = docx.text.paragraph.Paragraph(element, in_doc)
                runs_html = []
                for r in p.runs:
                    t = html.escape(r.text)
                    if not t:
                        continue
                    if r.bold and r.italic:
                        t = f"<b><i>{t}</i></b>"
                    elif r.bold:
                        t = f"<b>{t}</b>"
                    elif r.italic:
                        t = f"<i>{t}</i>"
                    runs_html.append(t)
                
                line = "".join(runs_html).strip()
                if not line:
                    story.append(Spacer(1, 6))
                    continue
                
                style_name = (p.style.name or "").lower()
                if "title" in style_name:
                    story.append(Paragraph(line, title_style))
                elif "heading 1" in style_name:
                    h1_style = ParagraphStyle('H1', parent=heading_style, fontSize=15, spaceBefore=12)
                    story.append(Paragraph(line, h1_style))
                elif "heading" in style_name:
                    story.append(Paragraph(line, heading_style))
                else:
                    story.append(Paragraph(line, normal_style))
                    story.append(Spacer(1, 5))
                    
            elif element.tag.endswith('tbl'):
                t = docx.table.Table(element, in_doc)
                table_data = []
                for row in t.rows:
                    row_cells = []
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        row_cells.append(Paragraph(html.escape(cell_text), normal_style))
                    table_data.append(row_cells)
                
                if table_data:
                    col_count = len(table_data[0]) if table_data else 1
                    col_width = 520 / max(col_count, 1)
                    tbl = Table(table_data, colWidths=[col_width] * col_count)
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(Spacer(1, 8))
                    story.append(tbl)
                    story.append(Spacer(1, 10))

        if not story:
            story.append(Paragraph("Hujjat bo'sh.", normal_style))

        pdf.build(story)
    except Exception as docx_err:
        print(f"DOCX to PDF detailed parse failed, using plain-text fallback: {docx_err}")
        # Plain text fallback
        in_doc = docx.Document(input_path)
        pdf = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        for p in in_doc.paragraphs:
            if p.text.strip():
                story.append(Paragraph(html.escape(p.text), normal_style))
                story.append(Spacer(1, 6))
        if not story:
            story.append(Paragraph("Hujjat bo'sh.", normal_style))
        pdf.build(story)

    return output_path

def docx_to_txt(input_path: str, output_path: str) -> str:
    """Extracts text from DOCX document"""
    doc = docx.Document(input_path)
    lines = []
    for p in doc.paragraphs:
        if p.text.strip():
            lines.append(p.text)
    for t in doc.tables:
        lines.append("\n--- [Jadval] ---")
        for r in t.rows:
            row_txt = [c.text.strip() for c in r.cells]
            lines.append(" | ".join(row_txt))
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(lines))
    return output_path

def docx_to_html(input_path: str, output_path: str) -> str:
    """Converts DOCX to formatted HTML file"""
    doc = docx.Document(input_path)
    html_lines = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<style>body{font-family:system-ui,-apple-system,sans-serif;max-width:850px;margin:2rem auto;padding:1.5rem;line-height:1.7;color:#1f2937;background:#f9fafb;}",
        ".content{background:#fff;padding:2.5rem;border-radius:12px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);}",
        "h1{color:#1e40af;} table{border-collapse:collapse;width:100%;margin:1.5rem 0;} th,td{border:1px solid #e5e7eb;padding:8px 12px;text-align:left;} th{background:#f3f4f6;}</style></head><body><div class='content'>"
    ]
    for p in doc.paragraphs:
        if not p.text.strip():
            continue
        line = html.escape(p.text)
        style = (p.style.name or "").lower()
        if "title" in style or "heading 1" in style:
            html_lines.append(f"<h1>{line}</h1>")
        elif "heading 2" in style:
            html_lines.append(f"<h2>{line}</h2>")
        elif "heading" in style:
            html_lines.append(f"<h3>{line}</h3>")
        else:
            html_lines.append(f"<p>{line}</p>")
            
    for t in doc.tables:
        html_lines.append("<table>")
        for i, r in enumerate(t.rows):
            tag = "th" if i == 0 else "td"
            cells = "".join(f"<{tag}>{html.escape(c.text.strip())}</{tag}>" for c in r.cells)
            html_lines.append(f"<tr>{cells}</tr>")
        html_lines.append("</table>")
        
    html_lines.append("</div></body></html>")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))
    return output_path

def docx_to_images(input_path: str, output_dir: str) -> str:
    """Converts DOCX to PDF then renders pages as PNG images"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    temp_pdf = Path(output_dir) / "temp_preview.pdf"
    docx_to_pdf(input_path, str(temp_pdf))
    res = pdf_to_images(str(temp_pdf), output_dir, fmt="png")
    if temp_pdf.exists():
        temp_pdf.unlink()
    return res

# ----------------- EXCEL & CSV CONVERSIONS -----------------

def xlsx_to_csv(input_path: str, output_path: str) -> str:
    """Converts XLSX sheet to CSV"""
    df = pd.read_excel(input_path)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path

def xlsx_to_json(input_path: str, output_path: str) -> str:
    """Converts XLSX to JSON"""
    df = pd.read_excel(input_path)
    df.to_json(output_path, orient="records", indent=2, force_ascii=False)
    return output_path

def xlsx_to_html(input_path: str, output_path: str) -> str:
    """Converts XLSX to styled HTML table"""
    excel = pd.ExcelFile(input_path)
    html_parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<style>body{font-family:sans-serif;margin:2rem;background:#f8fafc;color:#1e293b;}",
        ".sheet-title{font-size:1.4rem;font-weight:bold;margin:1.5rem 0 0.5rem;color:#2563eb;}",
        "table{border-collapse:collapse;width:100%;background:#fff;margin-bottom:2rem;box-shadow:0 1px 3px rgba(0,0,0,0.1);border-radius:8px;overflow:hidden;}",
        "th,td{border:1px solid #e2e8f0;padding:10px 14px;text-align:left;font-size:0.9rem;} th{background:#f1f5f9;font-weight:600;color:#334155;}",
        "tr:nth-child(even){background:#f8fafc;}</style></head><body>"
    ]
    for sheet_name in excel.sheet_names:
        df = pd.read_excel(input_path, sheet_name=sheet_name)
        html_parts.append(f"<div class='sheet-title'>Varaq: {sheet_name}</div>")
        html_parts.append(df.to_html(index=False, classes="table", border=0))
    html_parts.append("</body></html>")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    return output_path

def xlsx_to_pdf(input_path: str, output_path: str) -> str:
    """Converts Excel sheet to styled landscape PDF table"""
    normal_style, title_style, heading_style = get_base_styles()
    excel = pd.ExcelFile(input_path)
    
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )
    story = []
    
    for sheet_name in excel.sheet_names:
        df = pd.read_excel(input_path, sheet_name=sheet_name).fillna("")
        if df.empty:
            continue
            
        story.append(Paragraph(f"<b>Varaq: {html.escape(sheet_name)}</b>", heading_style))
        story.append(Spacer(1, 8))
        
        headers = [Paragraph(f"<b>{html.escape(str(c))}</b>", normal_style) for c in df.columns]
        data = [headers]
        
        max_rows = min(len(df), 100)
        for i in range(max_rows):
            row_items = [Paragraph(html.escape(str(val)), normal_style) for val in df.iloc[i]]
            data.append(row_items)
            
        col_count = len(df.columns)
        col_width = max(790 / max(col_count, 1), 60)
        
        t = Table(data, colWidths=[col_width] * col_count, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
        
    if not story:
        story.append(Paragraph("Jadvalda ma'lumot topilmadi.", normal_style))
        
    pdf.build(story)
    return output_path

def csv_to_xlsx(input_path: str, output_path: str) -> str:
    """Converts CSV to Excel XLSX"""
    df = pd.read_csv(input_path)
    df.to_excel(output_path, index=False)
    return output_path

def csv_to_json(input_path: str, output_path: str) -> str:
    """Converts CSV to JSON"""
    df = pd.read_csv(input_path)
    df.to_json(output_path, orient="records", indent=2, force_ascii=False)
    return output_path

def csv_to_html(input_path: str, output_path: str) -> str:
    """Converts CSV to HTML"""
    df = pd.read_csv(input_path)
    html_content = df.to_html(index=False)
    styled_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>body{{font-family:sans-serif;margin:2rem;}} table{{border-collapse:collapse;width:100%;}} th,td{{border:1px solid #ccc;padding:8px;text-align:left;}} th{{background:#eee;}}</style></head><body>{html_content}</body></html>"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(styled_html)
    return output_path

def csv_to_pdf(input_path: str, output_path: str) -> str:
    """Converts CSV to PDF table"""
    temp_xlsx = Path(output_path).with_suffix(".tmp.xlsx")
    csv_to_xlsx(input_path, str(temp_xlsx))
    res = xlsx_to_pdf(str(temp_xlsx), output_path)
    if temp_xlsx.exists():
        temp_xlsx.unlink()
    return res

# ----------------- POWERPOINT (PPTX) CONVERSIONS -----------------

def pptx_to_txt(input_path: str, output_path: str) -> str:
    """Extracts all text from PowerPoint presentation"""
    prs = Presentation(input_path)
    text_content = []
    for i, slide in enumerate(prs.slides, 1):
        slide_text = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    t = paragraph.text.strip()
                    if t:
                        slide_text.append(t)
        if slide_text:
            text_content.append(f"--- [Slayd {i}] ---\n" + "\n".join(slide_text))
            
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(text_content) if text_content else "Taqdimotda matn topilmadi.")
    return output_path

def pptx_to_pdf(input_path: str, output_path: str) -> str:
    """Renders PPTX slides into a landscape PDF summary"""
    normal_style, title_style, heading_style = get_base_styles()
    prs = Presentation(input_path)
    
    pdf = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    story = []
    
    for i, slide in enumerate(prs.slides, 1):
        story.append(Paragraph(f"<b>Slayd {i}</b>", title_style))
        story.append(Spacer(1, 10))
        
        has_content = False
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    t = paragraph.text.strip()
                    if t:
                        story.append(Paragraph(f"• {html.escape(t)}", normal_style))
                        story.append(Spacer(1, 6))
                        has_content = True
        if not has_content:
            story.append(Paragraph("<i>(Bu slaydda matn yo'q)</i>", normal_style))
        story.append(Spacer(1, 20))
        
    if not story:
        story.append(Paragraph("Taqdimot bo'sh.", normal_style))
        
    pdf.build(story)
    return output_path

def pdf_to_xlsx(input_path: str, output_path: str) -> str:
    """Extracts tables or structured content from PDF and converts to Excel XLSX"""
    import re
    doc = pymupdf.open(input_path)
    all_dfs = []
    try:
        for page_idx, page in enumerate(doc):
            tabs = page.find_tables()
            for t_idx, tab in enumerate(tabs):
                df = tab.extract()
                if df and len(df) > 1:
                    header = [str(h or f"Ustun_{i+1}") for i, h in enumerate(df[0])]
                    rows = df[1:]
                    all_dfs.append((f"Sahifa{page_idx+1}_Jadval{t_idx+1}", pd.DataFrame(rows, columns=header)))
        
        if not all_dfs:
            # Fallback: extract text lines
            lines = []
            for page in doc:
                lines.extend(page.get_text().splitlines())
            all_dfs.append(("Matn", pd.DataFrame({"Matn": [l for l in lines if l.strip()]})))

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet_name, df in all_dfs:
                clean_name = re.sub(r'[\/\\?*:[\]]', '', sheet_name)[:31]
                df.to_excel(writer, sheet_name=clean_name or "Sheet1", index=False)
    finally:
        doc.close()
    return output_path

def docx_to_speech(input_path: str, output_path: str) -> str:
    """Extracts text from DOCX and converts to MP3 voice audio via gTTS"""
    doc = docx.Document(input_path)
    full_text = []
    for para in doc.paragraphs:
        t = para.text.strip()
        if t:
            full_text.append(t)
    content = "\n".join(full_text)
    if not content:
        content = "Ushbu hujjatda o'qiladigan matn topilmadi."
    if len(content) > 4000:
        content = content[:4000]
    from gtts import gTTS
    tts = gTTS(text=content, lang="tr")
    tts.save(output_path)
    return output_path

def pptx_to_images(input_path: str, output_dir: str) -> str:
    """Converts presentation slides to images and zips them"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    prs = Presentation(input_path)
    normal_style, title_style, _ = get_base_styles()
    import zipfile
    out_zip = str(Path(output_dir) / "taqdimot_slaydlari.zip")
    temp_pdf = str(Path(output_dir) / "slides_temp.pdf")
    pptx_to_pdf(input_path, temp_pdf)
    
    # Render PDF pages to PNG
    doc = pymupdf.open(temp_pdf)
    img_files = []
    try:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            img_p = str(Path(output_dir) / f"slayd_{i+1}.png")
            pix.save(img_p)
            img_files.append(img_p)
    finally:
        doc.close()
        if os.path.exists(temp_pdf):
            os.remove(temp_pdf)

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for im in img_files:
            zf.write(im, arcname=Path(im).name)
            
    return out_zip
