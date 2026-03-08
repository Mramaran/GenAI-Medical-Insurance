import { useLocation, useNavigate } from "react-router-dom";

export default function InsurerSidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    { path: "/", label: "Dashboard", icon: "\u{1F4CA}" },
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
        width: 240,
        height: "100vh",
        background: "linear-gradient(180deg, #030712 0%, #111827 100%)",
        borderRight: "1px solid #1F2937",
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
          color: "#F59E0B",
          marginBottom: 8,
          display: "flex",
          alignItems: "center",
          gap: 10,
          cursor: "pointer",
        }}
      >
        <span style={{ fontSize: 26 }}>{"\u2696\uFE0F"}</span>
        ClaimChain
      </div>
      <div
        style={{
          fontSize: 11,
          color: "#6B7280",
          marginBottom: 36,
          paddingLeft: 38,
          letterSpacing: 1,
          textTransform: "uppercase",
        }}
      >
        Insurer Portal
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
                ? "linear-gradient(135deg, #D97706 0%, #F59E0B 100%)"
                : "transparent",
              color: isActive(item.path) ? "#fff" : "#9CA3AF",
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
          background: "rgba(245, 158, 11, 0.1)",
          borderRadius: 12,
          fontSize: 12,
          color: "#9CA3AF",
        }}
      >
        <div style={{ color: "#F59E0B", fontWeight: 600, marginBottom: 4 }}>
          Claims Officer View
        </div>
        Fraud Detection + AI Verdicts
      </div>
    </aside>
  );
}
