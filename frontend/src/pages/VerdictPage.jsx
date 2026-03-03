import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import Spinner from "../components/Spinner.jsx";
import ClaimTimeline from "../components/ClaimTimeline.jsx";
import { getClaim } from "../api.js";

export default function VerdictPage() {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
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
    // Poll for updates every 10 seconds
    const interval = setInterval(loadClaim, 10000);
    return () => clearInterval(interval);
  }, [claimId]);

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", gap: 12, color: "#94A3B8", paddingTop: 60 }}>
        <Spinner /> Loading claim {claimId}...
      </div>
    );
  }

  if (error) {
    return (
      <Card style={{ maxWidth: 600, marginTop: 40 }}>
        <div style={{ color: "#F87171", fontWeight: 500 }}>{"\u274C"} Error</div>
        <div style={{ color: "#FCA5A5", marginTop: 8 }}>{error}</div>
        <button
          onClick={() => navigate("/")}
          style={{
            marginTop: 16, padding: "10px 20px", border: "1px solid #1e3a5f",
            borderRadius: 8, background: "transparent", color: "#38BDF8", cursor: "pointer",
          }}
        >
          Back to Upload
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
  const proof = claim?.blockchain_proof || {};
  const events = claim?.events || [];

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Claim {claimId}
          </h1>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <Badge status={claim?.status} />
            {claim?.created_at && (
              <span style={{ color: "#64748B", fontSize: 13 }}>
                {new Date(claim.created_at).toLocaleString("en-IN")}
              </span>
            )}
          </div>
        </div>
        <button
          onClick={() => navigate("/claims")}
          style={{
            padding: "10px 20px", border: "1px solid #1e3a5f",
            borderRadius: 8, background: "transparent", color: "#38BDF8", cursor: "pointer",
          }}
        >
          {"\u{1F4CB}"} All Claims
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 24 }}>
        {/* ── Left column: Data + Verdict ──────────────────────────── */}
        <div>
          {/* Extracted Data */}
          <Card>
            <div style={{ fontSize: 15, fontWeight: 600, color: "#38BDF8", marginBottom: 16 }}>
              Extracted Data (OCR)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <Field label="Patient" value={patient.name} />
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
                label="Confidence"
                value={ext.confidence_score != null ? `${(ext.confidence_score * 100).toFixed(0)}%` : "N/A"}
              />
            </div>
          </Card>

          {/* AI Coverage Verdict */}
          {verdict.verdict_text && (
            <Card style={{ marginTop: 16, borderColor: "#6366F1" }}>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#A78BFA", marginBottom: 12 }}>
                AI Coverage Verdict (RAG)
              </div>
              <div style={{ color: "#E2E8F0", lineHeight: 1.7, whiteSpace: "pre-wrap" }}>
                {verdict.verdict_text}
              </div>
              <details style={{ marginTop: 16 }}>
                <summary style={{ color: "#64748B", fontSize: 12, cursor: "pointer" }}>
                  Query sent to RAG agent
                </summary>
                <div style={{
                  marginTop: 8, padding: 12, background: "#0F172A",
                  borderRadius: 8, fontSize: 13, color: "#94A3B8",
                }}>
                  {verdict.query_used}
                </div>
              </details>
            </Card>
          )}

          {/* Blockchain Proof */}
          <Card style={{ marginTop: 16 }}>
            <div style={{ fontSize: 15, fontWeight: 600, color: "#38BDF8", marginBottom: 16 }}>
              Blockchain Proof
            </div>
            <div style={{ display: "grid", gap: 12 }}>
              <ProofField label="Merkle Root" value={proof.merkle_root} mono />
              {proof.tx_hash ? (
                <div>
                  <div style={{ fontSize: 12, color: "#64748B", marginBottom: 2 }}>Transaction Hash</div>
                  <a
                    href={`https://sepolia.etherscan.io/tx/0x${proof.tx_hash.replace("0x", "")}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#38BDF8", fontFamily: "monospace", fontSize: 13 }}
                  >
                    0x{proof.tx_hash.replace("0x", "")}
                  </a>
                </div>
              ) : (
                <ProofField label="Transaction Hash" value={proof.error || "Not recorded"} />
              )}
              <ProofField label="Block Number" value={proof.block_number} mono />
              <ProofField label="Gas Used" value={proof.gas_used} />
            </div>
          </Card>
        </div>

        {/* ── Right column: Timeline ──────────────────────────────── */}
        <div>
          <Card>
            <div style={{ fontSize: 15, fontWeight: 600, color: "#38BDF8", marginBottom: 16 }}>
              On-Chain Timeline
            </div>
            <ClaimTimeline events={events} />
            <div style={{ marginTop: 16, textAlign: "center" }}>
              <button
                onClick={loadClaim}
                style={{
                  padding: "8px 16px", border: "1px solid #1e3a5f",
                  borderRadius: 8, background: "transparent", color: "#64748B",
                  cursor: "pointer", fontSize: 12,
                }}
              >
                {"\u{1F504}"} Refresh (auto-refreshes every 10s)
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
      <div style={{ fontSize: 12, color: "#64748B", marginBottom: 2 }}>{label}</div>
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

function ProofField({ label, value, mono }) {
  return (
    <div>
      <div style={{ fontSize: 12, color: "#64748B", marginBottom: 2 }}>{label}</div>
      <div style={{
        fontSize: 13,
        color: value ? "#94A3B8" : "#475569",
        fontFamily: mono ? "monospace" : "inherit",
        wordBreak: "break-all",
      }}>
        {value != null ? String(value) : "—"}
      </div>
    </div>
  );
}
