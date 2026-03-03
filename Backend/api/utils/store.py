"""In-memory claim storage for ClaimChain API."""

from datetime import datetime, timezone

# ── Storage ─────────────────────────────────────────────────────────────
_claims: dict[str, dict] = {}
_counter: int = 0


def _next_claim_id() -> str:
    """Generate a sequential claim ID like CLM-20260303-001."""
    global _counter
    _counter += 1
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"CLM-{date_str}-{_counter:03d}"


def generate_claim_id() -> str:
    """Public wrapper to generate the next claim ID."""
    return _next_claim_id()


def save_claim(claim_id: str, data: dict) -> None:
    """Save a new claim record."""
    data["claim_id"] = claim_id
    data.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    data.setdefault("status", "submitted")
    data.setdefault("events", [])
    _claims[claim_id] = data


def get_claim(claim_id: str) -> dict | None:
    """Retrieve a claim by ID, or None if not found."""
    return _claims.get(claim_id)


def get_all_claims() -> list[dict]:
    """Return all claims, newest first."""
    return sorted(
        _claims.values(),
        key=lambda c: c.get("created_at", ""),
        reverse=True,
    )


def update_claim(claim_id: str, updates: dict) -> dict | None:
    """Merge updates into an existing claim record. Returns updated record or None."""
    record = _claims.get(claim_id)
    if record is None:
        return None
    record.update(updates)
    return record
