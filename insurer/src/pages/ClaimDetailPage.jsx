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
  const fc = claim?.field_confidence || {};
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
              <Field label="Patient Name" value={patient.name} confidence={fc.patient_name} />
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
              <Field
                label="Confidence Score"
                value={ext.confidence_score != null ? `${(ext.confidence_score * 100).toFixed(0)}%` : "N/A"}
              />
            </div>
          </Card>

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
