# ClaimChain

GenAI-Powered Medical Insurance Claims Processing with Blockchain Verification

## Overview

ClaimChain is a comprehensive solution to streamline medical insurance claims processing. It leverages Generative AI for intelligent document analysis, policy validation, and fraud detection, combined with blockchain technology for immutable record-keeping and transparency. The system addresses the slow, opaque, and error-prone nature of traditional claims workflows by automating data extraction, coverage checks, and status tracking.

## Problem Statement

Medical insurance claims processing is slow and opaque, leading to delays and administrative overhead for patients and providers. Current processes involve manual reading of prescriptions, discharge summaries, bills, and policy documents, followed by data entry into insurer portals and back-and-forth clarifications. This slows down payment, increases overhead, and creates an opaque experience with little visibility into status, reasons for queries, or denials.

## Key Features

- **Intelligent Document Intake**: Uses OCR and NLP to extract data from medical documents (prescriptions, bills, discharge summaries, lab reports, ID proofs, policy documents) and normalize into structured claim records.
- **Policy Coverage Validation**: Parses policy wording, riders, and exclusions to automatically check claims against benefit rules (room rent caps, day-care procedures, waiting periods, co-pay, sub-limits).
- **Claim Drafting and Submission**: Generates pre-filled claim forms with checklists of required attachments and provides a conversational interface for clarifications.
- **Review and Adjudication Support**: Summarizes medical narratives and billing for adjudicators, highlighting necessary services and potential anomalies.
- **Blockchain Verification**: Stores cryptographic proofs of AI verdicts on-chain, ensuring tamper-proof audit trails and real-time status updates.
- **Dual Portals**: Separate interfaces for patients/providers and insurers, with on-chain event timelines.

## Architecture

The system consists of three main components:

1. **Backend (Python/FastAPI)**: Handles AI processing, API endpoints, and blockchain interactions.
2. **Frontend (React)**: Two portals - Customer Portal (port 3000) and Insurer Portal (port 3001).
3. **Blockchain (Solidity)**: Smart contract on Ethereum Sepolia for claim metadata and status tracking.

### System Flow

[Patient/Provider UI] → Upload docs/policy → [Backend + AI] → OCR/NLP & Policy Check → Generate claim JSON & Merkle hash → [Smart Contract] → Store hash & emit events → [UI] → Update timeline → [Insurer UI] → Review & update status → [Backend] → Update on-chain → [UI] → Reflect changes.

## Prerequisites

- Python 3.10+ with pip
- Node.js 18+ with npm
- Tesseract OCR installed
- Ollama running with `mistral` model (or set `USE_GEMINI=true` in `.env`)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Mramaran/GenAI-Medical-Insurance.git
cd GenAI-Medical-Insurance
```

### 2. Backend Setup

```bash
cd Backend/api
pip install -r requirements.txt
```

### 3. Frontend Setup (Customer Portal)

```bash
cd ../../frontend
npm install
```

### 4. Insurer Portal Setup

```bash
cd ../insurer
npm install
```

### 5. Blockchain Setup

- Deploy `blockchain/contracts/ClaimChain.sol` to Ethereum Sepolia using Remix IDE or similar.
- Save the ABI to `blockchain/abi/ClaimChain.json` and update contract address in configuration.

## Running the Application

### Start Backend (Port 8000)

```bash
cd Backend/api
python -m uvicorn main:app --reload --port 8000
```

Verify: Visit http://localhost:8000/docs for API documentation.

### Start Customer Portal (Port 3000)

```bash
cd frontend
npm run dev
```

Opens: http://localhost:3000

### Start Insurer Portal (Port 3001)

```bash
cd insurer
npm run dev
```

Opens: http://localhost:3001

## Quick Demo

1. Open http://localhost:3000 (Customer Portal) and http://localhost:3001 (Insurer Portal) side-by-side.
2. Upload medical documents and policy details in the Customer Portal.
3. Review and update claim status in the Insurer Portal.
4. Observe real-time updates via blockchain events.

## API Endpoints

- `/api/claims`: Claim analysis, submission, and retrieval.
- `/api/review`: Insurer review endpoints.
- `/api/chat`: Conversational interface for clarifications.

Refer to http://localhost:8000/docs for detailed API documentation.

## Technology Stack

- **Backend**: Python, FastAPI, Tesseract OCR, spaCy, LangChain, ChromaDB, Web3.py
- **Frontend**: React, Vite, React Router
- **Blockchain**: Solidity, Ethereum Sepolia
- **AI**: Ollama (Mistral), Google Gemini (optional)

## Contributing

This project is developed for TN-IMPACT 2026 Hackathon. Contributions are welcome via pull requests.

## License

[Specify license if applicable]

## Acknowledgments

- Open-source communities behind Tesseract, spaCy, LangChain, ChromaDB, Solidity, and React.
- TN-IMPACT 2026 organizers for the platform.