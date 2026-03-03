"""
Retriever tool for the agentic RAG.
Loads the persistent ChromaDB vector store and exposes a LangChain tool.
"""

from langchain.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from rag_config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


def get_vector_store() -> Chroma:
    """Load the persistent ChromaDB vector store."""
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
    )
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
    return vector_store


def get_retriever():
    """Create a retriever from the vector store with MMR search."""
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 8},
    )
    return retriever


# Module-level retriever instance
_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = get_retriever()
    return _retriever


@tool
def retrieve_policy_info(query: str) -> str:
    """Search and return relevant health insurance policy information.

    Use this tool to find specific details about the HealthShield Plus
    insurance policy, including coverage, exclusions, premiums, claims
    procedures, eligibility, and other policy terms.

    Args:
        query: The search query about insurance policy details.
    """
    retriever = _get_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant policy information found for the given query."

    results = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        results.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(results)
