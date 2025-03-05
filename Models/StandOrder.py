from pydantic import BaseModel

class CommandePresentoirRequest(BaseModel):
    partner_id: int  # ID du détaillant
    espace_type_id: int  # ID du présentoir