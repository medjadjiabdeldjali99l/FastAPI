from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt
# from PIL import Image
# import io
# import base64
from Tools.ImageCompress import convert_base64_to_webp

# def convert_base64_to_webp(base64_string):
#     # Supprimer le préfixe si présent (ex: "data:image/png;base64,")
#     if "," in base64_string:
#         base64_string = base64_string.split(",")[1]

#     # Décoder le Base64 en bytes
#     image_data = base64.b64decode(base64_string)
    
#     # Charger l'image avec PIL
#     image = Image.open(io.BytesIO(image_data))
    
#     # Sauvegarder en WebP en mémoire
#     webp_io = io.BytesIO()
#     image.save(webp_io, format="WEBP")
    
#     # Récupérer l'image WebP en Base64
#     webp_base64 = base64.b64encode(webp_io.getvalue()).decode("utf-8")
    
#     return webp_base64


class MainController():
    
    @staticmethod # Ready
    def get_actualite_events( request : Request, token : str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        category = odooDatabase.execute_kw(
            'crm.mobile.category',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[]],
            {'fields': ['id']} 
        )
        l = [i['id'] for i in category]
        

        pp={}
        for i in l :
            actualite = odooDatabase.execute_kw(
            'crm.mobile.category.item',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['categ_id' , '=', i],['state','=','published']]],
            {'fields': ['id','name','categ_id','description','state']} 
            )
            if actualite :



                # print ( " adel7A99999999999999" , actualite)
                chain=actualite[0]['categ_id'][1]
                session_id = odooDatabase.session

                for i in actualite :
                    i['image'] = f"{odooDatabase.base_url}web/image/crm.mobile.category.item/{i['id']}/image?session_id={session_id}"
                
                # for img in actualite:
                #     base64_image =  img['image'] # Une chaîne base64 valide ici
                #     # print(get_image_size(base64_image))
                #     img['image'] = convert_base64_to_webp(base64_image)
                if chain:
                    pp[chain]=actualite


        try:    
            return pp
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))






        

    