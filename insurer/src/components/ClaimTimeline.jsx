/**
 * Vertical timeline showing on-chain events for a claim.
 * Each event shows action, timestamp, block number, and clickable tx hash.
 */

const EVENT_STYLES = {
  ClaimSubmitted: { color: "#38BDF8", label: "AI Verdict Committed", icon: "\u{1F4DD}" },
  StatusUpdated: { color: "#FCD34D", label: "Status Updated", icon: "\u{1F504}" },
  // Specific statuses
  Approved: { color: "#34D399", label: "Insurer Approved", icon: "\u2705" },
  Rejected: { color: "#F87171", label: "Insurer Rejected", icon: "\u274C" },
  UnderReview: { color: "#FCD34D", label: "Under Review", icon: "\u{1F50D}" },
  QueryRaised: { color: "#FB923C", label: "Query Raised", icon: "\u2753" },
  Settled: { color: "#34D399", label: "Settled", icon: "\u{1F4B0}" },
};

function getEventStyle(event) {
  // Check if it's a StatusUpdated with a specific new_status
  if (event.event_type === "StatusUpdated" && event.data?.new_status) {
    const s = EVENT_STYLES[event.data.new_status];
    if (s) return s;
  }
  return EVENT_STYLES[event.event_type] || EVENT_STYLES.ClaimSubmitted;
}

function formatTimestamp(ts) {
  if (!ts) return "\u2014";
  const d = new Date(ts * 1000);
  return d.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ClaimTimeline({ events = [] }) {
  if (!events.length || (events.length === 1 && events[0].event_type === "error")) {
    return (
      <div
        style={{
          padding: 24,
          textAlign: "center",
          color: "#475569",
          fontSize: 14,
        }}
      >
        {events[0]?.error
          ? `Blockchain connection issue: ${events[0].error}`
          : "No on-chain events yet"}
      </div>
    );
  }

  return (
    <div style={{ position: "relative", paddingLeft: 32 }}>
      {/* Vertical line */}
      <div
        style={{
          position: "absolute",
          left: 11,
          top: 8,
          bottom: 8,
          width: 2,
          background: "#1e3a5f",
        }}
      />

      {events.map((event, i) => {
        const style = getEventStyle(event);
        return (
          <div
            key={i}
            style={{
              position: "relative",
              marginBottom: 24,
              animation: "fadeIn 0.3s ease-out",
              animationDelay: `${i * 0.1}s`,
              animationFillMode: "both",
            }}
          >
            {/* Dot on the line */}
            <div
              style={{
                position: "absolute",
                left: -27,
                top: 4,
                width: 14,
                height: 14,
                borderRadius: "50%",
                background: style.color,
                border: "3px solid #0A0F1E",
              }}
            />

            {/* Content */}
            <div
              style={{
                padding: 16,
                background: "#0F172A",
                borderRadius: 10,
                border: `1px solid ${style.color}22`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 8,
                }}
              >
                <div style={{ color: style.color, fontWeight: 600, fontSize: 14 }}>
                  {style.icon} {style.label}
                </div>
                <div style={{ color: "#64748B", fontSize: 12 }}>
                  {formatTimestamp(event.timestamp)}
                </div>
              </div>

              <div style={{ display: "flex", gap: 24, fontSize: 13 }}>
                {event.block_number && (
                  <div>
                    <span style={{ color: "#64748B" }}>Block </span>
                    <span style={{ color: "#94A3B8", fontFamily: "monospace" }}>
                      #{event.block_number}
                    </span>
                  </div>
                )}
                {event.tx_hash && (
                  <div>
                    <span style={{ color: "#64748B" }}>Tx </span>
                    <a
                      href={`https://sepolia.etherscan.io/tx/0x${event.tx_hash.replace("0x", "")}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: "#38BDF8", fontFamily: "monospace" }}
                    >
                      {event.tx_hash.slice(0, 10)}...{event.tx_hash.slice(-6)}
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
