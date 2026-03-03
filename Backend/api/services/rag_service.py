"""Wrapper around the existing RAG agent for policy coverage checks."""

import sys
import os

# Add RAG module to path - force it to be at position 0 to avoid config conflicts
_rag_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "RAG"))
# Remove if already present to re-insert at position 0
if _rag_dir in sys.path:
    sys.path.remove(_rag_dir)
sys.path.insert(0, _rag_dir)

from agent import query_agent


def check_coverage(extracted_data: dict) -> dict:
    """
    Build a natural-language query from extracted claim data and run it
    through the RAG agent to get a coverage verdict.

    Args:
        extracted_data: Dict from ExtractedClaim.model_dump()

    Returns:
        dict with verdict_text and query_used keys.
    """
    # Pull fields safely with defaults
    patient = extracted_data.get("patient") or {}
    hospital = extracted_data.get("hospital") or {}
    diagnosis = extracted_data.get("diagnosis") or {}
    treatment = extracted_data.get("treatment") or {}
    billing = extracted_data.get("billing") or {}

    name = patient.get("name", "Unknown")
    policy_number = patient.get("policy_number", "Unknown")
    procedures = ", ".join(treatment.get("procedures") or ["Unknown"])
    admission_type = treatment.get("admission_type", "Unknown")
    primary_diagnosis = diagnosis.get("primary_diagnosis", "Unknown")
    total_amount = billing.get("total_amount", "Unknown")
    hospital_name = hospital.get("name", "Unknown")

    query = (
        f"Patient: {name}, Policy: {policy_number}. "
        f"Procedure: {procedures}, Admission: {admission_type}. "
        f"Diagnosis: {primary_diagnosis}. "
        f"Total bill: Rs {total_amount}. Hospital: {hospital_name}. "
        f"Is this covered under the policy? What are the applicable sub-limits, "
        f"co-pay percentage, waiting periods, and estimated payable amount?"
    )

    verdict_text = query_agent(query)

    return {
        "verdict_text": verdict_text,
        "query_used": query,
    }
