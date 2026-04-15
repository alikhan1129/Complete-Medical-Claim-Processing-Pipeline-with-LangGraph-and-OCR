import logging
from typing import Dict, Any, List
from app.utils.llm import call_groq_llm

logger = logging.getLogger(__name__)

async def extract_discharge_summary(relevant_pages_text: str) -> Dict[str, Any]:
    """
    Extracts discharge summary data from relevant pages.
    """
    if not relevant_pages_text:
        return {"diagnosis": None, "admit_date": None, "discharge_date": None, "physician_name": None}

    prompt = f"""
    Extract the following discharge summary information from the text:
    - diagnosis
    - admit_date
    - discharge_date
    - physician_name

    TEXT:
    {relevant_pages_text}

    RETURN STRICT JSON ONLY.
    """
    
    try:
        result = await call_groq_llm(prompt)
        logger.info(f"Discharge Agent output: {result}")
        return result
    except Exception as e:
        logger.error(f"Error extracting discharge summary: {str(e)}")
        return {"diagnosis": None, "admit_date": None, "discharge_date": None, "physician_name": None}
