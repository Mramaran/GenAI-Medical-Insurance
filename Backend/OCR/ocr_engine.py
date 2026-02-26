"""
OCR engine: extracts raw text from images and PDFs.
- Images (JPG/PNG): Pillow preprocessing + pytesseract
- Scanned PDFs: pdf2image -> pytesseract per page
- Digital PDFs: PyMuPDF (fitz) direct text extraction
"""

from pathlib import Path

import pytesseract
import fitz  # PyMuPDF
from PIL import Image
from pdf2image import convert_from_path

from config import TESSERACT_CMD, POPPLER_PATH, IMAGE_DPI, MIN_TEXT_LENGTH
from preprocessor import preprocess_image, preprocess_from_path

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Supported file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"}
PDF_EXTENSIONS = {".pdf"}


def detect_file_type(file_path: str) -> str:
    """Determine how to process the file.

    Args:
        file_path: Path to the uploaded document.

    Returns:
        One of: 'image', 'digital_pdf', 'scanned_pdf'

    Raises:
        ValueError: If file type is not supported.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext in IMAGE_EXTENSIONS:
        return "image"

    if ext in PDF_EXTENSIONS:
        return _classify_pdf(file_path)

    raise ValueError(f"Unsupported file type: {ext}")


def _classify_pdf(file_path: str) -> str:
    """Check if a PDF is digital (has selectable text) or scanned."""
    doc = fitz.open(file_path)
    total_text = ""
    page_count = doc.page_count
    for page in doc:
        total_text += page.get_text()
    doc.close()

    avg_chars_per_page = len(total_text.strip()) / max(page_count, 1)
    if avg_chars_per_page >= MIN_TEXT_LENGTH:
        return "digital_pdf"
    return "scanned_pdf"


def extract_text_from_image(file_path: str) -> str:
    """OCR an image file using pytesseract with preprocessing.

    Args:
        file_path: Path to JPG/PNG/TIFF image.

    Returns:
        Extracted text string.
    """
    processed = preprocess_from_path(file_path)
    text = pytesseract.image_to_string(processed, lang="eng")
    return text.strip()


def extract_text_from_digital_pdf(file_path: str) -> str:
    """Extract text directly from a digital PDF using PyMuPDF.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Concatenated text from all pages.
    """
    doc = fitz.open(file_path)
    pages_text = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages_text.append(f"--- Page {page_num + 1} ---\n{text.strip()}")
    doc.close()
    return "\n\n".join(pages_text)


def extract_text_from_scanned_pdf(file_path: str) -> str:
    """OCR a scanned PDF by converting pages to images first.

    Args:
        file_path: Path to the scanned PDF.

    Returns:
        Concatenated OCR text from all pages.
    """
    convert_kwargs = {"dpi": IMAGE_DPI}
    if POPPLER_PATH:
        convert_kwargs["poppler_path"] = POPPLER_PATH

    images = convert_from_path(file_path, **convert_kwargs)
    pages_text = []
    for page_num, page_image in enumerate(images):
        processed = preprocess_image(page_image)
        text = pytesseract.image_to_string(processed, lang="eng")
        if text.strip():
            pages_text.append(f"--- Page {page_num + 1} ---\n{text.strip()}")
    return "\n\n".join(pages_text)


def extract_text(file_path: str) -> tuple[str, str]:
    """Main entry point: auto-detect file type and extract text.

    Args:
        file_path: Path to the uploaded document (image or PDF).

    Returns:
        Tuple of (extracted_text, extraction_method).
        extraction_method is one of: 'ocr_image', 'digital_pdf', 'ocr_scanned_pdf'
    """
    file_type = detect_file_type(file_path)

    if file_type == "image":
        text = extract_text_from_image(file_path)
        return text, "ocr_image"

    if file_type == "digital_pdf":
        text = extract_text_from_digital_pdf(file_path)
        return text, "digital_pdf"

    text = extract_text_from_scanned_pdf(file_path)
    return text, "ocr_scanned_pdf"
