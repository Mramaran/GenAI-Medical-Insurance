"""
Pydantic data models for structured medical document extraction.
These models define the contract between the OCR module and all consumers.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    DISCHARGE_SUMMARY = "discharge_summary"
    HOSPITAL_BILL = "hospital_bill"
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    UNKNOWN = "unknown"


class ItemizedCharge(BaseModel):
    description: str = Field(..., description="Line item description")
    amount: float = Field(..., description="Charge amount in INR")
    category: Optional[str] = Field(
        None,
        description="Category: room, surgery, medication, consultation, lab, misc",
    )


class PatientInfo(BaseModel):
    name: Optional[str] = Field(None, description="Patient full name")
    age: Optional[str] = Field(None, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")
    policy_number: Optional[str] = Field(None, description="Insurance policy number")


class HospitalInfo(BaseModel):
    name: Optional[str] = Field(None, description="Hospital or facility name")
    address: Optional[str] = Field(None, description="Hospital address")
    doctor_name: Optional[str] = Field(None, description="Attending doctor name")


class DiagnosisInfo(BaseModel):
    primary_diagnosis: Optional[str] = Field(None, description="Primary diagnosis")
    secondary_diagnoses: list[str] = Field(
        default_factory=list, description="Secondary diagnoses"
    )
    icd_codes: list[str] = Field(
        default_factory=list, description="ICD-10 codes if present"
    )


class TreatmentInfo(BaseModel):
    procedures: list[str] = Field(
        default_factory=list, description="Procedures performed"
    )
    medications: list[str] = Field(
        default_factory=list, description="Medications prescribed"
    )
    admission_type: Optional[str] = Field(
        None, description="inpatient, outpatient, or daycare"
    )


class BillingInfo(BaseModel):
    total_amount: Optional[float] = Field(None, description="Total bill amount in INR")
    itemized_charges: list[ItemizedCharge] = Field(
        default_factory=list, description="Itemized breakdown"
    )
    payment_mode: Optional[str] = Field(
        None, description="cash, card, insurance, cashless"
    )


class DateInfo(BaseModel):
    admission_date: Optional[str] = Field(None, description="Admission date (YYYY-MM-DD)")
    discharge_date: Optional[str] = Field(None, description="Discharge date (YYYY-MM-DD)")
    bill_date: Optional[str] = Field(None, description="Bill date (YYYY-MM-DD)")


class ExtractedClaim(BaseModel):
    """Complete structured extraction from a medical document."""

    patient: PatientInfo = Field(default_factory=PatientInfo)
    hospital: HospitalInfo = Field(default_factory=HospitalInfo)
    diagnosis: DiagnosisInfo = Field(default_factory=DiagnosisInfo)
    treatment: TreatmentInfo = Field(default_factory=TreatmentInfo)
    billing: BillingInfo = Field(default_factory=BillingInfo)
    dates: DateInfo = Field(default_factory=DateInfo)
    document_type: DocumentType = Field(default=DocumentType.UNKNOWN)
    raw_text: str = Field(default="", description="Original OCR text")
    extraction_method: str = Field(
        default="unknown",
        description="How text was extracted: ocr_image, ocr_scanned_pdf, digital_pdf",
    )
    confidence_score: float = Field(
        default=0.0,
        description="0.0-1.0 confidence in extraction quality",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Fields that could not be extracted",
    )
