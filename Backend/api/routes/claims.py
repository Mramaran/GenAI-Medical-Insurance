"""Claim endpoints: analyze, get, list."""

import os
import tempfile
import shutil

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.ocr_service import run_ocr
from services.rag_service import check_coverage
from services.blockchain import submit_claim_meta, get_claim_events
from utils.hashing import hash_file, hash_string, compute_merkle_root
from utils.store import generate_claim_id, save_claim, get_claim, get_all_claims

router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post("/analyze")
async def analyze_claim(
    files: list[UploadFile] = File(...),
    policy_number: str = Form(...),
):
    """
    Upload medical documents + policy number.
    Runs: OCR -> RAG -> Hash -> Blockchain.
    Returns structured claim data with on-chain proof.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Save uploaded files to a temp directory
    tmp_dir = tempfile.mkdtemp(prefix="claimchain_")
    saved_paths: list[str] = []

    try:
        for f in files:
            dest = os.path.join(tmp_dir, f.filename)
            with open(dest, "wb") as buf:
                content = await f.read()
                buf.write(content)
            saved_paths.append(dest)

        # ── Step 1: OCR extraction ──────────────────────────────────
        extracted_data = run_ocr(saved_paths, policy_number)

        # ── Step 2: RAG coverage check ──────────────────────────────
        verdict = check_coverage(extracted_data)

        # ── Step 3: Hash documents + verdict ────────────────────────
        doc_hashes = [hash_file(p) for p in saved_paths]
        verdict_hash = hash_string(verdict.get("verdict_text", ""))
        all_hashes = doc_hashes + [verdict_hash]
        merkle_root = compute_merkle_root(all_hashes)

        # ── Step 4: Submit to blockchain ────────────────────────────
        claim_id = generate_claim_id()
        chain_result = submit_claim_meta(claim_id, merkle_root)

        blockchain_proof = {
            "merkle_root": merkle_root,
            "tx_hash": chain_result.get("tx_hash"),
            "block_number": chain_result.get("block_number"),
            "gas_used": chain_result.get("gas_used"),
            "error": chain_result.get("error"),
        }

        # ── Step 5: Store ───────────────────────────────────────────
        claim_record = {
            "extracted_data": extracted_data,
            "verdict": verdict,
            "merkle_root": merkle_root,
            "tx_hash": chain_result.get("tx_hash"),
            "document_hashes": doc_hashes,
            "verdict_hash": verdict_hash,
            "blockchain_proof": blockchain_proof,
        }
        save_claim(claim_id, claim_record)

        return {
            "claim_id": claim_id,
            "extracted_data": extracted_data,
            "verdict": verdict,
            "blockchain_proof": blockchain_proof,
            "status": "submitted",
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=f"File processing error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Extraction error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.get("/{claim_id}")
async def get_claim_by_id(claim_id: str):
    """Get full claim data by ID, including on-chain events."""
    record = get_claim(claim_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Fetch on-chain events for this claim
    record["events"] = get_claim_events(claim_id)
    return record


@router.get("/")
async def list_claims():
    """List all claims (for insurer dashboard)."""
    return get_all_claims()
