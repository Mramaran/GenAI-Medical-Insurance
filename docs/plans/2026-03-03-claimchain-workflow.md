# ClaimChain — Hackathon Workflow & Execution Plan

## What You're Building

**ClaimChain**: A GenAI-powered medical insurance claims assistant where every AI coverage verdict is cryptographically committed on-chain BEFORE the insurer sees it. Patients get a tamper-proof, transparent claim timeline.

**Why it wins**: Insurance claim disputes are a massive real-world problem. Patients have no proof of what the AI/system originally assessed. ClaimChain makes every step — AI verdict, insurer decision, reasoning — immutable and verifiable on-chain. Blockchain isn't bolted on; it's the trust backbone.

---

## What You Already Have (First Cut Analysis)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| OCR Pipeline | WORKING | `Backend/OCR/` | Tesseract + PyMuPDF + spaCy + Ollama/Mistral. Extracts structured JSON from medical PDFs/images |
| RAG Agent | WORKING | `Backend/RAG/` | LangGraph agentic RAG with ChromaDB. 3 policy docs ingested. Answers coverage questions |
| Pydantic Models | WORKING | `Backend/OCR/models.py` | `ExtractedClaim` with patient, hospital, diagnosis, treatment, billing, dates |
| Policy Knowledge Base | WORKING | `Backend/RAG/policies/` | 3 markdown files: general policy, coverage details, claims procedures |
| Test Documents | AVAILABLE | `Backend/OCR/test_docs/` | Apollo Hospitals PDF, discharge summary, prescription |
| Architecture Diagram | DRAFTED | `Backend/architecture.md` | 8-step flow from upload to timeline |
| API Server | NOT STARTED | — | Need FastAPI to glue OCR + RAG + blockchain |
| Smart Contract | NOT STARTED | — | Need Solidity contract for claim hashes |
| Frontend | NOT STARTED | — | Need React/Next.js UI |

---

## Free Tools Stack

| Layer | Tool | Why | Cost |
|-------|------|-----|------|
| GenAI (Documents) | Google Gemini API (free tier) | Multimodal — can read images of prescriptions directly. 15 RPM free. Better for live demo than local Ollama | Free |
| GenAI (Fallback/Dev) | Ollama + Mistral (local) | Already set up. Use during development. Mention as "offline capability" in pitch | Free |
| OCR | Tesseract + PyMuPDF | Already working in your pipeline | Free |
| NLP/Embeddings | spaCy + nomic-embed-text | Already working | Free |
| RAG Vector DB | ChromaDB | Already working, persisted | Free |
| RAG Orchestration | LangGraph + LangChain | Already working | Free |
| Blockchain | Ethereum Sepolia Testnet | Free testnet ETH from faucets | Free |
| Smart Contracts | Solidity + Hardhat (or Remix IDE) | Remix is browser-based, zero setup | Free |
| Blockchain Interaction | ethers.js / web3.py | Connect frontend/backend to contract | Free |
| Backend API | FastAPI | Lightweight, async, auto-generates OpenAPI docs for demo | Free |
| Frontend | React (Vite) or Next.js | Fast dev, free hosting on Vercel | Free |
| Frontend UI | Tailwind CSS + shadcn/ui | Professional-looking UI quickly | Free |
| Hosting (Demo) | Vercel (frontend) + Render (backend) | Free tiers sufficient for demo | Free |
| Wallet (Demo) | MetaMask | Browser wallet for blockchain interaction | Free |
| Testnet ETH | Sepolia Faucets (Google, Alchemy, Infura) | Free test ETH for contract deployment | Free |

---

## Architecture Overview

```
                        CLAIMCHAIN ARCHITECTURE

[Hospital Staff / Patient]
        |
        | (1) Upload medical docs + policy number
        v
+------------------+
|   Frontend       |  React + Tailwind
|   (Vercel)       |  - Upload UI
|                  |  - Coverage verdict display
|                  |  - On-chain claim timeline
+--------+---------+
         |
         | REST API calls
         v
+------------------+
|   Backend API    |  FastAPI (Render)
|                  |
|  +-----------+   |  (2) OCR Pipeline: extract structured data
|  | OCR       |   |      from medical documents
|  +-----------+   |
|       |          |
|       v          |
|  +-----------+   |  (3) RAG Agent: check coverage against
|  | RAG       |   |      policy rules, generate verdict
|  +-----------+   |
|       |          |
|       v          |
|  +-----------+   |  (4) Compute SHA-256 hash of:
|  | Hash +    |   |      document hashes + AI verdict JSON
|  | Blockchain|   |      Call submitClaimMeta() on contract
|  +-----------+   |
+--------+---------+
         |
         | ethers.js / web3.py
         v
+------------------+
|  Smart Contract  |  Solidity on Sepolia
|  (ClaimChain)    |
|                  |  - submitClaimMeta(claimId, merkleRoot)
|                  |  - updateStatus(claimId, status, reasonHash)
|                  |  - getClaimHistory(claimId)
|                  |  - Events: ClaimSubmitted, StatusUpdated
+------------------+
         |
         | Events (frontend listens)
         v
+------------------+
|  Claim Timeline  |  React component
|  (Patient View)  |  Shows on-chain events:
|                  |  - "AI Verdict Committed" (hash)
|                  |  - "Claim Submitted" (timestamp)
|                  |  - "Insurer Approved/Rejected" (reason hash)
+------------------+
```

---

## Demo Flow (What Judges See)

This is the exact sequence you'll demo. Practice this flow.

### Scene 1: Hospital Staff Uploads Documents
1. Open ClaimChain web app
2. Enter policy number: `HSP-2025-TN-001`
3. Upload discharge summary PDF + hospital bill PDF
4. Click "Analyze & Submit Claim"

### Scene 2: AI Processes (10-15 seconds)
5. Loading screen shows: "Reading documents... Checking coverage... Computing proof..."
6. Backend runs OCR → extracts structured JSON
7. Backend sends extracted data to RAG agent → gets coverage verdict
8. Backend computes SHA-256 hash of (document hashes + verdict JSON)
9. Backend calls `submitClaimMeta()` on Sepolia contract

### Scene 3: Patient Sees Verdict + Proof
10. Screen shows:
    - **Coverage Verdict**: "Estimated coverage: 85% of your bill is payable"
    - **Reasons**: "Room rent within Silver tier limit (Rs.4,000/day). Cataract surgery covered — 24-month waiting period completed. 10% co-pay applies."
    - **Missing Documents**: "Pharmacy bill not uploaded — optional but may increase coverage"
    - **On-Chain Proof**: Link to Sepolia explorer showing the transaction with Merkle root
11. **Claim Timeline** shows first event: "AI Verdict Committed — Block #12345, Hash: 0xabc..."

### Scene 4: Insurer Reviews (Simulated)
12. Switch to "Insurer Dashboard" view
13. Insurer sees AI-summarized claim with structured data
14. Insurer clicks "Approve" (or "Reject" with mandatory reason)
15. Backend calls `updateStatus()` on contract

### Scene 5: Patient Sees Final Status
16. Patient's Claim Timeline updates:
    - Event 1: "AI Verdict Committed" — hash, timestamp
    - Event 2: "Claim Submitted to Insurer" — hash, timestamp
    - Event 3: "Insurer Approved" — reason hash, timestamp
17. **Key moment for judges**: "If the insurer had changed the AI verdict or denied without reason, the patient could verify the original AI assessment on-chain. This is impossible to tamper with."

---

## Day-by-Day Work Plan (7 Days)

### Day 1: Smart Contract + Backend API Skeleton

**Smart Contract (Remix IDE — no local setup needed):**
- Write `ClaimChain.sol` with:
  - `submitClaimMeta(string claimId, bytes32 merkleRoot)` — stores hash, emits event
  - `updateStatus(string claimId, uint8 status, bytes32 reasonHash)` — status enum (Submitted, UnderReview, Approved, Rejected, QueryRaised)
  - `getClaimHistory(string claimId)` — returns array of status changes
  - Events: `ClaimSubmitted(claimId, merkleRoot, timestamp)`, `StatusUpdated(claimId, status, reasonHash, timestamp)`
- Deploy to Sepolia testnet via Remix + MetaMask
- Save contract address and ABI

**Backend API Skeleton (FastAPI):**
- Create `Backend/api/` directory
- Set up FastAPI app with routes:
  - `POST /api/claim/analyze` — accepts file uploads + policy number
  - `GET /api/claim/{id}` — returns claim data + status
  - `POST /api/claim/{id}/review` — insurer approve/reject
- Wire OCR pipeline: import and call `process_document()` from existing OCR module
- Wire RAG agent: import and call `query_agent()` from existing RAG module
- Test: upload a PDF → get structured JSON back

**Deliverable**: Contract deployed on Sepolia. API returns OCR + RAG results for uploaded docs.

---

### Day 2: Backend Blockchain Integration + Hashing

**Connect Backend to Smart Contract:**
- Install `web3.py` in backend
- Create `Backend/api/blockchain.py`:
  - Load contract ABI + address
  - Use a backend wallet (private key in `.env` — Sepolia only, not real money)
  - Function: `submit_claim_to_chain(claim_id, document_hashes, verdict_json)` → computes SHA-256 Merkle root → calls `submitClaimMeta()`
  - Function: `update_claim_status(claim_id, status, reason)` → calls `updateStatus()`
  - Function: `get_claim_events(claim_id)` → reads contract events

**Hashing Logic:**
- Hash each uploaded document with SHA-256
- Hash the AI verdict JSON with SHA-256
- Combine all hashes into a Merkle root (simple binary tree)
- This Merkle root is what goes on-chain

**End-to-End Test:**
- Upload PDF → OCR extracts → RAG checks coverage → hash computed → submitted to Sepolia → verify on Etherscan
- This is the core flow. If this works, you have the hackathon demo.

**Deliverable**: Full backend pipeline works end-to-end. On-chain transactions visible on Sepolia Etherscan.

---

### Day 3: Frontend — Upload + Verdict Screen

**Set Up React App:**
- `npx create-vite@latest frontend --template react` (or Next.js if preferred)
- Install Tailwind CSS + shadcn/ui for fast, professional styling
- Create pages:
  - **Home/Upload Page**: File upload dropzone + policy number input + "Analyze" button
  - **Verdict Page**: Shows coverage verdict, reasons, missing docs, on-chain proof link

**Connect to Backend:**
- Upload files → call `POST /api/claim/analyze`
- Display structured verdict response
- Show loading states during processing

**Deliverable**: User can upload documents and see AI coverage verdict in the browser.

---

### Day 4: Frontend — Claim Timeline + Insurer Dashboard

**Claim Timeline Component:**
- Vertical timeline showing on-chain events
- Each event shows: action, timestamp, block number, transaction hash (link to Sepolia Etherscan)
- Poll backend for new events (or use WebSocket if time permits)

**Insurer Dashboard (Separate View/Route):**
- List of pending claims with AI summaries
- Click claim → see full extracted data + RAG verdict
- Approve/Reject buttons (Reject requires reason text input)
- On action → calls `POST /api/claim/{id}/review` → backend updates on-chain

**Deliverable**: Two working views — Patient (upload + timeline) and Insurer (review + decide).

---

### Day 5: Gemini Integration + Polish

**Swap Ollama for Gemini (Demo Mode):**
- Add Google Gemini API key to `.env`
- Create a Gemini-based extractor alongside the Ollama one
- Use Gemini for the demo (faster, multimodal — can read prescription images directly)
- Keep Ollama as fallback (mention in pitch: "works offline too")
- Update RAG agent to optionally use Gemini as the LLM

**Polish:**
- Error handling in API (file too large, unsupported format, contract call failed)
- Loading spinners and progress indicators in frontend
- Responsive layout (demo might be on a projector)

**Deliverable**: Demo runs on Gemini free tier. Looks polished.

---

### Day 6: Demo Data + End-to-End Testing

**Prepare Demo Data:**
- Use your existing test PDFs (Apollo Hospitals, discharge summary, prescription)
- Create a scripted demo scenario:
  - Patient "Rajesh Kumar", policy HSP-2025-TN-001 (Silver tier)
  - Admitted for cataract surgery (day-care procedure)
  - Total bill: Rs. 45,000
  - Expected verdict: ~85% covered (10% co-pay for Silver, room rent within limit, cataract covered after 24-month waiting period)
- Pre-test the exact flow you'll demo multiple times

**End-to-End Testing:**
- Run through the full demo flow 5+ times
- Test error cases: missing policy, unsupported file, network issues
- Check that on-chain events appear correctly on Sepolia Etherscan
- Time the demo — aim for under 5 minutes for the walkthrough

**Deliverable**: Demo is rehearsed, data is prepared, edge cases handled.

---

### Day 7: Pitch Deck + Deploy + Final Rehearsal

**Pitch Deck (5-7 slides):**
1. **Problem**: Claims processing is slow, opaque, and disputable. Patients have no proof.
2. **Solution**: ClaimChain — GenAI reads docs, checks coverage, commits verdict on-chain.
3. **Demo Screenshot / Architecture**: Show the architecture diagram.
4. **Live Demo**: Walk through the 5-scene flow.
5. **Why Blockchain Matters Here**: Not just a buzzword. On-chain verdicts = dispute-proof, tamper-proof, transparent. Answer the "why not a database?" question proactively.
6. **Impact**: Faster claims, fewer denials, trust between patients and insurers.
7. **Tech Stack**: Show the free tools. Mention it's all open-source and free-tier.

**Deploy:**
- Frontend → Vercel (free)
- Backend → Render (free tier) or Railway
- Contract already on Sepolia
- Test the deployed version, not just localhost

**Final Rehearsal:**
- Full run-through: pitch → live demo → Q&A prep
- Prepare answers for likely judge questions (see below)

**Deliverable**: Deployed, rehearsed, ready to present.

---

## Likely Judge Questions & Answers

**Q: "Why blockchain instead of just a database?"**
A: A database is controlled by one party — the insurer can modify records. On-chain data is immutable and verifiable by anyone. The patient can independently prove what the AI assessed without trusting the insurer's system. That's the point — trustless verification.

**Q: "What about gas fees and scalability?"**
A: We store only hashes on-chain (32 bytes per claim), not full documents. This keeps costs minimal. For production, Layer 2 solutions (Polygon, Optimism) offer near-zero fees. The architecture is chain-agnostic.

**Q: "What if the AI is wrong?"**
A: The AI proposes, humans decide. The insurer always has final authority. But if they override the AI, their reasoning is also recorded on-chain. This creates accountability on both sides.

**Q: "How does this handle privacy?"**
A: No personal data goes on-chain. Only cryptographic hashes of documents and verdicts. The actual data stays in the backend database. You can verify a claim without exposing its contents.

**Q: "Can this work with real insurers?"**
A: The OCR and RAG modules are production-grade patterns. The smart contract is simple and auditable. Integration with real insurer systems would be through their existing APIs (TPA portals). The architecture is designed for this.

---

## Key Files to Create

```
GenAI Insurance V1/
├── Backend/
│   ├── OCR/                    [EXISTS - WORKING]
│   ├── RAG/                    [EXISTS - WORKING]
│   ├── api/                    [CREATE]
│   │   ├── main.py             # FastAPI app
│   │   ├── routes/
│   │   │   ├── claims.py       # Claim endpoints
│   │   │   └── review.py       # Insurer endpoints
│   │   ├── services/
│   │   │   ├── ocr_service.py  # Wraps OCR pipeline
│   │   │   ├── rag_service.py  # Wraps RAG agent
│   │   │   └── blockchain.py   # Web3 contract interaction
│   │   ├── utils/
│   │   │   └── hashing.py      # SHA-256 + Merkle root
│   │   ├── requirements.txt
│   │   └── .env                # Gemini key, wallet key, contract address
│   └── architecture.md         [EXISTS - UPDATE]
│
├── blockchain/                  [CREATE]
│   ├── contracts/
│   │   └── ClaimChain.sol      # Smart contract
│   ├── scripts/
│   │   └── deploy.js           # Deployment script (if using Hardhat)
│   └── README.md               # Contract address, ABI location
│
├── frontend/                    [CREATE]
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Upload.jsx      # Document upload + policy input
│   │   │   ├── Verdict.jsx     # AI verdict + on-chain proof
│   │   │   ├── Timeline.jsx    # Claim timeline (on-chain events)
│   │   │   └── InsurerDash.jsx # Insurer review dashboard
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── VerdictCard.jsx
│   │   │   ├── TimelineEvent.jsx
│   │   │   └── ClaimSummary.jsx
│   │   └── services/
│   │       └── api.js          # Backend API calls
│   └── package.json
│
├── docs/
│   └── plans/
│       └── 2026-03-03-claimchain-workflow.md  [THIS FILE]
│
├── idea.md                      [EXISTS]
├── our statement.md             [EXISTS]
└── pitch/                       [CREATE ON DAY 7]
    └── slides.md                # Pitch deck outline
```

---

## What Makes This Win

1. **Blockchain isn't a gimmick**: On-chain AI verdicts solve a real trust problem. You can answer "why not a database?" convincingly.
2. **GenAI is doing real work**: OCR + RAG for document understanding and policy checking — not just a chatbot wrapper.
3. **End-to-end working demo**: Upload docs → AI verdict → on-chain proof → insurer review → patient timeline. Judges see the full journey.
4. **Privacy-preserving**: No personal data on-chain, only hashes. Shows you thought about compliance.
5. **All free tools**: Demonstrates resourcefulness. Everything is open-source or free-tier.
6. **Solo build**: If judges know you built this alone, it's even more impressive.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Ollama too slow for demo | Switch to Gemini API for demo. Keep Ollama as "offline feature" |
| Sepolia faucet issues | Get testnet ETH on Day 1. Have backup faucet URLs. Pre-fund wallet with extra ETH |
| Frontend takes too long | Use shadcn/ui components — don't design from scratch. Ugly-but-working beats pretty-but-broken |
| Contract bugs | Keep contract simple (2 functions + events). Test thoroughly on Day 1-2 |
| Network issues during demo | Pre-record a backup video of the full demo flow |
| Gemini rate limit during demo | Cache one demo result. Show cached if API is slow |
