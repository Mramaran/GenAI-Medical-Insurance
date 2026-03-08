# ClaimChain — How to Run

## Prerequisites

- Python 3.10+ with pip
- Node.js 18+ with npm
- Tesseract OCR installed
- Ollama running with `mistral` model (or set `USE_GEMINI=true` in `.env`)

---

## Step 1: Backend (port 8000)

```bash
cd Backend/api
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Verify: http://localhost:8000/docs

---

## Step 2: Customer Portal (port 3000)

```bash
cd frontend
npm install
npm run dev
```

Opens: http://localhost:3000

---

## Step 3: Insurer Portal (port 3001)

```bash
cd insurer
npm install
npm run dev
```

Opens: http://localhost:3001

---

## Quick Demo (Side-by-Side)

1. Open **localhost:3000** (left window) and **localhost:3001** (right window)
2. Customer Portal: Upload `Backend/OCR/test_docs/test_discharge_summary.md` with policy `HSP-2025-TN-001`
3. Customer Portal: See AI verdict + QR code + confidence dots
4. Insurer Portal: Click refresh — new claim appears on dashboard
5. Insurer Portal: Click claim — see fraud score + extracted data + approve/reject
6. Customer Portal: Check `/verify` page with the claim ID
7. Customer Portal: Click the chat bubble, ask "Is cataract surgery covered?"

---

## Ports

| Service | Port | URL |
|---|---|---|
| Backend API | 8000 | http://localhost:8000 |
| Customer Portal | 3000 | http://localhost:3000 |
| Insurer Portal | 3001 | http://localhost:3001 |

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Ollama not running | `ollama serve` then `ollama pull mistral` |
| Blockchain tx fails | App still works — blockchain errors show gracefully |
| CORS error | Restart backend — it allows ports 3000, 3001, 5173 |
| OCR poor results | Use the `.md` test files instead of scanned images |
| Chat fails | Ensure Ollama + mistral model is running |
