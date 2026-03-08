import { useState, useRef, useEffect } from "react";
import Spinner from "./Spinner.jsx";
import { chatQuestion } from "../api.js";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! Ask me anything about your insurance policy coverage, limits, or claim procedures." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const q = input.trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setInput("");
    setLoading(true);

    try {
      const res = await chatQuestion(q);
      setMessages((prev) => [...prev, { role: "bot", text: res.answer }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: `Sorry, I couldn't get an answer: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          width: 56,
          height: 56,
          borderRadius: "50%",
          border: "none",
          background: "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)",
          color: "#fff",
          fontSize: 28,
          cursor: "pointer",
          boxShadow: "0 4px 20px rgba(14, 165, 233, 0.4)",
          zIndex: 100,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
        title="Policy Q&A Chatbot"
      >
        {"\u{1F4AC}"}
      </button>
    );
  }

  return (
    <div
      style={{
        position: "fixed",
        bottom: 24,
        right: 24,
        width: 380,
        height: 500,
        borderRadius: 16,
        background: "#0F172A",
        border: "1px solid #1e3a5f",
        display: "flex",
        flexDirection: "column",
        zIndex: 100,
        boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "14px 16px",
          background: "linear-gradient(135deg, #0EA5E9 0%, #6366F1 100%)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ fontWeight: 600, fontSize: 15 }}>{"\u{1F4AC}"} Policy Assistant</div>
        <button
          onClick={() => setOpen(false)}
          style={{ background: "none", border: "none", color: "#fff", fontSize: 20, cursor: "pointer" }}
        >
          {"\u2715"}
        </button>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
              padding: "10px 14px",
              borderRadius: msg.role === "user" ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
              background: msg.role === "user"
                ? "linear-gradient(135deg, #0EA5E9, #6366F1)"
                : "#1E293B",
              color: "#F1F5F9",
              fontSize: 14,
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
            }}
          >
            {msg.text}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: "flex-start", display: "flex", alignItems: "center", gap: 8, color: "#64748B" }}>
            <Spinner size={16} /> Thinking...
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: 12, borderTop: "1px solid #1e3a5f", display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about your policy..."
          style={{
            flex: 1,
            padding: "10px 14px",
            border: "1px solid #1e3a5f",
            borderRadius: 8,
            background: "#0A0F1E",
            color: "#F1F5F9",
            fontSize: 14,
            outline: "none",
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          style={{
            padding: "10px 16px",
            border: "none",
            borderRadius: 8,
            background: !input.trim() || loading ? "#1e3a5f" : "#0EA5E9",
            color: "#fff",
            cursor: !input.trim() || loading ? "not-allowed" : "pointer",
            fontWeight: 600,
          }}
        >
          {"\u27A4"}
        </button>
      </div>
    </div>
  );
}
