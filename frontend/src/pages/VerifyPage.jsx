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
            onKeyDown={(e) => e.key === "Enter" && !loading && handleVerify()}
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
