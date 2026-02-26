# HealthShield Plus - Agentic RAG Setup Guide

## Prerequisites

- Python 3.10 or higher
- Ollama installed and running (https://ollama.com)

## Installation

### 1. Install and start Ollama

Download from https://ollama.com and install. Then pull the required models:

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

Make sure Ollama is running (it starts automatically on install).

### 2. Navigate to the RAG directory

```bash
cd "D:\Hackathons\TN IMPACT\GenAI Insurance V1\Backend\RAG"
```

### 3. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running

### Step 1: Ingest policy documents into ChromaDB

```bash
python ingest.py
```

This loads the placeholder policy documents from `policies/`, chunks them, and stores the embeddings in ChromaDB using `nomic-embed-text`.

### Step 2: Run the AI assistant

```bash
python main.py
```

### Example questions to try:

- "What is covered under the Gold tier?"
- "How do I file a cashless claim?"
- "What are the exclusions in this policy?"
- "What is the deductible for the Platinum plan?"
- "What is the waiting period for pre-existing conditions?"
- "How does the appeals process work?"
- "What are the premium rates for different tiers?"

## Architecture

```
User Question
     |
     v
+----------------------+
| generate_or_retrieve |  <- Mistral decides: retrieve or answer directly
+---------+------------+
          |
    +-----+-----+
    |  tools?   |
    +-----+-----+
     yes  |  no -> END
          v
+-----------------+
|    retrieve     |  <- ChromaDB vector search (MMR, k=4)
+--------+--------+
         v
+---------------------+
|  grade_documents    |  <- Mistral grades relevance
+--------+------------+
    +----+----+
    |relevant?|
    +----+----+
   yes   |   no
    v         v
+--------+  +------------------+
|generate|  |rewrite_question  | -> loops back to generate_or_retrieve
|_answer |  +------------------+
+----+---+
     v
    END
```

## Models Used

| Component   | Model             | Purpose                          |
|-------------|-------------------|----------------------------------|
| LLM         | mistral (7B)      | Reasoning, tool calling, grading |
| Embeddings  | nomic-embed-text  | Document and query embeddings    |

## File Structure

| File               | Purpose                                           |
|--------------------|---------------------------------------------------|
| `config.py`        | Configuration (paths, model settings)             |
| `policies/`        | Placeholder health insurance policy documents     |
| `ingest.py`        | Document loading, chunking, ChromaDB ingestion    |
| `retriever.py`     | ChromaDB retriever tool for LangChain agent       |
| `agent.py`         | LangGraph agentic RAG (nodes, graph, routing)     |
| `main.py`          | CLI entry point                                   |

## Updating Policies

To update with real policy documents:

1. Replace or add `.md` files in the `policies/` directory
2. Delete the `chroma_db/` directory (to clear old embeddings)
3. Re-run `python ingest.py`
4. Run `python main.py`
