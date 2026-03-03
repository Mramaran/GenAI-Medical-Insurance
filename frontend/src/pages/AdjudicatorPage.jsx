import { useState, useEffect } from "react";
import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import Spinner from "../components/Spinner.jsx";
import { listClaims, getClaim, reviewClaim } from "../api.js";

export default function AdjudicatorPage() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectInput, setShowRejectInput] = useState(false);

  useEffect(() => {
    loadClaims();
  }, []);

  const loadClaims = async () => {
    setLoading(true);
    try {
      const data = await listClaims();
      setClaims(data);
    } catch (err) {
      console.error("Failed to load claims:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (claimId) => {
    setSelectedId(claimId);
    setDetailLoading(true);
    setShowRejectInput(false);
    setRejectReason("");
    try {
      const data = await getClaim(claimId);
      setDetail(data);
    } catch (err) {
      setDetail({ _error: err.message });
    } finally {
      setDetailLoading(false);
    }
  };

  const handleAction = async (action) => {
    if (!selectedId) return;
    if (action === "reject" && !rejectReason.trim()) {
      setShowRejectInput(true);
      return;
    }
    setUpdating(true);
    try {
      await reviewClaim(selectedId, action, rejectReason);
      // Refresh
      await loadClaims();
      const refreshed = await getClaim(selectedId);
      setDetail(refreshed);
      setShowRejectInput(false);
      setRejectReason("");
    } catch (err) {
      alert("Review failed: " + err.message);
    } finally {
      setUpdating(false);
    }
  };

  const pendingClaims = claims.filter(
    (c) => c.status === "submitted" || c.status === "pending" || c.status === "under_review",
  );
  const processedClaims = claims.filter(
    (c) => c.status === "approved" || c.status === "rejected" || c.status === "settled",
  );

  const ext = detail?.extracted_data || {};
  const patient = ext.patient || {};
  const hospital = ext.hospital || {};
  const diagnosis = ext.diagnosis || {};
  const treatment = ext.treatment || {};
  const billing = ext.billing || {};

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
        Insurer Portal
      </h1>
      <p style={{ color: "#94A3B8", marginBottom: 32 }}>
        Review and adjudicate submitted claims
      </p>

      <div
        style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 24 }}
      >
        {/* ── Left: Claims list ─────────────────────────────────── */}
        <div>
          <div style={{ marginBottom: 24 }}>
            <h2
              style={{
                fontSize: 15,
                fontWeight: 600,
                color: "#FCD34D",
                marginBottom: 12,
              }}
            >
              {"\u23F3"} Pending ({pendingClaims.length})
            </h2>
            {loading ? (
              <div
                style={{
                  color: "#94A3B8",
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <Spinner size={16} /> Loading...
              </div>
            ) : pendingClaims.length === 0 ? (
              <div style={{ color: "#64748B", fontSize: 14 }}>
                No pending claims
              </div>
            ) : (
              <div style={{ display: "grid", gap: 8 }}>
                {pendingClaims.map((claim) => {
                  const id = claim.claim_id;
                  const pt = claim.extracted_data?.patient || {};
                  return (
                    <div
                      key={id}
                      onClick={() => handleSelect(id)}
                      style={{
                        padding: 14,
                        background: selectedId === id ? "#1E293B" : "#0F172A",
                        border: `1px solid ${selectedId === id ? "#38BDF8" : "#1e3a5f"}`,
                        borderRadius: 10,
                        cursor: "pointer",
                      }}
                    >
                      <div
                        style={{
                          fontSize: 12,
                          fontFamily: "monospace",
                          color: "#38BDF8",
                        }}
                      >
                        {id}
                      </div>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          marginTop: 8,
                        }}
                      >
                        <span style={{ color: "#94A3B8", fontSize: 13 }}>
                          {pt.name || "Unknown"}
                        </span>
                        <Badge status={claim.status} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {processedClaims.length > 0 && (
            <div>
              <h2
                style={{
                  fontSize: 15,
                  fontWeight: 600,
                  color: "#94A3B8",
                  marginBottom: 12,
                }}
              >
                {"\u2705"} Processed ({processedClaims.length})
              </h2>
              <div
                style={{
                  display: "grid",
                  gap: 8,
                  maxHeight: 300,
                  overflowY: "auto",
                }}
              >
                {processedClaims.map((claim) => {
                  const id = claim.claim_id;
                  return (
                    <div
                      key={id}
                      onClick={() => handleSelect(id)}
                      style={{
                        padding: 12,
                        background:
                          selectedId === id ? "#1E293B" : "transparent",
                        border: `1px solid ${selectedId === id ? "#38BDF8" : "#1e3a5f"}`,
                        borderRadius: 8,
                        cursor: "pointer",
                      }}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <span
                          style={{
                            fontSize: 12,
                            fontFamily: "monospace",
                            color: "#64748B",
                          }}
                        >
                          {id}
                        </span>
                        <Badge status={claim.status} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <button
            onClick={loadClaims}
            style={{
              width: "100%",
              marginTop: 16,
              padding: "10px",
              border: "1px solid #1e3a5f",
              borderRadius: 8,
              background: "transparent",
              color: "#94A3B8",
              cursor: "pointer",
              fontSize: 13,
            }}
          >
            {"\u{1F504}"} Refresh List
          </button>
        </div>

        {/* ── Right: Detail panel ──────────────────────────────── */}
        <Card>
          {!selectedId ? (
            <div
              style={{ textAlign: "center", padding: 60, color: "#64748B" }}
            >
              <div style={{ fontSize: 48, marginBottom: 16 }}>
                {"\u{1F4CB}"}
              </div>
              Select a claim to review
            </div>
          ) : detailLoading ? (
            <div style={{ textAlign: "center", padding: 60 }}>
              <Spinner />
              <div style={{ color: "#94A3B8", marginTop: 12 }}>
                Loading claim details...
              </div>
            </div>
          ) : detail?._error ? (
            <div style={{ color: "#F87171" }}>Error: {detail._error}</div>
          ) : detail ? (
            <div>
              {/* Header */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  marginBottom: 24,
                }}
              >
                <div>
                  <div style={{ fontSize: 12, color: "#64748B" }}>Claim ID</div>
                  <div style={{ fontFamily: "monospace", color: "#38BDF8" }}>
                    {detail.claim_id}
                  </div>
                </div>
                <Badge status={detail.status} />
              </div>

              {/* Patient / claim data */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 16,
                  marginBottom: 24,
                }}
              >
                <div>
                  <div style={{ fontSize: 12, color: "#64748B" }}>
                    Patient Name
                  </div>
                  <div>{patient.name || "N/A"}</div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "#64748B" }}>Hospital</div>
                  <div>{hospital.name || "N/A"}</div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "#64748B" }}>
                    Diagnosis
                  </div>
                  <div>{diagnosis.primary_diagnosis || "N/A"}</div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "#64748B" }}>
                    Procedures
                  </div>
                  <div>{(treatment.procedures || []).join(", ") || "N/A"}</div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "#64748B" }}>
                    Admission Type
                  </div>
                  <div>{treatment.admission_type || "N/A"}</div>
                </div>
                <div>
                  <div style={{ fontSize: 12, color: "#64748B" }}>
                    Total Amount
                  </div>
                  <div
                    style={{ fontWeight: 700, fontSize: 20, color: "#38BDF8" }}
                  >
                    {billing.total_amount != null
                      ? `\u20B9${Number(billing.total_amount).toLocaleString()}`
                      : "N/A"}
                  </div>
                </div>
              </div>

              {/* AI Verdict */}
              {detail.verdict?.verdict_text && (
                <div
                  style={{
                    padding: 16,
                    background: "rgba(167, 139, 250, 0.1)",
                    borderRadius: 10,
                    marginBottom: 24,
                    border: "1px solid rgba(167, 139, 250, 0.2)",
                  }}
                >
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      marginBottom: 8,
                      color: "#A78BFA",
                    }}
                  >
                    AI Coverage Analysis
                  </div>
                  <div
                    style={{
                      color: "#E2E8F0",
                      fontSize: 14,
                      lineHeight: 1.6,
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {detail.verdict.verdict_text}
                  </div>
                </div>
              )}

              {/* Actions — only for pending/submitted claims */}
              {(detail.status === "submitted" ||
                detail.status === "pending" ||
                detail.status === "under_review") && (
                <div>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      marginBottom: 12,
                    }}
                  >
                    Actions
                  </div>

                  {showRejectInput && (
                    <div style={{ marginBottom: 12 }}>
                      <input
                        type="text"
                        value={rejectReason}
                        onChange={(e) => setRejectReason(e.target.value)}
                        placeholder="Enter reason for rejection..."
                        style={{
                          width: "100%",
                          padding: "12px 16px",
                          border: "1px solid #DC2626",
                          borderRadius: 8,
                          background: "#0F172A",
                          color: "#F1F5F9",
                          fontSize: 14,
                          outline: "none",
                          marginBottom: 8,
                        }}
                      />
                    </div>
                  )}

                  <div style={{ display: "flex", gap: 12 }}>
                    <button
                      onClick={() => handleAction("approve")}
                      disabled={updating}
                      style={{
                        flex: 1,
                        padding: "12px 20px",
                        border: "none",
                        borderRadius: 8,
                        background:
                          "linear-gradient(135deg, #059669 0%, #10B981 100%)",
                        color: "#fff",
                        fontWeight: 600,
                        cursor: updating ? "not-allowed" : "pointer",
                      }}
                    >
                      {"\u2705"} Approve
                    </button>
                    <button
                      onClick={() => handleAction("reject")}
                      disabled={updating}
                      style={{
                        flex: 1,
                        padding: "12px 20px",
                        border: "none",
                        borderRadius: 8,
                        background:
                          "linear-gradient(135deg, #DC2626 0%, #EF4444 100%)",
                        color: "#fff",
                        fontWeight: 600,
                        cursor: updating ? "not-allowed" : "pointer",
                      }}
                    >
                      {"\u274C"} Reject
                    </button>
                  </div>
                  <div
                    style={{
                      marginTop: 8,
                      fontSize: 12,
                      color: "#475569",
                      textAlign: "center",
                    }}
                  >
                    Actions are recorded on-chain (Sepolia testnet)
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </Card>
      </div>
    </div>
  );
}
