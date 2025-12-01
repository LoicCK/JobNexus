from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    title: str
    company: str
    city: Optional[str] = None
    url: str
    contract_type: Optional[str] = "Alternance"
    target_diploma_level: str
    source: str