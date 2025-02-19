from fastapi import Request, HTTPException, status
from database import OdooDatabase
from typing import List ,Optional
from Models import TokenData
from Models.Image import Image
# from validators.Authentification import *

from Models.UserData import UserData
# from utils.Password import Password
from Models.SocialMedia import SocialMedia, SocialMediaType
# from utils import remove_none_values
import bcrypt



from Models import Token
from Tools.TokenTools import TokenTools
import jwt







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
        {'fields': ['id', 'name', 'pf_ids']}  # Fetch their portefeuille (pf_ids)
    )

    # Debugging: Print all deleguÃ©s and their pf_ids
    for delegue in delegues:
        print(f"Delegué ID: {delegue['id']}, PF_IDs: {delegue.get('pf_ids')}")

    matched_delegues = []
    for delegue in delegues:
        if pf_id in (delegue.get('pf_ids') or []):  # Ensure pf_ids is a list and check if pf_id matches
            matched_delegues.append({
                "name": delegue['name']
            })

    return {
        "detaillant": detailant['name'],
        "delegues": matched_delegues
    }

def create_record_in_new_table(odooDatabase : OdooDatabase, new_detaillant, phone: Optional[str] = None):
    
    # Crée un enregistrement dans la nouvelle table avec les détails du détaillant.
    plain_password= Password.generate_password()
    hashed_password = Password.hash_password(plain_password)
    hashed_password = plain_password   #
    
    nvlTableVals = {
        "id_user": new_detaillant['id'],
        "telephone": phone,
        "password": hashed_password
    }
    
    # Prévoir une fonction pour envoyer le plain password en SMS
    
    # Créer l'enregistrement dans info.cnx
    detNvlTable_id = odooDatabase.execute_kw('info.cnx', 'create', [nvlTableVals])
    if not detNvlTable_id:
        raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Erreur de création dans la nouvelle table"}
            )
    return detNvlTable_id

class AuthentificationController():

    @staticmethod # Works, but the rest of the data needs to be handled
    def me(request: Request, token: str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        

        token_data = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",token_data)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
        )


        print("=========================================auth====",token_data)



        user_1 = odooDatabase.execute_kw('info.cnx', 'read', [token_data.id])
        user_2 = odooDatabase.execute_kw('res.partner', 'read', [user_1[0]['id_user'][0]], {'fields': ['id','name', 'name_magasin', 'categorie_id', 'commune_id', 'street','code','etoile','nbr_points', 'state_id','new_tlp1']})	
        full_user = {**user_1[0],**user_2[0]}
        social_media = odooDatabase.execute_kw('reseau.sociaux', 'search_read',[[['iduser', '=', token_data.id]],['id','type','lien_profil']])
        ready_social_media = []

        for social in social_media:
            typeSocialMedia = next((smt for smt in SocialMediaType if smt.value == social['type']), None)
            print("asssssssssssssssssssssssssss",typeSocialMedia)
            ready_social_media.append(SocialMedia(id=social['id'], type=typeSocialMedia, url=social['lien_profil']))
        print ( " faussssssssssssssssse alerte")

        ready_images = []
        for image_id in full_user['images_magasins_ids']:
            image_url = f"{odooDatabase.base_url}/web/image/images.magasins/{image_id}/image"
            ready_images.append(Image(id=image_id, image=image_url))
        
            # Liste des champs à vérifier
        print( "farinaaaaaaaaaaaaaaaaaaaaaaaaa",ready_images)
        fields_to_check = [
            'id','name','telephone', 'name_magasin', 'street', 'email',
            'categorie_id', 'state_id', 'commune_id', 'images_magasins_ids', 'reseau_sociaux_ids','new_tlp1'] #Ajouter fields localisation
            
        # Calcul du pourcentage de profil rempli
        filled_fields = sum(1 for field in fields_to_check if full_user.get(field))
        
        total_fields = len(fields_to_check)

        result = get_delegues_for_detailant( full_user['id'],odooDatabase)
    
        ready_user = UserData(
            id=full_user.get('id'),
            nom=full_user.get('name'),
            tel=full_user.get('telephone'),
            raisonSociale=full_user.get('name_magasin'),
            adresse=full_user.get('street'),
            email=full_user.get('email'),
            idDetaillant=full_user.get('code'),
            niveauDetaillant=int(full_user.get('etoile', 0)) - 1 if full_user.get('etoile') else None,
            pointsDetaillant=int(full_user.get('nbr_points', 0)) if full_user.get('nbr_points') else None,
            natureCommerce=full_user.get('categorie_id', [None, None])[1],
            ville=full_user.get('commune_id', [None, None])[1],
            wilaya=full_user.get('state_id', [None, None])[1],
            pourcentageNiveau=80,
            pourcentageProfil=int((filled_fields / total_fields) * 100) if total_fields > 0 else 0,
            socialMedia=ready_social_media,
            images=ready_images,
            otherTel=full_user.get('new_tlp1'),
            delegue=result.get('delegues')
        )


        return {
            "status": True,
            "data": ready_user.dict()
        }

        
    @staticmethod # Ready
    def login(request: Request,UserLogin:dict):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz", type(UserLogin))

        det = odooDatabase.execute_kw('info.cnx', 'search', [[['telephone', '=', UserLogin.phone]]])

        print("detttttttttttttttttttttttttttttttttttttttt",det)

        users = None
        if det:
            users = odooDatabase.execute_kw('info.cnx', 'read', [det], {'fields': ['telephone','password','id','id_user','email','images_magasins_ids']})
        if not users:
            raise HTTPException(
                status_code=422, 
                detail="Numéro de téléphone introuvable"
            )
        if not Password.check_password(users[0]['password'], password):
            raise HTTPException(
                status_code=422, 
                detail="Mot de passe incorrect"
            )
        user = users[0]
        detailant = odooDatabase.execute_kw('res.partner', 'read', [user['id_user'][0]], {'fields': ['code','name','categorie_id', 'commune_id', 'street','code','etoile','nbr_points', 'state_id','new_tlp1','name_magasin']})
        token = generate_token(User(id=user["id"],telephone=user['telephone'], codeDetaillant=detailant[0]['code']))

        ready_images = []
        for image_id in users[0]['images_magasins_ids']:
            image_url = f"{odooDatabase.base_url}/web/image/images.magasins/{image_id}/image"
            ready_images.append(Image(image_id, image_url))

        
        social_media = odooDatabase.execute_kw('reseau.sociaux', 'search_read',[[['iduser', '=', users[0]['id']]],['id','type','lien_profil']])
        ready_social_media = []

        
        for social in social_media:
            typeSocialMedia = next((smt for smt in SocialMediaType if smt.value == social['type']), None)
            ready_social_media.append(SocialMedia(id=social['id'], type=typeSocialMedia, url=social['lien_profil']))
        

        result = get_delegues_for_detailant(users[0]['id_user'][0] ,odooDatabase)
        
        

        ready_user = UserData(
            id = users[0]['id_user'][0],
            nom = detailant[0]['name'],
            tel = users[0]['telephone'],
            raisonSociale = detailant[0]['name_magasin'],
            adresse = detailant[0]['street'],
            email = users[0]['email'],
            idDetaillant = detailant[0]['code'],
            niveauDetaillant = int(detailant[0]['etoile'])-1,
            pointsDetaillant = detailant[0]['nbr_points'],
            natureCommerce = detailant[0]['categorie_id'][1] if detailant[0]['categorie_id'] else None,
            ville = detailant[0]['commune_id'][1] if detailant[0]['commune_id'] else None,
            wilaya= detailant[0]['state_id'][1] if detailant[0]['state_id'] else None,
            pourcentageNiveau=80,
            # pourcentageProfil=int((filled_fields / total_fields) * 100),
            socialMedia = ready_social_media,
            images= ready_images,
            otherTel = detailant[0]['new_tlp1'],
            delegue =result['delegues']
            
        )
        return {
            "status": True,
            "token": token,
            "data" : ready_user.get_json()
        }



    # @staticmethod # Ready
    # def inscription(request: Request, data: RegisterUser):
    #     odooDatabase: OdooDatabase = request.app.state.odooDatabase
        
    #     # Verifier si le code détaillant existe sur la table res.partner
    #     det_id = odooDatabase.execute_kw('res.partner', 'search_read',[[['code', '=', data.codeDet]],['code']])
    #     if not det_id:
    #         raise HTTPException(
    #             status_code=422, 
    #             detail="Code détaillant n'existe pas"
    #         )
        
    #     # Verifier si le numéro de téléphone est déjà utilisé ou si le code détaillant est déjà associé à un compte
    #     det = odooDatabase.execute_kw('info.cnx', 'search_read', [['|',['telephone', '=', data.phone],['id_user', '=', det_id[0]['id']]]])
    #     if ( True in [det[i]['telephone'] == data.phone for i in range(len(det))] ):
    #         raise HTTPException(
    #             status_code=422, 
    #             detail="Numéro de téléphone déjà utilisé"
    #         )
    #     elif ( True in [det[i]['id_user'][0] == det_id[0]['id'] for i in range(len(det))] ):
    #         raise HTTPException(
    #             status_code=422, 
    #             detail="Code détaillant déjà associé à un compte"
    #         )
            
            
    #     # Créer un enregistrement dans la nouvelle table
    #     record_mobile_id = create_record_in_new_table(odooDatabase, det_id[0], phone=data.phone)
    #     if not record_mobile_id:
    #         raise HTTPException(
    #             status_code=503,
    #             detail="Erreur de connexion avec le serveur, veuillez réessayer"
    #         )
    #     return {
    #         "status": True,
    #         "message": "Votre mot de passe vous a été envoyé par SMS"
    #     }

    # @staticmethod # Ready -- check one case brk
    # def adhesion(request: Request, data : AdhererUser ) :  
    #     odooDatabase : OdooDatabase = request.app.state.odooDatabase
    #     det = odooDatabase.execute_kw('info.cnx', 'search', [[['telephone', '=', data.phone_compte]]])
    #     if det:
    #         raise HTTPException(
    #             status_code=422,
    #             detail="Ce numéro de téléphone est déjà associé à un compte"
    #         ) 
    #     region_id, pf_id = 13, 6 #Poour les tests brk on verra après kifeh nmappiw
    #     vals = {
    #         'name': data.name,
    #         'categorie_id' : data.categorie_id,
    #         'name_magasin': data.name_magasin,
    #         'state_id': data.state_id,
    #         'country_id': data.country_id,
    #         'commune_id': data.commune_id,
    #         'phone': data.phone_compte,
    #         'region_id': region_id,
    #         'pf_id': pf_id,
    #         'etoile': 2,    # Hard coded, un detaillant inscrit sera directement au niv 1 
            
    #         'company_type': 'company',
    #         'nature': [(6, 0, [2])],  # Relation many2many avec res.partner.nature.multiple
    #         'user_id': odooDatabase.uid,
    #         'commentaires':"TEST API VIA MobileApp"
    #     }
    #     # Filtrer les valeurs None
    #     filtered_vals = remove_none_values(vals)
        
    #     # Créer le nouveau détaillant dans Odoo
    #     new_detaillant_id = odooDatabase.execute_kw( 'res.partner', 'create', [filtered_vals])
        
    #     if not new_detaillant_id :
    #         raise HTTPException(
    #             status_code=503,
    #             detail="Erreur de connexion avec le serveur, veuillez réessayer"
    #         )
        
    #     #Génération du code détaillant
    #     sequence_code = 'res.partner.detaillant'
    #     code = odooDatabase.execute_kw('ir.sequence', 'next_by_code', [sequence_code])
    #     if code : 
    #         odooDatabase.execute_kw('res.partner', 'write', [[new_detaillant_id], {'code': code}])
    #     # else:
    #     #     # je pense hna supprimer le detaillant et return
    #     #     return {
    #     #         "status": False,
    #     #         "error": "Erreur de connexion au serveur, veuillez réessayer"
    #     #     }

    #     # Lire les détails du nouveau détaillant créé
    #     new_detaillant = odooDatabase.execute_kw('res.partner', 'read', [[new_detaillant_id], ['id']])[0]
        
    #     # Créer l'enregistrement dans la nouvelle table
    #     detNvlTable_id = create_record_in_new_table(odooDatabase, new_detaillant, phone=data.phone_compte)

    #     if not detNvlTable_id:
    #         raise HTTPException(
    #             status_code=503,
    #             detail="Erreur de connexion avec le serveur, veuillez réessayer"
    #         )
    #     return {
    #         "status": True,
    #         "message": "Votre mot de passe et votre code détaillant vous ont été envoyé par SMS"
    #     }

    # @staticmethod # Ready
    # def motDePasseOublie(request: Request, data : ForgotPwd) :
    #     odooDatabase : OdooDatabase = request.app.state.odooDatabase
    #     det_id = odooDatabase.execute_kw('info.cnx','search',[[['telephone', '=', data.phone]]])    
    #     if not det_id : 
    #         raise HTTPException(
    #             status_code=422,
    #             detail="Numéro de téléphone introuvable"
    #         )
        
    #     #Génerer un nv mdp
    #     plain_password = Password.generate_password()
    #     hashed_password = Password.hash_password(plain_password)
    #     odooDatabase.execute_kw('info.cnx', 'write', [det_id, {'password': hashed_password}])
        
    #     # Envoyer le nv mdp par SMS

    #     return {
    #         "status": True,
    #         "message": "Votre nouveau mot de passe vous a été envoyé par SMS"
    #     }
        