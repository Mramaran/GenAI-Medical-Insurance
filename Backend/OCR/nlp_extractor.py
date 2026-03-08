"""
NLP field extraction using spaCy NER and Ollama (mistral) LLM.
Two-stage approach:
  1. spaCy extracts entities: PERSON, ORG, DATE, MONEY, GPE
  2. Ollama mistral extracts full structured fields from raw text
"""

import json
import re
from typing import Optional

import spacy
from langchain_core.messages import HumanMessage, SystemMessage

from config import LLM_MODEL, LLM_TEMPERATURE, SPACY_MODEL, USE_GEMINI, GEMINI_API_KEY, GEMINI_MODEL
from models import (
    ExtractedClaim,
    PatientInfo,
    HospitalInfo,
    DiagnosisInfo,
    TreatmentInfo,
    BillingInfo,
    DateInfo,
    ItemizedCharge,
    DocumentType,
)


# --- Module-level singleton ---
_nlp_model = None


def _load_spacy_model():
    """Load spaCy model with singleton caching."""
    global _nlp_model
    if _nlp_model is None:
        _nlp_model = spacy.load(SPACY_MODEL)
    return _nlp_model


# --- Stage 1: spaCy NER ---

def extract_entities_spacy(text: str) -> dict:
    """Extract named entities from OCR text using spaCy.

    Args:
        text: Raw OCR text.

    Returns:
        Dict with keys: persons, organizations, dates, amounts, locations.
    """
    nlp = _load_spacy_model()
    doc = nlp(text[:100000])

    entities = {
        "persons": [],
        "organizations": [],
        "dates": [],
        "amounts": [],
        "locations": [],
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["persons"].append(ent.text)
        elif ent.label_ == "ORG":
            entities["organizations"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["amounts"].append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            entities["locations"].append(ent.text)

    # Deduplicate while preserving order
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))

    return entities


def extract_icd_codes(text: str) -> list[str]:
    """Extract ICD-10 codes using regex pattern matching.

    Args:
        text: Raw OCR text.

    Returns:
        List of ICD-10 code strings (e.g., ['E11.9', 'I10']).
    """
    pattern = r"\b[A-Z]\d{2}(?:\.\d{1,2})?\b"
    codes = re.findall(pattern, text)
    return list(dict.fromkeys(codes))


# --- Stage 2: Ollama LLM Structured Extraction ---

EXTRACTION_SYSTEM_PROMPT = """You are a medical document data extractor for an Indian health insurance system.
You will receive raw OCR text from hospital discharge summaries and bills.
Extract structured fields and return ONLY valid JSON. If a field cannot be found, use null.

Return this exact JSON structure:
{
  "document_type": "discharge_summary or hospital_bill or prescription or lab_report or unknown",
  "patient_name": "string or null",
  "patient_age": "string or null",
  "patient_gender": "string or null",
  "policy_number": "string or null",
  "hospital_name": "string or null",
  "hospital_address": "string or null",
  "doctor_name": "string or null",
  "primary_diagnosis": "string or null",
  "secondary_diagnoses": ["list of strings"],
  "procedures": ["list of strings"],
  "medications": ["list of strings"],
  "admission_type": "inpatient or outpatient or daycare or null",
  "admission_date": "YYYY-MM-DD or null",
  "discharge_date": "YYYY-MM-DD or null",
  "bill_date": "YYYY-MM-DD or null",
  "total_amount": "number or null",
  "itemized_charges": [{"description": "string", "amount": "number", "category": "room or surgery or medication or consultation or lab or misc"}],
  "payment_mode": "string or null"
}

Rules:
- Extract amounts as numbers without currency symbols (e.g., 15000 not Rs.15,000)
- Convert dates to YYYY-MM-DD format when possible
- For Indian hospital documents, look for MRD No, UHID, IP No as identifiers
- If the text mentions Rs, INR, or rupee symbols, those are amounts in Indian Rupees
- Be precise: only extract what is explicitly stated in the text"""


def _get_gemini_llm():
    """Get Gemini LLM instance."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=LLM_TEMPERATURE,
    )


def _get_ollama_llm():
    """Get Ollama LLM instance."""
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        format="json",
    )


def _get_extraction_llm():
    """Get the LLM for structured extraction — Gemini or Ollama based on config."""
    if USE_GEMINI and GEMINI_API_KEY:
        return _get_gemini_llm(), True  # (llm, is_gemini)
    else:
        return _get_ollama_llm(), False


def _parse_llm_json(content: str) -> dict:
    """Parse JSON from LLM response, handling markdown wrapping."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: try to find JSON in the response (common with Gemini wrapping in ```json)
        cleaned = re.sub(r"```json\s*", "", content)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    return {}
            return {}


def extract_fields_llm(raw_text: str, spacy_entities: dict) -> dict:
    """Use LLM (Gemini or Ollama) to extract structured fields from OCR text.
    If Gemini fails (rate limit, quota, etc.), automatically falls back to Ollama.

    Args:
        raw_text: The raw OCR text from the document.
        spacy_entities: Pre-extracted spaCy entities as hints.

    Returns:
        Dict with extracted fields matching the JSON schema.
    """
    llm, is_gemini = _get_extraction_llm()

    human_content = f"""Extract structured fields from this hospital document text.

spaCy pre-extracted entities (use as hints):
- Persons: {spacy_entities.get('persons', [])}
- Organizations: {spacy_entities.get('organizations', [])}
- Dates: {spacy_entities.get('dates', [])}
- Amounts: {spacy_entities.get('amounts', [])}
- Locations: {spacy_entities.get('locations', [])}

--- DOCUMENT TEXT START ---
{raw_text[:8000]}
--- DOCUMENT TEXT END ---"""

    # For Gemini, append "respond ONLY with JSON" to reinforce structured output
    prompt_suffix = "\n\nIMPORTANT: Respond with ONLY the JSON object, no markdown, no explanation." if is_gemini else ""

    messages = [
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT + prompt_suffix),
        HumanMessage(content=human_content),
    ]

    # Try primary LLM, fall back to Ollama if Gemini fails
    try:
        response = llm.invoke(messages)
        return _parse_llm_json(response.content)
    except Exception as e:
        if is_gemini:
            print(f"[NLP] Gemini failed ({e}), falling back to Ollama...")
            try:
                fallback_llm = _get_ollama_llm()
                response = fallback_llm.invoke(messages)
                return _parse_llm_json(response.content)
            except Exception as e2:
                print(f"[NLP] Ollama fallback also failed: {e2}")
                return {}
        else:
            raise


# --- Build Pydantic Model from Extractions ---

def _build_extracted_claim(
    llm_fields: dict,
    spacy_entities: dict,
    icd_codes: list[str],
    raw_text: str,
) -> ExtractedClaim:
    """Construct an ExtractedClaim from LLM output + spaCy entities."""
    patient = PatientInfo(
        name=llm_fields.get("patient_name"),
        age=llm_fields.get("patient_age"),
        gender=llm_fields.get("patient_gender"),
        policy_number=llm_fields.get("policy_number"),
    )

    hospital = HospitalInfo(
        name=llm_fields.get("hospital_name"),
        address=llm_fields.get("hospital_address"),
        doctor_name=llm_fields.get("doctor_name"),
    )

    # Merge LLM ICD codes with regex-extracted ones
    llm_icd = llm_fields.get("icd_codes", []) or []
    all_icd = list(dict.fromkeys(icd_codes + llm_icd))

    diagnosis = DiagnosisInfo(
        primary_diagnosis=llm_fields.get("primary_diagnosis"),
        secondary_diagnoses=llm_fields.get("secondary_diagnoses", []) or [],
        icd_codes=all_icd,
    )

    treatment = TreatmentInfo(
        procedures=llm_fields.get("procedures", []) or [],
        medications=llm_fields.get("medications", []) or [],
        admission_type=llm_fields.get("admission_type"),
    )

    # Build itemized charges
    raw_charges = llm_fields.get("itemized_charges", []) or []
    itemized = []
    for charge in raw_charges:
        if isinstance(charge, dict) and "description" in charge and "amount" in charge:
            try:
                itemized.append(ItemizedCharge(
                    description=charge["description"],
                    amount=float(charge["amount"]),
                    category=charge.get("category"),
                ))
            except (ValueError, TypeError):
                continue

    billing = BillingInfo(
        total_amount=_safe_float(llm_fields.get("total_amount")),
        itemized_charges=itemized,
        payment_mode=llm_fields.get("payment_mode"),
    )

    dates = DateInfo(
        admission_date=llm_fields.get("admission_date"),
        discharge_date=llm_fields.get("discharge_date"),
        bill_date=llm_fields.get("bill_date"),
    )

    # Determine document type
    doc_type_str = llm_fields.get("document_type", "unknown")
    try:
        doc_type = DocumentType(doc_type_str)
    except ValueError:
        doc_type = DocumentType.UNKNOWN

    # Compute missing fields and confidence
    missing = _compute_missing_fields(patient, hospital, diagnosis, treatment, billing, dates)
    total_fields = 11
    filled_fields = total_fields - len(missing)
    confidence = round(filled_fields / total_fields, 2)

    return ExtractedClaim(
        patient=patient,
        hospital=hospital,
        diagnosis=diagnosis,
        treatment=treatment,
        billing=billing,
        dates=dates,
        document_type=doc_type,
        raw_text=raw_text,
        confidence_score=confidence,
        missing_fields=missing,
    )


def _safe_float(value) -> Optional[float]:
    """Safely convert a value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _compute_missing_fields(
    patient: PatientInfo,
    hospital: HospitalInfo,
    diagnosis: DiagnosisInfo,
    treatment: TreatmentInfo,
    billing: BillingInfo,
    dates: DateInfo,
) -> list[str]:
    """Identify which important fields could not be extracted."""
    missing = []
    if not patient.name:
        missing.append("patient_name")
    if not patient.policy_number:
        missing.append("policy_number")
    if not hospital.name:
        missing.append("hospital_name")
    if not hospital.doctor_name:
        missing.append("doctor_name")
    if not diagnosis.primary_diagnosis:
        missing.append("primary_diagnosis")
    if not treatment.procedures:
        missing.append("procedures")
    if not treatment.admission_type:
        missing.append("admission_type")
    if billing.total_amount is None:
        missing.append("total_amount")
    if not dates.admission_date:
        missing.append("admission_date")
    if not dates.discharge_date:
        missing.append("discharge_date")
    if not dates.bill_date:
        missing.append("bill_date")
    return missing


# --- Main Export Function ---

def extract_structured_fields(raw_text: str) -> ExtractedClaim:
    """Main NLP extraction: runs spaCy NER + Ollama LLM extraction.

    Args:
        raw_text: Raw text from OCR engine.

    Returns:
        ExtractedClaim with all structured fields populated.
    """
    # Stage 1: spaCy NER
    spacy_entities = extract_entities_spacy(raw_text)
    icd_codes = extract_icd_codes(raw_text)

    # Stage 2: Ollama LLM structured extraction
    llm_fields = extract_fields_llm(raw_text, spacy_entities)

    # Build final model
    claim = _build_extracted_claim(llm_fields, spacy_entities, icd_codes, raw_text)
    return claim
