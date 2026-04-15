# Medical Claim Processing Pipeline

A production-ready FastAPI + LangGraph project for processing complex medical claim PDFs using the Groq API (Llama 3.3 70B).

## 🏗 Architecture

The system utilizes a sophisticated multi-agent orchestration pattern powered by **LangGraph** to handle multi-page, heterogeneous medical documents.

### High-Level Workflow:
1.  **FastAPI Endpoint**: Receives a `claim_id` and a PDF file.
2.  **PDF/OCR Loader**: 
    *   Attempts direct text extraction via `pdfplumber`.
    *   Falls back to **Tesseract OCR** for image-based or protected PDFs.
3.  **Segregator Agent**: 
    *   Analyzes 2,000-character page previews.
    *   Routes pages into functional categories (Identity, Bills, Discharge Summaries, Receipts, etc.).
4.  **Parallel Extraction Agents**:
    *   **ID Agent**: Extracts patient name, DOB, Policy #, and identifiers (MRN/Patient ID) by scanning claim forms, identity cards, and clinical summaries.
    *   **Discharge Summary Agent**: Extracts clinical data (Diagnosis, Dates, Physician).
    *   **Itemized Bill Agent**: Aggregates costs from multiple sources (Hospital Bills, Pharmacy Invoices, Cash Receipts) and performs cross-document arithmetic for a grand total.
5.  **Aggregator Node**: Finalizes the structured JSON response.

## 🛠 Key Features & Fixes

-   **Model Upgrade**: Uses `llama-3.3-70b-versatile` for high-reasoning extraction.
-   **Robust JSON Parsing**: Implements regex-based cleaning to strip LLM markdown formatting and a retry mechanism for failed parses.
-   **Intelligent Routing**: The Segregator is tuned to identify specific medical document types, ensuring the right context reaches the right agent.
-   **Cross-Document Arithmetic**: The Bill Agent is instructed to sum totals from disparate invoices (e.g., Hospital + Pharmacy + Cash Receipts) to ensure financial accuracy.
-   **Identifier Fallbacks**: The ID Agent proactively searches for MRN or Patient ID if a government ID number is not present.

## 🚀 Setup Instructions

1.  **Dependencies**:
    *   Python 3.10+
    *   Tesseract OCR installed on the system (default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
    *   Poppler (required for `pdf2image`).

2.  **Installation**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment**:
    Create a `.env` file:
    ```env
    GROQ_API_KEY=your_groq_api_key
    ```

4.  **Run**:
    ```bash
    python -m app.main
    ```

## 🔌 API Specification

### Process Claim
-   **URL**: `/api/process`
-   **Method**: `POST`
-   **Payload**: `multipart/form-data`
    -   `claim_id`: String
    -   `file`: PDF Document

### Response Schema:
```json
{
  "claim_id": "CLM-001",
  "identity": {
    "patient_name": "...",
    "dob": "...",
    "id_number": "...",
    "policy_number": "..."
  },
  "discharge_summary": {
    "diagnosis": "...",
    "admit_date": "...",
    "discharge_date": "...",
    "physician_name": "..."
  },
  "bill": {
    "items": [{"name": "...", "cost": 0.0}],
    "total_amount": 0.0
  }
}
```

## 🧪 Error Handling
-   **Automatic Retries**: Retries LLM calls once if JSON parsing fails.
-   **Graceful Fallbacks**: Returns `null` for missing fields instead of failing the entire request.
-   **Detailed Logging**: Tracks agent routing and extraction decisions for easy debugging.
