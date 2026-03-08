# ClaimChain — Diagram Descriptions for Figma

---

## Figure 1: System Architecture Diagram

### Layout: 3 horizontal layers stacked vertically with arrows between them

**Layer 1 — PRESENTATION LAYER (top)**
- Title bar: "Frontend — React 18 + Vite 5"
- Two boxes side by side:

| Customer Portal | Insurer Portal |
|----------------|---------------|
| Upload Documents | Review Claims |
| View AI Verdict | AI Summary View |
| Track Claim Status | Fraud Risk Score |
| Blockchain Timeline | Approve / Reject |

- Tech tags below: `React 18` `Vite 5` `React Router` `Axios`

**Arrow down:** `REST API (JSON)`

**Layer 2 — ORCHESTRATION LAYER (middle)**
- Title bar: "Backend — FastAPI + Python 3.13"
- Three boxes side by side:

| OCR Engine (Green) | Agentic RAG (Purple) | Blockchain Service (Orange) |
|--------------------|---------------------|---------------------------|
| Tesseract OCR | LangGraph Workflow | Web3.py |
| PyMuPDF (fitz) | ChromaDB Vector DB | SHA-256 Hashing |
| spaCy NER | Gemini / Mistral LLM | Merkle Root Builder |
| Confidence Scoring | Self-Correcting Agent | Contract Interaction |

- Tech tags below: `FastAPI` `Uvicorn` `Python 3.13` `Pydantic`

**Arrow down:** `SHA-256 Merkle Root`

**Layer 3 — BLOCKCHAIN LAYER (bottom)**
- Title bar: "Ethereum Sepolia — ClaimChain.sol"
- Single wide dark box:
  - `submitClaimMeta(claimId, merkleRoot)` → Immutable Proof
  - `updateStatus(claimId, status, reasonHash)` → Status Tracking
  - `getStatusHistory(claimId)` → Full Audit Timeline
  - Events: `ClaimSubmitted`, `StatusUpdated` → Frontend Polling
- Tech tags below: `Solidity 0.8.19` `Ethereum Sepolia` `Etherscan Verified`

### Suggested Colors
- Customer Portal / Insurer Portal: Blue (#2193b0 → #6dd5ed)
- OCR Engine: Green (#11998e → #38ef7d)
- Agentic RAG: Purple (#667eea → #764ba2)
- Blockchain Service: Orange (#f2994a → #f2c94c)
- Blockchain Layer: Dark (#0f0c29 → #302b63)
- Arrows: Gray (#999)

---

## Figure 2: End-to-End Claim Workflow

### Layout: Vertical numbered steps connected by lines/arrows

**Step 1** (Blue circle) — **Document Upload**
- Patient/hospital uploads discharge summary + hospital bill via Customer Portal
- Enters policy number for coverage lookup

**Step 2** (Green circle) — **OCR + NLP Extraction**
- Tesseract OCR extracts text from scanned documents
- spaCy NLP identifies patient name, diagnosis, procedures, billing amounts, dates
- Confidence score calculated (e.g., 92%)

**Step 3** (Purple circle) — **Agentic RAG — Policy Coverage Check**
- LangGraph agent retrieves relevant policy clauses from ChromaDB
- Grades document relevance, rewrites queries if needed
- Generates natural-language coverage verdict with co-pay, exclusion, and waiting period analysis

**Step 4** (Orange circle) — **Merkle Root Hashing + Blockchain Submission**
- SHA-256 hashes computed for each document and the AI verdict
- Combined into a Merkle root
- Submitted to ClaimChain smart contract on Ethereum Sepolia
- Transaction hash returned

**Step 5** (Cyan circle) — **Patient Views Result**
- Customer Portal displays: extracted data with confidence indicators
- AI coverage verdict
- Blockchain proof (Merkle root + Etherscan link)
- Live on-chain claim timeline

**Step 6** (Red circle) — **Insurer Reviews & Decides**
- Insurer Portal shows AI-summarized claim with fraud risk score
- Claims officer reviews and clicks Approve or Reject
- Decision recorded on-chain with reason hash

**Step 7** (Green circle) — **Transparent Tracking**
- Patient sees real-time on-chain timeline
- Every status change: Submitted → Under Review → Approved
- Timestamp and actor shown — fully verifiable on Etherscan

### Suggested Colors for Step Numbers
1. #667eea (Blue)
2. #11998e (Green)
3. #764ba2 (Purple)
4. #f2994a (Orange)
5. #2193b0 (Cyan)
6. #e44d26 (Red)
7. #38ef7d (Green)

---

## Figure 3: LangGraph Agentic RAG Pipeline

### Layout: Flowchart with decision diamonds and process boxes

```
                    ┌──────────┐
                    │  START   │
                    │  Claim   │
                    │  Query   │
                    └────┬─────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Node 1:            │
              │  generate_or_       │  ◇ DECISION
              │  retrieve           │
              │                     │
              │  LLM decides:       │
              │  retrieve from DB   │
              │  or answer directly │
              └──────┬────────┬─────┘
                     │        │
          ┌──────────┘        └──────────┐
          │ Needs retrieval              │ Can answer directly
          ▼                              │
   ┌──────────────┐                      │
   │  Node 2:     │                      │
   │  retrieve    │                      │
   │              │                      │
   │  ChromaDB    │                      │
   │  MMR search  │                      │
   │  k=4 docs    │                      │
   └──────┬───────┘                      │
          │                              │
          ▼                              │
   ┌──────────────┐                      │
   │  Node 3:     │                      │
   │  grade_      │  ◇ DECISION         │
   │  documents   │                      │
   │              │                      │
   │  Are clauses │                      │
   │  relevant?   │                      │
   └──┬───────┬───┘                      │
      │       │                          │
      │       └────────────┐             │
      │ Relevant ✓         │ Not relevant ✗
      │                    ▼             │
      │             ┌──────────────┐     │
      │             │  Node 4:     │     │
      │             │  rewrite_    │     │
      │             │  question    │     │
      │             │              │     │
      │             │  Reformulate │     │
      │             │  query       │     │
      │             └──────┬───────┘     │
      │                    │             │
      │                    ▼             │
      │              ┌──────────┐        │
      │              │ Loop back│        │
      │              │ to Node 2│        │
      │              │ (max 3x) │        │
      │              └──────────┘        │
      │                                  │
      └──────────┬───────────────────────┘
                 │
                 ▼
          ┌──────────────┐
          │  Node 5:     │
          │  generate_   │
          │  answer      │
          │              │
          │  Synthesize  │
          │  coverage    │
          │  verdict     │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │   OUTPUT     │
          │              │
          │  Coverage %  │
          │  Co-pay      │
          │  Exclusions  │
          │  Waiting     │
          │  periods     │
          │  Missing docs│
          └──────────────┘
```

### Node Descriptions for Figma

| Node | Type | Color | Label | Description |
|------|------|-------|-------|-------------|
| START | Rounded rect | Green border (#11998e) | START | Claim query from extracted OCR data |
| Node 1 | Diamond/Decision | Orange border (#f2994a) | generate_or_retrieve | LLM decides: retrieve from policy DB or answer directly? |
| Node 2 | Rounded rect | Blue border (#667eea) | retrieve | ChromaDB MMR search (k=4), nomic-embed-text embeddings |
| Node 3 | Diamond/Decision | Orange border (#f2994a) | grade_documents | LLM evaluates: are retrieved policy clauses relevant? |
| Node 4 | Rounded rect | Orange border (#f2994a) | rewrite_question | LLM reformulates query for better retrieval |
| Loop | Dashed border | Orange dashed (#f2994a) | Loop back to Node 2 (max 3x) | Self-correcting mechanism |
| Node 5 | Rounded rect | Green border (#11998e) | generate_answer | LLM synthesizes final coverage verdict from relevant clauses |
| OUTPUT | Rounded rect | Red border (#e44d26) | OUTPUT | Coverage %, co-pay, exclusions, waiting periods, missing docs |

### Arrow Labels
- Node 1 → Node 2: "Needs retrieval"
- Node 1 → Node 5: "Can answer directly"
- Node 3 → Node 5: "Relevant ✓"
- Node 3 → Node 4: "Not relevant ✗"
- Node 4 → Node 2: "Loop back (max 3x)"

---

## Figure 4: Customer Portal — Upload Page

### Layout: App shell with sidebar + main content

**Sidebar (dark, left side, ~200px wide):**
- Logo: "⚙ ClaimChain" in cyan (#64ffda)
- Nav items (vertical list):
  - Dashboard
  - **Upload Claim** ← active (highlighted background #1e2440, cyan text)
  - My Claims
  - Settings

**Main Content Area:**
- Page title: "Submit New Claim"
- **Upload Zone** (dashed border box, centered):
  - Cloud upload icon (large, centered)
  - "Drag & drop your medical documents here"
  - "Discharge Summary, Hospital Bill, Prescription"
  - "Browse Files · PDF, JPG, PNG supported"
- **Uploaded files** (two chips/tags):
  - 📄 discharge_summary.pdf ✓
  - 📄 hospital_bill.pdf ✓
- **Policy Number Input** + **Analyze Claim** button (purple gradient)
- **Progress Bar** (6 steps, horizontal):
  - Step 1: Upload ✓ (green, completed)
  - Step 2: OCR ✓ (green, completed)
  - Step 3: RAG (blue, active/pulsing)
  - Step 4: Hash (gray, pending)
  - Step 5: Chain (gray, pending)
  - Step 6: Done (gray, pending)

### Color Scheme
- Background: #0a0f1e (dark navy)
- Sidebar: #0d1224
- Cards/inputs: #1e2440
- Accent: #64ffda (cyan), #667eea (purple)
- Text: #e6f1ff (primary), #8892b0 (secondary)

---

## Figure 5: Customer Portal — Verdict Page

### Layout: App shell with sidebar + main content (grid of cards)

**Header row:**
- "Claim CLM-20260304-A1B2" (large title)
- Status badge: "Submitted" (green pill)

**Grid of cards (2 columns):**

**Card 1 — Patient Information** (top-left)
- Badge: "High Confidence" (green)
- Table:

| Field | Value |
|-------|-------|
| Name | Rajesh Kumar |
| Age / Gender | 58 / Male |
| Policy Number | HSP-2025-TN-001 |
| Admission | 15-Feb-2026 |
| Discharge | 17-Feb-2026 |

**Card 2 — Medical Details** (top-right)
- Badge: "High Confidence" (green)
- Table:

| Field | Value |
|-------|-------|
| Diagnosis | Senile Cataract, Right Eye |
| Procedure | Phacoemulsification + IOL |
| Hospital | Apollo Hospitals, Chennai |
| Doctor | Dr. S. Venkatesh |
| Total Bill | ₹1,50,000 (orange, bold) |

**Card 3 — AI Coverage Verdict** (full width)
- Title: "AI Coverage Verdict"
- Green bold: "Estimated Coverage: ~85% of billed amount"
- Paragraph explaining:
  - Cataract surgery covered after 2-year waiting period (completed)
  - Room rent capped at ₹1,000/day (2 days = ₹2,000 vs ₹4,000 billed — ₹2,000 deducted)
  - Co-pay 5% applies
  - Estimated payable: ₹1,27,500
  - Patient responsibility: ₹22,500

**Card 4 — Blockchain Proof** (full width)
- 🔗 Blockchain Proof
- Merkle Root: `0x7a3f8b2c1d4e5f6a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6` (monospace, blue)
- Tx Hash: `0xabc123...def789` (green) · "View on Etherscan →" (blue link)

---

## Figure 6: Insurer Portal — Claim Review

### Layout: App shell with sidebar + main content

**Sidebar:**
- Logo: "⚙ ClaimChain INSURER" (orange accent instead of cyan)
- Nav items:
  - Dashboard
  - **Review Claims** ← active
  - Approved
  - Rejected

**Main Content:**

**Header row:**
- "Claim CLM-20260304-A1B2" (large title)
- Status badge: "Under Review" (orange pill)

**Fraud Risk Score Bar** (full width):
- Label: "Fraud Risk Score"
- Progress bar track (dark): filled 22% with green gradient
- Score label: "LOW (22/100)" in green

**Grid of cards (2 columns):**

**Card 1 — Claim Summary** (left)

| Field | Value |
|-------|-------|
| Patient | Rajesh Kumar, 58M |
| Policy | HSP-2025-TN-001 |
| Diagnosis | Senile Cataract |
| Procedure | Phacoemulsification + IOL |
| Total Bill | ₹1,50,000 (bold) |
| AI Payable Est. | ₹1,27,500 (85%) (green, bold) |

**Card 2 — Confidence & Flags** (right)

| Check | Status |
|-------|--------|
| OCR Confidence | 92% (green badge) |
| Waiting Period | Met (green badge) |
| Room Rent | Exceeded (orange badge) ₹2K over |
| Documents | Complete (green badge) |
| Anomalies | None (green badge) |

**On-Chain Timeline** (below cards):
- Title: "On-Chain Timeline"
- Vertical timeline with dots + lines:
  - 🟢 Claim Submitted — Merkle root recorded
    - 2026-03-04 10:23:15 · Tx: 0xabc...789
  - 🟠 Status: Under Review
    - 2026-03-04 10:25:02 · Tx: 0xdef...456

**Action Buttons** (bottom-right, two buttons):
- ✓ Approve Claim (green gradient button)
- ✗ Reject Claim (red gradient button)

---

## Global Design Tokens for Figma

### Colors
| Token | Hex | Usage |
|-------|-----|-------|
| bg-primary | #0a0f1e | Main background |
| bg-sidebar | #0d1224 | Sidebar background |
| bg-card | #1e2440 | Card / input backgrounds |
| text-primary | #e6f1ff | Main text |
| text-secondary | #8892b0 | Labels, descriptions |
| accent-cyan | #64ffda | Logo, section titles |
| accent-purple | #667eea | Buttons, links |
| accent-green | #38ef7d | Success, confirmed |
| accent-orange | #f2994a | Warning, in-progress |
| accent-red | #e44d26 | Error, reject |
| border | #2d3561 | Card borders, dividers |

### Typography
| Element | Font | Size | Weight |
|---------|------|------|--------|
| Page title | Inter | 20-22px | 700 |
| Card title | Inter | 13-14px | 600 |
| Body text | Inter | 12-13px | 400 |
| Badge | Inter | 10-11px | 700 |
| Monospace (hashes) | JetBrains Mono / Fira Code | 11px | 400 |

### Spacing
| Token | Value |
|-------|-------|
| Sidebar width | 200px |
| Card padding | 16px |
| Card border-radius | 10-12px |
| Grid gap | 16px |
| Section gap | 20-24px |
