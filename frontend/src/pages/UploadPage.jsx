import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/Card.jsx";
import Spinner from "../components/Spinner.jsx";
import { analyzeClaim } from "../api.js";

export default function UploadPage() {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [policyNumber, setPolicyNumber] = useState("HSP-2025-TN-001");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = Array.from(e.dataTransfer.files);
    if (dropped.length) setFiles((prev) => [...prev, ...dropped]);
  };

  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...selected]);
  };

  const removeFile = (idx) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleSubmit = async () => {
    if (!files.length) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      setStep("Reading documents (OCR)...");

      const data = await analyzeClaim(files, policyNumber);
      setStep("Done!");
      setResult(data);

      // Navigate to verdict page after a brief pause
      if (data.claim_id) {
        setTimeout(() => navigate(`/verdict/${data.claim_id}`), 1500);
      }
    } catch (err) {
      setError(err.message);
      setStep("");
    } finally {
      setLoading(false);
    }
  };

  /* ── helpers to pull nested V1 fields ─────────────────────────── */
  const ext = result?.extracted_data || {};
  const patient = ext.patient || {};
  const hospital = ext.hospital || {};
  const diagnosis = ext.diagnosis || {};
  const treatment = ext.treatment || {};
  const billing = ext.billing || {};
  const dates = ext.dates || {};
  const verdict = result?.verdict || {};

  return (
    <div>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
        Submit Medical Claim
      </h1>
      <p style={{ color: "#94A3B8", marginBottom: 32 }}>
        Upload medical documents for AI-powered OCR extraction + RAG coverage
        check
      </p>

      <Card style={{ maxWidth: 640 }}>
        {/* Policy number */}
        <div style={{ marginBottom: 20 }}>
          <label
            style={{
              display: "block",
              fontSize: 13,
              color: "#94A3B8",
              marginBottom: 6,
            }}
          >
            Policy Number
          </label>
          <input
            type="text"
            value={policyNumber}
            onChange={(e) => setPolicyNumber(e.target.value)}
            placeholder="e.g. HSP-2025-TN-001"
            style={{
              width: "100%",
              padding: "12px 16px",
              border: "1px solid #1e3a5f",
              borderRadius: 10,
              background: "#0F172A",
              color: "#F1F5F9",
              fontSize: 15,
              outline: "none",
            }}
          />
        </div>

        {/* Drop zone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => document.getElementById("fileInput").click()}
          style={{
            border: `2px dashed ${dragOver ? "#38BDF8" : "#1e3a5f"}`,
            borderRadius: 12,
            padding: 40,
            textAlign: "center",
            cursor: "pointer",
            transition: "all 0.2s",
            background: dragOver ? "rgba(56, 189, 248, 0.05)" : "transparent",
          }}
        >
          <input
            id="fileInput"
            type="file"
            accept="image/*,.pdf"
            multiple
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          <div style={{ fontSize: 48, marginBottom: 12 }}>{"\u{1F4C4}"}</div>
          <div style={{ fontWeight: 500, marginBottom: 6 }}>
            Drop files here or click to browse
          </div>
          <div style={{ color: "#64748B", fontSize: 13 }}>
            PDF, PNG, JPG — multiple files supported
          </div>
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div style={{ marginTop: 16, display: "grid", gap: 6 }}>
            {files.map((f, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "8px 12px",
                  background: "#0F172A",
                  borderRadius: 8,
                  fontSize: 13,
                }}
              >
                <span style={{ color: "#38BDF8" }}>{f.name}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(i);
                  }}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#F87171",
                    cursor: "pointer",
                    fontSize: 16,
                  }}
                >
                  {"\u2715"}
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={!files.length || loading}
          style={{
            width: "100%",
            marginTop: 24,
            padding: "14px 24px",
            border: "none",
            borderRadius: 10,
            background:
              !files.length || loading
                ? "#1e3a5f"
                : "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)",
            color: "#fff",
            fontSize: 16,
            fontWeight: 600,
            cursor: !files.length || loading ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 10,
          }}
        >
          {loading ? (
            <>
              <Spinner size={20} />
              {step || "Processing..."}
            </>
          ) : (
            <>{"\u{1F4E4}"} Analyze & Submit Claim</>
          )}
        </button>
      </Card>

      {/* ── Error ──────────────────────────────────────────────── */}
      {error && (
        <Card style={{ marginTop: 24, maxWidth: 640, borderColor: "#DC2626" }}>
          <div style={{ color: "#F87171", fontWeight: 500 }}>
            {"\u274C"} Error
          </div>
          <div style={{ color: "#FCA5A5", marginTop: 8 }}>{error}</div>
        </Card>
      )}

      {/* ── Result ─────────────────────────────────────────────── */}
      {result && (
        <div style={{ maxWidth: 640 }}>
          {/* Claim ID banner */}
          <Card
            style={{ marginTop: 24, borderColor: "#059669" }}
          >
            <div
              style={{ color: "#34D399", fontWeight: 600, marginBottom: 12 }}
            >
              {"\u2705"} Claim Submitted Successfully
            </div>
            <div style={{ display: "flex", gap: 24 }}>
              <div>
                <div style={{ fontSize: 12, color: "#64748B" }}>Claim ID</div>
                <div style={{ fontFamily: "monospace", color: "#38BDF8" }}>
                  {result.claim_id}
                </div>
              </div>
              <div>
                <div style={{ fontSize: 12, color: "#64748B" }}>Status</div>
                <div style={{ color: "#FCD34D" }}>{result.status}</div>
              </div>
            </div>
          </Card>

          {/* Extracted data summary */}
          <Card style={{ marginTop: 16 }}>
            <div
              style={{
                fontSize: 15,
                fontWeight: 600,
                color: "#38BDF8",
                marginBottom: 16,
              }}
            >
              Extracted Data (OCR)
            </div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 16,
              }}
            >
              <Field label="Patient" value={patient.name} />
              <Field label="Age / Gender" value={`${patient.age || "?"} / ${patient.gender || "?"}`} />
              <Field label="Policy #" value={patient.policy_number} />
              <Field label="Hospital" value={hospital.name} />
              <Field label="Diagnosis" value={diagnosis.primary_diagnosis} />
              <Field
                label="Procedures"
                value={(treatment.procedures || []).join(", ") || "N/A"}
              />
              <Field label="Admission Type" value={treatment.admission_type} />
              <Field
                label="Total Amount"
                value={
                  billing.total_amount != null
                    ? `\u20B9${Number(billing.total_amount).toLocaleString()}`
                    : "N/A"
                }
                highlight
              />
              <Field label="Admission" value={dates.admission_date} />
              <Field label="Discharge" value={dates.discharge_date} />
              <Field
                label="Confidence"
                value={
                  ext.confidence_score != null
                    ? `${(ext.confidence_score * 100).toFixed(0)}%`
                    : "N/A"
                }
              />
            </div>
          </Card>

          {/* RAG Verdict */}
          {verdict.verdict_text && (
            <Card style={{ marginTop: 16, borderColor: "#6366F1" }}>
              <div
                style={{
                  fontSize: 15,
                  fontWeight: 600,
                  color: "#A78BFA",
                  marginBottom: 12,
                }}
              >
                AI Coverage Verdict (RAG)
              </div>
              <div
                style={{
                  color: "#E2E8F0",
                  lineHeight: 1.7,
                  whiteSpace: "pre-wrap",
                }}
              >
                {verdict.verdict_text}
              </div>
              <details style={{ marginTop: 16 }}>
                <summary
                  style={{ color: "#64748B", fontSize: 12, cursor: "pointer" }}
                >
                  Query sent to RAG agent
                </summary>
                <div
                  style={{
                    marginTop: 8,
                    padding: 12,
                    background: "#0F172A",
                    borderRadius: 8,
                    fontSize: 13,
                    color: "#94A3B8",
                  }}
                >
                  {verdict.query_used}
                </div>
              </details>
            </Card>
          )}

          {/* Raw JSON (collapsible) */}
          <Card style={{ marginTop: 16 }}>
            <details>
              <summary
                style={{
                  color: "#64748B",
                  fontSize: 13,
                  cursor: "pointer",
                  fontWeight: 500,
                }}
              >
                Raw JSON Response
              </summary>
              <pre
                style={{
                  marginTop: 12,
                  background: "#0F172A",
                  padding: 16,
                  borderRadius: 8,
                  fontSize: 12,
                  overflow: "auto",
                  maxHeight: 400,
                  color: "#E2E8F0",
                }}
              >
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </Card>
        </div>
      )}
    </div>
  );
}

/* Small helper component */
function Field({ label, value, highlight }) {
  return (
    <div>
      <div style={{ fontSize: 12, color: "#64748B", marginBottom: 2 }}>
        {label}
      </div>
      <div
        style={{
          fontWeight: highlight ? 700 : 400,
          fontSize: highlight ? 18 : 14,
          color: highlight ? "#38BDF8" : "#F1F5F9",
        }}
      >
        {value || "N/A"}
      </div>
    </div>
  );
}
