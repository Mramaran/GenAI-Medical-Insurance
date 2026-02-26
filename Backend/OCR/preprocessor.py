"""
Image preprocessing for OCR quality improvement.
Uses Pillow for grayscale conversion, contrast enhancement,
noise reduction, and binarization.
"""

from PIL import Image, ImageFilter, ImageEnhance


def preprocess_image(image: Image.Image) -> Image.Image:
    """Full preprocessing pipeline for OCR.

    Args:
        image: PIL Image object (from file or pdf2image).

    Returns:
        Preprocessed PIL Image ready for pytesseract.
    """
    image = _convert_grayscale(image)
    image = _enhance_contrast(image)
    image = _remove_noise(image)
    image = _binarize(image)
    return image


def _convert_grayscale(image: Image.Image) -> Image.Image:
    """Convert to grayscale."""
    return image.convert("L")


def _enhance_contrast(image: Image.Image) -> Image.Image:
    """Increase contrast for faded text."""
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(2.0)


def _remove_noise(image: Image.Image) -> Image.Image:
    """Apply median filter to reduce noise."""
    return image.filter(ImageFilter.MedianFilter(size=3))


def _binarize(image: Image.Image) -> Image.Image:
    """Apply binary threshold for clean text extraction."""
    threshold = 150
    return image.point(lambda p: 255 if p > threshold else 0, mode="1")


def preprocess_from_path(image_path: str) -> Image.Image:
    """Load and preprocess an image from file path.

    Args:
        image_path: Path to the image file.

    Returns:
        Preprocessed PIL Image.
    """
    image = Image.open(image_path)
    return preprocess_image(image)
