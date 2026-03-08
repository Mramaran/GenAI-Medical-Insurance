"""Policy Q&A chatbot endpoint using existing RAG agent."""

import asyncio
import sys
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add RAG module to path once at import time (thread-safe)
_rag_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "RAG"))
if _rag_path not in sys.path:
    sys.path.insert(0, _rag_path)

from agent import query_agent  # noqa: E402

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """
    Ask a question about the insurance policy.
    Uses the existing RAG agent to retrieve and answer from policy documents.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Run synchronous LLM call in a thread pool to avoid blocking the event loop
        answer = await asyncio.to_thread(query_agent, body.question.strip())
        return ChatResponse(answer=answer)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Chat failed. Ensure Ollama is running with the mistral model.",
        )
