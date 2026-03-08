/**
 * ClaimChain V1 API client
 * Matches Backend/api endpoints exactly.
 */

const BASE = "http://localhost:8000";

/**
 * POST /api/claims/analyze
 * Upload medical documents + policy number for OCR + RAG analysis.
 */
export async function analyzeClaim(files, policyNumber) {
  const fd = new FormData();
  files.forEach((f) => fd.append("files", f));
  fd.append("policy_number", policyNumber || "");
  const res = await fetch(`${BASE}/api/claims/analyze`, {
    method: "POST",
    body: fd,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

/**
 * GET /api/claims
 * List all claims (for insurer dashboard).
 */
export async function listClaims() {
  const res = await fetch(`${BASE}/api/claims/`);
  if (!res.ok) throw new Error("Failed to fetch claims");
  return res.json();
}

/**
 * GET /api/claims/{claimId}
 * Get full claim data by ID.
 */
export async function getClaim(claimId) {
  const res = await fetch(`${BASE}/api/claims/${claimId}`);
  if (!res.ok) throw new Error(`Claim ${claimId} not found`);
  return res.json();
}

/**
 * POST /api/claims/{claimId}/review
 * Insurer approve/reject action.
 */
export async function reviewClaim(claimId, action, reason = "") {
  const res = await fetch(`${BASE}/api/claims/${claimId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, reason }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Review failed");
  }
  return res.json();
}

/**
 * GET /  — health check
 */
export function healthCheck() {
  return fetch(`${BASE}/`).then((r) => r.json());
}
