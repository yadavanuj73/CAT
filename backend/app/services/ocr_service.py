"""
PDF Extraction and OCR Service.
Uses PyMuPDF (fitz) for text and structure extraction,
with OCR image fallback for scanned pages.
Calculates extraction confidence and marks uncertain results.
"""

import io
import os
from typing import Dict, List, Tuple
import fitz  # PyMuPDF
from PIL import Image

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def extract_pages_from_pdf(file_path: str) -> List[Dict]:
    """
    Extract page content, images, and evaluate digital text quality.
    Returns list of page dicts with:
    { page_num, text, is_scanned, confidence, image_count }
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    doc = fitz.open(file_path)
    pages = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text").strip()
        images = page.get_images()

        is_scanned = False
        confidence = 0.95

        # Heuristic: if page has very little text but contains an image, it is scanned
        if len(text) < 80 and len(images) > 0:
            is_scanned = True
            # Attempt OCR if pytesseract is installed
            if PYTESSERACT_AVAILABLE:
                try:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    ocr_text = pytesseract.image_to_string(img)
                    if len(ocr_text.strip()) > len(text):
                        text = ocr_text.strip()
                        confidence = 0.75  # OCR extractions receive lower base confidence
                    else:
                        confidence = 0.60
                except Exception:
                    confidence = 0.40
            else:
                confidence = 0.45

        # Penalize strange non-printable or replacement character rates
        if text:
            replacement_chars = text.count("") + text.count("?")
            if len(text) > 0 and (replacement_chars / len(text)) > 0.05:
                confidence = max(0.2, confidence - 0.3)

        pages.append({
            "page_num": page_idx + 1,
            "text": text,
            "is_scanned": is_scanned,
            "confidence": round(confidence, 2),
            "image_count": len(images),
        })

    doc.close()
    return pages


def compute_overall_confidence(pages: List[Dict]) -> float:
    """Compute weighted overall confidence across all pages."""
    if not pages:
        return 0.0
    total_conf = sum(p["confidence"] for p in pages)
    return round(total_conf / len(pages), 2)
