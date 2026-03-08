# TN-IMPACT 2026 — PPT Content

## Slide 1 — Title Slide

| Field | Content |
|---|---|
| **Problem Statement Number** | *(fill in your assigned number)* |
| **Problem Statement Title** | GenAI-Powered Medical Insurance Claims Processing with Blockchain Verification |

---

## Slide 2 — Team Details

| Field | Content |
|---|---|
| **Team Name** | *(your team name)* |
| **College Mentor Name** | *(your mentor's name)* |
| **College Name** | *(your college name)* |

**Table:**

| S.NO | STUDENT NAME | SEMESTER | DEPARTMENT |
|------|-------------|----------|------------|
| 1 | *(Member 1)* | *(Sem)* | *(Dept)* |
| 2 | *(Member 2)* | *(Sem)* | *(Dept)* |
| 3 | *(Member 3)* | *(Sem)* | *(Dept)* |

---

## Slide 3 — Problem Statement

Medical insurance claims processing is slow, opaque, and error-prone. Patients and providers face manual data entry from prescriptions, discharge summaries, and bills into insurer portals, followed by repeated back-and-forth clarifications. This delays payments, increases administrative overhead, and leaves all stakeholders with limited visibility into claim status, coverage reasoning, and denial causes. There is no trustless verification mechanism — patients must rely entirely on the insurer's word for what happened and when.

---

## Slide 4 — Problem Description

**Current Pain Points:**

- Hospital staff manually reads discharge summaries, bills, and prescriptions, then re-enters data into insurer systems — slow and error-prone
- Policy coverage rules (room rent caps, waiting periods, co-pays, exclusions) are buried in dense documents — manual interpretation leads to incorrect claim submissions
- Patients have zero visibility into why a claim was partially approved, queried, or denied
- No tamper-proof audit trail exists — claim status changes are opaque and disputable
- Fraud detection relies on manual review of high volumes of claims, missing subtle patterns

**Scale of the Problem:**

India processes over 1.5 crore health insurance claims annually. Manual processing takes 15-30 days on average. Up to 30% of claims face queries or rejections due to incomplete documentation or policy mismatches — most of which are preventable with intelligent pre-validation.

---

## Slide 5 — Objectives

1. **Automate Document Intake** — Use OCR + NLP (Tesseract, spaCy) to extract structured data from medical documents (discharge summaries, hospital bills, prescriptions) with confidence scoring

2. **Intelligent Policy Validation** — Deploy an Agentic RAG pipeline (LangGraph + ChromaDB) that retrieves relevant policy clauses and generates natural-language coverage verdicts with co-pay, exclusion, and waiting period analysis

3. **Blockchain-Backed Transparency** — Record cryptographic proofs (Merkle roots of document hashes + AI verdicts) on Ethereum Sepolia, giving patients a tamper-proof, publicly verifiable claim timeline

4. **Dual-Portal Experience** — Build separate Customer and Insurer portals so both sides of the claim lifecycle are visible: patients track status in real-time, insurers review AI-summarized claims with fraud risk indicators

5. **Fraud Risk Detection** — Flag anomalies (unusually high bills, short stays with expensive procedures, missing documents) with rule-based scoring to assist Special Investigation Unit (SIU) teams

---

## Slide 6 — Solution Architecture *(add a diagram)*

```
┌─────────────────────────────────────────────────────────┐
│            FRONTEND (React + Vite)                      │
│   ┌──────────────────┐  ┌────────────────────────┐      │
│   │  Customer Portal  │  │   Insurer Portal       │      │
│   │  - Upload Docs    │  │   - Review Claims      │      │
│   │  - View Verdict   │  │   - Approve/Reject     │      │
│   │  - Track Status   │  │   - Fraud Risk Score   │      │
│   └────────┬─────────┘  └──────────┬─────────────┘      │
└────────────┼────────────────────────┼────────────────────┘
             │         REST API       │
┌────────────▼────────────────────────▼────────────────────┐
│              BACKEND (FastAPI)                            │
│  ┌───────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ OCR Engine │  │ Agentic RAG  │  │ Blockchain Service│  │
│  │ Tesseract  │  │ LangGraph    │  │ Web3.py           │  │
│  │ + spaCy    │  │ + ChromaDB   │  │ + Merkle Hashing  │  │
│  │ NLP        │  │ + Gemini/    │  │                   │  │
│  │            │  │   Mistral    │  │                   │  │
│  └─────┬─────┘  └──────┬───────┘  └────────┬──────────┘  │
└────────┼───────────────┼────────────────────┼─────────────┘
         │               │                    │
   Extract Data    Coverage Verdict    Submit Proof
         │               │                    │
         ▼               ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│          Ethereum Sepolia (ClaimChain.sol)                │
│   submitClaimMeta() → updateStatus() → getStatusHistory()│
│   Immutable Claim Timeline + Merkle Root Verification    │
└──────────────────────────────────────────────────────────┘
```

**Key Tech Stack (as bullet points beside diagram):**
- OCR: Tesseract + PyMuPDF + spaCy NER
- RAG: LangGraph (5-node agentic workflow) + ChromaDB + Gemini/Mistral
- Blockchain: Solidity 0.8.19 on Ethereum Sepolia
- Frontend: React 18 + Vite
- Backend: FastAPI + Python

---

## Slide 7 — End-to-End Claim Workflow *(add a step-flow graphic)*

**Step 1: Document Upload**
Patient/hospital uploads discharge summary + hospital bill with policy number

**Step 2: AI Document Extraction (OCR + NLP)**
Tesseract OCR + spaCy extracts patient info, diagnosis, procedures, billing — with confidence score (e.g., 92%)

**Step 3: Policy Coverage Check (Agentic RAG)**
LangGraph agent retrieves policy clauses from ChromaDB, grades relevance, and generates a natural-language verdict:
*"Cataract surgery covered after 2-year waiting period (met). Room rent within ₹1000/day limit. Co-pay 5%. Estimated payable: 85%"*

**Step 4: Blockchain Proof**
SHA-256 hashes of documents + verdict → Merkle root → submitted to ClaimChain smart contract on Ethereum Sepolia

**Step 5: Patient Views Result**
Customer portal shows extracted data, AI verdict, blockchain transaction hash (linked to Etherscan), and live claim timeline

**Step 6: Insurer Reviews & Decides**
Insurer portal shows AI summary + fraud risk score → Approve/Reject → status update recorded on-chain

**Step 7: Transparent Tracking**
Patient sees real-time on-chain timeline with every status change, timestamp, and actor — fully verifiable

---

## Slide 8 — Findings

**Key Technical Findings:**

1. **OCR Accuracy** — Tesseract + spaCy NLP pipeline achieves reliable extraction of patient names, diagnosis, procedures, and billing amounts from scanned documents; confidence scoring identifies fields needing human review

2. **Agentic RAG Superiority** — The 5-node LangGraph workflow (retrieve → grade → rewrite → generate) outperforms simple RAG by self-correcting poor retrievals; the agent decides *when* to retrieve vs. answer directly

3. **Blockchain Feasibility** — Merkle root submission on Sepolia confirms claims can be cryptographically verified at low gas cost; QR code scanning enables trustless verification without requiring login or technical knowledge

4. **Graceful Degradation Works** — Each module (OCR, RAG, Blockchain) operates independently; if one fails, the claim still processes with available components — critical for real-world reliability

5. **Fraud Detection Potential** — Rule-based anomaly scoring (high bills, short stays, missing documents) surfaces suspicious claims effectively for insurer review

6. **Dual-Portal UX** — Separating customer and insurer views demonstrates the full claim lifecycle and builds trust through transparency on both sides

---

## Slide 9 — Conclusion

**ClaimChain** demonstrates that combining GenAI with blockchain creates a fundamentally better insurance claims experience:

- **For Patients**: Clear, natural-language explanations of coverage decisions + tamper-proof on-chain timeline = trust and transparency
- **For Hospitals**: Automated document extraction eliminates manual data entry, reducing submission errors and processing time
- **For Insurers**: AI-summarized claims with fraud risk scoring enable faster, more accurate adjudication at lower operational cost

**What We Built:**
A working end-to-end prototype with OCR document extraction, agentic RAG policy validation, Ethereum blockchain proof recording, and dual-portal UI — all with graceful degradation for production reliability.

**Future Scope:**
- PostgreSQL persistence + email/SMS notifications
- Multi-language support (English/Hindi/Tamil)
- PDF claim summary export with QR verification code
- Analytics dashboard for claim patterns and processing metrics

*GenAI + Blockchain = Transparent, Fast, and Trustworthy Insurance Claims*
