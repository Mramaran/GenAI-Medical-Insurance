import { useLocation, useNavigate } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    { path: "/", label: "Submit Claim", icon: "\u{1F4E4}" },
    { path: "/claims", label: "My Claims", icon: "\u{1F4CB}" },
    { path: "/insurer", label: "Insurer Portal", icon: "\u2696\uFE0F" },
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
        AI + Blockchain
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
