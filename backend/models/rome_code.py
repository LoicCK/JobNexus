from pydantic import BaseModel


class RomeCode(BaseModel):
    libelle: str
    code: str
