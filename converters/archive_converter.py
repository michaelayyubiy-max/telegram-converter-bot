import os
import zipfile
import tarfile
from pathlib import Path
from typing import List, Tuple

def extract_archive(archive_path: str, extract_dir: str) -> Tuple[List[str], str]:
    """Extracts ZIP or TAR archive safely, returns list of extracted file paths and summary info"""
    ext_path = Path(extract_dir).resolve()
    ext_path.mkdir(parents=True, exist_ok=True)
    
    extracted_files = []
    
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, 'r') as zf:
            for member in zf.infolist():
                target_path = (ext_path / member.filename).resolve()
                if ext_path in target_path.parents or target_path == ext_path:
                    if not member.is_dir():
                        zf.extract(member, extract_dir)
                        extracted_files.append(str(target_path))
    elif tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, 'r:*') as tf:
            for member in tf.getmembers():
                target_path = (ext_path / member.name).resolve()
                if ext_path in target_path.parents or target_path == ext_path:
                    if member.isfile():
                        tf.extract(member, extract_dir)
                        extracted_files.append(str(target_path))
    else:
        raise ValueError("Noma'lum yoki qo'llab-quvvatlanmaydigan arxiv formati")
        
    summary = f"📦 Jami {len(extracted_files)} ta fayl arxivdan chiqarildi."
    return extracted_files, summary

def create_zip_archive(file_paths: List[str], output_zip: str) -> str:
    """Creates a ZIP archive containing the provided files"""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fp in file_paths:
            p = Path(fp)
            if p.exists() and p.is_file():
                zf.write(p, arcname=p.name)
    return output_zip
