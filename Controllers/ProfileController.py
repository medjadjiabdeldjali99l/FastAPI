from fastapi import Request, HTTPException, status ,UploadFile, File
from database import OdooDatabase

from Tools.TokenTools import TokenTools
from Models.UserUpdate import *

from Models.SocialMedia import SocialMedia
from PIL import Image
import base64
from io import BytesIO
# import base64
# from PIL import Image
# import requests
# from io import BytesIO







from datetime import datetime, timedelta, timezone



DELEGUE_GROUP_XML_ID="crm_plv.group_plvp_commercial"
SUP_GROUP_XML_ID="crm_plv.group_plvp_superviseur"

def get_delegues_for_detailant(detailant_id ,odooDatabase):

    # Step 1: Get the DÃ©tailant record
    detailant = odooDatabase.execute_kw(
        'res.partner', 'search_read',
        [[('id', '=', detailant_id)]],  # Filter by the provided DÃ©tailant ID
        {'fields': ['id', 'name', 'pf_id']}  # Fetch the DÃ©tailant's portefeuille (pf_id)
    )

    if not detailant:
        raise HTTPException(status_code=404, detail=f"Détailant with ID {detailant_id} not found")

    detailant = detailant[0]
    pf_id = detailant.get('pf_id')


    if isinstance(pf_id, list) and pf_id:  # Ensure it's a non-empty list
        pf_id = pf_id[0]  # Extract the ID (e.g., 43)


    if not pf_id:
        return {"detaillant": detailant['name'], "delegues": []}

    group = odooDatabase.execute_kw(
        'ir.model.data', 'search_read',
        [[('model', '=', 'res.groups'), ('module', '=', DELEGUE_GROUP_XML_ID.split('.')[0]),
        ('name', '=', DELEGUE_GROUP_XML_ID.split('.')[1])]],
        {'fields': ['res_id']}
    )

    if not group:
        raise HTTPException(status_code=404, detail=f"Delegué group '{DELEGUE_GROUP_XML_ID}' not found")

    delegue_group_id = group[0]['res_id']

    delegues = odooDatabase.execute_kw(
        'res.users', 'search_read',
        [[('groups_id', 'in', delegue_group_id)]],  # Users in the deleguÃ© group
        {'fields': ['id', 'name', 'login', 'pf_ids']}  # Fetch their portefeuille (pf_ids)
    )

    

    matched_delegues = []
    for delegue in delegues:
        if pf_id in (delegue.get('pf_ids') or []):  # Ensure pf_ids is a list and check if pf_id matches
            matched_delegues.append({
                "id": delegue['id'],
                "name": delegue['name'],
                "login": delegue['login']
            })

    return {
        "detaillant": detailant['name'],
        "delegues": matched_delegues
    }

def convert_to_base64(file: UploadFile) -> str:
    content = file.file.read()
    encoded = base64.b64encode(content).decode("utf-8")
    return encoded


def compress_base64_image(base64_str: str, max_size: tuple = (800, 800), quality: int = 70) -> str:
    # 1. Décoder le base64 vers bytes
    image_bytes = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_bytes))

    # 2. Redimensionner si trop grand
    image.thumbnail(max_size)

    # 3. Réenregistrer avec qualité réduite
    buffer = BytesIO()
    image.save(buffer, format='JPEG', optimize=True, quality=quality)
    buffer.seek(0)

    # 4. Réencoder en base64
    compressed_bytes = buffer.read()
    compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
    return compressed_base64

class ProfileController():

    @staticmethod # Ready
    def update_profile(request: Request, token: str, data: UserDataVal):

        token_data = TokenTools.check_token(token)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
        )


        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        user_id = token_data['id']
        # print( user_id)
        # Retrieve user data from info.cnx
        users = odooDatabase.execute_kw('info.cnx', 'read', [[user_id]], {'fields': ['state','partner_id','candidate_id', 'id']})
   
        if not users:
            # print("user false")
            raise HTTPException(
                status_code=404,
                detail="Utilisateur introuvable"
            )
        user = users[0]
        
        # Prepare update data for info.cnx
        update_data_info = {}
        
        if data.email is not None:
            update_data_info['email'] = data.email
        if update_data_info:
            # Modify info.cnx
            odooDatabase.execute_kw('info.cnx', 'write', [user['id'], update_data_info])
        
        # Prepare update data for res.partner
        update_data_partner = {}
        if data.nom is not None:
            update_data_partner['name'] = data.nom
        if data.raisonSociale is not None:
            update_data_partner['name_magasin'] = data.raisonSociale
        if data.adresse is not None:
            update_data_partner['street'] = data.adresse
        if data.otherTel is not None:
            update_data_partner['new_tlp1'] = data.otherTel
        # if data.localisation is not None:
        #     update_data_partner['localisation'] = data.localisation
        if update_data_partner:
            if user['state']=='partner':

                if 'partner_id' in user and user['partner_id']:

                    odooDatabase.execute_kw('res.partner', 'write', [user['partner_id'][0], update_data_partner])
            if user['state']=='candidate':
                pass

        return {
            "status": True,
            "message": "Profile updated successfully"
        }
    
    @staticmethod # Ready
    def add_social_media(request : Request, token : str, social : SocialMedia):

        token_data = TokenTools.check_token(token)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
        )


        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        newVals = {
            "iduser":token_data['id'],
            "type":social.type.value,
            "lien_profil":social.url
        }
        new_social_id = odooDatabase.execute_kw('reseau.sociaux','create',[newVals])
        if not new_social_id : 
            raise HTTPException(
                status_code=422,
                detail="Erreur d'ajout du réseau social"
            )
        return {
            "status": True,
            "message": "Réseau ajouté avec succès"
        }    
    

    @staticmethod # Ready
    def delete_social_media(request: Request, token: str, id: int):

        token_data = TokenTools.check_token(token)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
        )

        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        odooDatabase.execute_kw('reseau.sociaux', 'unlink', [[id]])
        
        return {
            "status": True,
            "message": "Réseau supprimé avec succès"
        }
    
    # @staticmethod # Ready
    # def add_image(request: Request, token: str, image_data: str):

    #     token_data = TokenTools.check_token(token)
    #     if not token_data : 
    #         raise HTTPException(
    #             status_code=401,  
    #             detail={"status": False, "error": "Token Invalide"}
    #     )
    #     # print ( "stringggg================================================================================== c fait ",image_data[0:100])
        
    #     # imageData = base64.b64decode(image_data)
    #     # print(imageData[:100])

    #     # # Ouvrir l'image avec Pillow
    #     # image = Image.open(BytesIO(imageData))
    #     # image = Image.open(BytesIO(imageData))
    #     # image.save("test.jpg")  # Pour être sûr que le fichier est bien là
    #     # image.show() 

    #     # print ( "====================open==============================================")

    #     user_id = token_data['id']
    #     compressed_image_data = compress_base64_image(image_data)
    #     odooDatabase: OdooDatabase = request.app.state.odooDatabase
    #     image_id = odooDatabase.execute_kw('images.magasins', 'create', [{
    #         'id_user': user_id,
    #         'image': compressed_image_data,
    #     }])
    #     # print ( " fitnaaaaaaaaa",image_id)
    #     return {
    #         "status": True,
    #         "message": "Image ajoutée avec succès",
    #         "image_id": image_id
    #     }
    


    @staticmethod # Ready
    def add_image(request: Request, token: str, image_data:UploadFile = File(...) ):

        
        



        token_data = TokenTools.check_token(token)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
        )
        # print ( "stringggg================================================================================== c fait ",image_data[0:100])
        
        # imageData = base64.b64decode(image_data)
        # print(imageData[:100])

        # # Ouvrir l'image avec Pillow
        # image = Image.open(BytesIO(imageData))
        # image = Image.open(BytesIO(imageData))
        # image.save("test.jpg")  # Pour être sûr que le fichier est bien là
        # image.show() 

        # print ( "====================open==============================================")
        print ( image_data)
        content = image_data.file.read()
        base64_str = base64.b64encode(content).decode("utf-8")


        user_id = token_data['id']
        compressed_image_data = compress_base64_image(base64_str)
        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        image_id = odooDatabase.execute_kw('images.magasins', 'create', [{
            'id_user': user_id,
            'image': compressed_image_data,
        }])
        # print ( " fitnaaaaaaaaa",image_id)
        return {
            "status": True,
            "message": "Image ajoutée avec succès",
            "image_id": image_id
        }
    
    @staticmethod # Ready
    def delete_image(request : Request, token : str, id : int ):
        print ( "=====================================hada id ",id)

        token_data = TokenTools.check_token(token)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
        )

        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        odooDatabase.execute_kw('images.magasins', 'unlink', [[id]])
        return{"status" :True, "message":"Image supprimée avec succès"}



