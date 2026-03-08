# ClaimChain Two-Portal Split + Differentiator Features — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split the single-portal ClaimChain app into two separate portals (Customer Portal on port 3000, Insurer Portal on port 3001) and add four differentiator features: QR Code + Verification Page, Fraud Risk Scoring, Policy Q&A Chatbot, and Confidence Indicators.

**Architecture:** The Customer Portal (`frontend/`) serves patients/hospitals with claim submission, tracking, public verification, and a policy chatbot. The Insurer Portal (`insurer/`) serves claims officers with a dashboard, detailed claim review, fraud risk scoring, and confidence indicators. Both portals hit the same FastAPI backend (`Backend/api/` on port 8000). Shared components (Card, Badge, Spinner, ClaimTimeline) are copied into the insurer project.

**Tech Stack:** React 18 + Vite 5, FastAPI, spaCy, LangGraph RAG, Web3.py, ChromaDB, `qrcode.react` (QR codes)

---

## Task 1: Create the Insurer Portal Project Structure

**Files:**
- Create: `insurer/package.json`
- Create: `insurer/vite.config.js`
- Create: `insurer/index.html`
- Create: `insurer/src/main.jsx`
- Create: `insurer/src/App.jsx`
- Create: `insurer/src/api.js`
- Create: `insurer/src/components/Card.jsx`
- Create: `insurer/src/components/Badge.jsx`
- Create: `insurer/src/components/Spinner.jsx`
- Create: `insurer/src/components/ClaimTimeline.jsx`

**Step 1: Create `insurer/package.json`**

```json
{
  "name": "claimchain-insurer",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^7.13.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.1",
    "vite": "^5.4.1"
  }
}
```

**Step 2: Create `insurer/vite.config.js`**

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 3001 },
});
```

**Step 3: Create `insurer/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ClaimChain Insurer Portal</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

**Step 4: Create `insurer/src/main.jsx`**

```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

**Step 5: Create `insurer/src/api.js`**

Copy from `frontend/src/api.js` — identical content (same backend on port 8000).

**Step 6: Copy shared components**

Copy these files from `frontend/src/components/` into `insurer/src/components/`:
- `Card.jsx`
- `Badge.jsx`
- `Spinner.jsx`
- `ClaimTimeline.jsx`

All files are identical — no modifications needed.

**Step 7: Create `insurer/src/App.jsx` (Insurer Shell)**

```jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import InsurerSidebar from "./components/InsurerSidebar.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ClaimDetailPage from "./pages/ClaimDetailPage.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          background: #030712;
          font-family: 'Inter', -apple-system, sans-serif;
          color: #E2E8F0;
        }
        a { color: inherit; text-decoration: none; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e2d47; border-radius: 3px; }
        input, textarea, select { font-family: inherit; }
      `}</style>

      <InsurerSidebar />

      <main style={{ marginLeft: 240, padding: "40px 48px", minHeight: "100vh" }}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/claims/:claimId" element={<ClaimDetailPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
```

**Step 8: Install dependencies**

Run: `cd insurer && npm install`

**Step 9: Verify insurer dev server starts**

Run: `cd insurer && npm run dev`
Expected: Vite dev server starts on http://localhost:3001 (will show blank page until pages are created)

**Step 10: Commit**

```bash
git add insurer/package.json insurer/vite.config.js insurer/index.html insurer/src/
git commit -m "feat: scaffold insurer portal project (port 3001)"
```

---

## Task 2: Build the Insurer Sidebar Component

**Files:**
- Create: `insurer/src/components/InsurerSidebar.jsx`

**Step 1: Create `insurer/src/components/InsurerSidebar.jsx`**

```jsx
import { useLocation, useNavigate } from "react-router-dom";

export default function InsurerSidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    { path: "/", label: "Dashboard", icon: "\u{1F4CA}" },
  ];

  const isActive = (path) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  return (
    <aside
      style={{
        position: "fixed",
        left: 0,
        top: 0,
        width: 240,
        height: "100vh",
        background: "linear-gradient(180deg, #030712 0%, #111827 100%)",
        borderRight: "1px solid #1F2937",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        zIndex: 10,
      }}
    >
      <div
        onClick={() => navigate("/")}
        style={{
          fontSize: 18,
          fontWeight: 700,
          color: "#F59E0B",
          marginBottom: 8,
          display: "flex",
          alignItems: "center",
          gap: 10,
          cursor: "pointer",
        }}
      >
        <span style={{ fontSize: 26 }}>{"\u2696\uFE0F"}</span>
        ClaimChain
      </div>
      <div
        style={{
          fontSize: 11,
          color: "#6B7280",
          marginBottom: 36,
          paddingLeft: 38,
          letterSpacing: 1,
          textTransform: "uppercase",
        }}
      >
        Insurer Portal
      </div>

      <nav style={{ flex: 1 }}>
        {items.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            style={{
              width: "100%",
              padding: "14px 16px",
              marginBottom: 8,
              border: "none",
              borderRadius: 10,
              background: isActive(item.path)
                ? "linear-gradient(135deg, #D97706 0%, #F59E0B 100%)"
                : "transparent",
              color: isActive(item.path) ? "#fff" : "#9CA3AF",
              fontSize: 14,
              fontWeight: 500,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 12,
              transition: "all 0.2s",
            }}
          >
            <span style={{ fontSize: 18 }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <div
        style={{
          padding: "16px",
          background: "rgba(245, 158, 11, 0.1)",
          borderRadius: 12,
          fontSize: 12,
          color: "#9CA3AF",
        }}
      >
        <div style={{ color: "#F59E0B", fontWeight: 600, marginBottom: 4 }}>
          Claims Officer View
        </div>
        Fraud Detection + AI Verdicts
      </div>
    </aside>
  );
}
```

**Step 2: Commit**

```bash
git add insurer/src/components/InsurerSidebar.jsx
git commit -m "feat: add insurer sidebar with amber/dark theme"
```

---

## Task 3: Build Insurer Dashboard Page

**Files:**
- Create: `insurer/src/pages/DashboardPage.jsx`

**Step 1: Create `insurer/src/pages/DashboardPage.jsx`**

```jsx
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import Spinner from "../components/Spinner.jsx";
import { listClaims } from "../api.js";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadClaims();
    const interval = setInterval(loadClaims, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadClaims = async () => {
    try {
      const data = await listClaims();
      setClaims(data);
    } catch (err) {
      console.error("Failed to load claims:", err);
    } finally {
      setLoading(false);
    }
  };

  const pendingClaims = claims.filter(
    (c) => c.status === "submitted" || c.status === "pending" || c.status === "under_review",
  );
  const approvedClaims = claims.filter((c) => c.status === "approved" || c.status === "settled");
  const rejectedClaims = claims.filter((c) => c.status === "rejected");

  const stats = [
    { label: "Total Claims", value: claims.length, color: "#38BDF8" },
    { label: "Pending Review", value: pendingClaims.length, color: "#FCD34D" },
    { label: "Approved", value: approvedClaims.length, color: "#34D399" },
    { label: "Rejected", value: rejectedClaims.length, color: "#F87171" },
  ];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Claims Dashboard</h1>
          <p style={{ color: "#6B7280" }}>Review and adjudicate submitted insurance claims</p>
        </div>
        <button
          onClick={loadClaims}
          style={{
            padding: "10px 20px",
            border: "1px solid #1F2937",
            borderRadius: 8,
            background: "transparent",
            color: "#F59E0B",
            cursor: "pointer",
            fontSize: 14,
          }}
        >
          {"\u{1F504}"} Refresh
        </button>
      </div>

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {stats.map((s) => (
          <Card key={s.label}>
            <div style={{ fontSize: 12, color: "#6B7280", marginBottom: 8 }}>{s.label}</div>
            <div style={{ fontSize: 32, fontWeight: 800, color: s.color }}>{s.value}</div>
          </Card>
        ))}
      </div>

      {loading ? (
        <div style={{ display: "flex", alignItems: "center", gap: 12, color: "#6B7280" }}>
          <Spinner /> Loading claims...
        </div>
      ) : (
        <>
          {/* Pending claims */}
          <h2 style={{ fontSize: 18, fontWeight: 600, color: "#FCD34D", marginBottom: 16 }}>
            {"\u23F3"} Pending Review ({pendingClaims.length})
          </h2>
          {pendingClaims.length === 0 ? (
            <Card><div style={{ textAlign: "center", padding: 24, color: "#6B7280" }}>No pending claims</div></Card>
          ) : (
            <div style={{ display: "grid", gap: 12, marginBottom: 32 }}>
              {pendingClaims.map((claim) => (
                <ClaimRow key={claim.claim_id} claim={claim} onClick={() => navigate(`/claims/${claim.claim_id}`)} />
              ))}
            </div>
          )}

          {/* Processed claims */}
          {(approvedClaims.length > 0 || rejectedClaims.length > 0) && (
            <>
              <h2 style={{ fontSize: 18, fontWeight: 600, color: "#6B7280", marginBottom: 16, marginTop: 24 }}>
                {"\u2705"} Processed ({approvedClaims.length + rejectedClaims.length})
              </h2>
              <div style={{ display: "grid", gap: 12 }}>
                {[...approvedClaims, ...rejectedClaims].map((claim) => (
                  <ClaimRow key={claim.claim_id} claim={claim} onClick={() => navigate(`/claims/${claim.claim_id}`)} />
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

function ClaimRow({ claim, onClick }) {
  const pt = claim.extracted_data?.patient || {};
  const billing = claim.extracted_data?.billing || {};
  return (
    <Card>
      <div
        onClick={onClick}
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}
      >
        <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 11, color: "#6B7280" }}>Claim ID</div>
            <div style={{ fontFamily: "monospace", color: "#F59E0B", fontSize: 13 }}>{claim.claim_id}</div>
          </div>
          <div>
            <div style={{ fontSize: 11, color: "#6B7280" }}>Patient</div>
            <div style={{ fontSize: 14 }}>{pt.name || "Unknown"}</div>
          </div>
          {billing.total_amount != null && (
            <div>
              <div style={{ fontSize: 11, color: "#6B7280" }}>Amount</div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>{"\u20B9"}{Number(billing.total_amount).toLocaleString()}</div>
            </div>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <Badge status={claim.status} />
          <span style={{ color: "#6B7280", fontSize: 20 }}>{"\u203A"}</span>
        </div>
      </div>
    </Card>
  );
}
```

**Step 2: Verify the dashboard renders**

Run: `cd insurer && npm run dev`
Expected: Dashboard page loads at http://localhost:3001 showing stats and claim list (or empty state if no claims exist)

**Step 3: Commit**

```bash
git add insurer/src/pages/DashboardPage.jsx
git commit -m "feat: add insurer dashboard page with stats and claim list"
```

---

## Task 4: Build Insurer Claim Detail Page

**Files:**
- Create: `insurer/src/pages/ClaimDetailPage.jsx`

**Step 1: Create `insurer/src/pages/ClaimDetailPage.jsx`**

This is the existing AdjudicatorPage detail panel, refactored as a full page with routing.

```jsx
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import Spinner from "../components/Spinner.jsx";
import ClaimTimeline from "../components/ClaimTimeline.jsx";
import { getClaim, reviewClaim } from "../api.js";

export default function ClaimDetailPage() {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectInput, setShowRejectInput] = useState(false);
  const [error, setError] = useState(null);

  const loadClaim = async () => {
    try {
      const data = await getClaim(claimId);
      setClaim(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClaim();
    const interval = setInterval(loadClaim, 10000);
    return () => clearInterval(interval);
  }, [claimId]);

  const handleAction = async (action) => {
    if (action === "reject" && !rejectReason.trim()) {
      setShowRejectInput(true);
      return;
    }
    setUpdating(true);
    try {
      await reviewClaim(claimId, action, rejectReason);
      await loadClaim();
      setShowRejectInput(false);
      setRejectReason("");
    } catch (err) {
      alert("Review failed: " + err.message);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 12, color: "#6B7280", paddingTop: 60 }}>
        <Spinner /> Loading claim {claimId}...
      </div>
    );
  }

  if (error) {
    return (
      <Card style={{ maxWidth: 600, marginTop: 40 }}>
        <div style={{ color: "#F87171", fontWeight: 500 }}>{"\u274C"} Error: {error}</div>
        <button
          onClick={() => navigate("/")}
          style={{
            marginTop: 16, padding: "10px 20px", border: "1px solid #1F2937",
            borderRadius: 8, background: "transparent", color: "#F59E0B", cursor: "pointer",
          }}
        >
          Back to Dashboard
        </button>
      </Card>
    );
  }

  const ext = claim?.extracted_data || {};
  const patient = ext.patient || {};
  const hospital = ext.hospital || {};
  const diagnosis = ext.diagnosis || {};
  const treatment = ext.treatment || {};
  const billing = ext.billing || {};
  const dates = ext.dates || {};
  const verdict = claim?.verdict || {};
  const events = claim?.events || [];
  const fraud = claim?.fraud_score || null;
  const isPending = ["submitted", "pending", "under_review"].includes(claim?.status);

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32 }}>
        <div>
          <button
            onClick={() => navigate("/")}
            style={{
              padding: "6px 16px", border: "1px solid #1F2937", borderRadius: 6,
              background: "transparent", color: "#6B7280", cursor: "pointer", fontSize: 13, marginBottom: 12,
            }}
          >
            {"\u2190"} Dashboard
          </button>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Claim {claimId}</h1>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <Badge status={claim?.status} />
            {claim?.created_at && (
              <span style={{ color: "#6B7280", fontSize: 13 }}>
                {new Date(claim.created_at).toLocaleString("en-IN")}
              </span>
            )}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 24 }}>
        {/* Left column: Data + Verdict + Actions */}
        <div>
          {/* Extracted data */}
          <Card>
            <div style={{ fontSize: 15, fontWeight: 600, color: "#F59E0B", marginBottom: 16 }}>
              Extracted Data (OCR)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <Field label="Patient Name" value={patient.name} />
              <Field label="Age / Gender" value={`${patient.age || "?"} / ${patient.gender || "?"}`} />
              <Field label="Policy #" value={patient.policy_number} />
              <Field label="Hospital" value={hospital.name} />
              <Field label="Diagnosis" value={diagnosis.primary_diagnosis} />
              <Field label="Procedures" value={(treatment.procedures || []).join(", ") || "N/A"} />
              <Field label="Admission Type" value={treatment.admission_type} />
              <Field
                label="Total Amount"
                value={billing.total_amount != null ? `\u20B9${Number(billing.total_amount).toLocaleString()}` : "N/A"}
                highlight
              />
              <Field label="Admission" value={dates.admission_date} />
              <Field label="Discharge" value={dates.discharge_date} />
              <Field
                label="Confidence Score"
                value={ext.confidence_score != null ? `${(ext.confidence_score * 100).toFixed(0)}%` : "N/A"}
              />
            </div>
          </Card>

          {/* Fraud Risk Score (placeholder — will be populated after Task 7) */}
          {fraud && (
            <Card style={{ marginTop: 16, borderColor: fraud.level === "high" ? "#DC2626" : fraud.level === "medium" ? "#F59E0B" : "#059669" }}>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#F59E0B", marginBottom: 12 }}>
                Fraud Risk Assessment
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
                <div style={{
                  width: 80, height: 80, borderRadius: "50%",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 28, fontWeight: 800,
                  background: fraud.level === "high" ? "rgba(220,38,38,0.2)" : fraud.level === "medium" ? "rgba(245,158,11,0.2)" : "rgba(5,150,105,0.2)",
                  color: fraud.level === "high" ? "#F87171" : fraud.level === "medium" ? "#FCD34D" : "#34D399",
                  border: `3px solid ${fraud.level === "high" ? "#DC2626" : fraud.level === "medium" ? "#F59E0B" : "#059669"}`,
                }}>
                  {fraud.score}
                </div>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 600, textTransform: "capitalize", color: fraud.level === "high" ? "#F87171" : fraud.level === "medium" ? "#FCD34D" : "#34D399" }}>
                    {fraud.level} Risk
                  </div>
                  <div style={{ marginTop: 8 }}>
                    {(fraud.flags || []).map((flag, i) => (
                      <div key={i} style={{ fontSize: 13, color: "#9CA3AF", marginBottom: 4 }}>
                        {"\u26A0\uFE0F"} {flag}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* AI Verdict */}
          {verdict.verdict_text && (
            <Card style={{ marginTop: 16, borderColor: "#6366F1" }}>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#A78BFA", marginBottom: 12 }}>
                AI Coverage Analysis
              </div>
              <div style={{ color: "#E2E8F0", fontSize: 14, lineHeight: 1.7, whiteSpace: "pre-wrap" }}>
                {verdict.verdict_text}
              </div>
            </Card>
          )}

          {/* Actions */}
          {isPending && (
            <Card style={{ marginTop: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>Actions</div>

              {showRejectInput && (
                <input
                  type="text"
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Enter reason for rejection..."
                  style={{
                    width: "100%", padding: "12px 16px", border: "1px solid #DC2626",
                    borderRadius: 8, background: "#111827", color: "#E2E8F0", fontSize: 14,
                    outline: "none", marginBottom: 12,
                  }}
                />
              )}

              <div style={{ display: "flex", gap: 12 }}>
                <button
                  onClick={() => handleAction("approve")}
                  disabled={updating}
                  style={{
                    flex: 1, padding: "14px 20px", border: "none", borderRadius: 8,
                    background: "linear-gradient(135deg, #059669 0%, #10B981 100%)",
                    color: "#fff", fontWeight: 600, fontSize: 15,
                    cursor: updating ? "not-allowed" : "pointer",
                  }}
                >
                  {"\u2705"} Approve
                </button>
                <button
                  onClick={() => handleAction("reject")}
                  disabled={updating}
                  style={{
                    flex: 1, padding: "14px 20px", border: "none", borderRadius: 8,
                    background: "linear-gradient(135deg, #DC2626 0%, #EF4444 100%)",
                    color: "#fff", fontWeight: 600, fontSize: 15,
                    cursor: updating ? "not-allowed" : "pointer",
                  }}
                >
                  {"\u274C"} Reject
                </button>
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: "#4B5563", textAlign: "center" }}>
                Actions are recorded on-chain (Sepolia testnet)
              </div>
            </Card>
          )}
        </div>

        {/* Right column: Timeline */}
        <div>
          <Card>
            <div style={{ fontSize: 15, fontWeight: 600, color: "#F59E0B", marginBottom: 16 }}>
              On-Chain Timeline
            </div>
            <ClaimTimeline events={events} />
            <div style={{ marginTop: 16, textAlign: "center" }}>
              <button
                onClick={loadClaim}
                style={{
                  padding: "8px 16px", border: "1px solid #1F2937",
                  borderRadius: 8, background: "transparent", color: "#6B7280",
                  cursor: "pointer", fontSize: 12,
                }}
              >
                {"\u{1F504}"} Refresh
              </button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, highlight }) {
  return (
    <div>
      <div style={{ fontSize: 12, color: "#6B7280", marginBottom: 2 }}>{label}</div>
      <div style={{
        fontWeight: highlight ? 700 : 400,
        fontSize: highlight ? 18 : 14,
        color: highlight ? "#F59E0B" : "#E2E8F0",
      }}>
        {value || "N/A"}
      </div>
    </div>
  );
}
```

**Step 2: Verify navigation works**

Run: Open http://localhost:3001 — Dashboard should load. Click a claim row — should navigate to `/claims/{claimId}` detail page.

**Step 3: Commit**

```bash
git add insurer/src/pages/ClaimDetailPage.jsx
git commit -m "feat: add insurer claim detail page with OCR data, verdict, and actions"
```

---

## Task 5: Refactor Customer Portal — Remove Insurer Route, Update Sidebar

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/components/Sidebar.jsx`

**Step 1: Update `frontend/src/App.jsx` — remove AdjudicatorPage import and route, add VerifyPage**

```jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import VerdictPage from "./pages/VerdictPage.jsx";
import ClaimsPage from "./pages/ClaimsPage.jsx";
import VerifyPage from "./pages/VerifyPage.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          background: #0A0F1E;
          font-family: 'Inter', -apple-system, sans-serif;
          color: #F1F5F9;
        }
        a { color: inherit; text-decoration: none; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e2d47; border-radius: 3px; }
        input, textarea, select { font-family: inherit; }
      `}</style>

      <Sidebar />

      <main
        style={{ marginLeft: 220, padding: "40px 48px", minHeight: "100vh" }}
      >
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/verdict/:claimId" element={<VerdictPage />} />
          <Route path="/claims" element={<ClaimsPage />} />
          <Route path="/verify" element={<VerifyPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
```

**Step 2: Update `frontend/src/components/Sidebar.jsx` — replace Insurer Portal link with Verify link**

```jsx
import { useLocation, useNavigate } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    { path: "/", label: "Submit Claim", icon: "\u{1F4E4}" },
    { path: "/claims", label: "My Claims", icon: "\u{1F4CB}" },
    { path: "/verify", label: "Verify Claim", icon: "\u{1F50D}" },
  ];

  const isActive = (path) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  return (
    <aside
      style={{
        position: "fixed",
        left: 0,
        top: 0,
        width: 220,
        height: "100vh",
        background: "linear-gradient(180deg, #0F172A 0%, #1E293B 100%)",
        borderRight: "1px solid #1e3a5f",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        zIndex: 10,
      }}
    >
      <div
        onClick={() => navigate("/")}
        style={{
          fontSize: 18,
          fontWeight: 700,
          color: "#38BDF8",
          marginBottom: 8,
          display: "flex",
          alignItems: "center",
          gap: 10,
          cursor: "pointer",
        }}
      >
        <span style={{ fontSize: 26 }}>{"\u{1F3E5}"}</span>
        ClaimChain
      </div>
      <div
        style={{
          fontSize: 11,
          color: "#64748B",
          marginBottom: 36,
          paddingLeft: 38,
        }}
      >
        Patient Portal
      </div>

      <nav style={{ flex: 1 }}>
        {items.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            style={{
              width: "100%",
              padding: "14px 16px",
              marginBottom: 8,
              border: "none",
              borderRadius: 10,
              background: isActive(item.path)
                ? "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)"
                : "transparent",
              color: isActive(item.path) ? "#fff" : "#94A3B8",
              fontSize: 14,
              fontWeight: 500,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 12,
              transition: "all 0.2s",
            }}
          >
            <span style={{ fontSize: 18 }}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      <div
        style={{
          padding: "16px",
          background: "rgba(56, 189, 248, 0.1)",
          borderRadius: 12,
          fontSize: 12,
          color: "#94A3B8",
        }}
      >
        <div style={{ color: "#38BDF8", fontWeight: 600, marginBottom: 4 }}>
          AI-Powered
        </div>
        OCR + RAG + Blockchain
      </div>
    </aside>
  );
}
```

**Step 3: Commit**

```bash
git add frontend/src/App.jsx frontend/src/components/Sidebar.jsx
git commit -m "feat: refactor customer portal - remove insurer route, add verify link"
```

---

## Task 6: Update Backend CORS to Allow Both Portals

**Files:**
- Modify: `Backend/api/main.py`

**Step 1: Add `localhost:3001` to CORS origins**

In `Backend/api/main.py`, update the `allow_origins` list:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 2: Commit**

```bash
git add Backend/api/main.py
git commit -m "feat: add insurer portal origin (port 3001) to CORS"
```

---

## Task 7: Add QR Code to Customer Portal VerdictPage

**Files:**
- Modify: `frontend/package.json` (add `qrcode.react` dependency)
- Modify: `frontend/src/pages/VerdictPage.jsx`

**Step 1: Install qrcode.react**

Run: `cd frontend && npm install qrcode.react`

**Step 2: Update `frontend/src/pages/VerdictPage.jsx`**

Add QR code import at the top:

```jsx
import { QRCodeSVG } from "qrcode.react";
```

After the "Blockchain Proof" Card section (after line 178 in the current file), add a new QR Code card:

```jsx
          {/* QR Code Receipt */}
          {proof.tx_hash && (
            <Card style={{ marginTop: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#38BDF8", marginBottom: 16 }}>
                Claim QR Receipt
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
                <div style={{ background: "#fff", padding: 12, borderRadius: 12 }}>
                  <QRCodeSVG
                    value={`https://sepolia.etherscan.io/tx/0x${proof.tx_hash.replace("0x", "")}`}
                    size={120}
                    level="M"
                  />
                </div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 8 }}>
                    Scan to verify on Etherscan
                  </div>
                  <div style={{ fontSize: 12, color: "#64748B", lineHeight: 1.6 }}>
                    This QR code links directly to the blockchain transaction
                    proving your claim was recorded immutably before insurer review.
                  </div>
                  <button
                    onClick={() => {
                      const svg = document.querySelector("#qr-receipt svg");
                      if (!svg) return;
                      const data = new XMLSerializer().serializeToString(svg);
                      const blob = new Blob([data], { type: "image/svg+xml" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `ClaimChain-${claimId}-QR.svg`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    style={{
                      marginTop: 12, padding: "8px 16px", border: "1px solid #1e3a5f",
                      borderRadius: 8, background: "transparent", color: "#38BDF8",
                      cursor: "pointer", fontSize: 13,
                    }}
                  >
                    {"\u2B07\uFE0F"} Download QR
                  </button>
                </div>
              </div>
            </Card>
          )}
```

Wrap the QR code `<div>` with `id="qr-receipt"` so the download button can find it:

Change `<div style={{ background: "#fff", ...` to:
```jsx
<div id="qr-receipt" style={{ background: "#fff", padding: 12, borderRadius: 12 }}>
```

**Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/pages/VerdictPage.jsx
git commit -m "feat: add QR code receipt to verdict page with download button"
```

---

## Task 8: Create Customer Portal Verify Page

**Files:**
- Create: `frontend/src/pages/VerifyPage.jsx`

**Step 1: Create `frontend/src/pages/VerifyPage.jsx`**

```jsx
import { useState } from "react";
import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import Spinner from "../components/Spinner.jsx";
import ClaimTimeline from "../components/ClaimTimeline.jsx";
import { getClaim } from "../api.js";

export default function VerifyPage() {
  const [claimId, setClaimId] = useState("");
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleVerify = async () => {
    if (!claimId.trim()) return;
    setLoading(true);
    setError(null);
    setClaim(null);
    try {
      const data = await getClaim(claimId.trim());
      setClaim(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const events = claim?.events || [];
  const proof = claim?.blockchain_proof || {};

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
        Verify Claim On-Chain
      </h1>
      <p style={{ color: "#94A3B8", marginBottom: 32 }}>
        Enter a Claim ID to view its immutable blockchain timeline. No login required.
      </p>

      <Card style={{ maxWidth: 560 }}>
        <div style={{ display: "flex", gap: 12 }}>
          <input
            type="text"
            value={claimId}
            onChange={(e) => setClaimId(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleVerify()}
            placeholder="e.g. CLM-20260306-001"
            style={{
              flex: 1, padding: "12px 16px", border: "1px solid #1e3a5f",
              borderRadius: 10, background: "#0F172A", color: "#F1F5F9",
              fontSize: 15, outline: "none", fontFamily: "monospace",
            }}
          />
          <button
            onClick={handleVerify}
            disabled={!claimId.trim() || loading}
            style={{
              padding: "12px 24px", border: "none", borderRadius: 10,
              background: !claimId.trim() || loading ? "#1e3a5f" : "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)",
              color: "#fff", fontWeight: 600, cursor: !claimId.trim() || loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? <Spinner size={18} /> : "Verify"}
          </button>
        </div>
      </Card>

      {error && (
        <Card style={{ marginTop: 24, maxWidth: 560, borderColor: "#DC2626" }}>
          <div style={{ color: "#F87171" }}>{"\u274C"} {error}</div>
        </Card>
      )}

      {claim && (
        <div style={{ maxWidth: 560, marginTop: 24 }}>
          {/* Claim status header */}
          <Card>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div>
                <div style={{ fontSize: 12, color: "#64748B" }}>Claim ID</div>
                <div style={{ fontFamily: "monospace", color: "#38BDF8" }}>{claim.claim_id}</div>
              </div>
              <Badge status={claim.status} />
            </div>
            {proof.merkle_root && (
              <div style={{ marginTop: 8 }}>
                <div style={{ fontSize: 12, color: "#64748B", marginBottom: 4 }}>Merkle Root</div>
                <div style={{ fontFamily: "monospace", fontSize: 12, color: "#94A3B8", wordBreak: "break-all" }}>
                  {proof.merkle_root}
                </div>
              </div>
            )}
            {proof.tx_hash && (
              <div style={{ marginTop: 8 }}>
                <div style={{ fontSize: 12, color: "#64748B", marginBottom: 4 }}>Transaction</div>
                <a
                  href={`https://sepolia.etherscan.io/tx/0x${proof.tx_hash.replace("0x", "")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "#38BDF8", fontFamily: "monospace", fontSize: 13 }}
                >
                  View on Etherscan {"\u2197\uFE0F"}
                </a>
              </div>
            )}
          </Card>

          {/* Timeline */}
          <Card style={{ marginTop: 16 }}>
            <div style={{ fontSize: 15, fontWeight: 600, color: "#38BDF8", marginBottom: 16 }}>
              On-Chain Event Timeline
            </div>
            <ClaimTimeline events={events} />
          </Card>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Verify verify page works**

Open http://localhost:3000/verify. Enter a valid Claim ID. Should show on-chain timeline.

**Step 3: Commit**

```bash
git add frontend/src/pages/VerifyPage.jsx
git commit -m "feat: add public claim verification page with on-chain timeline"
```

---

## Task 9: Create Fraud Risk Scoring Backend Service

**Files:**
- Create: `Backend/api/services/fraud_scorer.py`
- Modify: `Backend/api/routes/claims.py`

**Step 1: Create `Backend/api/services/fraud_scorer.py`**

```python
"""
Rule-based fraud risk scoring for insurance claims.
Returns a 0-100 score with flagged rules and risk level.
"""

from datetime import datetime


# Diagnoses that are commonly excluded or associated with fraud
_HIGH_RISK_DIAGNOSES = [
    "cosmetic", "plastic surgery", "rhinoplasty", "liposuction",
    "hair transplant", "fertility", "ivf", "dental implant",
    "lasik", "botox", "breast augmentation",
]


def score_claim(extracted_data: dict) -> dict:
    """
    Score a claim for fraud risk based on extracted data.

    Args:
        extracted_data: The ExtractedClaim dict from OCR pipeline.

    Returns:
        {
            "score": int (0-100),
            "level": "low" | "medium" | "high",
            "flags": list[str]
        }
    """
    score = 0
    flags = []

    billing = extracted_data.get("billing", {})
    dates = extracted_data.get("dates", {})
    diagnosis = extracted_data.get("diagnosis", {})
    treatment = extracted_data.get("treatment", {})
    missing = extracted_data.get("missing_fields", [])

    total_amount = billing.get("total_amount")

    # Rule 1: High bill amount (> 5,00,000)
    if total_amount is not None:
        try:
            amount = float(total_amount)
            if amount > 500000:
                score += 30
                flags.append(f"High bill amount: Rs.{amount:,.0f} (threshold: Rs.5,00,000)")
        except (ValueError, TypeError):
            pass

    # Rule 2: Short stay + high bill (< 24hrs AND > 2,00,000)
    admission_date = dates.get("admission_date")
    discharge_date = dates.get("discharge_date")
    if admission_date and discharge_date and total_amount:
        try:
            fmt_candidates = ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d %b %Y", "%d-%b-%Y"]
            admit_dt = None
            disc_dt = None
            for fmt in fmt_candidates:
                try:
                    admit_dt = datetime.strptime(admission_date, fmt)
                    disc_dt = datetime.strptime(discharge_date, fmt)
                    break
                except ValueError:
                    continue

            if admit_dt and disc_dt:
                stay_hours = (disc_dt - admit_dt).total_seconds() / 3600
                if stay_hours < 24 and float(total_amount) > 200000:
                    score += 25
                    flags.append(f"Short stay ({stay_hours:.0f}hrs) with high bill (Rs.{float(total_amount):,.0f})")
        except (ValueError, TypeError):
            pass

    # Rule 3: Missing documents (> 3 missing fields)
    if isinstance(missing, list) and len(missing) > 3:
        score += 20
        flags.append(f"Missing {len(missing)} fields: {', '.join(missing[:5])}")

    # Rule 4: High-risk diagnosis
    primary = (diagnosis.get("primary_diagnosis") or "").lower()
    for keyword in _HIGH_RISK_DIAGNOSES:
        if keyword in primary:
            score += 15
            flags.append(f"High-risk diagnosis category: {diagnosis.get('primary_diagnosis')}")
            break

    # Rule 5: Weekend admission
    if admission_date:
        try:
            fmt_candidates = ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y", "%d %b %Y", "%d-%b-%Y"]
            for fmt in fmt_candidates:
                try:
                    admit_dt = datetime.strptime(admission_date, fmt)
                    if admit_dt.weekday() >= 5:  # Saturday=5, Sunday=6
                        score += 5
                        flags.append(f"Weekend admission ({admit_dt.strftime('%A')})")
                    break
                except ValueError:
                    continue
        except (ValueError, TypeError):
            pass

    # Rule 6: Round bill amount
    if total_amount is not None:
        try:
            amount = float(total_amount)
            if amount >= 10000 and amount % 10000 == 0:
                score += 5
                flags.append(f"Perfectly round bill amount: Rs.{amount:,.0f}")
        except (ValueError, TypeError):
            pass

    # Cap at 100
    score = min(score, 100)

    # Determine risk level
    if score <= 25:
        level = "low"
    elif score <= 50:
        level = "medium"
    else:
        level = "high"

    return {
        "score": score,
        "level": level,
        "flags": flags,
    }
```

**Step 2: Wire fraud scorer into `Backend/api/routes/claims.py`**

Add import at the top of `claims.py`:

```python
from services.fraud_scorer import score_claim
```

In the `analyze_claim()` function, after the RAG verdict step (after `verdict = check_coverage(...)`) and before the hashing step, add:

```python
        # ── Step 2b: Fraud risk scoring ────────────────────────────
        fraud_score = score_claim(extracted_data)
```

Then in the `claim_record` dict, add the fraud score:

```python
        claim_record = {
            "extracted_data": extracted_data,
            "verdict": verdict,
            "fraud_score": fraud_score,
            "merkle_root": merkle_root,
            ...
        }
```

And in the `response` dict, also add it:

```python
        response = {
            "claim_id": claim_id,
            "extracted_data": extracted_data,
            "verdict": verdict,
            "fraud_score": fraud_score,
            "blockchain_proof": blockchain_proof,
            "status": "submitted",
        }
```

**Step 3: Verify fraud scorer works**

Run: Start the backend (`cd Backend/api && python -m uvicorn main:app --reload`). Submit a test claim. The response should include a `fraud_score` field with `score`, `level`, and `flags`.

**Step 4: Commit**

```bash
git add Backend/api/services/fraud_scorer.py Backend/api/routes/claims.py
git commit -m "feat: add rule-based fraud risk scoring to claim analysis pipeline"
```

---

## Task 10: Create Chat Endpoint for Policy Q&A

**Files:**
- Create: `Backend/api/routes/chat.py`
- Modify: `Backend/api/main.py`

**Step 1: Create `Backend/api/routes/chat.py`**

```python
"""Policy Q&A chatbot endpoint using existing RAG agent."""

import sys
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """
    Ask a question about the insurance policy.
    Uses the existing RAG agent to retrieve and answer from policy documents.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Add RAG module to path
        rag_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "RAG"))
        if rag_path not in sys.path:
            sys.path.insert(0, rag_path)

        from agent import query_agent

        answer = query_agent(body.question.strip())
        return ChatResponse(answer=answer)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {e}. Ensure Ollama is running with the mistral model.",
        )
```

**Step 2: Register chat router in `Backend/api/main.py`**

Add import:

```python
from routes.chat import router as chat_router
```

Add router:

```python
app.include_router(chat_router)
```

**Step 3: Verify endpoint works**

Run: `curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"question": "Is knee replacement covered?"}'`
Expected: JSON response with `{ "answer": "..." }`

**Step 4: Commit**

```bash
git add Backend/api/routes/chat.py Backend/api/main.py
git commit -m "feat: add /api/chat endpoint for policy Q&A using RAG agent"
```

---

## Task 11: Create Customer Portal ChatWidget Component

**Files:**
- Create: `frontend/src/components/ChatWidget.jsx`
- Modify: `frontend/src/api.js`
- Modify: `frontend/src/App.jsx`

**Step 1: Add `chatQuestion` function to `frontend/src/api.js`**

Append to the end of `api.js`:

```js
/**
 * POST /api/chat
 * Ask a policy question via RAG chatbot.
 */
export async function chatQuestion(question) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Chat failed" }));
    throw new Error(err.detail || "Chat request failed");
  }
  return res.json();
}
```

**Step 2: Create `frontend/src/components/ChatWidget.jsx`**

```jsx
import { useState, useRef, useEffect } from "react";
import Spinner from "./Spinner.jsx";
import { chatQuestion } from "../api.js";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! Ask me anything about your insurance policy coverage, limits, or claim procedures." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const q = input.trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setInput("");
    setLoading(true);

    try {
      const res = await chatQuestion(q);
      setMessages((prev) => [...prev, { role: "bot", text: res.answer }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: `Sorry, I couldn't get an answer: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          width: 56,
          height: 56,
          borderRadius: "50%",
          border: "none",
          background: "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)",
          color: "#fff",
          fontSize: 28,
          cursor: "pointer",
          boxShadow: "0 4px 20px rgba(14, 165, 233, 0.4)",
          zIndex: 100,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
        title="Policy Q&A Chatbot"
      >
        {"\u{1F4AC}"}
      </button>
    );
  }

  return (
    <div
      style={{
        position: "fixed",
        bottom: 24,
        right: 24,
        width: 380,
        height: 500,
        borderRadius: 16,
        background: "#0F172A",
        border: "1px solid #1e3a5f",
        display: "flex",
        flexDirection: "column",
        zIndex: 100,
        boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "14px 16px",
          background: "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ fontWeight: 600, fontSize: 15 }}>{"\u{1F4AC}"} Policy Assistant</div>
        <button
          onClick={() => setOpen(false)}
          style={{ background: "none", border: "none", color: "#fff", fontSize: 20, cursor: "pointer" }}
        >
          {"\u2715"}
        </button>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
              padding: "10px 14px",
              borderRadius: msg.role === "user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
              background: msg.role === "user"
                ? "linear-gradient(135deg, #0EA5E9, #6366F1)"
                : "#1E293B",
              color: "#F1F5F9",
              fontSize: 14,
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
            }}
          >
            {msg.text}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 8, color: "#64748B" }}>
            <Spinner size={16} /> Thinking...
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: 12, borderTop: "1px solid #1e3a5f", display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about your policy..."
          style={{
            flex: 1,
            padding: "10px 14px",
            border: "1px solid #1e3a5f",
            borderRadius: 8,
            background: "#0A0F1E",
            color: "#F1F5F9",
            fontSize: 14,
            outline: "none",
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          style={{
            padding: "10px 16px",
            border: "none",
            borderRadius: 8,
            background: !input.trim() || loading ? "#1e3a5f" : "#0EA5E9",
            color: "#fff",
            cursor: !input.trim() || loading ? "not-allowed" : "pointer",
            fontWeight: 600,
          }}
        >
          {"\u27A4"}
        </button>
      </div>
    </div>
  );
}
```

**Step 3: Add ChatWidget to `frontend/src/App.jsx`**

Add import:

```jsx
import ChatWidget from "./components/ChatWidget.jsx";
```

Add `<ChatWidget />` just before the closing `</BrowserRouter>`:

```jsx
      <ChatWidget />
    </BrowserRouter>
```

**Step 4: Verify chatbot appears and works**

Open http://localhost:3000. A floating chat bubble should appear in the bottom-right corner. Click it. Type a question like "Is surgery covered?" and verify a response comes back from the RAG agent.

**Step 5: Commit**

```bash
git add frontend/src/components/ChatWidget.jsx frontend/src/api.js frontend/src/App.jsx
git commit -m "feat: add floating policy Q&A chatbot widget using RAG agent"
```

---

## Task 12: Add Confidence Indicators to Backend

**Files:**
- Modify: `Backend/api/routes/claims.py`

**Step 1: Add field confidence computation**

In `Backend/api/routes/claims.py`, after OCR extraction and before RAG check, add a helper function and call it:

Add this function at the module level (above `analyze_claim`):

```python
def _compute_field_confidence(extracted_data: dict) -> dict:
    """Compute per-field confidence indicators based on extraction results."""
    missing = extracted_data.get("missing_fields", [])
    overall = extracted_data.get("confidence_score", 0.5)

    fields = {
        "patient_name": "patient.name",
        "patient_age": "patient.age",
        "patient_gender": "patient.gender",
        "policy_number": "patient.policy_number",
        "hospital_name": "hospital.name",
        "primary_diagnosis": "diagnosis.primary_diagnosis",
        "procedures": "treatment.procedures",
        "admission_type": "treatment.admission_type",
        "total_amount": "billing.total_amount",
        "admission_date": "dates.admission_date",
        "discharge_date": "dates.discharge_date",
    }

    confidence = {}
    for field_key, path in fields.items():
        parts = path.split(".")
        val = extracted_data
        for p in parts:
            val = val.get(p, None) if isinstance(val, dict) else None
            if val is None:
                break

        if field_key in missing or val is None or val == "" or val == []:
            confidence[field_key] = "low"
        elif overall >= 0.7:
            confidence[field_key] = "high"
        else:
            confidence[field_key] = "medium"

    return confidence
```

In the `analyze_claim` function, after the OCR extraction step, add:

```python
        # ── Step 1b: Compute field confidence indicators ──────────
        field_confidence = _compute_field_confidence(extracted_data)
```

Add `field_confidence` to the `claim_record` and `response` dicts:

```python
        claim_record = {
            "extracted_data": extracted_data,
            "verdict": verdict,
            "fraud_score": fraud_score,
            "field_confidence": field_confidence,
            ...
        }
```

```python
        response = {
            ...
            "field_confidence": field_confidence,
            ...
        }
```

**Step 2: Commit**

```bash
git add Backend/api/routes/claims.py
git commit -m "feat: add per-field confidence indicators to claim analysis"
```

---

## Task 13: Add Confidence Dots to Customer Portal VerdictPage

**Files:**
- Modify: `frontend/src/pages/VerdictPage.jsx`

**Step 1: Add a ConfidenceDot helper component**

Add this at the bottom of `VerdictPage.jsx` (alongside the existing Field and ProofField helpers):

```jsx
function ConfidenceDot({ level }) {
  const colors = { high: "#34D399", medium: "#FCD34D", low: "#F87171" };
  const labels = { high: "High confidence", medium: "Medium confidence", low: "Low confidence" };
  return (
    <span
      title={labels[level] || "Unknown"}
      style={{
        display: "inline-block",
        width: 8,
        height: 8,
        borderRadius: "50%",
        background: colors[level] || "#64748B",
        marginLeft: 6,
        verticalAlign: "middle",
      }}
    />
  );
}
```

**Step 2: Update the Field component to accept and display confidence**

Replace the existing `Field` helper in VerdictPage:

```jsx
function Field({ label, value, highlight, confidence }) {
  return (
    <div>
      <div style={{ fontSize: 12, color: "#64748B", marginBottom: 2 }}>
        {label}
        {confidence && <ConfidenceDot level={confidence} />}
      </div>
      <div style={{
        fontWeight: highlight ? 700 : 400,
        fontSize: highlight ? 18 : 14,
        color: highlight ? "#38BDF8" : "#F1F5F9",
      }}>
        {value || "N/A"}
      </div>
    </div>
  );
}
```

**Step 3: Pass confidence to each Field**

In the Extracted Data grid section, read the `field_confidence` from claim data:

```jsx
  const fc = claim?.field_confidence || {};
```

Then update each `<Field>` to pass the corresponding confidence:

```jsx
<Field label="Patient" value={patient.name} confidence={fc.patient_name} />
<Field label="Age / Gender" value={`${patient.age || "?"} / ${patient.gender || "?"}`} confidence={fc.patient_age} />
<Field label="Policy #" value={patient.policy_number} confidence={fc.policy_number} />
<Field label="Hospital" value={hospital.name} confidence={fc.hospital_name} />
<Field label="Diagnosis" value={diagnosis.primary_diagnosis} confidence={fc.primary_diagnosis} />
<Field label="Procedures" value={(treatment.procedures || []).join(", ") || "N/A"} confidence={fc.procedures} />
<Field label="Admission Type" value={treatment.admission_type} confidence={fc.admission_type} />
<Field
  label="Total Amount"
  value={billing.total_amount != null ? `\u20B9${Number(billing.total_amount).toLocaleString()}` : "N/A"}
  highlight
  confidence={fc.total_amount}
/>
<Field label="Admission" value={dates.admission_date} confidence={fc.admission_date} />
<Field label="Discharge" value={dates.discharge_date} confidence={fc.discharge_date} />
```

**Step 4: Commit**

```bash
git add frontend/src/pages/VerdictPage.jsx
git commit -m "feat: add confidence indicator dots to verdict page extracted data"
```

---

## Task 14: Add Confidence Dots to Insurer ClaimDetailPage

**Files:**
- Modify: `insurer/src/pages/ClaimDetailPage.jsx`

**Step 1: Add the same ConfidenceDot helper and update Field**

Add at the bottom of `ClaimDetailPage.jsx`:

```jsx
function ConfidenceDot({ level }) {
  const colors = { high: "#34D399", medium: "#FCD34D", low: "#F87171" };
  const labels = { high: "High confidence", medium: "Medium confidence", low: "Low confidence" };
  return (
    <span
      title={labels[level] || "Unknown"}
      style={{
        display: "inline-block",
        width: 8,
        height: 8,
        borderRadius: "50%",
        background: colors[level] || "#6B7280",
        marginLeft: 6,
        verticalAlign: "middle",
      }}
    />
  );
}
```

Update the existing `Field` helper to accept `confidence`:

```jsx
function Field({ label, value, highlight, confidence }) {
  return (
    <div>
      <div style={{ fontSize: 12, color: "#6B7280", marginBottom: 2 }}>
        {label}
        {confidence && <ConfidenceDot level={confidence} />}
      </div>
      <div style={{
        fontWeight: highlight ? 700 : 400,
        fontSize: highlight ? 18 : 14,
        color: highlight ? "#F59E0B" : "#E2E8F0",
      }}>
        {value || "N/A"}
      </div>
    </div>
  );
}
```

**Step 2: Read field_confidence and pass to Fields**

Add near the other data destructuring:

```jsx
  const fc = claim?.field_confidence || {};
```

Update each `<Field>` in the extracted data grid to pass `confidence={fc.field_name}` — same pattern as Task 13.

**Step 3: Commit**

```bash
git add insurer/src/pages/ClaimDetailPage.jsx
git commit -m "feat: add confidence indicator dots to insurer claim detail page"
```

---

## Task 15: Final Integration Test — Side-by-Side Demo

**Step 1: Start all three services**

Terminal 1 (Backend):
```bash
cd Backend/api && python -m uvicorn main:app --reload --port 8000
```

Terminal 2 (Customer Portal):
```bash
cd frontend && npm run dev
```

Terminal 3 (Insurer Portal):
```bash
cd insurer && npm run dev
```

**Step 2: Demo walkthrough**

Open two browser windows side by side:
- Left: http://localhost:3000 (Customer Portal)
- Right: http://localhost:3001 (Insurer Portal)

1. **Customer Portal** — Upload a test medical document, see AI verdict + QR code
2. **Insurer Portal** — Dashboard auto-refreshes, new claim appears with fraud score
3. **Insurer Portal** — Click claim, see extracted data with confidence dots, fraud risk meter, AI verdict
4. **Insurer Portal** — Click "Approve"
5. **Customer Portal** — Status updates to "Approved" on My Claims page
6. **Customer Portal** — Visit `/verify`, enter claim ID, see on-chain timeline
7. **Customer Portal** — Click chat bubble, ask "Is knee replacement covered?"

**Step 3: Verify all features work**

- [ ] Customer Portal loads on port 3000 with blue/green theme
- [ ] Insurer Portal loads on port 3001 with dark/amber theme
- [ ] QR code appears on VerdictPage after submission
- [ ] Verify page shows on-chain timeline for valid claim ID
- [ ] Fraud score appears in claim data (and renders on insurer detail page)
- [ ] Confidence dots appear on both portals' extracted data fields
- [ ] Chatbot opens, sends question, receives RAG answer
- [ ] Approve/reject actions work and reflect across both portals

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete two-portal split with QR, fraud scoring, chatbot, confidence indicators"
```

---

## Summary of All New Files

| File | Portal | Purpose |
|---|---|---|
| `insurer/package.json` | Insurer | NPM config |
| `insurer/vite.config.js` | Insurer | Vite dev server (port 3001) |
| `insurer/index.html` | Insurer | HTML entry |
| `insurer/src/main.jsx` | Insurer | React root |
| `insurer/src/App.jsx` | Insurer | Router + dark theme shell |
| `insurer/src/api.js` | Insurer | API client (same backend) |
| `insurer/src/components/InsurerSidebar.jsx` | Insurer | Amber-themed sidebar |
| `insurer/src/components/Card.jsx` | Insurer | Shared component (copied) |
| `insurer/src/components/Badge.jsx` | Insurer | Shared component (copied) |
| `insurer/src/components/Spinner.jsx` | Insurer | Shared component (copied) |
| `insurer/src/components/ClaimTimeline.jsx` | Insurer | Shared component (copied) |
| `insurer/src/pages/DashboardPage.jsx` | Insurer | Claims overview + stats |
| `insurer/src/pages/ClaimDetailPage.jsx` | Insurer | Full claim review + fraud + actions |
| `frontend/src/pages/VerifyPage.jsx` | Customer | Public on-chain claim verification |
| `frontend/src/components/ChatWidget.jsx` | Customer | Floating RAG chatbot |
| `Backend/api/services/fraud_scorer.py` | Backend | Rule-based fraud scoring engine |
| `Backend/api/routes/chat.py` | Backend | Policy Q&A endpoint |

## Summary of Modified Files

| File | Change |
|---|---|
| `frontend/src/App.jsx` | Remove insurer route, add `/verify` route, add `<ChatWidget />` |
| `frontend/src/components/Sidebar.jsx` | Replace "Insurer Portal" with "Verify Claim", change subtitle to "Patient Portal" |
| `frontend/src/pages/VerdictPage.jsx` | Add QR code section + confidence dots |
| `frontend/src/api.js` | Add `chatQuestion()` function |
| `Backend/api/main.py` | Add CORS for port 3001, register chat router |
| `Backend/api/routes/claims.py` | Wire fraud scorer + field confidence into analyze pipeline |
