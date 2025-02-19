from enum import Enum
from pydantic import BaseModel, ConfigDict

class SocialMediaType(str, Enum):
    Viber = "viber"
    Whatsapp = "whatsapp"
    X = "x"
    Facebook = "facebook"
    Instagram = "instagram"
    TikTok = "tiktok"

class SocialMedia(BaseModel):
    id: int
    type: SocialMediaType
    url: str

    model_config = ConfigDict(use_enum_values=True)
