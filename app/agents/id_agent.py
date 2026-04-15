import logging
from typing import Dict, Any, List
from app.utils.llm import call_groq_llm

logger = logging.getLogger(__name__)

async def extract_id_data(relevant_pages_text: str) -> Dict[str, Any]:
    """
    Extracts patient identity information from relevant pages.
    """
    if not relevant_pages_text:
        return {"patient_name": None, "dob": None, "id_number": None, "policy_number": None}

    prompt = f"""
    Extract the following patient identity information from the text:
    - patient_name
    - dob
    - id_number (Search for: Government ID #, Driver's License #, MRN, OR Patient ID. Return only the ID string, no explanations.)
    - policy_number

    TEXT:
    {relevant_pages_text}

    RULES:
    - Return ONLY valid JSON.
    - If a field is missing, use null.
    - DO NOT include sentences like "Not explicitly mentioned".
    """
    
    try:
        result = await call_groq_llm(prompt)
        logger.info(f"ID Agent output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error extracting ID data: {str(e)}")
        return {"patient_name": None, "dob": None, "id_number": None, "policy_number": None}
