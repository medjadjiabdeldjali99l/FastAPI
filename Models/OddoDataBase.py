from pydantic import BaseModel
from os import getenv
from dotenv import load_dotenv

load_dotenv()  # Charger les variables d'environnement avant tout

class OdooCredentials(BaseModel):
    url: str
    db: str
    username: str
    password: str

    def __init__(self, **data):
        super().__init__(
            url=getenv("ODOO_URL", ""),
            db=getenv("ODOO_DB", ""),
            username=getenv("ODOO_USERNAME", ""),
            password=getenv("ODOO_PASSWORD", ""),
        )
