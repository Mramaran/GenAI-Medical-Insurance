"""Claim endpoints: analyze, get, list."""

import os
import re
import tempfile
import shutil
import traceback

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.ocr_service import run_ocr
from services.rag_service import check_coverage
from services.blockchain import submit_claim_meta, get_claim_events
from services.fraud_scorer import score_claim

from utils.hashing import hash_file, hash_string, compute_merkle_root
from utils.store import generate_claim_id, save_claim, get_claim, get_all_claims, find_claim_by_doc_hash

router = APIRouter(prefix="/api/claims", tags=["claims"])


def _compute_field_confidence(extracted_data: dict) -> dict:
    """Compute per-field confidence indicators based on extraction results."""
    missing = extracted_data.get("missing_fields", [])
    overall = extracted_data.get("confidence_score", 0.5)

    fields = {
        "patient_name": "patient.name",
        "patient_age": "patient.age",
        "patient_gender": "patient.gender",
        "policy_number": "patient.policy_number",
        "hospital_name": "hospital.name",
        "primary_diagnosis": "diagnosis.primary_diagnosis",
        "procedures": "treatment.procedures",
        "admission_type": "treatment.admission_type",
        "total_amount": "billing.total_amount",
        "admission_date": "dates.admission_date",
        "discharge_date": "dates.discharge_date",
    }

    confidence = {}
    for field_key, path in fields.items():
        parts = path.split(".")
        val = extracted_data
        for p in parts:
            val = val.get(p, None) if isinstance(val, dict) else None
            if val is None:
                break

        if field_key in missing or val is None or val == "" or val == []:
            confidence[field_key] = "low"
        elif overall >= 0.7:
            confidence[field_key] = "high"
        else:
            confidence[field_key] = "medium"

    return confidence


@router.post("/analyze")
async def analyze_claim(
    files: list[UploadFile] = File(...),
    policy_number: str = Form(...),
):
    """
    Upload medical documents + policy number.
    Runs: OCR -> RAG -> Hash -> Blockchain.
    Returns structured claim data with on-chain proof.
    Gracefully degrades: if blockchain fails, OCR + RAG results are still returned.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Validate policy number format (e.g. HSP-2025-TN-001)
    if not policy_number or not policy_number.strip():
        raise HTTPException(status_code=400, detail="Policy number is required")

    policy_number = policy_number.strip()
    if not re.match(r"^HSP-\d{4}-[A-Z]{2}-\d{3}$", policy_number):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid policy number format '{policy_number}'. Expected format: HSP-YYYY-XX-NNN (e.g. HSP-2025-TN-001)",
        )

    # Save uploaded files to a temp directory
    tmp_dir = tempfile.mkdtemp(prefix="claimchain_")
    saved_paths: list[str] = []
    warnings: list[str] = []

    try:
        for f in files:
            # Sanitize filename to prevent path traversal attacks
            safe_name = os.path.basename(f.filename) if f.filename else "unnamed_file"
            dest = os.path.join(tmp_dir, safe_name)
            with open(dest, "wb") as buf:
                content = await f.read()
                buf.write(content)
            saved_paths.append(dest)

        # ── Step 1: OCR extraction ──────────────────────────────────
        try:
            extracted_data = run_ocr(saved_paths, policy_number)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"OCR extraction failed: {e}. Check that Tesseract is installed and spaCy model is loaded.",
            )

        # ── Step 1b: Validate required fields before proceeding ─────
        _REQUIRED_FIELDS = {
            "total_amount": ("billing", "total_amount"),
            "admission_date": ("dates", "admission_date"),
            "discharge_date": ("dates", "discharge_date"),
            "patient_name": ("patient", "name"),
            "primary_diagnosis": ("diagnosis", "primary_diagnosis"),
        }
        missing_required = []
        for label, (section, field) in _REQUIRED_FIELDS.items():
            val = extracted_data.get(section, {}).get(field)
            if val is None or val == "" or val == "null":
                missing_required.append(label)

        if missing_required:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Claim rejected: the uploaded document is missing required fields — "
                    f"{', '.join(missing_required)}. "
                    f"Please upload a complete hospital bill or discharge summary."
                ),
            )

        # ── Step 1c: Compute field confidence indicators ──────────
        field_confidence = _compute_field_confidence(extracted_data)

        # ── Step 1d: Fraud risk scoring ─────────────────────────────
        try:
            fraud_risk = score_claim(extracted_data)
        except Exception:
            fraud_risk = {"score": 0, "level": "low", "flags": []}

        # ── Step 2: RAG coverage check ──────────────────────────────
        try:
            verdict = check_coverage(extracted_data)
        except Exception as e:
            warnings.append(f"RAG coverage check failed: {e}")
            verdict = {
                "verdict_text": "Coverage check unavailable — the RAG agent could not be reached. Ensure Ollama is running.",
                "query_used": "N/A",
            }

        # ── Step 3: Hash documents + verdict ────────────────────────
        doc_hashes = [hash_file(p) for p in saved_paths]

        # ── Step 3b: Check for duplicate documents ───────────────────
        # Allow re-submission only if the previous claim was rejected
        existing = find_claim_by_doc_hash(doc_hashes)
        if existing and existing.get("status") != "rejected":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"This document has already been submitted under claim "
                    f"{existing['claim_id']} (status: {existing.get('status', 'unknown')}). "
                    f"Duplicate claims are not allowed."
                ),
            )

        verdict_hash = hash_string(verdict.get("verdict_text", ""))
        all_hashes = doc_hashes + [verdict_hash]
        merkle_root = compute_merkle_root(all_hashes)

        # ── Step 4: Submit to blockchain (graceful degradation) ─────
        claim_id = generate_claim_id()
        chain_result = submit_claim_meta(claim_id, merkle_root)

        if chain_result.get("error"):
            warnings.append(f"Blockchain: {chain_result['error']}")

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
            "field_confidence": field_confidence,
            "fraud_risk": fraud_risk,
            "merkle_root": merkle_root,
            "tx_hash": chain_result.get("tx_hash"),
            "document_hashes": doc_hashes,
            "verdict_hash": verdict_hash,
            "blockchain_proof": blockchain_proof,
        }
        save_claim(claim_id, claim_record)

        response = {
            "claim_id": claim_id,
            "extracted_data": extracted_data,
            "verdict": verdict,
            "field_confidence": field_confidence,
            "fraud_risk": fraud_risk,
            "blockchain_proof": blockchain_proof,
            "status": "submitted",
        }
        if warnings:
            response["warnings"] = warnings
        return response

    except HTTPException:
        raise  # Re-raise HTTP errors as-is
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=f"File processing error: {e}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.get("/{claim_id}")
async def get_claim_by_id(claim_id: str):
    """Get full claim data by ID, including on-chain events."""
    record = get_claim(claim_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Return a copy with fresh on-chain events to avoid mutating stored data
    result = {**record, "events": get_claim_events(claim_id)}
    return result


@router.get("/")
async def list_claims():
    """List all claims (for insurer dashboard)."""
    return get_all_claims()
