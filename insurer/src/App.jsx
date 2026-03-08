import { BrowserRouter, Routes, Route } from "react-router-dom";
import InsurerSidebar from "./components/InsurerSidebar.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import ClaimDetailPage from "./pages/ClaimDetailPage.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          background: #030712;
          font-family: 'Inter', -apple-system, sans-serif;
          color: #E2E8F0;
        }
        a { color: inherit; text-decoration: none; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #1e2d47; border-radius: 3px; }
        input, textarea, select { font-family: inherit; }
      `}</style>

      <InsurerSidebar />

      <main style={{ marginLeft: 240, padding: "40px 48px", minHeight: "100vh" }}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/claims/:claimId" element={<ClaimDetailPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
