# ClaimChain V1 — Verification Checklist

> Use this checklist to verify every component of the ClaimChain implementation.
> Check each box after confirming it works.

---

## Prerequisites

Before testing, ensure these are running/installed:

| Requirement | Check Command | Expected |
|---|---|---|
| Python 3.10+ | `python --version` | 3.10 or higher |
| Node.js 18+ | `node --version` | 18.x or higher |
| spaCy model | `python -c "import spacy; spacy.load('en_core_web_sm')"` | No error |
| Ollama running | `curl http://localhost:11434/api/tags` | JSON response |
| Mistral model pulled | `ollama list` | `mistral` in list |
| Tesseract OCR | `tesseract --version` | Version output |

---

## 1. File Structure Verification

### Blockchain (`blockchain/`)
- [ ] `blockchain/contracts/ClaimChain.sol` exists
- [ ] `blockchain/abi/ClaimChain.json` exists (pre-generated ABI)
- [ ] `blockchain/README.md` exists (deployment instructions)

### Backend API (`Backend/api/`)
- [ ] `Backend/api/main.py` — FastAPI entry point
- [ ] `Backend/api/routes/__init__.py`
- [ ] `Backend/api/routes/claims.py` — `/api/claims/analyze`, `/api/claims/`, `/api/claims/{id}`
- [ ] `Backend/api/routes/review.py` — `/api/claims/{id}/review`
- [ ] `Backend/api/services/__init__.py`
- [ ] `Backend/api/services/ocr_service.py` — Wraps existing OCR pipeline
- [ ] `Backend/api/services/rag_service.py` — Wraps existing RAG agent
- [ ] `Backend/api/services/blockchain.py` — web3.py contract interaction
- [ ] `Backend/api/utils/__init__.py`
- [ ] `Backend/api/utils/store.py` — In-memory claim storage
- [ ] `Backend/api/utils/hashing.py` — SHA-256 + Merkle root
- [ ] `Backend/api/.env` — Real config (private key, contract address)
- [ ] `Backend/api/.env.example` — Template
- [ ] `Backend/api/requirements.txt`

### Frontend (`frontend/`)
- [ ] `frontend/src/App.jsx` — Router with 4 routes
- [ ] `frontend/src/api.js` — API client (5 functions)
- [ ] `frontend/src/main.jsx` — React entry
- [ ] `frontend/src/components/Sidebar.jsx` — Navigation
- [ ] `frontend/src/components/Card.jsx` — Card container
- [ ] `frontend/src/components/Badge.jsx` — Status badges
- [ ] `frontend/src/components/Spinner.jsx` — Loading spinner
- [ ] `frontend/src/components/ClaimTimeline.jsx` — On-chain events timeline
- [ ] `frontend/src/pages/UploadPage.jsx` — Document upload + OCR + RAG
- [ ] `frontend/src/pages/ClaimsPage.jsx` — List all claims
- [ ] `frontend/src/pages/VerdictPage.jsx` — Full claim detail view
- [ ] `frontend/src/pages/AdjudicatorPage.jsx` — Insurer portal

---

## 2. Backend API Tests

### Start the backend
```bash
cd Backend/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2.1 Health Check
```bash
curl http://localhost:8000/
```
- [ ] Returns `{"message":"ClaimChain API is running","version":"1.0.0"}`

### 2.2 Swagger Docs
- [ ] Open `http://localhost:8000/docs` in browser
- [ ] See all 4 endpoints listed:
  - POST `/api/claims/analyze`
  - GET `/api/claims/`
  - GET `/api/claims/{claim_id}`
  - POST `/api/claims/{claim_id}/review`

### 2.3 Upload a Claim (OCR + RAG Pipeline)
```bash
curl -X POST http://localhost:8000/api/claims/analyze \
  -F "files=@/path/to/your/medical-bill.pdf" \
  -F "policy_number=HSP-2025-TN-001"
```
- [ ] Returns JSON with `claim_id` (format: `CLM-YYYYMMDD-NNN`)
- [ ] `extracted_data` contains nested `patient`, `hospital`, `diagnosis`, `treatment`, `billing`
- [ ] `verdict` contains `verdict_text` and `query_used`
- [ ] `blockchain_proof` contains `merkle_root` (0x-prefixed 64-char hex)
- [ ] `status` is `"submitted"`
- [ ] If blockchain is configured: `tx_hash` and `block_number` are present
- [ ] If blockchain is NOT configured: `error` field explains why

### 2.4 List Claims
```bash
curl http://localhost:8000/api/claims/
```
- [ ] Returns array of claim objects
- [ ] Each claim has `claim_id`, `status`, `extracted_data`

### 2.5 Get Single Claim
```bash
curl http://localhost:8000/api/claims/CLM-XXXXXXXX-001
```
(Replace with actual claim ID from step 2.3)
- [ ] Returns full claim record
- [ ] Includes `events` array (on-chain events from blockchain)

### 2.6 Review a Claim — Approve
```bash
curl -X POST http://localhost:8000/api/claims/CLM-XXXXXXXX-001/review \
  -H "Content-Type: application/json" \
  -d '{"action":"approve","reason":"All documentation verified"}'
```
- [ ] Returns `new_status: "approved"`
- [ ] `reason_hash` is 0x-prefixed hex
- [ ] If blockchain configured: `tx_hash` present

### 2.7 Review a Claim — Reject (requires reason)
```bash
curl -X POST http://localhost:8000/api/claims/CLM-XXXXXXXX-001/review \
  -H "Content-Type: application/json" \
  -d '{"action":"reject","reason":"Missing discharge summary"}'
```
- [ ] Returns `new_status: "rejected"`

### 2.8 Review Validation — Reject without reason
```bash
curl -X POST http://localhost:8000/api/claims/CLM-XXXXXXXX-001/review \
  -H "Content-Type: application/json" \
  -d '{"action":"reject","reason":""}'
```
- [ ] Returns 400 error: `"A reason is required when action is 'reject'"`

### 2.9 Invalid Claim ID
```bash
curl http://localhost:8000/api/claims/NONEXISTENT-ID
```
- [ ] Returns 404: `"Claim not found"`

---

## 3. Frontend Tests

### Start the frontend
```bash
cd frontend
npm install
npm run dev
```
- [ ] Opens on `http://localhost:3000` (configured in vite.config.js)

### 3.1 Navigation (Sidebar)
- [ ] Sidebar shows 3 links: Submit Claim, My Claims, Insurer Portal
- [ ] Clicking each navigates to correct page
- [ ] Active link is highlighted

### 3.2 Upload Page (`/`)
- [ ] Page title: "Submit Medical Claim"
- [ ] Policy number field pre-filled with `HSP-2025-TN-001`
- [ ] Drop zone accepts drag-and-drop files
- [ ] Click on drop zone opens file browser
- [ ] Selected files show in list below drop zone
- [ ] "X" button removes individual files
- [ ] Submit button disabled when no files selected
- [ ] After upload: shows loading spinner with step text
- [ ] On success: shows green "Claim Submitted Successfully" card
- [ ] Shows extracted data grid (Patient, Hospital, Diagnosis, etc.)
- [ ] Shows AI Coverage Verdict (RAG) in purple card
- [ ] Auto-navigates to Verdict page after ~1.5 seconds
- [ ] On error: shows red error card

### 3.3 Verdict Page (`/verdict/:claimId`)
- [ ] Header shows Claim ID and status badge
- [ ] Left column: Extracted Data (OCR) grid with all fields
- [ ] Left column: AI Coverage Verdict (RAG) card with expandable query
- [ ] Left column: Blockchain Proof card (merkle root, tx hash, block, gas)
- [ ] Tx hash is a clickable link to Sepolia Etherscan
- [ ] Right column: On-Chain Timeline with colored dots
- [ ] Timeline shows ClaimSubmitted event (blue)
- [ ] After approve/reject: timeline shows additional events
- [ ] Auto-refreshes every 10 seconds
- [ ] "All Claims" button navigates to `/claims`

### 3.4 Claims Page (`/claims`)
- [ ] Lists all submitted claims
- [ ] Each claim shows: Claim ID, Patient, Hospital, Amount, Status
- [ ] Status shown as colored badge
- [ ] On-chain recorded claims show green checkmark
- [ ] "View Details" button navigates to verdict page
- [ ] "Refresh" button reloads the list
- [ ] Empty state: shows "No claims found" message

### 3.5 Insurer Portal (`/insurer`)
- [ ] Title: "Insurer Portal"
- [ ] Left panel: Pending claims list (submitted/pending/under_review)
- [ ] Left panel: Processed claims list (approved/rejected/settled)
- [ ] Clicking a claim loads detail in right panel
- [ ] Selected claim has blue border highlight
- [ ] Right panel shows: Claim ID, Patient, Hospital, Diagnosis, Procedures, Amount
- [ ] AI Coverage Analysis section (purple) shows verdict text
- [ ] Approve button (green gradient)
- [ ] Reject button (red gradient)
- [ ] Clicking Reject first time shows reason input field
- [ ] After entering reason and clicking Reject again: claim is rejected
- [ ] After approve: claim moves from Pending to Processed list
- [ ] Status badge updates after action
- [ ] "Refresh List" button at bottom

---

## 4. Blockchain Verification

### 4.1 Configuration
- [ ] `Backend/api/.env` has `SEPOLIA_RPC_URL` set
- [ ] `Backend/api/.env` has `WALLET_PRIVATE_KEY` set (no 0x prefix)
- [ ] `Backend/api/.env` has `CONTRACT_ADDRESS` set
- [ ] Wallet has SepoliaETH balance for gas fees

### 4.2 Smart Contract (already deployed)
- [ ] Contract at `0xcd1872D3036898C5EE39542a66bf4fb8b0c8AE1A` on Sepolia
- [ ] Verify on Etherscan: `https://sepolia.etherscan.io/address/0xcd1872D3036898C5EE39542a66bf4fb8b0c8AE1A`

### 4.3 On-Chain Transactions
After submitting a claim through the UI:
- [ ] `blockchain_proof.tx_hash` is returned in API response
- [ ] Transaction visible on Sepolia Etherscan
- [ ] ClaimSubmitted event emitted with correct claimId and merkle root

After approving/rejecting through the UI:
- [ ] `review_tx_hash` is returned in review response
- [ ] StatusUpdated event emitted on-chain
- [ ] Timeline component shows new event

### 4.4 Data Integrity
- [ ] Each document gets a SHA-256 hash
- [ ] Verdict text gets a SHA-256 hash
- [ ] Merkle root is computed from all hashes
- [ ] Merkle root is what gets committed on-chain

---

## 5. End-to-End Flow Test

Complete this entire flow without errors:

1. [ ] Start Ollama (`ollama serve`)
2. [ ] Start Backend (`cd Backend/api && uvicorn main:app --reload --port 8000`)
3. [ ] Start Frontend (`cd frontend && npm run dev`)
4. [ ] Open `http://localhost:3000`
5. [ ] Upload a medical bill PDF on the Upload page
6. [ ] Verify extracted data appears (Patient, Hospital, Amount, etc.)
7. [ ] Verify AI Coverage Verdict appears
8. [ ] Automatic redirect to Verdict page
9. [ ] Verify Blockchain Proof section has merkle root
10. [ ] Navigate to "My Claims" — see the claim listed
11. [ ] Navigate to "Insurer Portal" — see claim in Pending list
12. [ ] Click the claim — see full details in right panel
13. [ ] Click "Approve" — status changes to "approved"
14. [ ] Claim moves from Pending to Processed list
15. [ ] Go back to Verdict page — timeline shows approval event

---

## 6. Remaining Tasks (Not Yet Implemented)

| Task | Description | Status |
|---|---|---|
| Task 9 | Gemini Integration (Demo Mode) — USE_GEMINI flag for fallback when Ollama unavailable | Pending |
| Task 10 | End-to-End Polish + Demo Prep — Error handling improvements, demo scenario doc | Pending |
| Task 11 | Deployment Configuration — Vercel (frontend) + Render (backend) | Pending |
| Task 12 | Pitch Deck + Next Stage Instructions — Presentation outline + instructions | Pending |

---

## Quick Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | `cd Backend/api && pip install -r requirements.txt` |
| `[E050] Can't find model 'en_core_web_sm'` | `pip install spacy && python -m spacy download en_core_web_sm` |
| OCR returns empty data | Ensure Tesseract is installed and in PATH |
| RAG verdict is empty | Ensure Ollama is running (`ollama serve`) and Mistral is pulled (`ollama pull mistral`) |
| Blockchain proof shows error | Check `.env` has correct private key and wallet has SepoliaETH |
| Frontend CORS error | Backend must be on port 8000; frontend on 3000 or 5173 |
| `npm run dev` fails | `cd frontend && npm install` first |
| Claim ID format wrong | Should be `CLM-YYYYMMDD-NNN` |

---

## File Count Summary

| Component | Files | Status |
|---|---|---|
| Blockchain | 3 | Done (Tasks 1) |
| Backend API | 13 | Done (Tasks 2-5) |
| Frontend | 12 | Done (Tasks 6-8) |
| **Total** | **28** | **Tasks 1-8 Complete** |
