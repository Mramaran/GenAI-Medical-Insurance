"""ClaimChain API — FastAPI application entry point."""

import os
import sys
from dotenv import load_dotenv

# Load .env FIRST, before any other imports that depend on env vars
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.claims import router as claims_router
from routes.review import router as review_router
from routes.chat import router as chat_router

app = FastAPI(
    title="ClaimChain API",
    description="GenAI-powered medical insurance claims with on-chain proof",
    version="1.0.0",
)

# CORS — allow React dev server and common deployment origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(claims_router)
app.include_router(review_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "ClaimChain API is running", "version": "1.0.0"}


@app.on_event("startup")
async def startup():
    print("ClaimChain API running on http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print(f"Python: {sys.executable}")
    print(f"USE_GEMINI: {os.getenv('USE_GEMINI')}")
    # Verify Gemini package is available
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("langchain-google-genai: OK")
    except ImportError as e:
        print(f"langchain-google-genai: MISSING — {e}")
        print(f"sys.path: {sys.path[:5]}")
