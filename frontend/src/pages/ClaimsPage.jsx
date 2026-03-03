import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/Card.jsx";
import Badge from "../components/Badge.jsx";
import Spinner from "../components/Spinner.jsx";
import { listClaims } from "../api.js";

export default function ClaimsPage() {
  const navigate = useNavigate();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 32,
        }}
      >
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            My Claims
          </h1>
          <p style={{ color: "#94A3B8" }}>
            Track submitted claims and view AI verdicts
          </p>
        </div>
        <button
          onClick={loadClaims}
          style={{
            padding: "10px 20px",
            border: "1px solid #1e3a5f",
            borderRadius: 8,
            background: "transparent",
            color: "#38BDF8",
            cursor: "pointer",
            fontSize: 14,
          }}
        >
          {"\u{1F504}"} Refresh
        </button>
      </div>

      {loading ? (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            color: "#94A3B8",
          }}
        >
          <Spinner /> Loading claims...
        </div>
      ) : claims.length === 0 ? (
        <Card>
          <div style={{ textAlign: "center", padding: 40 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>{"\u{1F4CB}"}</div>
            <div style={{ color: "#94A3B8" }}>
              No claims found. Upload your first claim to get started.
            </div>
          </div>
        </Card>
      ) : (
        <div style={{ display: "grid", gap: 16 }}>
          {claims.map((claim) => {
            const claimId = claim.claim_id;
            const ext = claim.extracted_data || {};
            const patient = ext.patient || {};
            const hospital = ext.hospital || {};
            const billing = ext.billing || {};

            return (
              <Card key={claimId}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}
                >
                  <div>
                    <div style={{ fontSize: 12, color: "#64748B", marginBottom: 4 }}>
                      Claim ID
                    </div>
                    <div
                      style={{
                        fontFamily: "monospace",
                        color: "#38BDF8",
                        marginBottom: 12,
                      }}
                    >
                      {claimId}
                    </div>

                    <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
                      <div>
                        <div style={{ fontSize: 12, color: "#64748B" }}>Patient</div>
                        <div>{patient.name || "N/A"}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: 12, color: "#64748B" }}>Hospital</div>
                        <div>{hospital.name || "N/A"}</div>
                      </div>
                      {billing.total_amount != null && (
                        <div>
                          <div style={{ fontSize: 12, color: "#64748B" }}>Amount</div>
                          <div style={{ fontWeight: 600 }}>
                            {"\u20B9"}{Number(billing.total_amount).toLocaleString()}
                          </div>
                        </div>
                      )}
                      <div>
                        <div style={{ fontSize: 12, color: "#64748B" }}>Status</div>
                        <Badge status={claim.status} />
                      </div>
                      {claim.tx_hash && (
                        <div>
                          <div style={{ fontSize: 12, color: "#64748B" }}>On-Chain</div>
                          <div style={{ color: "#34D399", fontSize: 13 }}>{"\u2705"} Recorded</div>
                        </div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => navigate(`/verdict/${claimId}`)}
                    style={{
                      padding: "10px 20px",
                      border: "none",
                      borderRadius: 8,
                      background: "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)",
                      color: "#fff",
                      cursor: "pointer",
                      fontSize: 14,
                      fontWeight: 500,
                    }}
                  >
                    View Details
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
