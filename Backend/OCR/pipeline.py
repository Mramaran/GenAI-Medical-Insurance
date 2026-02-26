"""
Main OCR+NLP pipeline orchestrator.
Exports clean functions for integration with API server and RAG module.
"""

from pathlib import Path

from models import ExtractedClaim
from ocr_engine import extract_text
from nlp_extractor import extract_structured_fields, _compute_missing_fields


def process_document(file_path: str, policy_number: str = None) -> ExtractedClaim:
    """Process a single uploaded document through OCR + NLP pipeline.

    This is the primary integration function. Call this from an API server.

    Args:
        file_path: Path to the uploaded document (image or PDF).
        policy_number: Optional policy number (from form input).

    Returns:
        ExtractedClaim with all structured fields.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If file type is unsupported.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    # Step 1: OCR - extract raw text
    raw_text, extraction_method = extract_text(file_path)

    if not raw_text.strip():
        return ExtractedClaim(
            raw_text="",
            extraction_method=extraction_method,
            confidence_score=0.0,
            missing_fields=["all_fields_empty_ocr"],
        )

    # Step 2: NLP - extract structured fields
    claim = extract_structured_fields(raw_text)

    # Set metadata
    claim.extraction_method = extraction_method
    claim.raw_text = raw_text

    # Override policy number if provided externally
    if policy_number and not claim.patient.policy_number:
        claim.patient.policy_number = policy_number

    return claim


def process_multiple_documents(
    file_paths: list[str],
    policy_number: str = None,
) -> ExtractedClaim:
    """Process multiple documents and merge into a single ExtractedClaim.

    Useful when hospital uploads both a discharge summary and a bill.
    Fields from later documents fill in gaps from earlier ones.

    Args:
        file_paths: List of paths to uploaded documents.
        policy_number: Optional policy number from form input.

    Returns:
        Merged ExtractedClaim combining all documents.
    """
    if not file_paths:
        raise ValueError("No file paths provided.")

    extractions = []
    for fp in file_paths:
        claim = process_document(fp, policy_number)
        extractions.append(claim)

    if len(extractions) == 1:
        return extractions[0]

    return _merge_extractions(extractions, policy_number)


def _merge_extractions(
    extractions: list[ExtractedClaim],
    policy_number: str = None,
) -> ExtractedClaim:
    """Merge multiple ExtractedClaim objects, filling gaps from each.

    Strategy: for each field, use the first non-null/non-empty value
    found across all extractions. Lists are concatenated and deduplicated.
    """
    merged = ExtractedClaim()

    for claim in extractions:
        # Patient info
        if not merged.patient.name and claim.patient.name:
            merged.patient.name = claim.patient.name
        if not merged.patient.age and claim.patient.age:
            merged.patient.age = claim.patient.age
        if not merged.patient.gender and claim.patient.gender:
            merged.patient.gender = claim.patient.gender
        if not merged.patient.policy_number and claim.patient.policy_number:
            merged.patient.policy_number = claim.patient.policy_number

        # Hospital info
        if not merged.hospital.name and claim.hospital.name:
            merged.hospital.name = claim.hospital.name
        if not merged.hospital.address and claim.hospital.address:
            merged.hospital.address = claim.hospital.address
        if not merged.hospital.doctor_name and claim.hospital.doctor_name:
            merged.hospital.doctor_name = claim.hospital.doctor_name

        # Diagnosis
        if not merged.diagnosis.primary_diagnosis and claim.diagnosis.primary_diagnosis:
            merged.diagnosis.primary_diagnosis = claim.diagnosis.primary_diagnosis
        merged.diagnosis.secondary_diagnoses = list(dict.fromkeys(
            merged.diagnosis.secondary_diagnoses + claim.diagnosis.secondary_diagnoses
        ))
        merged.diagnosis.icd_codes = list(dict.fromkeys(
            merged.diagnosis.icd_codes + claim.diagnosis.icd_codes
        ))

        # Treatment
        merged.treatment.procedures = list(dict.fromkeys(
            merged.treatment.procedures + claim.treatment.procedures
        ))
        merged.treatment.medications = list(dict.fromkeys(
            merged.treatment.medications + claim.treatment.medications
        ))
        if not merged.treatment.admission_type and claim.treatment.admission_type:
            merged.treatment.admission_type = claim.treatment.admission_type

        # Billing
        if not merged.billing.total_amount and claim.billing.total_amount:
            merged.billing.total_amount = claim.billing.total_amount
        if not merged.billing.itemized_charges and claim.billing.itemized_charges:
            merged.billing.itemized_charges = claim.billing.itemized_charges
        if not merged.billing.payment_mode and claim.billing.payment_mode:
            merged.billing.payment_mode = claim.billing.payment_mode

        # Dates
        if not merged.dates.admission_date and claim.dates.admission_date:
            merged.dates.admission_date = claim.dates.admission_date
        if not merged.dates.discharge_date and claim.dates.discharge_date:
            merged.dates.discharge_date = claim.dates.discharge_date
        if not merged.dates.bill_date and claim.dates.bill_date:
            merged.dates.bill_date = claim.dates.bill_date

    # Combine raw texts
    merged.raw_text = "\n\n=== NEXT DOCUMENT ===\n\n".join(
        c.raw_text for c in extractions if c.raw_text
    )
    merged.extraction_method = ", ".join(
        c.extraction_method for c in extractions
    )

    # Override policy number if provided
    if policy_number:
        merged.patient.policy_number = policy_number

    # Recompute confidence and missing fields
    merged.missing_fields = _compute_missing_fields(
        merged.patient, merged.hospital, merged.diagnosis,
        merged.treatment, merged.billing, merged.dates,
    )
    total_fields = 11
    filled = total_fields - len(merged.missing_fields)
    merged.confidence_score = round(filled / total_fields, 2)

    return merged
