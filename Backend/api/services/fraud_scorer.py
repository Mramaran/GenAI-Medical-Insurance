"""
Rule-based fraud risk scoring for insurance claims.
Rules derived from HealthShield Plus policy (HSP-2025-TN-001).
Returns a 0-100 score with flagged rules and risk level.
"""

from datetime import datetime

# ── Date parsing helper ──────────────────────────────────────────────────
_DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d-%b-%Y"]


def _parse_date(date_str: str):
    """Try multiple date formats and return a datetime or None."""
    if not date_str:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


# ── Policy exclusions (from coverage_details.md §7.1) ────────────────────
_EXCLUDED_KEYWORDS = [
    # Cosmetic / aesthetic
    "cosmetic", "plastic surgery", "rhinoplasty", "liposuction",
    "botox", "breast augmentation", "hair transplant", "aesthetic",
    # Weight management
    "weight management", "obesity surgery", "bariatric",
    # Infertility / assisted reproduction
    "fertility", "ivf", "iui", "assisted reproduction", "infertility",
    # Dental (non-hospitalization)
    "dental implant", "dental filling", "dental crown", "orthodontic",
    # Substance abuse
    "alcohol abuse", "drug abuse", "substance abuse", "de-addiction",
    # Self-inflicted
    "self-inflicted", "attempted suicide",
    # Vision / hearing aids
    "spectacles", "contact lens", "hearing aid",
    # Experimental
    "experimental", "unproven treatment",
]

# ── Day care procedures (from coverage_details.md §3) ────────────────────
# These are legitimately < 24 hours and should NOT trigger the short-stay rule
_DAY_CARE_PROCEDURES = [
    "cataract", "dialysis", "chemotherapy", "radiotherapy",
    "tonsillectomy", "lithotripsy", "arthroscopy", "angioplasty",
    "angiography", "endoscop", "stent", "pci",
    "dental surgery", "biopsy", "colonoscopy", "gastroscopy",
]

# Maximum sum insured across all tiers (Diamond = Rs.25,00,000)
_MAX_SUM_INSURED = 2500000


def _is_day_care(procedures: list[str], diagnosis: str) -> bool:
    """Check if the claim involves a known day care procedure."""
    all_text = " ".join(procedures).lower() + " " + diagnosis.lower()
    return any(dc in all_text for dc in _DAY_CARE_PROCEDURES)


def score_claim(extracted_data: dict) -> dict:
    """
    Score a claim for fraud risk based on extracted data and policy rules.

    Args:
        extracted_data: The ExtractedClaim dict from OCR pipeline.

    Returns:
        {
            "score": int (0-100),
            "level": "low" | "medium" | "high",
            "flags": list[str]
        }
    """
    score = 0
    flags = []

    billing = extracted_data.get("billing", {})
    dates = extracted_data.get("dates", {})
    diagnosis = extracted_data.get("diagnosis", {})
    treatment = extracted_data.get("treatment", {})
    missing = extracted_data.get("missing_fields", [])

    total_amount = billing.get("total_amount")
    primary = (diagnosis.get("primary_diagnosis") or "").lower()
    procedures = treatment.get("procedures") or []
    admission_date = dates.get("admission_date")
    discharge_date = dates.get("discharge_date")

    # ── Rule 1: Excluded diagnosis (+20) ─────────────────────────────────
    # Check against policy exclusions (§7.1 Permanent Exclusions)
    for keyword in _EXCLUDED_KEYWORDS:
        if keyword in primary:
            score += 20
            flags.append(
                f"Policy exclusion detected: '{diagnosis.get('primary_diagnosis')}' "
                f"matches excluded category '{keyword}'"
            )
            break

    # ── Rule 2: Bill exceeds maximum sum insured (+25) ───────────────────
    # No tier can exceed Rs.25,00,000 (Diamond)
    if total_amount is not None:
        try:
            amount = float(total_amount)
            if amount > _MAX_SUM_INSURED:
                score += 25
                flags.append(
                    f"Bill Rs.{amount:,.0f} exceeds maximum sum insured "
                    f"Rs.{_MAX_SUM_INSURED:,.0f} (Diamond tier)"
                )
        except (ValueError, TypeError):
            pass

    # ── Rule 3: Short stay + high bill, day care aware (+25) ─────────────
    # Flag < 24hr stays with bill > Rs.2L, unless it's a day care procedure
    admit_dt = _parse_date(admission_date)
    disc_dt = _parse_date(discharge_date)

    if admit_dt and disc_dt and total_amount is not None:
        try:
            stay_hours = (disc_dt - admit_dt).total_seconds() / 3600
            amount = float(total_amount)
            if 0 <= stay_hours < 24 and amount > 200000:
                if not _is_day_care(procedures, primary):
                    score += 25
                    flags.append(
                        f"Short stay ({stay_hours:.0f}hrs) with high bill "
                        f"(Rs.{amount:,.0f}) — not a day care procedure"
                    )
        except (ValueError, TypeError):
            pass

    # ── Rule 4: Late claim filing (+15) ──────────────────────────────────
    # Policy requires claims within 15 days of discharge (§3.1)
    if disc_dt:
        days_since_discharge = (datetime.now() - disc_dt).days
        if days_since_discharge > 15:
            score += 15
            flags.append(
                f"Late filing: {days_since_discharge} days since discharge "
                f"(policy deadline: 15 days)"
            )

    # ── Rule 5: Round bill amount (+5) ───────────────────────────────────
    if total_amount is not None:
        try:
            amount = float(total_amount)
            if amount >= 10000 and amount % 10000 == 0:
                score += 5
                flags.append(f"Perfectly round bill amount: Rs.{amount:,.0f}")
        except (ValueError, TypeError):
            pass

    # ── Rule 6: Single itemized charge > 50% of total (+10) ─────────────
    itemized = billing.get("itemized_charges") or []
    if total_amount is not None and itemized:
        try:
            total = float(total_amount)
            if total > 0:
                for charge in itemized:
                    if isinstance(charge, dict):
                        charge_amt = float(charge.get("amount", 0))
                        if charge_amt > total * 0.5:
                            score += 10
                            flags.append(
                                f"Single charge '{charge.get('description', 'unknown')}' "
                                f"(Rs.{charge_amt:,.0f}) is "
                                f"{charge_amt / total * 100:.0f}% of total bill"
                            )
                            break
        except (ValueError, TypeError):
            pass

    # ── Rule 7: Too many missing fields (+15) ────────────────────────────
    # Many missing fields suggest fabricated or incomplete documents
    if isinstance(missing, list) and len(missing) > 3:
        score += 15
        flags.append(f"Missing {len(missing)} fields: {', '.join(missing[:5])}")

    # ── Final scoring ────────────────────────────────────────────────────
    score = min(score, 100)

    if score <= 25:
        level = "low"
    elif score <= 50:
        level = "medium"
    else:
        level = "high"

    return {
        "score": score,
        "level": level,
        "flags": flags,
    }
