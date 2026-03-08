# ClaimChain — Differentiator Design (Hackathon Winning Strategy)

> **Goal**: Make ClaimChain unbeatable against teams doing "OCR + dashboard".
> **Context**: 48-hr hackathon. Judges evaluate working demo + innovation + business impact equally.

---

## Competitive Advantage Summary

| What Others Build | What ClaimChain Has | Our Extra Edge |
|---|---|---|
| OCR scan → form fill | OCR + spaCy + LLM extraction | Confidence indicators per field |
| Basic chatbot | Agentic RAG (LangGraph + ChromaDB) | Live policy Q&A chatbot for patients |
| Simple dashboard | Two separate portals (Customer + Insurer) | Side-by-side demo, two user journeys |
| No blockchain | Full Ethereum Sepolia proof chain | QR code claim receipts, public verify page |
| No fraud detection | — | Fraud risk scoring with visual meter |
| Single-user view | — | Patient AND insurer perspectives |

---

## Architecture: Two-Portal Split

### Portal 1: Customer Portal (`localhost:3000`)

The patient/hospital-facing app. Clean, friendly, blue/green theme.

| Route | Page | Purpose |
|---|---|---|
| `/` | UploadPage | Upload medical docs + policy number, submit claim |
| `/verdict/:claimId` | VerdictPage | AI verdict + blockchain proof + **QR code** |
| `/claims` | MyClaimsPage | Track all my claims + status badges |
| `/verify` | **VerifyPage** *(NEW)* | Public trustless verification — enter Claim ID, see on-chain timeline |
| *(floating)* | **ChatWidget** *(NEW)* | Policy Q&A chatbot using RAG agent |

### Portal 2: Insurer Portal (`localhost:3001`)

The insurance company-facing app. Professional, data-dense, dark theme.

| Route | Page | Purpose |
|---|---|---|
| `/` | DashboardPage | Pending + processed claims overview with counts |
| `/claims/:claimId` | ClaimDetailPage | Full OCR data + AI verdict + **fraud risk meter** + **confidence indicators** + approve/reject |

### Shared Backend (`localhost:8000`)

Both portals hit the same FastAPI backend. No backend changes for the split — just CORS allows both ports.

### Demo Flow (Two Windows Side-by-Side)

```
┌─ Customer Portal (left) ─────────┐  ┌─ Insurer Portal (right) ──────────┐
│                                    │  │                                     │
│  1. Upload discharge summary       │  │  (waiting for claims...)            │
│  2. See AI verdict + blockchain    │  │                                     │
│  3. Get QR code receipt            │  │  4. New claim appears!              │
│  4. Ask chatbot "Is this covered?" │  │  5. See fraud score (green ✓)       │
│                                    │  │  6. See confidence per field        │
│                                    │  │  7. Click "Approve"                 │
│  8. Status updates to "Approved"!  │  │                                     │
│  9. On-chain timeline shows it     │  │  8. Tx confirmed on Sepolia         │
│ 10. Scan QR → verify on Etherscan  │  │                                     │
└────────────────────────────────────┘  └─────────────────────────────────────┘
```

---

## Feature 1: Patient Verification Portal + QR Code

### What
A `/verify` page in the Customer Portal. No login needed. Anyone with a Claim ID can see the full on-chain timeline — fetched directly from blockchain events.

After claim submission, a QR code is generated encoding:
```
https://sepolia.etherscan.io/tx/{tx_hash}
```

The QR code appears on the VerdictPage and can be downloaded/printed.

### Why It Wins
- **No other team** gives patients trustless verification
- QR code on a discharge summary = physical proof of digital claim
- Judges can scan the QR themselves during demo → instant "wow"
- Demonstrates blockchain isn't just a buzzword — it has a user-facing purpose

### Technical Implementation
- **New page**: `VerifyPage.jsx` in Customer Portal
  - Input: Claim ID text field
  - Calls: `GET /api/claims/{claimId}` (already exists)
  - Displays: ClaimTimeline component (already built) + Etherscan links
- **QR Code**: Use `qrcode.react` npm package
  - Generate on VerdictPage after successful submission
  - Encode Etherscan transaction URL
  - Add "Download QR" button
- **Backend**: No changes needed — existing endpoints suffice

### Build Estimate: ~1-2 hours

---

## Feature 2: Fraud Risk Scoring

### What
A rule-based anomaly scoring engine that runs during claim analysis. Returns a 0-100 risk score with flagged rules.

### Scoring Rules

| Rule | Condition | Points | Rationale |
|---|---|---|---|
| High bill amount | total > ₹5,00,000 | +30 | Top 5% of claims by value |
| Short stay, high bill | stay < 24hrs AND bill > ₹2,00,000 | +25 | Common fraud pattern |
| Missing documents | missing_fields count > 3 | +20 | Incomplete claims correlate with fraud |
| High-risk diagnosis | diagnosis in watchlist (cosmetic, fertility, etc.) | +15 | Commonly excluded or fraudulent |
| Weekend admission | admitted on Saturday/Sunday | +5 | Slightly elevated fraud rate |
| Round bill amount | bill is exact round number (₹1,00,000) | +5 | Real bills rarely perfectly round |

### Risk Levels
- **0-25**: Low Risk (green) — auto-approve candidate
- **26-50**: Medium Risk (yellow) — standard review
- **51-100**: High Risk (red) — flag for detailed investigation

### Display
- **Insurer Portal**: Color-coded risk meter (arc gauge) on ClaimDetailPage
- **Flagged rules** listed below the meter so insurer knows *why*

### Technical Implementation
- **New service**: `Backend/api/services/fraud_scorer.py`
  - Input: extracted_data dict
  - Output: `{ score: int, level: str, flags: list[str] }`
- **Wire into** `routes/claims.py` → `analyze_claim()` — run after OCR, add score to claim record
- **New component**: `RiskMeter.jsx` — arc gauge with color gradient
- **Backend**: Minimal — pure Python, no ML dependencies

### Why It Wins
- Addresses the "3-10% of healthcare costs are fraudulent" stat (cite WHO/NHCAA)
- Visual fraud meter is immediately understood by non-technical judges
- Rule-based = explainable (judges can ask "why is this flagged?" and you can show exact rules)
- No other OCR+dashboard team will have this

### Build Estimate: ~2-3 hours

---

## Feature 3: Policy Q&A Chatbot Widget

### What
A floating chat bubble (bottom-right corner) on Customer Portal pages. Patient types natural language questions, gets answers from policy documents via the existing RAG agent.

### Example Interactions
```
Patient: "Is knee replacement surgery covered?"
Bot: "Yes, knee replacement is covered under the Surgical Benefits
      section. The policy covers up to ₹3,00,000 for joint replacement
      procedures after a 2-year waiting period..."

Patient: "What documents do I need to file a claim?"
Bot: "To file a claim you need: 1) Discharge Summary, 2) Hospital
      Bills (itemized), 3) Doctor's Prescription, 4) Investigation
      Reports, 5) Pre-authorization letter (if applicable)..."
```

### Technical Implementation
- **New endpoint**: `POST /api/chat` in `Backend/api/routes/chat.py`
  - Input: `{ question: str }`
  - Calls: `query_agent(question)` from existing RAG
  - Output: `{ answer: str }`
- **New component**: `ChatWidget.jsx`
  - Floating button (bottom-right, expandable)
  - Chat history in scrollable container
  - Text input + send button
  - Shows typing indicator while waiting for RAG response
- **Integration**: Import ChatWidget in Customer Portal's App.jsx (appears on all pages)

### Why It Wins
- Transforms from "hospital tool" to "patient empowerment tool"
- Uses your existing RAG agent — no new AI setup needed
- Interactive demo moment: judge asks a policy question live → gets instant answer
- Shows the "GenAI" in your project name isn't just OCR

### Build Estimate: ~2-3 hours

---

## Feature 4: Confidence Indicators on Extracted Data

### What
Each extracted field gets a colored confidence badge:
- **High** (green dot) — AI is confident in extraction
- **Medium** (yellow dot) — Partially confident, may need review
- **Low** (red dot) — Uncertain or missing, requires manual check

### Data Source
Your OCR pipeline already computes:
- `confidence_score` (0.0 - 1.0) on the overall extraction
- `missing_fields` list of fields that couldn't be extracted

Use these to derive per-field confidence:
- Field present + not in missing_fields → High
- Field present but in a "fuzzy extraction" list → Medium
- Field in missing_fields or empty → Low

### Display
- On VerdictPage (Customer Portal): Small colored dot next to each field label
- On ClaimDetailPage (Insurer Portal): Same dots + tooltip "AI confidence: High/Medium/Low"
- Insurer can filter/sort by "fields needing review"

### Why It Wins
- Shows AI isn't a black box — builds trust
- Insurers know exactly which fields to double-check
- Demonstrates technical depth (explainable AI)
- Simple visual, huge impact in demo

### Build Estimate: ~1 hour (mostly frontend, minimal backend)

---

## Feature Priority (Build Order)

| Priority | Feature | Impact | Effort | Do First? |
|---|---|---|---|---|
| **P0** | Two-Portal Split | Demo presentation | 2-3 hrs | Yes — restructure first |
| **P1** | Fraud Risk Score | Business impact + wow | 2-3 hrs | Yes — judges love it |
| **P1** | Verification + QR Code | Blockchain wow | 1-2 hrs | Yes — unique differentiator |
| **P2** | Policy Chatbot | User-facing wow | 2-3 hrs | Yes — interactive demo moment |
| **P3** | Confidence Indicators | Technical depth | 1 hr | Yes — quick win |

**Total estimated effort: ~9-12 hours** (fits within remaining hackathon time)

---

## Pitch Talking Points (New)

### "Why ClaimChain is Different"

1. **"We don't just digitize claims — we make them tamper-proof."**
   Every AI verdict is hashed and committed on Ethereum before the insurer sees it. No one can change the AI's assessment after the fact.

2. **"Patients get a QR code receipt they can verify themselves."**
   Scan it → see the entire claim timeline on a public blockchain explorer. No login, no trust required.

3. **"Our AI doesn't just read documents — it flags fraud."**
   Rule-based anomaly scoring catches the patterns that cost healthcare 3-10% annually (WHO/NHCAA statistic).

4. **"Patients can ask policy questions in plain language."**
   The chatbot uses Retrieval-Augmented Generation against actual policy documents — not hallucinated answers.

5. **"We built two portals because claims have two sides."**
   Patient submits on one screen, insurer reviews on another. In the demo, you see both in real-time.

---

## What This Gives You Over "OCR + Dashboard" Teams

```
Them:  Upload → OCR → Dashboard → Done.
You:   Upload → OCR → RAG Verdict → Fraud Score → Blockchain Proof
       → QR Receipt → Patient Chatbot → Insurer Review → On-Chain
       Timeline → Public Verification.
```

**They have 3 steps. You have 10.**
**They have 1 user. You have 2 portals.**
**They have 0 blockchain. You have Ethereum.**
**They have 0 fraud detection. You have a risk engine.**

---

## Bonus Ideas (If Time Permits)

These are stretch goals — only attempt if core features are done:

1. **Email/SMS Notification Mock** — Show a "notification sent" toast when claim status changes (no real email, just the UI simulation)
2. **Claim Analytics Chart** — A small bar chart on the insurer dashboard showing claims by status (submitted/approved/rejected) using a lightweight chart library
3. **Dark/Light Theme Toggle** — Simple theme switcher to show UI polish
4. **Export Claim PDF** — Button to download claim summary as PDF (using browser print)
5. **Multilingual Toggle** — Even if just English/Hindi on the upload page labels, it shows India-market awareness
