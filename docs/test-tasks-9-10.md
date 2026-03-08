# Test Guide — Tasks 9 & 10

## Task 9: Gemini Integration

### Test A: Ollama Mode (Default)

Ensure `.env` has:
```
USE_GEMINI=false
```

```bash
cd Backend/api
uvicorn main:app --reload --port 8000
```

Upload a document — should work as before using local Ollama/Mistral.

---

### Test B: Gemini Mode

1. Get a free API key from https://aistudio.google.com/apikey
2. Update `.env`:
```
USE_GEMINI=true
GEMINI_API_KEY=your_actual_key_here
```
3. Restart backend
4. Upload same document — should be **noticeably faster** (3-5x)

### What to verify:
- [ ] Ollama mode: extraction + verdict works (USE_GEMINI=false)
- [ ] Gemini mode: extraction + verdict works (USE_GEMINI=true + key)
- [ ] Fallback: if Gemini key is empty, falls back to Ollama automatically
- [ ] No code changes needed to switch — just `.env` toggle

---

## Task 10: Polish & Error Handling

### Test C: Multi-Step Progress Bar

1. Open `http://localhost:3000`
2. Upload a PDF and click "Analyze & Submit Claim"
3. Verify the **Processing Pipeline** card appears with 6 steps:
   - [ ] Step 1: Uploading documents...
   - [ ] Step 2: Reading documents (OCR + NLP)...
   - [ ] Step 3: Checking policy coverage (RAG)...
   - [ ] Step 4: Computing cryptographic hashes...
   - [ ] Step 5: Recording proof on blockchain...
   - [ ] Step 6: Done! Redirecting...
4. Completed steps show green checkmark, current step has spinner
5. Auto-redirects to Verdict page after completion

---

### Test D: Graceful Degradation

**RAG fails (Ollama not running):**
1. Stop Ollama (`taskkill /F /IM ollama.exe` or close it)
2. Upload a document
3. Verify:
   - [ ] OCR extraction still works
   - [ ] Verdict shows: "Coverage check unavailable..."
   - [ ] Response includes `warnings` array
   - [ ] No 500 crash

**Blockchain fails (no SepoliaETH / wrong key):**
1. Set `WALLET_PRIVATE_KEY=wrong_key` in `.env`
2. Upload a document
3. Verify:
   - [ ] OCR + RAG still work
   - [ ] `blockchain_proof.error` field explains the issue
   - [ ] Claim is still stored and accessible

---

### Test E: Demo Scenario

1. Open `Backend/OCR/test_docs/demo_scenario.md` — read the script
2. Upload `DISCHARGE_SUMMARY.pdf` + `APOLLO_HOSPITALS.pdf`
3. Verify extracted data roughly matches:
   - [ ] Patient name found
   - [ ] Hospital name found
   - [ ] Total amount found
   - [ ] Diagnosis found
4. Verify AI verdict mentions coverage / co-pay / waiting period

---

## Quick Commands

```bash
# Start backend
cd Backend/api && uvicorn main:app --reload --port 8000

# Start frontend
cd frontend && npm run dev

# Test upload via curl
curl -X POST http://localhost:8000/api/claims/analyze \
  -F "files=@Backend/OCR/test_docs/DISCHARGE_SUMMARY.pdf" \
  -F "policy_number=HSP-2025-TN-001"
```
