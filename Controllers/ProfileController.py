from fastapi import Request, HTTPException, status
from database import OdooDatabase

from Tools.TokenTools import TokenTools
from Models.UserUpdate import *

from Models.SocialMedia import SocialMedia
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

    # Debugging: Print all deleguÃ©s and their pf_ids
    for delegue in delegues:
        print(f"Delegué ID: {delegue['id']}, PF_IDs: {delegue.get('pf_ids')}")

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



class ProfileController():

    @staticmethod # Ready
    def update_profile(request: Request, token: str, data: UserDataVal):

        token_data = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",token_data)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
        )


        print("=========================================auth====",token_data)
        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        user_id = token_data['id']
        # print( user_id)
        # Retrieve user data from info.cnx
        users = odooDatabase.execute_kw('info.cnx', 'read', [[user_id]], {'fields': ['state','partner_id','candidate_id', 'id']})
        print("updatttttttttttttttttttttttttttttttttttttttt",users)
        if not users:
            # print("user false")
            raise HTTPException(
                status_code=404,
                detail="Utilisateur introuvable"
            )
        user = users[0]
        
        # Prepare update data for info.cnx
        update_data_info = {}
        # print("the last data" )
        # print(data)
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
            print ( "bismalahiiiiiiiiiiiiiiiiiiiiiii",user)
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
        print("userrrrrrrrrrrrrrrrrrrrrr",token_data)
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
        print("userrrrrrrrrrrrrrrrrrrrrr",token_data)
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
    
    @staticmethod # Ready
    def add_image(request: Request, token: str, image_data: str):

        token_data = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",token_data)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
        )

        user_id = token_data['id']
        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        image_id = odooDatabase.execute_kw('images.magasins', 'create', [{
            'id_user': user_id,
            'image': image_data,
        }])
        return {
            "status": True,
            "message": "Image ajoutée avec succès",
            "image_id": image_id
        }
    
    @staticmethod # Ready
    def delete_image(request : Request, token : str, id : int ):

        token_data = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",token_data)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
        )

        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        odooDatabase.execute_kw('images.magasins', 'unlink', [[id]])
        return{"status" :True, "message":"Image supprimée avec succès"}






    # @staticmethod #ready
    # def info_users(request : Request, token : str):

        

    #       # Affiche les détails du champ obligation_id
    #     print("its nott me ")
    #     print("''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''")
    #     print("Headers:", request.headers)         # Les en-têtes de la requête
    #     print("Query params:", request.query_params)  
    #     print(token)
    #     print("'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''")
    #     user_id = request.query_params.get("allo")
        
        

    #     odooDatabase : OdooDatabase = request.app.state.odooDatabase


        

















        
    #     user = odooDatabase.execute_kw(
    #         'info.cnx',  # Modèle Odoo
    #         'search_read',  # Méthode pour lire les données
    #         [[['id', '=', user_id]]],  # Condition : ID utilisateur
    #         {'fields': ['id', 'telephone']}  # Champs à récupérer
    #     )
    #     print(user) 


    #     # employees = odooDatabase.execute_kw(
    #     #     'hr.employee',  # Modèle Odoo
    #     #     'search_read',  # Méthode pour rechercher et lire les données
    #     #     [[
    #     #         '|',  # OU logique pour combiner plusieurs conditions
    #     #         '|',  # Combine la première et deuxième condition
    #     #         ['job_title', 'ilike', 'Délégué'],  # Recherche "Délégué" (sensibilité à la casse/accentuation)
    #     #         # ['job_title', 'ilike', 'delegue'],  # Recherche "delegue" (sans accent)
    #     #         ['job_title', 'ilike', 'Superviseur']  # Recherche "Superviseur"
    #     #     ]],
    #     #     {'fields': ['id', 'name', 'job_title','mobile_phone','work_email']}  # Champs à récupérer
    #     # )

    #     # # Affiche les employés trouvés
    #     # print(employees)


    #     print ( "powershemmmmmmmmmmmmmmmmmmmmmmmmmm")


    #     # recupirer tt les rsx avec un id de lutilisateur dans la table info.cnx 
    #     # reseaux = odooDatabase.execute_kw(
    #     #     'reseau.sociaux',  # Modèle Odoo
    #     #     'search_read',  # Méthode pour chercher et lire des enregistrements
    #     #     [[['iduser', '=', user_id]]],  # Condition : `iduser` = l'ID utilisateur
    #     #     {'fields': ['id', 'type', 'lien_profil']}  # Champs à récupérer
    #     # )
    #     # print(reseaux)  # Affichez les réseaux sociaux associés































    #     user = check_token(token)
    #     if not user : 
    #         raise HTTPException(
    #             status_code=401,  
    #             detail={"status": False, "error": "Token Invalide"}
    #         )

    #     user_id = user.id
    #     users = odooDatabase.execute_kw('info.cnx', 'read', [[user_id]], {'fields': []})

    #     if not users:
    #         # print("user false")
    #         raise HTTPException(
    #             status_code=404,
    #             detail="Utilisateur introuvable"
    #         )
    #     user = users[0]

    #     u = odooDatabase.execute_kw(
    #         'res.partner',  # Modèle Odoo
    #         'search_read',  # Méthode utilisée pour la recherche et la lecture
    #         [[['id', '=', user['id_user'][0]]]],
    #         {'fields': ['id','name','name_magasin','street','new_tlp1']} 
      
    #     )

    #     u[0]['telephone']=user['telephone']
    #     u[0]['email']=user['email']

    #     name_id= odooDatabase.execute_kw('res.partner', 'read', [user['id_user'][0]] , {'fields': ['niveau_id']})
       
    #     u[0]['niveau']=name_id[0]['niveau_id'][1]

    #     result = get_delegues_for_detailant(27845 ,odooDatabase)
        
    #     u[0]['delegue']=result['delegues']


    #     # delegue = odooDatabase.execute_kw(
    #     #     'res.partner',  # Modèle Odoo
    #     #     'search_read',  # Méthode utilisée pour la recherche et la lecture
    #     #     [[['id', '=', 15731]]],
    #     #     {'fields': ['pf_id','region_id','name']} 
      
    #     # )

    #     # print ( "hada dETAILLANTTTTTTTTTTTTTTTTTTT",delegue)

    #     # print ( "'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''")

    #     # users_with_pf_id = odooDatabase.execute_kw(
    #     #     'res.users',  # Modèle Odoo correspondant à la table res_users
    #     #     'search_read',  # Méthode pour chercher et lire des enregistrements
    #     #     [[
    #     #         ['region_id', '!=', False]  # Condition : pf_id IS NOT NULL
    #     #     ]],
    #     #     {
    #     #         'fields': ['id','pf_ids', 'active', 'pf_id','partner_id']  # Colonnes à récupérer
    #     #     }
    #     # )

    #     # for i in users_with_pf_id:
    #     #     print(i)






    #     # # liste_des_delegues_afficter=[[6967, 'BASLIMANE Rayane']]
    #     # liste_des_delegues_afficter=[]
    #     # for i in users_with_pf_id :
    #     #     # if delegue[0]['pf_id'][0] in i['pf_ids'] or delegue[0]['pf_id'][0] in i['pf_id']:
    #     #     if delegue[0]['pf_id'][0] in i['pf_ids']:    
    #     #         liste_des_delegues_afficter.append(i['partner_id'])


    #     # print( "hadi hiya la liste li naffichiwha f front " ,liste_des_delegues_afficter )
























    #     # attachment = odooDatabase.execute_kw(
    #     #     'ir.attachment',  # Modèle
    #     #     'search_read',  # Méthode de lecture
    #     #     [[['id', '=', 3345]]],  # Condition : ID de l'attachement
    #     #     {'fields': ['db_datas']}  # Récupérer uniquement les données binaires
    #     # )
    #     # print(attachment)
    #     # print("ùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùù")

    #     # if attachment:
    #     #     # Récupérer les données binaires (db_datas)
    #     #     image_data = attachment[0]['db_datas']
            
    #     #     # Décoder les données binaires
    #     #     image_bytes = base64.b64decode(image_data)

    #     #     # Ouvrir l'image avec PIL
    #     #     image = Image.open(BytesIO(image_bytes))

    #     #     # Afficher l'image
    #     #     image.show()

        





        








    #     try:    
    #         return u
    #     except HTTPException as e:
    #         raise e
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))
