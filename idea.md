# GenAI insurance 
## Ideas:
###  MVP story
Patient treated for X, hospital uploads docs, GenAI pre‑checks coverage, backend submits claim meta on blockchain, insurer  updates status, patient sees an on‑chain timeline
### end‑to‑end flow
#### Claim pre‑check
    - Hospital staff uploads discharge summary and bill + enters policy number.
    - Backend:
        - Runs OCR and field extraction.
        - Queries policy RAG index.
        - Generates structured verdict JSON and natural‑language explanation.

#### User experience
Patient sees:
    - “Estimated coverage: 85% of your bill seems payable.”
    - Reasons: “Room rent within limit; cataract surgery covered after 2‑year waiting period, which you’ve completed; 5% co‑pay applies.”
    - Missing docs: “Discharge summary signature missing; please upload.”

#### Blockchain recording
    - Backend computes Merkle root over document hashes and AI verdict text, calls submitClaimMeta on smart contract.
    - Contract emits ClaimSubmitted, which front‑end subscribes to and displays as first event in a “Claim Timeline” component.

#### Insurer action (demo‑simulated)
    - Claims officer UI fetches claim from backend, reviews AI summary, and clicks Approve or Reject.
    - Backend calls updateStatus on contract with new status and (optionally) hash of insurer’s reasoning note.
    - Patient UI updates with “On‑chain Events” timeline showing who did what and when.

## 