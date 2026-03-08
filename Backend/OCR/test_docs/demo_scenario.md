# ClaimChain Demo Scenario

## Patient Profile

| Field | Value |
|---|---|
| **Name** | Rajesh Kumar |
| **Age** | 45 |
| **Gender** | Male |
| **Policy Number** | HSP-2025-TN-001 |
| **Policy Tier** | Silver |
| **Sum Insured** | Rs 3,00,000 |
| **Policy Start** | January 2024 (> 24 months ago) |

## Hospital & Treatment

| Field | Value |
|---|---|
| **Hospital** | Apollo Hospitals, Chennai |
| **Doctor** | Dr. Priya Sharma |
| **Diagnosis** | Age-related Cataract (ICD: H26.9) |
| **Procedure** | Phacoemulsification with IOL implant |
| **Admission Type** | Day-care |
| **Admission Date** | 2026-02-20 |
| **Discharge Date** | 2026-02-20 |

## Billing Breakdown

| Item | Amount (Rs) | Category |
|---|---|---|
| Surgery (Phacoemulsification) | 35,000 | surgery |
| Medicines | 5,000 | medication |
| Consumables (IOL lens, drapes) | 3,000 | misc |
| Surgeon/Doctor Fee | 2,000 | consultation |
| **Total** | **45,000** | — |

## Expected AI Verdict

The RAG agent should determine:

1. **Cataract surgery** is listed as a **covered day-care procedure** under HealthShield Plus
2. **24-month waiting period** for cataract: **COMPLETED** (policy started Jan 2024 > 24 months)
3. **Co-payment**: 10% (Silver tier)
4. **Room rent**: Not applicable (day-care, no overnight stay)
5. **Estimated payable**: Rs 40,500 (Rs 45,000 minus 10% co-pay)
6. **No exclusions** apply — age-related cataract is not in the exclusion list

## Demo Script (5 Scenes)

### Scene 1: Document Upload (Customer Portal)
1. Open Customer Portal (`localhost:3000`)
2. Policy number is pre-filled: HSP-2025-TN-001
3. Drag and drop: `DISCHARGE_SUMMARY.pdf` + `APOLLO_HOSPITALS.pdf`
4. Click "Analyze & Submit Claim"
5. **Show**: Multi-step progress bar advancing through OCR -> RAG -> Blockchain

### Scene 2: AI Verdict Display
6. Auto-redirects to Verdict page
7. **Point out**: Extracted patient data (Rajesh Kumar, Apollo Hospitals, Rs 45,000)
8. **Point out**: AI verdict says "Cataract surgery is covered, 10% co-pay, Rs 40,500 payable"
9. **Point out**: Blockchain Proof section — merkle root, tx hash (clickable Etherscan link)

### Scene 3: Insurer Review (Insurer Portal)
10. Switch to Insurer Portal (`localhost:3001`)
11. See the new claim in the Pending list
12. Click on the claim — see all extracted data + AI verdict
13. Click "Approve" — status changes, on-chain transaction fires

### Scene 4: Patient Timeline
14. Switch back to Customer Portal
15. Refresh the Verdict page
16. **Point out**: On-chain timeline now shows TWO events:
    - "ClaimSubmitted" — with block number + Etherscan link
    - "Approved" — with insurer's on-chain transaction

### Scene 5: Blockchain Verification
17. Click the Etherscan link in the timeline
18. **Point out**: This is a REAL transaction on Ethereum Sepolia testnet
19. **Key message**: "The patient can verify the original AI verdict was committed before the insurer ever saw it. This is tamper-proof — no one can change history."

## Test Documents to Use

- `DISCHARGE_SUMMARY.pdf` — Contains patient info, diagnosis, treatment details
- `APOLLO_HOSPITALS.pdf` — Contains hospital bill with itemized charges
- `PRESCRIPTION.pdf` — Optional: can upload as third document to show multi-doc support

## Talking Points During Demo

- "Most insurance AI tools are black boxes. We make the AI's decision transparent and immutable."
- "The merkle root committed on-chain is the SHA-256 hash of all documents + the AI verdict combined."
- "If someone tries to alter the verdict after the fact, the hash won't match — tamper-proof."
- "Every status change (submitted, approved, rejected) is a separate blockchain transaction."
- "All of this runs on free tools — Ollama (local AI), Tesseract (OCR), Ethereum Sepolia (testnet)."

## Fallback: If Something Fails

| Problem | Quick Fix |
|---|---|
| Ollama slow/down | Set `USE_GEMINI=true` in `.env` (needs API key) |
| Blockchain tx fails | Show OCR + RAG results — blockchain error is displayed gracefully |
| OCR gives poor results | Use the digital PDF (DISCHARGE_SUMMARY.pdf), not scanned images |
| Frontend won't load | Check `npm run dev` is running on port 3000 |
