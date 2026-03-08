import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = Path(__file__).parent
POLICIES_DIR = BASE_DIR / "policies"
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")

# --- ChromaDB ---
COLLECTION_NAME = "health_insurance_policies"

# --- Chunking ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- Ollama Models ---
LLM_MODEL = "mistral"
EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_BASE_URL = "http://localhost:11434"

# --- Gemini (demo mode — faster than local Ollama) ---
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
