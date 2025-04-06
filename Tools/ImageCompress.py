from PIL import Image
import io
import base64

def convert_base64_to_webp(base64_string):
    # Supprimer le préfixe si présent (ex: "data:image/png;base64,")
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]

    # Décoder le Base64 en bytes
    image_data = base64.b64decode(base64_string)
    
    # Charger l'image avec PIL
    image = Image.open(io.BytesIO(image_data))
    
    # Sauvegarder en WebP en mémoire
    webp_io = io.BytesIO()
    image.save(webp_io, format="WEBP")
    
    # Récupérer l'image WebP en Base64
    webp_base64 = base64.b64encode(webp_io.getvalue()).decode("utf-8")
    
    return webp_base64