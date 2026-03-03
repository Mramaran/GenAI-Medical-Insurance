"""Insurer review endpoints: approve, reject, query."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.blockchain import update_claim_status
from utils.hashing import hash_string
from utils.store import get_claim, update_claim

router = APIRouter(prefix="/api/claims", tags=["review"])

# Status mapping: action string -> contract enum int
_ACTION_MAP = {
    "approve": 2,    # ClaimStatus.Approved
    "reject": 3,     # ClaimStatus.Rejected
    "query": 4,      # ClaimStatus.QueryRaised
    "under_review": 1,  # ClaimStatus.UnderReview
    "settle": 5,     # ClaimStatus.Settled
}


class ReviewRequest(BaseModel):
    action: str       # "approve", "reject", "query"
    reason: str = ""  # Required for reject/query, optional for approve


@router.post("/{claim_id}/review")
async def review_claim(claim_id: str, body: ReviewRequest):
    """
    Insurer approve/reject/query a claim.
    Writes the decision on-chain via updateStatus().
    """
    # Validate claim exists
    record = get_claim(claim_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Validate action
    action = body.action.lower()
    if action not in _ACTION_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{body.action}'. Must be one of: {', '.join(_ACTION_MAP.keys())}",
        )

    # Reject and query require a reason
    if action in ("reject", "query") and not body.reason.strip():
        raise HTTPException(
            status_code=400,
            detail=f"A reason is required when action is '{action}'",
        )

    status_int = _ACTION_MAP[action]
    reason_hash = hash_string(body.reason) if body.reason else hash_string("")

    # Write to blockchain
    chain_result = update_claim_status(claim_id, status_int, reason_hash)

    # Update in-memory store
    new_status = action if action != "under_review" else "under_review"
    if action == "approve":
        new_status = "approved"
    elif action == "reject":
        new_status = "rejected"
    elif action == "query":
        new_status = "query_raised"
    elif action == "settle":
        new_status = "settled"

    update_claim(claim_id, {
        "status": new_status,
        "review_reason": body.reason,
        "review_reason_hash": reason_hash,
        "review_tx_hash": chain_result.get("tx_hash"),
    })

    return {
        "claim_id": claim_id,
        "new_status": new_status,
        "reason_hash": reason_hash,
        "tx_hash": chain_result.get("tx_hash"),
        "block_number": chain_result.get("block_number"),
        "blockchain_error": chain_result.get("error"),
    }
