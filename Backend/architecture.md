[Patient/Provider UI] 
    └──➤ (1) Upload docs/policy 
              │
              ▼
[Backend Server + AI]──➤ (2) OCR/NLP & Policy Check:contentReference[oaicite:26]{index=26}:contentReference[oaicite:27]{index=27}
      │                   │
      └──➤ (3) Generate claim JSON and compute Merkle hash
              │
              ▼
[Smart Contract on Blockchain]──➤ (4) Store claim hash, emit ClaimSubmitted:contentReference[oaicite:28]{index=28}
      │                                    │
      ▼                                    │
[Patient/Provider UI] ◀──(5) Listen for ClaimSubmitted event, update UI:contentReference[oaicite:29]{index=29}
      │
[Insurer UI]──➤ (6) Fetch claim, review → (Approve/Reject) ──➤ [Backend]
                                        └──➤ (7) updateStatus on-chain:contentReference[oaicite:30]{index=30}
      │
      ▼
[Patient/Provider UI] ◀──(8) Listen for StatusUpdated event, update Timeline