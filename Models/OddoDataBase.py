from pydantic import BaseModel
from os import getenv
from dotenv import load_dotenv

load_dotenv()  # Charger les variables d'environnement

class OdooCredentials(BaseModel):
    url: str = getenv("ODOO_URL")
    db: str = getenv("ODOO_DB")
    username: str = getenv("ODOO_USERNAME")
    password: str = getenv("ODOO_PASSWORD")
