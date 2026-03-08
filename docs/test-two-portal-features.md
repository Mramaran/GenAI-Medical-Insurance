# Two-Portal Split — Feature Test Checklist

> Run all 3 services first:
> - `cd Backend/api && python -m uvicorn main:app --reload --port 8000`
> - `cd frontend && npm run dev` (port 3000)
> - `cd insurer && npm run dev` (port 3001)

---

## Test 1: Customer Portal (localhost:3000)

- [ ] Sidebar shows: Submit Claim, My Claims, **Verify Claim** (no Insurer Portal link)
- [ ] Sidebar subtitle says **"Patient Portal"**
- [ ] Upload page works — drag a `.md` or `.pdf` file + policy number
- [ ] After submit, redirects to Verdict page

## Test 2: QR Code on Verdict Page

- [ ] Verdict page shows **"Claim QR Receipt"** card (only if blockchain tx succeeded)
- [ ] QR code renders inside a white box
- [ ] "Download QR" button downloads an SVG file
- [ ] QR code encodes the Etherscan transaction URL

## Test 3: Confidence Indicators (Customer Portal)

- [ ] Each extracted data field has a **colored dot** next to the label
- [ ] Green dot = High confidence, Yellow = Medium, Red = Low
- [ ] Hover over dot shows tooltip (e.g., "High confidence")

## Test 4: Verify Page (localhost:3000/verify)

- [ ] Page loads with title "Verify Claim On-Chain"
- [ ] Enter a valid Claim ID → shows status, merkle root, Etherscan link, timeline
- [ ] Enter an invalid Claim ID → shows error message
- [ ] No login required — public access

## Test 5: Policy Q&A Chatbot

- [ ] Floating blue chat bubble in bottom-right corner on ALL pages
- [ ] Click bubble → chat panel opens with welcome message
- [ ] Type "Is cataract surgery covered?" → get RAG response
- [ ] Type "What documents do I need?" → get RAG response
- [ ] Close button (X) collapses back to bubble
- [ ] Loading spinner shows while waiting for response

## Test 6: Insurer Portal (localhost:3001)

- [ ] Dark theme with **amber/gold** accent colors
- [ ] Sidebar says **"Insurer Portal"** and **"Claims Officer View"**
- [ ] Dashboard shows 4 stat cards: Total, Pending, Approved, Rejected
- [ ] Dashboard lists pending claims with Claim ID, Patient, Amount
- [ ] Refresh button works
- [ ] Auto-refreshes every 10 seconds

## Test 7: Insurer Claim Detail Page

- [ ] Click a claim row → navigates to `/claims/{claimId}`
- [ ] Shows extracted OCR data with **confidence dots**
- [ ] Shows **Fraud Risk Assessment** card with:
  - Score number in colored circle
  - Risk level (Low/Medium/High)
  - Flagged rules listed below
- [ ] Shows AI Coverage Analysis verdict
- [ ] Shows On-Chain Timeline (right column)
- [ ] Approve/Reject buttons work (for pending claims)
- [ ] "Back to Dashboard" button works

## Test 8: Fraud Risk Scoring

- [ ] Low-risk claim (Rs 45,000 cataract) → green score, 0-25 range
- [ ] High-risk claim (use `test_high_fraud.md` below) → red score, 51+ range
- [ ] Flagged rules show specific reasons

## Test 9: Cross-Portal Flow (Side-by-Side Demo)

1. [ ] Customer Portal: Upload document → get verdict + QR code
2. [ ] Insurer Portal: New claim appears on dashboard
3. [ ] Insurer Portal: Click claim → see fraud score + confidence dots
4. [ ] Insurer Portal: Click "Approve"
5. [ ] Customer Portal: My Claims page shows status updated to "Approved"
6. [ ] Customer Portal: Verify page shows full on-chain timeline with both events

---

## Test Documents

### Low-Risk: `test_discharge_summary.md` (already in test_docs/)
- Patient: Rajesh Kumar, 45/M
- Bill: Rs 45,000 (cataract surgery)
- Expected fraud score: **0-5 (Low)**

### High-Risk: Upload the content below as a `.md` file
See `Backend/OCR/test_docs/test_high_fraud.md`
