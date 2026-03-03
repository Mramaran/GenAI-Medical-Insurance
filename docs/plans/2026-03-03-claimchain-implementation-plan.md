# ClaimChain Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a GenAI medical insurance claims system where AI coverage verdicts are cryptographically committed on Ethereum (Sepolia) before the insurer sees them, giving patients a tamper-proof claim timeline.

**Architecture:** Three-layer system — (1) React frontend for document upload, verdict display, and on-chain timeline, (2) FastAPI backend that orchestrates existing OCR + RAG pipelines and connects to blockchain via web3.py, (3) Solidity smart contract on Sepolia that stores claim hashes and status updates as immutable events.

**Tech Stack:** Python 3.10+, FastAPI, Tesseract, spaCy, Ollama/Gemini, LangGraph, ChromaDB, Solidity, Hardhat/Remix, ethers.js, web3.py, React (Vite), Tailwind CSS, shadcn/ui

---

## Existing Codebase Map

Before touching anything, here is exactly what exists and how the pieces connect.

### Backend/OCR/ — Document Extraction Pipeline (WORKING)

| File | Purpose | Key Exports |
|------|---------|-------------|
| `config.py` | Tesseract path, Poppler path, Ollama config, spaCy model name | `TESSERACT_CMD`, `LLM_MODEL`, `SPACY_MODEL` |
| `models.py` | Pydantic data models for all extracted fields | `ExtractedClaim`, `PatientInfo`, `HospitalInfo`, `DiagnosisInfo`, `TreatmentInfo`, `BillingInfo`, `DateInfo`, `ItemizedCharge`, `DocumentType` |
| `preprocessor.py` | Image enhancement (grayscale, contrast, binarize) for better OCR | `preprocess_image(image_path) -> Image` |
| `ocr_engine.py` | Auto-detects file type, extracts raw text | `extract_text(file_path) -> (text, method)` |
| `nlp_extractor.py` | Two-stage extraction: spaCy NER + Ollama LLM | `extract_structured_fields(raw_text) -> ExtractedClaim` |
| `pipeline.py` | Main orchestrator — the function you call | `process_document(file_path, policy_number) -> ExtractedClaim`, `process_multiple_documents(file_paths, policy_number) -> ExtractedClaim` |
| `main.py` | CLI entry point | Not needed for API integration |

**How to call it from outside:**
```python
import sys
sys.path.insert(0, "Backend/OCR")
from pipeline import process_document, process_multiple_documents

claim = process_document("path/to/file.pdf", policy_number="HSP-2025-TN-001")
# claim is an ExtractedClaim Pydantic model
# claim.model_dump() gives you a dict
```

### Backend/RAG/ — Policy Verification Agent (WORKING)

| File | Purpose | Key Exports |
|------|---------|-------------|
| `config.py` | ChromaDB path, model names, chunking config | `CHROMA_PERSIST_DIR`, `LLM_MODEL`, `EMBEDDING_MODEL` |
| `ingest.py` | Ingests `.md` policy files into ChromaDB | `ingest_to_chromadb()` — run once, already done |
| `retriever.py` | ChromaDB retriever with MMR search (k=4) | `retrieve_policy_info(query) -> str` (LangChain tool) |
| `agent.py` | LangGraph agentic RAG with grading + rewriting | `query_agent(question) -> str` |
| `policies/` | 3 markdown files: general_policy.md, coverage_details.md, claims_procedures.md | — |
| `chroma_db/` | Pre-built vector database (already ingested) | — |

**How to call it from outside:**
```python
import sys
sys.path.insert(0, "Backend/RAG")
from agent import query_agent

answer = query_agent("Is cataract surgery covered under policy HSP-2025-TN-001 Silver tier?")
# answer is a plain string with the RAG response
```

**Important:** Both modules use Ollama (mistral) locally. The RAG agent uses `nomic-embed-text` for embeddings. Ollama must be running at `http://localhost:11434`.

### Backend/OCR/test_docs/ — Sample Documents

- `APOLLO_HOSPITALS.pdf` — Hospital bill
- `DISCHARGE_SUMMARY.pdf` — Discharge summary
- `PRESCRIPTION.pdf` — Prescription

### What Does NOT Exist Yet

- API server (FastAPI) to glue OCR + RAG + blockchain
- Smart contract (Solidity) for on-chain claim recording
- Hashing/Merkle logic for tamper-proof verdicts
- Frontend (React) for upload, verdict, timeline, insurer dashboard
- Blockchain interaction layer (web3.py / ethers.js)
- Gemini integration as an alternative to Ollama

---

## System Architecture

```
+------------------------------------------------------------------+
|                        CLAIMCHAIN SYSTEM                          |
+------------------------------------------------------------------+
|                                                                   |
|  [FRONTEND - React + Vite + Tailwind]                            |
|  Port 5173 (dev) / Vercel (prod)                                 |
|                                                                   |
|  Pages:                                                          |
|  /              -> Upload documents + enter policy number         |
|  /verdict/:id   -> AI verdict + on-chain proof + timeline         |
|  /insurer       -> Insurer dashboard (list claims, approve/reject)|
|                                                                   |
|  Calls Backend REST API via fetch/axios                          |
|                                                                   |
+------------------------------+------------------------------------+
                               |
                          REST API calls
                               |
+------------------------------v------------------------------------+
|                                                                   |
|  [BACKEND - FastAPI]                                             |
|  Port 8000                                                       |
|                                                                   |
|  POST /api/claims/analyze                                        |
|    -> Accepts: multipart files + policy_number                   |
|    -> Runs: OCR pipeline -> RAG verdict -> hash -> blockchain    |
|    -> Returns: { claim_id, extracted_data, verdict, tx_hash }    |
|                                                                   |
|  GET /api/claims/{id}                                            |
|    -> Returns: full claim data + status + on-chain events        |
|                                                                   |
|  GET /api/claims                                                 |
|    -> Returns: list of all claims (for insurer dashboard)        |
|                                                                   |
|  POST /api/claims/{id}/review                                    |
|    -> Accepts: { action: "approve"|"reject", reason: "..." }    |
|    -> Runs: update status on blockchain                          |
|    -> Returns: { tx_hash, new_status }                           |
|                                                                   |
|  Internal Services:                                              |
|  +------------------+  +------------------+  +----------------+  |
|  | ocr_service.py   |  | rag_service.py   |  | blockchain.py  |  |
|  | Wraps OCR        |  | Wraps RAG agent  |  | web3.py calls  |  |
|  | pipeline.py      |  | agent.py         |  | to contract    |  |
|  +------------------+  +------------------+  +----------------+  |
|                                                                   |
|  +------------------+  +------------------+                      |
|  | hashing.py       |  | store.py         |                      |
|  | SHA-256 + Merkle |  | In-memory claim  |                      |
|  | root computation |  | storage (dict)   |                      |
|  +------------------+  +------------------+                      |
|                                                                   |
+------------------------------+------------------------------------+
                               |
                          web3.py calls
                               |
+------------------------------v------------------------------------+
|                                                                   |
|  [SMART CONTRACT - Solidity on Sepolia]                          |
|                                                                   |
|  ClaimChain.sol                                                  |
|                                                                   |
|  State:                                                          |
|  mapping(string claimId => ClaimRecord)                          |
|  ClaimRecord: { merkleRoot, status, statusHistory[], timestamps }|
|                                                                   |
|  Functions:                                                      |
|  submitClaimMeta(claimId, merkleRoot) -> emit ClaimSubmitted     |
|  updateStatus(claimId, status, reasonHash) -> emit StatusUpdated |
|  getClaimRecord(claimId) -> ClaimRecord (view)                   |
|  getStatusHistory(claimId) -> StatusEntry[] (view)               |
|                                                                   |
|  Events:                                                         |
|  ClaimSubmitted(claimId, merkleRoot, submitter, timestamp)       |
|  StatusUpdated(claimId, oldStatus, newStatus, reasonHash, ts)    |
|                                                                   |
|  Status Enum:                                                    |
|  0=Submitted, 1=UnderReview, 2=Approved, 3=Rejected,            |
|  4=QueryRaised, 5=Settled                                        |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Data Flow (End-to-End)

```
Step 1: UPLOAD
  Hospital staff uploads [discharge_summary.pdf, hospital_bill.pdf]
  + enters policy_number = "HSP-2025-TN-001"
  Frontend sends POST /api/claims/analyze (multipart form)

Step 2: OCR EXTRACTION
  Backend saves files to temp directory
  Calls process_multiple_documents([file1, file2], policy_number)
  Gets back: ExtractedClaim {
    patient: { name: "Rajesh Kumar", age: "45", policy_number: "HSP-2025-TN-001" },
    hospital: { name: "Apollo Hospitals Chennai" },
    diagnosis: { primary: "Cataract - Age Related", icd: ["H26.9"] },
    treatment: { procedures: ["Phacoemulsification"], admission_type: "daycare" },
    billing: { total_amount: 45000, itemized: [...] },
    dates: { admission: "2026-02-20", discharge: "2026-02-20" },
    confidence_score: 0.91
  }

Step 3: RAG COVERAGE CHECK
  Backend constructs a query from extracted data:
    "Patient Rajesh Kumar, policy HSP-2025-TN-001, Silver tier.
     Procedure: Phacoemulsification (cataract surgery), daycare admission.
     Total bill: Rs 45,000. Hospital: Apollo Hospitals Chennai.
     Is this covered? What are the sub-limits, co-pay, waiting periods?"

  Calls query_agent(query) -> gets verdict string:
    "Cataract surgery is listed as a covered day-care procedure under
     HealthShield Plus. For Silver tier: room rent limit Rs 4,000/day
     (not applicable for daycare). Co-payment: 10%. 24-month waiting
     period for cataract applies — verify enrollment date. Estimated
     payable: Rs 40,500 (Rs 45,000 - 10% co-pay)."

Step 4: HASH + BLOCKCHAIN
  Backend computes:
    doc_hash_1 = SHA-256(discharge_summary.pdf bytes)
    doc_hash_2 = SHA-256(hospital_bill.pdf bytes)
    verdict_hash = SHA-256(verdict_json_string)
    merkle_root = SHA-256(doc_hash_1 + doc_hash_2 + verdict_hash)

  Backend generates claim_id = "CLM-20260303-001"
  Backend calls contract.submitClaimMeta(claim_id, merkle_root)
  Gets back: tx_hash = "0xabc123..."

Step 5: STORE + RESPOND
  Backend stores in memory:
    claims["CLM-20260303-001"] = {
      extracted_data: ExtractedClaim,
      verdict: verdict_string,
      merkle_root: merkle_root,
      tx_hash: tx_hash,
      status: "submitted",
      document_hashes: [doc_hash_1, doc_hash_2],
      verdict_hash: verdict_hash
    }

  Returns to frontend:
    {
      claim_id: "CLM-20260303-001",
      extracted_data: { ... },
      verdict: { summary: "...", estimated_coverage: 90, copay: 10, ... },
      blockchain_proof: { tx_hash: "0xabc...", merkle_root: "0xdef...", block: 12345 },
      status: "submitted"
    }

Step 6: INSURER REVIEW
  Insurer opens /insurer dashboard
  GET /api/claims -> sees list of submitted claims
  Clicks "CLM-20260303-001"
  GET /api/claims/CLM-20260303-001 -> sees full data + AI verdict
  Clicks "Approve"
  POST /api/claims/CLM-20260303-001/review { action: "approve", reason: "All docs verified" }
  Backend calls contract.updateStatus(claim_id, 2, reason_hash)
  Returns: { tx_hash: "0xdef456...", new_status: "approved" }

Step 7: PATIENT TIMELINE
  Patient refreshes /verdict/CLM-20260303-001
  GET /api/claims/CLM-20260303-001
  Timeline shows:
    [1] AI Verdict Committed - Block #12345 - 0xabc... - 10:30 AM
    [2] Claim Submitted       - Block #12345 - 0xabc... - 10:30 AM
    [3] Insurer Approved       - Block #12350 - 0xdef... - 11:15 AM
  Each event links to Sepolia Etherscan
```

---

## File Structure (What to Create)

```
GenAI Insurance V1/
|
+-- Backend/
|   +-- OCR/                         [EXISTS - DO NOT MODIFY]
|   |   +-- config.py
|   |   +-- models.py                # ExtractedClaim - shared model
|   |   +-- preprocessor.py
|   |   +-- ocr_engine.py
|   |   +-- nlp_extractor.py
|   |   +-- pipeline.py              # process_document(), process_multiple_documents()
|   |   +-- main.py
|   |   +-- requirements.txt
|   |   +-- test_docs/
|   |       +-- APOLLO_HOSPITALS.pdf
|   |       +-- DISCHARGE_SUMMARY.pdf
|   |       +-- PRESCRIPTION.pdf
|   |
|   +-- RAG/                         [EXISTS - DO NOT MODIFY]
|   |   +-- config.py
|   |   +-- agent.py                 # query_agent(question) -> str
|   |   +-- retriever.py
|   |   +-- ingest.py
|   |   +-- main.py
|   |   +-- policies/
|   |   |   +-- general_policy.md
|   |   |   +-- coverage_details.md
|   |   |   +-- claims_procedures.md
|   |   +-- chroma_db/               # Pre-built vector DB
|   |
|   +-- api/                         [CREATE - NEW]
|       +-- main.py                  # FastAPI app, CORS, startup
|       +-- routes/
|       |   +-- claims.py            # POST /analyze, GET /{id}, GET /
|       |   +-- review.py            # POST /{id}/review
|       +-- services/
|       |   +-- ocr_service.py       # Wraps OCR pipeline calls
|       |   +-- rag_service.py       # Wraps RAG agent calls
|       |   +-- blockchain.py        # web3.py contract interaction
|       +-- utils/
|       |   +-- hashing.py           # SHA-256 + Merkle root
|       |   +-- store.py             # In-memory claim storage (dict)
|       +-- requirements.txt         # FastAPI, web3, python-dotenv, uvicorn
|       +-- .env.example             # Template for env vars
|
+-- blockchain/                      [CREATE - NEW]
|   +-- contracts/
|   |   +-- ClaimChain.sol           # Smart contract
|   +-- abi/
|   |   +-- ClaimChain.json          # ABI (copy from Remix after compile)
|   +-- README.md                    # Contract address, deploy instructions
|
+-- frontend/                        [CREATE - NEW]
|   +-- src/
|   |   +-- App.jsx                  # Router setup
|   |   +-- pages/
|   |   |   +-- Upload.jsx           # File upload + policy number form
|   |   |   +-- Verdict.jsx          # AI verdict + proof + timeline
|   |   |   +-- InsurerDashboard.jsx # Claims list + approve/reject
|   |   +-- components/
|   |   |   +-- FileUpload.jsx       # Drag-and-drop file upload
|   |   |   +-- VerdictCard.jsx      # Coverage verdict display
|   |   |   +-- ClaimTimeline.jsx    # On-chain event timeline
|   |   |   +-- ClaimSummary.jsx     # Extracted data summary card
|   |   +-- services/
|   |   |   +-- api.js               # Backend API calls (fetch wrapper)
|   |   +-- index.css                # Tailwind imports
|   +-- package.json
|   +-- tailwind.config.js
|   +-- vite.config.js
|
+-- docs/
|   +-- plans/
|       +-- 2026-03-03-claimchain-workflow.md        [EXISTS]
|       +-- 2026-03-03-claimchain-implementation-plan.md  [THIS FILE]
|
+-- idea.md                          [EXISTS]
+-- our statement.md                 [EXISTS]
```

---

## Task-by-Task Implementation

### Task 1: Smart Contract — ClaimChain.sol

**Files:**
- Create: `blockchain/contracts/ClaimChain.sol`
- Create: `blockchain/README.md`

**What to build:**
- Solidity contract with Solidity ^0.8.19
- `ClaimStatus` enum: Submitted(0), UnderReview(1), Approved(2), Rejected(3), QueryRaised(4), Settled(5)
- `StatusEntry` struct: status, reasonHash, timestamp, updatedBy
- `ClaimRecord` struct: merkleRoot, currentStatus, submitter, submittedAt, statusHistory (array of StatusEntry)
- `mapping(string => ClaimRecord) public claims`
- `submitClaimMeta(string calldata claimId, bytes32 merkleRoot)`: stores record, emits `ClaimSubmitted` event. Requires merkleRoot != 0 and claim doesn't already exist.
- `updateStatus(string calldata claimId, ClaimStatus newStatus, bytes32 reasonHash)`: updates status, pushes to history, emits `StatusUpdated`. Requires claim exists.
- `getClaimRecord(string calldata claimId)`: view function returning merkleRoot, currentStatus, submitter, submittedAt
- `getStatusHistory(string calldata claimId)`: view function returning StatusEntry array
- Events: `ClaimSubmitted(string claimId, bytes32 merkleRoot, address submitter, uint256 timestamp)`, `StatusUpdated(string claimId, ClaimStatus oldStatus, ClaimStatus newStatus, bytes32 reasonHash, uint256 timestamp)`
- Owner access control: only contract owner can call `updateStatus` (simulates insurer authority)

**Deploy using Remix IDE:**
1. Open remix.ethereum.org
2. Paste contract, compile with Solidity 0.8.19+
3. Connect MetaMask (Sepolia testnet)
4. Deploy, copy contract address + ABI
5. Save ABI to `blockchain/abi/ClaimChain.json`
6. Document address in `blockchain/README.md`

**Test in Remix:**
- Call `submitClaimMeta("TEST-001", 0xabc...)` — verify event emitted
- Call `updateStatus("TEST-001", 2, 0xdef...)` — verify status changed
- Call `getClaimRecord("TEST-001")` — verify data returned
- Call `getStatusHistory("TEST-001")` — verify 2 entries

**Commit:** `feat: add ClaimChain smart contract for on-chain claim tracking`

---

### Task 2: Backend API — Skeleton + OCR Integration

**Files:**
- Create: `Backend/api/main.py`
- Create: `Backend/api/routes/claims.py`
- Create: `Backend/api/services/ocr_service.py`
- Create: `Backend/api/utils/store.py`
- Create: `Backend/api/requirements.txt`
- Create: `Backend/api/.env.example`

**What to build:**

**`main.py`** — FastAPI app:
- FastAPI instance with title "ClaimChain API"
- CORS middleware allowing `http://localhost:5173` (React dev server)
- Include routes from `routes/claims.py`
- Startup event: print "ClaimChain API running"

**`utils/store.py`** — In-memory claim storage:
- Python dict: `claims = {}`
- Helper functions: `save_claim(claim_id, data)`, `get_claim(claim_id)`, `get_all_claims()`, `update_claim(claim_id, updates)`
- Each claim record: `{ claim_id, extracted_data, verdict, merkle_root, tx_hash, status, document_hashes, verdict_hash, created_at, events: [] }`

**`services/ocr_service.py`** — Wrapper around existing OCR:
- Add `Backend/OCR` to sys.path
- Import `process_document`, `process_multiple_documents` from `pipeline`
- Function `run_ocr(file_paths: list[str], policy_number: str) -> dict`: calls `process_multiple_documents`, returns `claim.model_dump()`
- Handle errors: FileNotFoundError, ValueError

**`routes/claims.py`** — API endpoints:
- `POST /api/claims/analyze`: accepts `UploadFile` list + `policy_number` form field. Saves files to temp dir, calls `ocr_service.run_ocr()`, generates claim_id (`CLM-YYYYMMDD-NNN`), stores in memory, returns extracted data
- `GET /api/claims/{claim_id}`: returns stored claim data
- `GET /api/claims`: returns list of all claims (for insurer dashboard)

**`requirements.txt`:**
```
fastapi
uvicorn[standard]
python-multipart
python-dotenv
web3
```

**`.env.example`:**
```
# Blockchain
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
WALLET_PRIVATE_KEY=your_sepolia_wallet_private_key
CONTRACT_ADDRESS=your_deployed_contract_address

# Optional: Gemini (for demo)
GEMINI_API_KEY=your_gemini_api_key
```

**How to test:**
```bash
cd Backend/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# In another terminal:
curl -X POST http://localhost:8000/api/claims/analyze \
  -F "files=@../OCR/test_docs/DISCHARGE_SUMMARY.pdf" \
  -F "policy_number=HSP-2025-TN-001"
```
Expected: JSON with claim_id, extracted patient/hospital/billing data.

**Commit:** `feat: add FastAPI skeleton with OCR integration`

---

### Task 3: Backend API — RAG Service Integration

**Files:**
- Create: `Backend/api/services/rag_service.py`
- Modify: `Backend/api/routes/claims.py` (add RAG call to analyze endpoint)

**What to build:**

**`services/rag_service.py`** — Wrapper around existing RAG:
- Add `Backend/RAG` to sys.path
- Import `query_agent` from `agent`
- Function `check_coverage(extracted_data: dict) -> dict`:
  - Builds a natural language query from extracted_data fields (patient name, policy number, procedure, admission type, total amount, hospital)
  - Calls `query_agent(query)`
  - Returns `{ verdict_text: str, query_used: str }`

**Query template:**
```
Patient: {name}, Policy: {policy_number}.
Procedure: {procedures}, Admission: {admission_type}.
Diagnosis: {primary_diagnosis}.
Total bill: Rs {total_amount}. Hospital: {hospital_name}.
Is this covered under the policy? What are the applicable sub-limits,
co-pay percentage, waiting periods, and estimated payable amount?
```

**Modify `routes/claims.py`** — Add RAG to the analyze flow:
- After OCR extraction, call `rag_service.check_coverage(extracted_data)`
- Store verdict in claim record
- Return verdict alongside extracted data

**How to test:**
- Ensure Ollama is running with mistral + nomic-embed-text
- Upload a test PDF, verify response includes both extracted data AND coverage verdict
```bash
curl -X POST http://localhost:8000/api/claims/analyze \
  -F "files=@../OCR/test_docs/DISCHARGE_SUMMARY.pdf" \
  -F "policy_number=HSP-2025-TN-001"
```
Expected: Response now includes `verdict` field with coverage analysis.

**Commit:** `feat: integrate RAG coverage check into claims API`

---

### Task 4: Backend — Hashing + Blockchain Service

**Files:**
- Create: `Backend/api/utils/hashing.py`
- Create: `Backend/api/services/blockchain.py`
- Modify: `Backend/api/routes/claims.py` (add hashing + blockchain to analyze flow)
- Reference: `blockchain/abi/ClaimChain.json` (ABI from Task 1)

**What to build:**

**`utils/hashing.py`** — SHA-256 + Merkle root:
- Function `hash_file(file_path: str) -> str`: reads file bytes, returns SHA-256 hex digest
- Function `hash_string(text: str) -> str`: SHA-256 of UTF-8 encoded string
- Function `compute_merkle_root(hashes: list[str]) -> str`:
  - Takes list of hex hash strings
  - Pairs them, hashes each pair: SHA-256(hash_a + hash_b)
  - If odd number, duplicate last hash
  - Repeats until single root remains
  - Returns hex string (prefix with "0x" for blockchain)

**`services/blockchain.py`** — web3.py contract interaction:
- Load `.env` for RPC URL, private key, contract address
- Load ABI from `blockchain/abi/ClaimChain.json`
- Initialize web3 provider and contract instance
- Function `submit_claim_meta(claim_id: str, merkle_root: str) -> dict`:
  - Converts merkle_root hex string to bytes32
  - Builds + signs + sends transaction calling `submitClaimMeta()`
  - Waits for receipt
  - Returns `{ tx_hash, block_number, gas_used }`
- Function `update_claim_status(claim_id: str, status: int, reason_hash: str) -> dict`:
  - Calls `updateStatus()` on contract
  - Returns `{ tx_hash, block_number }`
- Function `get_claim_events(claim_id: str) -> list[dict]`:
  - Reads `ClaimSubmitted` and `StatusUpdated` events filtered by claimId
  - Returns list of `{ event_type, tx_hash, block_number, timestamp, data }`

**Modify `routes/claims.py`** — Full pipeline:
- After OCR + RAG, compute hashes:
  - Hash each uploaded file
  - Hash the verdict text
  - Compute Merkle root
- Call `blockchain.submit_claim_meta(claim_id, merkle_root)`
- Store tx_hash, merkle_root, document_hashes, verdict_hash in claim record
- Return blockchain proof in response

**How to test:**
- Deploy contract from Task 1, put address in `.env`
- Get Sepolia ETH from faucet (Google "Sepolia faucet")
- Upload test PDF through API
- Check Sepolia Etherscan for the transaction
- Verify merkle_root matches on-chain data

**Commit:** `feat: add SHA-256 hashing and blockchain integration`

---

### Task 5: Backend — Insurer Review Endpoint

**Files:**
- Create: `Backend/api/routes/review.py`
- Modify: `Backend/api/main.py` (include review router)

**What to build:**

**`routes/review.py`** — Insurer actions:
- `POST /api/claims/{claim_id}/review`:
  - Accepts JSON body: `{ action: "approve" | "reject" | "query", reason: "string" }`
  - Maps action to status enum: approve=2, reject=3, query=4
  - Hashes the reason string: `hash_string(reason)`
  - Calls `blockchain.update_claim_status(claim_id, status_int, reason_hash)`
  - Updates claim in store with new status + tx_hash
  - Returns `{ claim_id, new_status, tx_hash, reason_hash }`

**Modify `main.py`:**
- Add `from routes.review import router as review_router`
- Include in app

**How to test:**
```bash
# First create a claim via Task 2-4 flow
# Then approve it:
curl -X POST http://localhost:8000/api/claims/CLM-20260303-001/review \
  -H "Content-Type: application/json" \
  -d '{"action": "approve", "reason": "All documents verified, coverage confirmed"}'
```
Expected: Response with new status + Sepolia tx_hash. Etherscan shows StatusUpdated event.

**Commit:** `feat: add insurer review endpoint with on-chain status update`

---

### Task 6: Frontend — Project Setup + Upload Page

**Files:**
- Create: `frontend/` (entire React project via Vite)
- Key files: `src/App.jsx`, `src/pages/Upload.jsx`, `src/components/FileUpload.jsx`, `src/services/api.js`

**What to build:**

**Project setup:**
```bash
cd "GenAI Insurance V1"
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install react-router-dom axios lucide-react
```

**`src/services/api.js`** — Backend API wrapper:
- Base URL: `http://localhost:8000` (configurable)
- `analyzeClaim(files, policyNumber)`: POST multipart to `/api/claims/analyze`
- `getClaim(claimId)`: GET `/api/claims/{claimId}`
- `getAllClaims()`: GET `/api/claims`
- `reviewClaim(claimId, action, reason)`: POST to `/api/claims/{claimId}/review`

**`src/App.jsx`** — Router:
- Route `/` -> Upload page
- Route `/verdict/:claimId` -> Verdict page
- Route `/insurer` -> Insurer dashboard

**`src/components/FileUpload.jsx`**:
- Drag-and-drop zone for PDF/image files
- Shows file names + sizes after selection
- Accepts multiple files
- File type validation (PDF, PNG, JPG only)

**`src/pages/Upload.jsx`**:
- Policy number text input
- FileUpload component
- "Analyze & Submit Claim" button
- Loading state with progress messages: "Reading documents...", "Checking coverage...", "Recording on blockchain..."
- On success: redirect to `/verdict/{claim_id}`

**How to test:**
```bash
cd frontend
npm run dev
```
- Open http://localhost:5173
- Upload a PDF + enter policy number
- Verify it calls backend and redirects to verdict page

**Commit:** `feat: add React frontend with upload page`

---

### Task 7: Frontend — Verdict Page + Claim Timeline

**Files:**
- Create: `src/pages/Verdict.jsx`
- Create: `src/components/VerdictCard.jsx`
- Create: `src/components/ClaimTimeline.jsx`
- Create: `src/components/ClaimSummary.jsx`

**What to build:**

**`src/components/ClaimSummary.jsx`** — Extracted data display:
- Card showing: patient name, age, policy number
- Hospital name, doctor
- Primary diagnosis, procedures
- Total bill amount, itemized breakdown
- Admission/discharge dates
- Confidence score badge

**`src/components/VerdictCard.jsx`** — AI coverage verdict:
- Green/yellow/red banner based on coverage percentage
- Verdict text (the RAG response)
- Estimated coverage amount
- Co-pay percentage
- Missing documents list (if any)
- "Proof Hash" section showing merkle_root + link to Sepolia Etherscan tx

**`src/components/ClaimTimeline.jsx`** — On-chain event history:
- Vertical timeline (line with dots)
- Each event: icon + label + timestamp + block number + tx hash (clickable link to `https://sepolia.etherscan.io/tx/{hash}`)
- Event types: "AI Verdict Committed" (blue), "Claim Submitted" (blue), "Under Review" (yellow), "Approved" (green), "Rejected" (red), "Query Raised" (orange)
- Auto-refreshes every 10 seconds (poll GET /api/claims/{id})

**`src/pages/Verdict.jsx`**:
- Reads `claimId` from URL params
- Calls `getClaim(claimId)` on mount
- Renders: ClaimSummary + VerdictCard + ClaimTimeline
- Loading skeleton while fetching

**How to test:**
- Create a claim through upload page
- Verify verdict page shows all sections
- Verify Etherscan links work (open in new tab)
- Approve claim from backend (curl), verify timeline updates

**Commit:** `feat: add verdict page with claim summary, verdict card, and timeline`

---

### Task 8: Frontend — Insurer Dashboard

**Files:**
- Create: `src/pages/InsurerDashboard.jsx`

**What to build:**

**`src/pages/InsurerDashboard.jsx`**:
- Calls `getAllClaims()` on mount
- Table/card list of all claims: claim_id, patient name, hospital, amount, status, date
- Click a claim -> expands to show full extracted data + AI verdict
- Two action buttons: "Approve" (green) and "Reject" (red)
- Reject requires a reason (text input modal/inline)
- On action: calls `reviewClaim(claimId, action, reason)`
- Shows success with tx_hash link to Etherscan
- Refreshes claim list after action

**Navigation:**
- Add a simple navbar/header to App.jsx with links: "Submit Claim" (/) and "Insurer Portal" (/insurer)

**How to test:**
- Create 2-3 claims through upload
- Open /insurer, verify all claims appear
- Approve one, reject another with reason
- Verify on-chain events update
- Switch to /verdict/{id} and verify timelines updated

**Commit:** `feat: add insurer dashboard with approve/reject functionality`

---

### Task 9: Gemini Integration (Demo Mode)

**Files:**
- Modify: `Backend/OCR/nlp_extractor.py` (add Gemini option alongside Ollama)
- Modify: `Backend/RAG/agent.py` (add Gemini LLM option)
- Modify: `Backend/OCR/config.py` (add GEMINI_API_KEY)
- Modify: `Backend/RAG/config.py` (add GEMINI_API_KEY)

**What to build:**

**Option A (Recommended — minimal changes):**
- Add `USE_GEMINI=true` flag to `.env`
- In `nlp_extractor.py`: if USE_GEMINI, use `langchain-google-genai` ChatGoogleGenerativeAI instead of ChatOllama for the LLM extraction step. Same prompt, different model.
- In `agent.py`: if USE_GEMINI, use ChatGoogleGenerativeAI instead of ChatOllama for the agent LLM. Keep ChromaDB + nomic-embed-text embeddings (these stay local — Gemini doesn't do embeddings for free).
- Install: `pip install langchain-google-genai`

**Why Gemini for demo:**
- Faster inference than local Ollama (important for live demo)
- Gemini 1.5 Flash free tier: 15 requests/minute, sufficient for demo
- Multimodal: could directly process images without Tesseract (stretch goal, not required)

**Fallback:** If Gemini is down or rate-limited, set `USE_GEMINI=false` and Ollama kicks in.

**How to test:**
- Set `USE_GEMINI=true` and `GEMINI_API_KEY` in `.env`
- Run the same upload flow
- Verify extraction + RAG still work, but faster
- Time comparison: Ollama vs Gemini (Gemini should be 3-5x faster)

**Commit:** `feat: add Gemini API support as alternative to Ollama`

---

### Task 10: End-to-End Polish + Demo Prep

**Files:**
- Modify: various frontend components (loading states, error handling)
- Create: `Backend/OCR/test_docs/demo_scenario.md` (scripted demo data)

**What to build:**

**Error handling:**
- Backend: return proper HTTP error codes (400 for bad input, 500 for OCR/RAG failure, 503 for blockchain connection issue)
- Frontend: show user-friendly error messages, not stack traces
- Blockchain: if tx fails, still return OCR + RAG results with a "blockchain unavailable" warning

**Loading states:**
- Upload page: multi-step progress indicator
  - Step 1: "Reading documents..." (OCR)
  - Step 2: "Checking policy coverage..." (RAG)
  - Step 3: "Recording proof on blockchain..." (web3)
  - Step 4: "Done!" (redirect)

**Demo scenario documentation (`demo_scenario.md`):**
```
Patient: Rajesh Kumar, Age 45, Male
Policy: HSP-2025-TN-001 (Silver Tier, Sum Insured: Rs 3,00,000)
Hospital: Apollo Hospitals, Chennai
Doctor: Dr. Priya Sharma
Diagnosis: Age-related Cataract (ICD: H26.9)
Procedure: Phacoemulsification with IOL implant (day-care)
Admission: 2026-02-20, Discharge: 2026-02-20
Total Bill: Rs 45,000
  - Surgery: Rs 35,000
  - Medicines: Rs 5,000
  - Consumables: Rs 3,000
  - Doctor Fee: Rs 2,000

Expected AI Verdict:
- Cataract surgery: covered as day-care procedure
- 24-month waiting period: COMPLETED (policy start assumed > 24 months ago)
- Co-pay: 10% (Silver tier)
- Estimated payable: Rs 40,500
- Room rent: N/A (day-care)
```

**Commit:** `feat: add error handling, loading states, and demo scenario`

---

### Task 11: Deployment

**Frontend -> Vercel:**
```bash
cd frontend
npm run build
# Push to GitHub, connect repo to Vercel
# Set env var: VITE_API_URL = https://your-backend.onrender.com
```

**Backend -> Render:**
- Create `Backend/api/Procfile` or use Render's build commands:
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set env vars: SEPOLIA_RPC_URL, WALLET_PRIVATE_KEY, CONTRACT_ADDRESS, GEMINI_API_KEY
- Note: Render free tier sleeps after 15 min inactivity. Wake it up 5 min before demo.

**Contract:** Already on Sepolia from Task 1.

**Test deployed version:**
- Open Vercel URL
- Upload test PDF
- Verify full flow works end-to-end on deployed infra
- Check Sepolia Etherscan for transactions

**Commit:** `feat: add deployment configuration`

---

### Task 12: Pitch Deck

**Files:**
- Create: `pitch/slides.md` (outline for presentation)

**Pitch structure (5-7 minutes):**

**Slide 1 — The Problem (30 sec)**
- Insurance claims take 30+ days
- Patients have zero visibility into why claims are delayed/denied
- No proof of what the system originally assessed

**Slide 2 — ClaimChain Solution (30 sec)**
- GenAI reads medical documents and checks coverage instantly
- Every AI verdict is committed on-chain BEFORE the insurer sees it
- Tamper-proof, transparent claim lifecycle

**Slide 3 — Architecture (30 sec)**
- Show the 3-layer diagram: Frontend -> Backend (OCR + RAG) -> Blockchain
- Highlight: "No personal data on-chain — only cryptographic hashes"

**Slide 4 — LIVE DEMO (3 min)**
- Walk through the 5-scene demo flow from the workflow doc
- End with: "The patient can verify the original AI verdict on Etherscan right now"

**Slide 5 — Why Blockchain, Not a Database? (30 sec)**
- Database: controlled by one party, records can be changed
- Blockchain: immutable, verifiable by anyone, no single point of trust
- "The patient doesn't need to trust the insurer's IT system"

**Slide 6 — Impact + Feasibility (30 sec)**
- Faster claims: AI pre-check reduces manual review time
- Fewer disputes: both sides have verifiable proof
- Built entirely with free, open-source tools
- Architecture is production-ready with L2 scaling

**Slide 7 — Team + Tech Stack (15 sec)**
- Solo developer
- Python, FastAPI, LangGraph, ChromaDB, Solidity, React
- All free-tier tools

---

## Dependency Graph (Task Order)

```
Task 1: Smart Contract (Remix)          -- no dependencies
Task 2: API Skeleton + OCR              -- no dependencies
Task 3: RAG Integration                 -- depends on Task 2
Task 4: Hashing + Blockchain            -- depends on Task 1 + Task 3
Task 5: Insurer Review Endpoint         -- depends on Task 4
Task 6: Frontend Setup + Upload         -- depends on Task 2
Task 7: Verdict Page + Timeline         -- depends on Task 4 + Task 6
Task 8: Insurer Dashboard               -- depends on Task 5 + Task 6
Task 9: Gemini Integration              -- depends on Task 3
Task 10: Polish + Demo Prep             -- depends on Task 7 + Task 8
Task 11: Deployment                     -- depends on Task 10
Task 12: Pitch Deck                     -- depends on Task 10
```

**Parallelizable:**
- Task 1 (contract) and Task 2 (API skeleton) can be done simultaneously
- Task 6 (frontend setup) can start as soon as Task 2 is done, in parallel with Tasks 3-5
- Task 9 (Gemini) can be done anytime after Task 3
- Task 11 (deploy) and Task 12 (pitch) can be done in parallel

---

## Day-to-Task Mapping

| Day | Tasks | Deliverable |
|-----|-------|-------------|
| Day 1 | Task 1 (Contract) + Task 2 (API + OCR) | Contract on Sepolia + API returning OCR data |
| Day 2 | Task 3 (RAG) + Task 4 (Hashing + Blockchain) | Full backend pipeline: upload -> OCR -> RAG -> on-chain |
| Day 3 | Task 5 (Review endpoint) + Task 6 (Frontend setup + upload) | Insurer endpoint + working upload page |
| Day 4 | Task 7 (Verdict + Timeline) + Task 8 (Insurer dashboard) | Complete frontend with all pages |
| Day 5 | Task 9 (Gemini) + Task 10 (Polish) | Fast demo mode + error handling |
| Day 6 | Task 10 (continued) + Task 11 (Deploy) | Deployed and tested end-to-end |
| Day 7 | Task 12 (Pitch) + Full rehearsal | Pitch deck + rehearsed demo |

---

## Environment Setup Checklist

Before starting Task 1, ensure you have:

- [ ] **Node.js 18+** installed (`node --version`)
- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **Ollama** running with `mistral` + `nomic-embed-text` models (`ollama list`)
- [ ] **MetaMask** browser extension with Sepolia testnet selected
- [ ] **Sepolia ETH** in your MetaMask wallet (use Google Cloud faucet or Alchemy faucet)
- [ ] **Tesseract OCR** installed and in PATH (`tesseract --version`)
- [ ] **Git** configured for commits
- [ ] **(Optional)** Google Gemini API key from ai.google.dev (free tier)
- [ ] **(Optional)** Infura/Alchemy API key for Sepolia RPC (free tier)
