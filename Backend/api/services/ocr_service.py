"""Wrapper around the existing OCR pipeline."""

import sys
import os

# Add OCR module to path
_ocr_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "OCR"))
# Remove if already present to re-insert at position 0
if _ocr_dir in sys.path:
    sys.path.remove(_ocr_dir)
sys.path.insert(0, _ocr_dir)

from pipeline import process_document, process_multiple_documents


def run_ocr(file_paths: list[str], policy_number: str) -> dict:
    """
    Run the OCR pipeline on uploaded files.

    Args:
        file_paths: List of absolute paths to uploaded files.
        policy_number: The patient's policy number.

    Returns:
        dict: Extracted claim data from the OCR pipeline (model_dump of ExtractedClaim).
    """
    if len(file_paths) == 1:
        claim = process_document(file_paths[0], policy_number=policy_number)
    else:
        claim = process_multiple_documents(file_paths, policy_number=policy_number)

    return claim.model_dump()
