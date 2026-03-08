import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import VerdictPage from "./pages/VerdictPage.jsx";
import ClaimsPage from "./pages/ClaimsPage.jsx";
import VerifyPage from "./pages/VerifyPage.jsx";
import ChatWidget from "./components/ChatWidget.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          background: #0A0F1E;
          font-family: 'Inter', -apple-system, sans-serif;
          color: #F1F5F9;
        }
        a { color: inherit; text-decoration: none; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e2d47; border-radius: 3px; }
        input, textarea, select { font-family: inherit; }
      `}</style>

      <Sidebar />

      <main
        style={{ marginLeft: 220, padding: "40px 48px", minHeight: "100vh" }}
      >
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/verdict/:claimId" element={<VerdictPage />} />
          <Route path="/claims" element={<ClaimsPage />} />
          <Route path="/verify" element={<VerifyPage />} />
        </Routes>
      </main>

      <ChatWidget />
    </BrowserRouter>
  );
}
