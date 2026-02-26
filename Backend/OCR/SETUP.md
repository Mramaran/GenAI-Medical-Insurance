# Medical Document OCR+NLP Pipeline - Setup Guide

## Prerequisites

- Python 3.10 or higher
- Ollama installed and running with `mistral` model
- Tesseract OCR installed
- Poppler (for PDF to image conversion)

## System Dependencies

### 1. Tesseract OCR

**Windows:**
Download installer from https://github.com/UB-Mannheim/tesseract/wiki and install to `C:\Program Files\Tesseract-OCR\`. Make sure to check "Add to PATH" during installation.

**Linux (Ubuntu/Debian):**
```bash
sudo apt install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

### 2. Poppler (required for scanned PDF processing)

**Windows:**
1. Download from https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to a folder (e.g., `C:\poppler`)
3. Set environment variable: `POPPLER_PATH=C:\poppler\Library\bin`

**Linux (Ubuntu/Debian):**
```bash
sudo apt install poppler-utils
```

**Mac:**
```bash
brew install poppler
```

### 3. Ollama

Make sure Ollama is running with the `mistral` model:
```bash
ollama pull mistral
```

## Python Installation

### 1. Navigate to the OCR directory

```bash
cd "D:\Hackathons\TN IMPACT\GenAI Insurance V1\Backend\OCR"
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy language model

```bash
python -m spacy download en_core_web_sm
```

## Usage

### Getting Sample Medical Documents

**Quick Start:** Sample documents are already available in `test_docs/` folder!
- `sample_discharge_summary.txt` - Complete discharge summary
- `sample_hospital_bill.txt` - Itemized hospital bill
- `sample_prescription.txt` - Doctor's prescription

See [test_docs/QUICK_START.md](test_docs/QUICK_START.md) for usage examples.

For additional samples from open datasets:

1. **MIMIC-III Clinical Database** (requires registration): https://physionet.org/content/mimiciii/
2. **MTSamples** (free medical transcription samples): https://www.mtsamples.com/
3. **Kaggle Medical Datasets**: Search for "medical records" or "hospital discharge"
4. **Create mock documents**: Use templates with realistic (but fictional) patient data

Place additional test documents in the `test_docs/` folder:
```
test_docs/
├── sample_discharge_summary.txt    [✓ Provided]
├── sample_hospital_bill.txt        [✓ Provided]
├── sample_prescription.txt         [✓ Provided]
├── discharge_summary.pdf           [Your documents]
├── hospital_bill.jpg               [Your documents]
└── lab_report.pdf                  [Your documents]
```

### Process a single document

```bash
python main.py test_docs/DISCHARGE_SUMMARY.pdf --policy HSP-2025-TN-001
```

### Process multiple documents (merges results)

```bash
python main.py test_docs/DISCHARGE_SUMMARY.pdf test_docs/APOLLO_HOSPITALS.pdf --policy HSP-2025-TN-001
```

### Include raw OCR text in output

```bash
python main.py test_docs/DISCHARGE_SUMMARY.pdf --policy HSP-2025-TN-001 --raw
```

### Supported file types

- Images: JPG, JPEG, PNG, TIFF, TIF, BMP
- PDFs: Digital (text-based) and scanned

## Output

The pipeline outputs a structured JSON with:

```json
{
  "patient": { "name": "...", "age": "...", "gender": "...", "policy_number": "..." },
  "hospital": { "name": "...", "address": "...", "doctor_name": "..." },
  "diagnosis": { "primary_diagnosis": "...", "secondary_diagnoses": [...], "icd_codes": [...] },
  "treatment": { "procedures": [...], "medications": [...], "admission_type": "..." },
  "billing": { "total_amount": 0.0, "itemized_charges": [...], "payment_mode": "..." },
  "dates": { "admission_date": "...", "discharge_date": "...", "bill_date": "..." },
  "document_type": "discharge_summary",
  "extraction_method": "ocr_image",
  "confidence_score": 0.73,
  "missing_fields": ["policy_number", "bill_date"]
}
```

## Data Flow

```
Upload file(s) + policy_number
       |
       v
pipeline.process_document()
       |
       +---> ocr_engine.extract_text()
       |         |---> Image:       preprocess -> pytesseract
       |         |---> Digital PDF: PyMuPDF -> get_text()
       |         |---> Scanned PDF: pdf2image -> preprocess -> pytesseract
       |
       +---> nlp_extractor.extract_structured_fields()
       |         |---> Stage 1: spaCy NER (persons, orgs, dates, amounts)
       |         |---> Stage 2: Ollama mistral (structured JSON extraction)
       |
       v
ExtractedClaim (Pydantic JSON)
```

## File Structure

| File               | Purpose                                           |
|--------------------|---------------------------------------------------|
| `config.py`        | Tesseract/Poppler paths, Ollama model config      |
| `models.py`        | Pydantic data models (ExtractedClaim, etc.)       |
| `preprocessor.py`  | Image preprocessing for OCR quality               |
| `ocr_engine.py`    | Core OCR: auto-detect file type, extract text     |
| `nlp_extractor.py` | spaCy NER + Ollama LLM structured extraction      |
| `pipeline.py`      | Orchestrator: `process_document()` main API       |
| `main.py`          | CLI entry point for testing                       |

## Integration with RAG Module

The OCR module is designed for future integration with the RAG policy checker:

```python
from OCR.pipeline import process_document
from RAG.agent import query_agent

claim = process_document("test_docs/hospital_bill.jpg", "HSP-2025-TN-001")
query = f"Is {claim.diagnosis.primary_diagnosis} covered? Total bill: Rs.{claim.billing.total_amount}"
verdict = query_agent(query)
```

## Quick Start Example

1. Download a sample discharge summary from MTSamples or create a mock document
2. Place it in `test_docs/sample_discharge.pdf`
3. Run:
   ```bash
   python main.py test_docs/sample_discharge.pdf --policy HSP-2025-TN-001 --raw
   ```
4. Check the JSON output for extracted medical data
