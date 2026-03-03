# Testing ClaimChain — Current Progress

## What's Runnable Right Now

The **Backend API** (Tasks 1-3) + **Test Frontend** are ready. You can:
- Upload medical PDFs via a full React UI
- See structured extracted data (OCR)
- See AI coverage verdict (RAG)
- View all claims in a list
- Open the Insurer Portal (review buttons exist but endpoint isn't wired yet)

Blockchain integration is not built yet — comes in Tasks 4-5.

---

## Quick Start (2 terminals)

### Terminal 1 — Backend API
```bash
cd "C:\Users\mrmar\OneDrive\Documents\TN IMPACT\GenAI Insurance V1\Backend\api"
uvicorn main:app --reload --port 8000
```

### Terminal 2 — Frontend
```bash
cd "C:\Users\mrmar\OneDrive\Documents\TN IMPACT\GenAI Insurance V1\frontend"
npm run dev
```

Then open: **http://localhost:3000**

---

## Prerequisites

Make sure these are running/installed **before** starting:

### 1. Ollama (REQUIRED)
```bash
# Check if Ollama is running
ollama list

# You need these two models:
ollama pull mistral
ollama pull nomic-embed-text

# Ollama must be running at http://localhost:11434
```

### 2. Tesseract OCR (REQUIRED)
```bash
tesseract --version
# If not installed: download from https://github.com/UB-Mannheim/tesseract/wiki
# Make sure it's in your PATH
```

### 3. spaCy Model (REQUIRED)
```bash
python -m spacy download en_core_web_sm
```

### 4. Python Dependencies
```bash
cd "Backend/OCR"
pip install -r requirements.txt

cd "../RAG"
pip install -r requirements.txt

cd "../api"
pip install -r requirements.txt
```

### 5. Node.js (REQUIRED for frontend)
```bash
node --version    # Need 18+
cd frontend
npm install       # Already done — but run if node_modules is missing
```

---

## Test via Frontend UI (Recommended)

### Page 1: Submit Claim
1. Open **http://localhost:3000**
2. You land on "Submit Claim" page
3. Policy number is pre-filled: `HSP-2025-TN-001`
4. Drag-and-drop or click to upload a PDF from `Backend/OCR/test_docs/`
   - Try `DISCHARGE_SUMMARY.pdf` first
5. Click **"Analyze & Submit Claim"**
6. Wait 30-60 seconds (OCR + RAG with local Ollama)
7. You'll see:
   - **Green success banner** with Claim ID
   - **Extracted Data** — patient, hospital, diagnosis, billing, dates, confidence
   - **AI Coverage Verdict** — full RAG analysis with sub-limits, co-pay, etc.
   - **Raw JSON** — collapsible full response

### Page 2: My Claims
1. Click "My Claims" in the sidebar
2. See all submitted claims in a list
3. Click "View Details" on any claim to expand and see the AI verdict
4. Blockchain proof shows "Not yet recorded on-chain" (expected — Task 4)

### Page 3: Insurer Portal
1. Click "Insurer Portal" in the sidebar
2. Left panel shows pending claims
3. Click a claim to see details + AI verdict on the right
4. Approve/Reject buttons exist but will show an error popup — this is expected
   - The review endpoint (`POST /api/claims/{id}/review`) is Task 5

---

## Test via curl (Alternative)

### Health Check
```bash
curl http://localhost:8000/
```
**Expected:** `{"message":"ClaimChain API is running","version":"1.0.0"}`

### Upload & Analyze
```bash
curl -X POST http://localhost:8000/api/claims/analyze \
  -F "files=@../OCR/test_docs/DISCHARGE_SUMMARY.pdf" \
  -F "policy_number=HSP-2025-TN-001"
```

### Upload Multiple Documents
```bash
curl -X POST http://localhost:8000/api/claims/analyze \
  -F "files=@../OCR/test_docs/DISCHARGE_SUMMARY.pdf" \
  -F "files=@../OCR/test_docs/APOLLO_HOSPITALS.pdf" \
  -F "policy_number=HSP-2025-TN-001"
```

### Get a Claim by ID
```bash
curl http://localhost:8000/api/claims/CLM-20260303-001
```

### List All Claims
```bash
curl http://localhost:8000/api/claims/
```

### Swagger API Docs
Open in browser: **http://localhost:8000/docs**

---

## What to Look For

### OCR Output (extracted_data)
- `patient.name` — patient name from the PDF
- `hospital.name` — hospital name
- `diagnosis.primary_diagnosis` — diagnosis text
- `billing.total_amount` — total bill amount
- `confidence_score` — OCR confidence (0-1)

### RAG Verdict (verdict)
- `verdict_text` — coverage analysis mentioning: sub-limits, co-pay, waiting periods, estimated payable
- `query_used` — the exact question sent to the RAG agent

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'pipeline'` | Run backend from `Backend/api/` directory, not project root |
| `ConnectionError: localhost:11434` | Start Ollama: `ollama serve` |
| `TesseractNotFoundError` | Install Tesseract and add to PATH |
| `OSError: [E050] Can't find model 'en_core_web_sm'` | Run: `python -m spacy download en_core_web_sm` |
| Very slow response (>2 min) | Normal for first run — Ollama loads model into memory. Second run faster. |
| `ChromaDB` errors | Run `cd Backend/RAG && python ingest.py` to rebuild vector DB |
| Frontend blank page | Check browser console. Make sure backend is on port 8000. |
| CORS errors in browser | Backend CORS allows `localhost:3000`. Check ports match. |
| `npm run dev` fails | Run `npm install` in `frontend/` directory first |

---

## What's NOT Working Yet (Coming in Tasks 4-12)

| Feature | Status | Task |
|---------|--------|------|
| Blockchain proof (merkle_root, tx_hash) | `null` in responses | Task 4 |
| Insurer review endpoint | Approve/Reject buttons error | Task 5 |
| On-chain claim timeline | Not built | Task 7 |
| Gemini mode (fast demo) | Using local Ollama only | Task 9 |
| Deployment (Vercel + Render) | Local only | Task 11 |
