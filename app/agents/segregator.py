import logging
from typing import Dict, Any, List
from app.utils.llm import call_groq_llm

logger = logging.getLogger(__name__)

async def classify_pages(pages: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Classifies each page of the PDF into predefined categories.
    """
    # Increase preview to 2000 chars for better classification
    pages_for_classification = []
    for page in pages:
        pages_for_classification.append({
            "page_number": page["page_number"],
            "text_preview": page["text"][:2000] 
        })

    prompt = f"""
    Analyze the text from each page and classify it into the most appropriate categories.
    
    CATEGORIES & CRITERIA:
    - identity_document: Includes Government IDs, Passport, Driver's License, OR any page containing Patient ID, MRN, or Policy details.
    - itemized_bill: Any document listing costs, quantities, pharmacy invoices, outpatient bills, or hospital charges.
    - discharge_summary: Clinical summaries, hospital course, admission/discharge dates, and diagnosis.
    - claim_forms: Official insurance claim submission forms.
    - cheque_or_bank_details: Bank statements, cancelled cheques, or bank account info.
    - prescription: Doctor's prescriptions (Rx).
    - investigation_report: Lab results, radiology reports (X-ray, CT), or pathology.
    - cash_receipt: Simple receipts for payments made.
    - other: Any other documents like registration forms or cover letters.

    PAGES:
    {pages_for_classification}

    OUTPUT MUST BE STRICT JSON ONLY:
    {{
      "page_map": {{
        "1": ["identity_document", "claim_forms"],
        "10": ["itemized_bill"]
      }}
    }}
    """
    
    try:
        result = await call_groq_llm(prompt)
        logger.info(f"Page classification result: {result}")
        
        # Ensure we always return a dict
        if isinstance(result, dict):
            return result.get("page_map", {})
        else:
            logger.error(f"LLM returned non-dict result: {type(result)}")
            return {}
            
    except Exception as e:
        logger.error(f"Error classifying pages: {str(e)}")
        raise e  # Let the graph node handle or propagate the error
