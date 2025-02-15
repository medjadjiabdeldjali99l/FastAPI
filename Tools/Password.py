from passlib.context import CryptContext

# Définition du contexte de hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Password:
    """Classe utilitaire pour la gestion des mots de passe."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe en clair correspond au haché."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Retourne le hachage sécurisé du mot de passe."""
        return pwd_context.hash(password)

# Exemple d'utilisation
# hashed = Password.get_password_hash("monmotdepasse")
# print(Password.verify_password("monmotdepasse", hashed))  # True
# print(Password.verify_password("mauvaismotdepasse", hashed))  # False
