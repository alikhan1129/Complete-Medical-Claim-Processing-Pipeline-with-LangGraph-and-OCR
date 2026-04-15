import logging
from typing import Dict, Any, List
from app.utils.llm import call_groq_llm

logger = logging.getLogger(__name__)

async def extract_itemized_bill(relevant_pages_text: str) -> Dict[str, Any]:
    """
    Extracts itemized bill data from relevant pages.
    """
    if not relevant_pages_text:
        return {"items": [], "total_amount": 0.0}

    prompt = f"""
    Analyze the text which contains multiple billing documents.
    
    COMPUTATION RULES:
    1. Extract ALL individual line items {{"name", "cost"}} from every page.
    2. The 'total_amount' MUST be the sum of the final totals from each document:
       - Hospital Bill Total (e.g., $6,418.65)
       - Pharmacy Bill Total (e.g., $206.35)
       - Cash Receipt Total (e.g., $285.00)
    3. Final 'total_amount' = sum of these totals.

    OUTPUT FORMAT:
    {{
      "items": [ {{"name": "...", "cost": 0.0}}, ... ],
      "total_amount": 0.0
    }}

    TEXT:
    {relevant_pages_text}

    RETURN STRICT JSON ONLY.
    """
    
    try:
        result = await call_groq_llm(prompt)
        logger.info(f"Bill Agent output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error extracting itemized bill: {str(e)}")
        return {"items": [], "total_amount": 0.0}
