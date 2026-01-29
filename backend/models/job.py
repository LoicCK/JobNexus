from typing import Optional

from pydantic import BaseModel


class Job(BaseModel):
    search_query: Optional[str] = None
    title: str
    company: str
    city: Optional[str] = None
    url: str
    contract_type: Optional[str] = "Alternance"
    target_diploma_level: str
    source: str
