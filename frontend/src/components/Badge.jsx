export default function Badge({ status }) {
  const colors = {
    submitted: { bg: "#FEF3C7", text: "#D97706" },
    pending: { bg: "#FEF3C7", text: "#D97706" },
    approved: { bg: "#D1FAE5", text: "#059669" },
    rejected: { bg: "#FEE2E2", text: "#DC2626" },
    "under review": { bg: "#DBEAFE", text: "#2563EB" },
    "under_review": { bg: "#DBEAFE", text: "#2563EB" },
    "query_raised": { bg: "#FEF3C7", text: "#D97706" },
    settled: { bg: "#D1FAE5", text: "#047857" },
  };

  const c = colors[status?.toLowerCase()] || colors.submitted;

  return (
    <span
      style={{
        display: "inline-block",
        padding: "4px 12px",
        borderRadius: 20,
        background: c.bg,
        color: c.text,
        fontSize: 12,
        fontWeight: 600,
        textTransform: "capitalize",
      }}
    >
      {status || "unknown"}
    </span>
  );
}
