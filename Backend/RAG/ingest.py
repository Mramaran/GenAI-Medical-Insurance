"""
Document ingestion pipeline for Health Insurance Policy RAG.
Loads markdown policy documents, chunks them, and stores in ChromaDB.
"""

import os
from uuid import uuid4
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from config import (
    POLICIES_DIR,
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
)


def load_policy_documents(policies_dir: Path) -> list[Document]:
    """Load all markdown files from the policies directory."""
    documents = []
    for file_path in sorted(policies_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        doc = Document(
            page_content=content,
            metadata={
                "source": file_path.name,
                "file_path": str(file_path),
            },
        )
        documents.append(doc)
        print(f"  Loaded: {file_path.name} ({len(content)} chars)")
    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split documents into chunks using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"  Split {len(documents)} documents into {len(chunks)} chunks")
    return chunks


def ingest_to_chromadb(chunks: list[Document]) -> Chroma:
    """Embed and store document chunks into ChromaDB."""
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
    )

    # Create persistent vector store
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )

    # Generate unique IDs for each chunk
    uuids = [str(uuid4()) for _ in range(len(chunks))]

    # Add documents to the vector store
    vector_store.add_documents(documents=chunks, ids=uuids)
    print(f"  Stored {len(chunks)} chunks in ChromaDB at '{CHROMA_PERSIST_DIR}'")

    return vector_store


def main():
    print("=" * 60)
    print("Health Insurance Policy - Document Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load documents
    print("\n[1/3] Loading policy documents...")
    documents = load_policy_documents(POLICIES_DIR)
    if not documents:
        print("  ERROR: No .md files found in", POLICIES_DIR)
        return

    # Step 2: Chunk documents
    print("\n[2/3] Chunking documents...")
    chunks = chunk_documents(documents)

    # Step 3: Ingest into ChromaDB
    print("\n[3/3] Ingesting into ChromaDB...")
    vector_store = ingest_to_chromadb(chunks)

    # Verification: quick test query
    print("\n" + "=" * 60)
    print("Verification - Test Query: 'What is the deductible?'")
    print("=" * 60)
    results = vector_store.similarity_search("What is the deductible?", k=2)
    for i, doc in enumerate(results):
        print(f"\n--- Result {i + 1} (source: {doc.metadata.get('source', 'N/A')}) ---")
        print(doc.page_content[:300] + "...")

    print("\n Ingestion complete!")


if __name__ == "__main__":
    main()
