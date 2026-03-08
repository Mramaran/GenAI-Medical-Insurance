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
