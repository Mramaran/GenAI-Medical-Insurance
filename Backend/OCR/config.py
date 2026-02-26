import os
import platform
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
TEST_DOCS_DIR = BASE_DIR / "test_docs"

# --- Tesseract OCR ---
if platform.system() == "Windows":
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    TESSERACT_CMD = "tesseract"

# --- Poppler (required by pdf2image on Windows) ---
POPPLER_PATH = os.getenv("POPPLER_PATH", None)

# --- PDF/Image Settings ---
IMAGE_DPI = 300
MIN_TEXT_LENGTH = 50  # Below this per page, treat PDF as scanned

# --- spaCy ---
SPACY_MODEL = "en_core_web_sm"

# --- Ollama (shared config with RAG module) ---
LLM_MODEL = "mistral"
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_TEMPERATURE = 0
