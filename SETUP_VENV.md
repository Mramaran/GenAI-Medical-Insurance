# ClaimChain — Setup & Run with Virtual Environment

Complete guide to setting up and running the ClaimChain project using Python virtual environments.

---

## Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Tesseract OCR** installed ([download here](https://github.com/tesseract-ocr/tesseract))
- **Ollama** running with `mistral` model (or use Gemini API)

---

## Step 1: Create Virtual Environment

### Windows (PowerShell)
```powershell
# Navigate to project root
cd "C:\Users\mrmar\OneDrive\Documents\TN IMPACT\GenAI Insurance V1"

# Create virtual environment in Backend folder
cd Backend
python -m venv venv
```

### macOS/Linux
```bash
cd Backend
python3 -m venv venv
```

---

## Step 2: Activate Virtual Environment

### Windows (PowerShell)
```powershell
.\venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)
```cmd
venv\Scripts\activate.bat
```

### macOS/Linux
```bash
source venv/bin/activate
```

**You should see `(venv)` prefix in your terminal prompt.**

---

## Step 3: Install Python Dependencies

```bash
# In Backend folder with venv activated
cd api
pip install -r requirements.txt

# Optional: Install spaCy language model (for NLP)
python -m spacy download en_core_web_sm
```

---

## Step 4: Configure Environment Variables

Create a `.env` file in `Backend/api/`:

```bash
# Backend/api/.env

# Use Gemini (faster) or Ollama (local)
USE_GEMINI=true
GEMINI_API_KEY=your_gemini_api_key_here

# Blockchain (optional - app works without it)
WEB3_PROVIDER_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=your_contract_address
PRIVATE_KEY=your_private_key
```

---

## Step 5: Start Backend (Port 8000)

```bash
# In Backend/api with venv activated
python -m uvicorn main:app --reload --port 8000
```

**Verify:** Open http://localhost:8000/docs in your browser

Keep this terminal running and open new terminals for the frontends.

---

## Step 6: Install Frontend Dependencies

### Customer Portal (Port 3000)

```bash
# New terminal (no venv needed for Node.js)
cd frontend
npm install
```

### Insurer Portal (Port 3001)

```bash
# Another new terminal
cd insurer
npm install
```

---

## Step 7: Start Frontend Portals

### Customer Portal

```bash
cd frontend
npm run dev
```

**Opens:** http://localhost:3000

### Insurer Portal

```bash
cd insurer
npm run dev
```

**Opens:** http://localhost:3001

---

## Running Everything Together

### Terminal 1 (Backend)
```powershell
cd Backend
.\venv\Scripts\Activate.ps1
cd api
python -m uvicorn main:app --reload --port 8000
```

### Terminal 2 (Customer Portal)
```powershell
cd frontend
npm run dev
```

### Terminal 3 (Insurer Portal)
```powershell
cd insurer
npm run dev
```

---

## Quick Test Demo

1. **Upload Claim** (Customer Portal - http://localhost:3000)
   - Go to "Upload" page
   - Upload `Backend/OCR/test_docs/test_discharge_summary.md`
   - Enter policy: `HSP-2025-TN-001`
   - Submit and see AI verdict + fraud score

2. **Review Claim** (Insurer Portal - http://localhost:3001)
   - Click refresh on dashboard
   - Click the new claim to see details
   - Approve or Reject with notes

3. **Verify Claim** (Customer Portal)
   - Go to "Verify" page
   - Enter the claim ID
   - See blockchain verification (if configured)

4. **Chat Assistant** (Customer Portal)
   - Click chat bubble (bottom-right)
   - Ask: "Is cataract surgery covered?"
   - Get policy-aware responses

---

## Deactivating Virtual Environment

When you're done working:

```bash
deactivate
```

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Customer Portal | 3000 | http://localhost:3000 |
| Insurer Portal | 3001 | http://localhost:3001 |

---

## Troubleshooting

### Virtual Environment Issues

**Problem:** `Activate.ps1 cannot be loaded` (PowerShell)  
**Fix:** Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Problem:** `pip` not found after activation  
**Fix:** Ensure Python is in PATH, or use full path:
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Backend Issues

**Problem:** Ollama/Mistral not working  
**Fix:** Start Ollama and pull model:
```bash
ollama serve
ollama pull mistral
```
Or set `USE_GEMINI=true` in `.env`

**Problem:** Tesseract OCR not found  
**Fix:** Install Tesseract and add to PATH, or configure path in `Backend/OCR/config.py`

**Problem:** Module import errors  
**Fix:** Ensure venv is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Frontend Issues

**Problem:** CORS errors  
**Fix:** Restart backend - it allows ports 3000, 3001, 5173

**Problem:** Port already in use  
**Fix:** Use different port:
```bash
npm run dev -- --port 3002
```

---

## Additional Setup (Optional)

### RAG System
```bash
cd Backend/RAG
pip install -r requirements.txt
python ingest.py  # Build vector database
```

### Blockchain (Ganache)
```bash
# Install Ganache: https://trufflesuite.com/ganache/
# Deploy contract in blockchain/contracts/
# Update CONTRACT_ADDRESS in .env
```

---

## Development Tips

1. **Keep venv activated** while working on Python code
2. **Use separate terminals** for each service (backend, 2 frontends)
3. **Hot reload** is enabled - changes reflect automatically
4. **Check logs** in terminal for errors
5. **API docs** at http://localhost:8000/docs for testing endpoints

---

## Next Steps

- Customize test documents in `Backend/OCR/test_docs/`
- Modify policies in `Backend/RAG/policies/`
- Adjust fraud scoring in `Backend/api/services/fraud_scorer.py`
- Configure blockchain in `.env` for immutable claim records
