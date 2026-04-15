from pydantic import BaseModel
from typing import List, Optional

class IdentityData(BaseModel):
    patient_name: Optional[str] = None
    dob: Optional[str] = None
    id_number: Optional[str] = None
    policy_number: Optional[str] = None

class DischargeSummaryData(BaseModel):
    diagnosis: Optional[str] = None
    admit_date: Optional[str] = None
    discharge_date: Optional[str] = None
    physician_name: Optional[str] = None

class BillItem(BaseModel):
    name: str
    cost: float

class BillData(BaseModel):
    items: List[BillItem]
    total_amount: float

class ClaimResponse(BaseModel):
    claim_id: str
    identity: Optional[IdentityData] = None
    discharge_summary: Optional[DischargeSummaryData] = None
    bill: Optional[BillData] = None
