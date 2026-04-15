from typing import Dict, Any

def aggregate_results(claim_id: str, identity: Dict[str, Any], discharge: Dict[str, Any], bill: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combines the results from all extraction agents into a final JSON structure.
    """
    return {
        "claim_id": claim_id,
        "identity": identity if identity else None,
        "discharge_summary": discharge if discharge else None,
        "bill": bill if bill else None
    }
