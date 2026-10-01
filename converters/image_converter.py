import os
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
import cv2

# Register HEIC / HEIF support for iPhone photos
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception as e:
    print(f"pillow_heif warning: {e}")

def load_image(input_path: str) -> Image.Image:
    """Loads image, adding native SVG rendering support via PyMuPDF"""
    ext = Path(input_path).suffix.lower()
    if ext == ".svg":
        import pymupdf
        with open(input_path, "rb") as f:
            svg_data = f.read()
        doc = pymupdf.open(stream=svg_data, filetype="svg")
        pix = doc[0].get_pixmap(dpi=200)
        im = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return im
    return Image.open(input_path)

def convert_image_format(input_path: str, output_path: str, target_format: str, quality: int = 90) -> str:
    """Converts image to target format (JPG, PNG, WEBP, BMP, ICO, TIFF, PDF)"""
    im = load_image(input_path)
    try:
        fmt = target_format.upper()
        
        # Format mapping & adjustments
        if fmt in ["JPG", "JPEG"]:
            if im.mode in ("RGBA", "LA", "P"):
                # Fill transparent with white
                bg = Image.new("RGB", im.size, (255, 255, 255))
                if im.mode == "P":
                    im = im.convert("RGBA")
                bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
                im = bg
            elif im.mode != "RGB":
                im = im.convert("RGB")
            im.save(output_path, "JPEG", quality=quality, optimize=True)
            
        elif fmt == "PNG":
            im.save(output_path, "PNG", optimize=True)
            
        elif fmt == "WEBP":
            im.save(output_path, "WEBP", quality=quality)
            
        elif fmt == "BMP":
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.save(output_path, "BMP")
            
        elif fmt == "ICO":
            if im.mode not in ("RGBA", "RGB"):
                im = im.convert("RGBA")
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            im.save(output_path, format="ICO", sizes=icon_sizes)
            
        elif fmt == "TIFF":
            im.save(output_path, "TIFF")
            
        elif fmt == "PDF":
            if im.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", im.size, (255, 255, 255))
                if im.mode == "P":
                    im = im.convert("RGBA")
                bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
                im = bg
            elif im.mode != "RGB":
                im = im.convert("RGB")
            im.save(output_path, "PDF", resolution=100.0)
            
        else:
            im.save(output_path, fmt)
            
    finally:
        im.close()
        
    return output_path

def convert_to_telegram_sticker(input_path: str, output_path: str) -> str:
    """Converts image to Telegram Sticker standard (WEBP, 512x512 max, transparent padding)"""
    im = load_image(input_path)
    try:
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        im.thumbnail((512, 512), Image.Resampling.LANCZOS)
        im.save(output_path, "WEBP")
    finally:
        im.close()
    return output_path

def convert_to_grayscale(input_path: str, output_path: str) -> str:
    """Converts image to Black & White (Grayscale)"""
    im = load_image(input_path)
    try:
        gray = ImageOps.grayscale(im)
        gray.save(output_path)
    finally:
        im.close()
    return output_path

def invert_image_colors(input_path: str, output_path: str) -> str:
    """Inverts image colors (negative effect)"""
    im = load_image(input_path)
    try:
        if im.mode == "RGBA":
            r, g, b, a = im.split()
            rgb_im = Image.merge("RGB", (r, g, b))
            inv = ImageOps.invert(rgb_im)
            r2, g2, b2 = inv.split()
            final_im = Image.merge("RGBA", (r2, g2, b2, a))
        else:
            rgb_im = im.convert("RGB")
            final_im = ImageOps.invert(rgb_im)
        final_im.save(output_path)
    finally:
        im.close()
    return output_path

def compress_image(input_path: str, output_path: str, quality: int = 40) -> str:
    """Compresses image to reduce file size significantly"""
    im = load_image(input_path)
    try:
        max_dim = 1920
        if max(im.size) > max_dim:
            im.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            if im.mode == "P":
                im = im.convert("RGBA")
            bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
            im = bg
        elif im.mode != "RGB":
            im = im.convert("RGB")
            
        im.save(output_path, "JPEG", quality=quality, optimize=True)
    finally:
        im.close()
    return output_path

def scan_qr_code(input_path: str) -> str:
    """Scans and reads QR code from an image"""
    img = cv2.imread(input_path)
    if img is None:
        return "Rasm formatini o'qib bo'lmadi."
        
    detector = cv2.QRCodeDetector()
    val, pts, qr_code = detector.detectAndDecode(img)
    if val:
        return val
    return "Rasmda QR-kod topilmadi."

def ocr_extract_text(input_path: str) -> str:
    """Extracts text from image using RapidOCR"""
    try:
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR()
        result, elapse = ocr(input_path)
        if not result:
            return "Rasm ichida hech qanday matn topilmadi."
            
        lines = [item[1] for item in result if len(item) > 1 and item[1].strip()]
        return "\n".join(lines) if lines else "Rasm ichida hech qanday matn topilmadi."
    except Exception as e:
        return f"Matnni ajratishda xatolik: {e}"
