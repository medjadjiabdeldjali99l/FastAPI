from fastapi import Request, HTTPException, status
from database import OdooDatabase
from typing import List ,Optional
from Models.TokenData import TokenData
from Models.Image import Image

from Models.UserData import *

from Tools.Password import Password
from Models.SocialMedia import SocialMedia, SocialMediaType
import bcrypt


from Tools import historiqueConnexionAndActions
from Models.UserConnexion import *
from Models import Token
from Tools.TokenTools import TokenTools
import jwt




from datetime import datetime, timedelta, timezone
from passlib.exc import UnknownHashError


import random
import time
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

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

def remove_none_values(d):
    # Filtrer les paires clé-valeur où la valeur est None.
    return {k: v for k, v in d.items() if v is not None}



def create_record_in_new_table(odooDatabase : OdooDatabase, new_detaillant, phone: Optional[str] = None):
    
    # Crée un enregistrement dans la nouvelle table avec les détails du détaillant.

    plain_password=Password.get_random_string(8)
    # print ("password plain adhhh =============================================",plain_password)
    hashed_password = Password.get_password_hash(plain_password)
    # hashed_password = plain_password   #
    
    nvlTableVals = {
        "candidate_id": new_detaillant['id'],
        "telephone": phone,
        "password": hashed_password,
        "state" :'candidate'

    }
    
    # Créer l'enregistrement dans info.cnx
    detNvlTable_id = odooDatabase.execute_kw('info.cnx', 'create', [nvlTableVals])
    if not detNvlTable_id:
        raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Erreur de création dans la nouvelle table"}
            )
    return detNvlTable_id , plain_password

def create_record_in_new_table_respartner(odooDatabase : OdooDatabase, new_detaillant, phone: Optional[str] = None):
    
    # Crée un enregistrement dans la nouvelle table avec les détails du détaillant.

    plain_password=Password.get_random_string(8)
    # print ("password plainn inscr==============================================",plain_password)
    hashed_password = Password.get_password_hash(plain_password)
    # hashed_password = plain_password   #
    
    nvlTableVals = {
        "partner_id": new_detaillant['id'],
        "telephone": phone,
        "password": hashed_password,
        "state" : 'partner'
    }
    
    # Créer l'enregistrement dans info.cnx
    detNvlTable_id = odooDatabase.execute_kw('info.cnx', 'create', [nvlTableVals])
    if not detNvlTable_id:
        raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Erreur de création dans la nouvelle table"}
            )
    return detNvlTable_id , plain_password


class AuthentificationController():

    @staticmethod # Works, but the rest of the data needs to be handled
    def me(request: Request, token: str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        

        token_data = TokenTools.check_token(token)
        if not token_data : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
        )



        etatDeCnx = token_data['state']
        # print ( 'hamouddaaa',token_data['id'])
        user_1 = odooDatabase.execute_kw('info.cnx', 'read', [token_data['id']])
        if not user_1:
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
        )

        if etatDeCnx == 'candidate' :
            user_2 = odooDatabase.execute_kw('partner.candidate', 'read', [user_1[0]['candidate_id'][0]], {'fields': ['name','categorie_id', 'commune_id', 'state_id','name_magasin','state','email','phone']})	
      

            ready_user = CondidateData(
                id = user_2[0].get('id'),
                idHelp=token_data['id'],
                nom = user_2[0].get('name'),
                tel = user_2[0].get('phone'),
                raisonSociale = user_2[0].get('name_magasin') if user_2[0].get('name_magasin') else None ,
                adresse = user_2[0].get('street') if user_2[0].get('street') else None,
                email = user_2[0].get('email') if user_2[0].get('email') else None ,
                natureCommerce = user_2[0]['categorie_id'][1] if user_2[0]['categorie_id'] else None,
                ville = user_2[0]['commune_id'][1] if user_2[0]['commune_id'] else None,
                wilaya= user_2[0]['state_id'][1] if user_2[0]['state_id'] else None,
                etatCondidat = etatDeCnx if etatDeCnx else None
                
            )

            return {
                "status" : True,
                "token" : token,
                "data": ready_user.dict() 
            }
        elif etatDeCnx == 'partner' :
            
            user_2 = odooDatabase.execute_kw('res.partner', 'read', [user_1[0]['partner_id'][0]], {'fields': ['id','name', 'name_magasin', 'categorie_id', 'commune_id', 'street','code','etoile','nbr_points', 'state_id','new_tlp1']})	
            full_user = {**user_1[0],**user_2[0]}
            social_media = odooDatabase.execute_kw('reseau.sociaux', 'search_read',[[['iduser', '=', token_data['id']]],['id','type','lien_profil']])
            ready_social_media = []

            for social in social_media:
                typeSocialMedia = next((smt for smt in SocialMediaType if smt.value == social['type']), None)
                ready_social_media.append(SocialMedia(id=social['id'], type=typeSocialMedia, url=social['lien_profil']))
        

            ready_images = []
            for image_id in full_user['images_magasins_ids']:
                image_url = f"{odooDatabase.base_url}/web/image/images.magasins/{image_id}/image"
                ready_images.append(Image(id=image_id, image=image_url))
            
                # Liste des champs à vérifier

            
            fields_to_check = [
                'id','name','telephone', 'name_magasin', 'street', 'email',
                'categorie_id', 'state_id', 'commune_id', 'images_magasins_ids', 'reseau_sociaux_ids','new_tlp1'] #Ajouter fields localisation
                
            # Calcul du pourcentage de profil rempli
            filled_fields = sum(1 for field in fields_to_check if full_user.get(field))
            
            total_fields = len(fields_to_check)

            result = get_delegues_for_detailant( full_user['id'],odooDatabase)
        
            ready_user = UserData(
                id=full_user.get('id'),
                idHelp=token_data['id'],
                nom=full_user.get('name') if full_user.get('name') else None,
                tel=full_user.get('telephone') if full_user.get('telephone') else None,
                raisonSociale=full_user.get('name_magasin') if full_user.get('name_magasin') else None,
                adresse=full_user.get('street') if full_user.get('street') else None  ,
                email=full_user.get('email') if full_user.get('email') else None ,
                idDetaillant=full_user.get('code') if full_user.get('code') else None ,
                niveauDetaillant=int(full_user.get('etoile', 0)) - 1 if full_user.get('etoile') else None,
                pointsDetaillant=int(full_user.get('nbr_points', 0)) if full_user.get('nbr_points') else None,
                natureCommerce=full_user.get('categorie_id', [None, None])[1] if full_user.get('categorie_id') else None,
                ville = full_user.get('commune_id', [None, None])[1] if full_user.get('commune_id') else None,
                wilaya=full_user.get('state_id', [None, None])[1] if full_user.get('state_id') else None,
                pourcentageNiveau=80,
                pourcentageProfil=int((filled_fields / total_fields) * 100) if total_fields > 0 else 0,
                socialMedia=ready_social_media,
                images=ready_images,
                otherTel=full_user.get('new_tlp1') if full_user.get('new_tlp1') else None ,
                delegue=result.get('delegues') if result.get('delegues') else None,
                etatCondidat = etatDeCnx if etatDeCnx else None

            )


            return {
                "status": True,
                "data": ready_user.dict()
            }

        
    @staticmethod # Ready
    def login(request: Request,UserLogin:dict):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        
        bloque = odooDatabase.execute_kw('info.cnx', 'search', [[['telephone', '=', UserLogin.phone],['active', '=', "False"]]])

        if not bloque:
            raise HTTPException(
                status_code=422, 
                detail="detaillant bloquee"
            )

        det = odooDatabase.execute_kw('info.cnx', 'search', [[['telephone', '=', UserLogin.phone]]])
        # print ( "103333333333333333333333333333",det)

      

        users = None
        if det:
            users = odooDatabase.execute_kw('info.cnx', 'read', [det], {'fields': ['telephone','password','id','id_user','email','images_magasins_ids','state','partner_id','candidate_id']})
        if not users:
            raise HTTPException(
                status_code=422, 
                detail="Numéro de téléphone introuvable"
            )
        hashed=Password.get_password_hash(UserLogin.password)
        

        
        

        try:
            if not Password.verify_password(UserLogin.password, users[0]['password']):
                raise HTTPException(
                    status_code=422, 
                    detail="Mot de passe incorrect"
                )
        except UnknownHashError:
            raise HTTPException(
                status_code=400, 
                detail="Le format du mot de passe est invalide ou bien le hachage est mal fait"
            )

        user = users[0]

        
        bb=historiqueConnexionAndActions(True)
        


        if ( user['state']=='candidate'):

            Condidat = odooDatabase.execute_kw('partner.candidate', 'read', [user['candidate_id'][0]], {'fields': ['name','categorie_id', 'commune_id', 'state_id','name_magasin','state','email','phone']})
            dat=TokenData(id=user["id"],telephone=user['telephone'], state=user['state']).dict()

            access_token_expires = timedelta(days=1) 
            token= TokenTools.generate_token(data=dat,expires_delta=access_token_expires)

            yy=TokenTools.check_token(token)

            ready_user = CondidateData(
                id = Condidat[0].get('id'),
                idHelp=det[0],
                nom = Condidat[0].get('name'),
                tel = Condidat[0].get('phone'),
                raisonSociale = Condidat[0].get('name_magasin') if Condidat[0].get('name_magasin') else None ,
                adresse = Condidat[0].get('street') if Condidat[0].get('street') else None,
                email = Condidat[0].get('email') if Condidat[0].get('email') else None ,
                natureCommerce = Condidat[0]['categorie_id'][1] if Condidat[0]['categorie_id'] else None,
                ville = Condidat[0]['commune_id'][1] if Condidat[0]['commune_id'] else None,
                wilaya= Condidat[0]['state_id'][1] if Condidat[0]['state_id'] else None,
                etatCondidat = user['state'] if user['state'] else None
                
            )

            return {
                "status" : True,
                "token" : token,
                "data": ready_user.dict() 
            }

        else:


            detailant = odooDatabase.execute_kw('res.partner', 'read', [user['partner_id'][0]], {'fields': ['code','name','categorie_id', 'commune_id', 'street','code','etoile','nbr_points', 'state_id','new_tlp1','name_magasin']})

            dat=TokenData(id=user["id"],telephone=user['telephone'], state=user['state']).dict()
     
            access_token_expires = timedelta(days=30) 
            token= TokenTools.generate_token(data=dat,expires_delta=access_token_expires)
            yy=TokenTools.check_token(token)
            
            
            
            ready_images = []
            for image_id in users[0]['images_magasins_ids']:
                image_url = f"{odooDatabase.base_url}/web/image/images.magasins/{image_id}/image"
                ready_images.append(Image(id=image_id, image=image_url))
            
            print("imaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaggge", ready_images)

            
            social_media = odooDatabase.execute_kw('reseau.sociaux', 'search_read',[[['iduser', '=', users[0]['id']]],['id','type','lien_profil']])
            ready_social_media = []

            
            for social in social_media:
                typeSocialMedia = next((smt for smt in SocialMediaType if smt.value == social['type']), None)
                ready_social_media.append(SocialMedia(id=social['id'], type=typeSocialMedia, url=social['lien_profil']))
            

            result = get_delegues_for_detailant(users[0]['partner_id'][0] ,odooDatabase)
            
        
            ready_user = UserData(
                id = users[0]['partner_id'][0],
                idHelp=det[0],
                nom = detailant[0].get('name'),
                tel = users[0].get('telephone'),
                raisonSociale = detailant[0].get('name_magasin') if detailant[0].get('name_magasin') else None ,
                adresse = detailant[0].get('street') if detailant[0].get('street') else None,
                email = users[0].get('email') if users[0].get('email') else None ,
                idDetaillant = detailant[0].get('code') if detailant[0].get('code') else None ,
                niveauDetaillant = int(detailant[0].get('etoile'))-1,
                pointsDetaillant = detailant[0].get('nbr_points'),
                natureCommerce = detailant[0]['categorie_id'][1] if detailant[0]['categorie_id'] else None,
                ville = detailant[0]['commune_id'][1] if detailant[0]['commune_id'] else None,
                wilaya= detailant[0]['state_id'][1] if detailant[0]['state_id'] else None,
                pourcentageNiveau=80,
                # pourcentageProfil=int((filled_fields / total_fields) * 100),
                socialMedia = ready_social_media,
                images= ready_images,
                otherTel = detailant[0].get('new_tlp1') if detailant[0].get('new_tlp1') else None ,
                delegue =result.get('delegues'),
                etatCondidat=user['state'] if user['state'] else None
                
            )
            return {
                "status": True,
                "token": token,
                "data": ready_user.dict()
            }


    
    @staticmethod # Ready
    def inscription(request: Request, data: RegisterUser):
        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        
    
        # Verifier si le code détaillant existe sur la table res.partner
        det_id = odooDatabase.execute_kw('res.partner', 'search_read',[[['code', '=', data.codeDet]],['code','phone']])
      
        if not det_id:
            raise HTTPException(
                status_code=422, 
                detail="Code détaillant n'existe pas"
            )
        if data.phone != det_id[0]['phone'] :
            raise HTTPException(
                status_code=422, 
                detail="Numéro Téléphone Erroné"
            )
       
        # Verifier si le numéro de téléphone est déjà utilisé ou si le code détaillant est déjà associé à un compte
        det = odooDatabase.execute_kw('info.cnx', 'search_read', [['|',['telephone', '=', data.phone],['id_user', '=', det_id[0]['id']]]])
      
        if ( True in [det[i]['telephone'] == data.phone for i in range(len(det))] ):
            raise HTTPException(
                status_code=422, 
                detail="Numéro de téléphone déjà utilisé"
            )
        elif ( True in [det[i]['id_user'][0] == det_id[0]['id'] for i in range(len(det))] ):
            raise HTTPException(
                status_code=422, 
                detail="Code détaillant déjà associé à un compte"
            )
            
            
        # Créer un enregistrement dans la nouvelle table
        record_mobile_id ,passwordPlain = create_record_in_new_table_respartner(odooDatabase, det_id[0], phone=data.phone)

        # print ( "salahhhhhhhhhhhhhhhhhhhhhhhhhh",passwordPlain)

        detaillant_adher = odooDatabase.execute_kw('info.cnx', 'read', [[record_mobile_id], ['id','telephone','password','state']])
        
        if not record_mobile_id:
            raise HTTPException(
                status_code=503,
                detail="Erreur de connexion avec le serveur, veuillez réessayer"
            )
        return {
            "status": True,
            "password" : passwordPlain ,
            "message": "Votre mot de passe vous a été envoyé par SMS"
        }



    
    @staticmethod # Ready -- check one case brk
    def adhesion(request: Request, data : AdhererUser ) :  
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        det = odooDatabase.execute_kw('info.cnx', 'search', [[['telephone', '=', data.phone_compte]]])
        if det:
            raise HTTPException(
                status_code=422,
                detail="Ce numéro de téléphone est déjà associé à un compte"
            ) 
        
        region_id, pf_id = 13, 6 #Poour les tests brk on verra après k
        vals = {
            'name': data.name,
            'categorie_id' : data.categorie_id,
            'name_magasin': data.name_magasin,
            'state_id': data.state_id,
            # 'country_id': data.country_id,
            'commune_id': data.commune_id,
            'phone': data.phone_compte
            # 'state':'draft'
            # 'region_id': region_id,
            # 'pf_id': pf_id,
            # 'etoile': 2,    # Hard coded, un detaillant inscrit sera directement au niv 1 
            
            # 'company_type': 'company',
            # 'nature': [(6, 0, [2])],  # Relation many2many avec res.partner.nature.multiple
            # 'user_id': odooDatabase.uid,
            # 'commentaires':"TEST API VIA MobileApp"
        }

        filtered_vals = remove_none_values(vals)
        # print ("nommmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm",filtered_vals )
        

        new_detaillant_id = odooDatabase.execute_kw( 'partner.candidate','create', [filtered_vals])
        
        # Créer le nouveau détaillant dans Odoo
        # new_detaillant_id = odooDatabase.execute_kw( 'res.partner', 'create', [filtered_vals])
        
        if not new_detaillant_id :
            raise HTTPException(
                status_code=503,
                detail="Erreur de connexion avec le serveur, veuillez réessayer"
            )
        
        # Lire les détails du nouveau détaillant créé
        new_detaillant = odooDatabase.execute_kw('partner.candidate', 'read', [[new_detaillant_id], ['id']])[0]

        # Créer l'enregistrement dans la nouvelle table
        detNvlTable_id ,passwordPlain= create_record_in_new_table(odooDatabase, new_detaillant, phone=data.phone_compte)

        # print("salahhhhhhhhhhhhhhhhhhhhhhhh",passwordPlain)

        info_envoyer = odooDatabase.execute_kw('info.cnx', 'read', [[detNvlTable_id]])
        
        if not detNvlTable_id:
            raise HTTPException(
                status_code=503,
                detail="Erreur de connexion avec le serveur, veuillez réessayer"
            )

        return {
            "status": True,
            "password" : passwordPlain,
            "message": "Votre mot de passe et votre code détaillant vous ont été envoyé par SMS"
        }

    @staticmethod
    def motDePasseOublie(request: Request, data: ForgotPwd):
        odooDatabase: OdooDatabase = request.app.state.odooDatabase

        # Étape 1 : Trouver l'utilisateur dans `info.cnx`
        user_data = odooDatabase.execute_kw(
            "info.cnx", "search_read",
            [[["telephone", "=", data.phone]]],
            {"fields": ["id", "login", "telephone", "candidate_id", "partner_id"]}
        )

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        user = user_data[0]
        info_cnx_id = user["id"]

        # Étape 2 : Récupérer les noms du candidat et du partenaire en une seule requête
        record_ids = []
        if user.get("candidate_id"):
            record_ids.append(("partner.candidate", user["candidate_id"][0]))
        if user.get("partner_id"):
            record_ids.append(("res.partner", user["partner_id"][0]))

        record_names = {}
        if record_ids:
            for model, rec_id in record_ids:
                records = odooDatabase.execute_kw(model, "read", [[rec_id]], {"fields": ["name"]})
                if records:
                    record_names[model] = records[0]["name"]

        user_name = record_names.get("partner.candidate") or record_names.get("res.partner") or "Unknown"

        # Étape 3 : Récupérer `res_model_id` et `activity_type_id` en une seule requête
        models_data = odooDatabase.execute_kw(
            "ir.model", "search_read",
            [[["model", "=", "info.cnx"]]],
            {"fields": ["id"]}
        )

        activity_type_data = odooDatabase.execute_kw(
            "mail.activity.type", "search_read",
            [[["category", "=", "default"]]],
            {"fields": ["id"]}
        )

        if not models_data or not activity_type_data:
            raise HTTPException(status_code=400, detail="Required models not found in Odoo.")

        res_model_id = models_data[0]["id"]
        activity_type_id = activity_type_data[0]["id"]

        # Étape 4 : Récupérer le groupe ERP Manager et ses utilisateurs en une seule requête
        group_data = odooDatabase.execute_kw(
            "ir.model.data", "search_read",
            [[["module", "=", "base"], ["name", "=", "group_erp_manager"]]],
            {"fields": ["res_id"]}
        )

        if not group_data:
            raise HTTPException(status_code=422, detail="ERP Manager group not found")

        group_id = group_data[0]["res_id"]

        erp_managers = odooDatabase.execute_kw(
            "res.users", "search_read",
            [[["groups_id", "in", [group_id]]]],
            {"fields": ["id"]}
        )

        if not erp_managers:
            raise HTTPException(status_code=400, detail="No ERP managers found.")

        manager_ids = [manager["id"] for manager in erp_managers]

        # Étape 5 : Création des activités en une seule requête
        activities = [{
            "res_model_id": res_model_id,
            "res_id": info_cnx_id,
            "activity_type_id": activity_type_id,
            "summary": f"Demande de réinitialisation du mot de passe ({user_name}).",
            "note": f"""
                <p><b>Utilisateur :</b> {user_name}<br>
                <b>Téléphone :</b> {user["telephone"]}<br>
                <b>Action requise :</b> Générer un nouveau mot de passe et l'envoyer.</p>
            """,
            "user_id": manager_id,
        } for manager_id in manager_ids]

        odooDatabase.execute_kw("mail.activity", "create", [activities])

        return {
            "status": True,
            "message": "Votre nouveau mot de passe vous a été envoyé par SMS"
        }

















































#message 

    @staticmethod
    def mdpoublier(request: Request, data: ForgotPwd):
        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        # Étape 1 : Trouver l'utilisateur dans `info.cnx`
        user_data = odooDatabase.execute_kw(
            "info.cnx", "search_read",
            [[["telephone", "=", data.phone]]],
            {"fields": ["id", "login", "telephone", "candidate_id", "partner_id"]}
        )

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        otp = str(random.randint(100000, 999999))
        r.setex(f"otp:{data.phone}", 300, otp)  
        print ( "==========================================",otp)


        # send_sms(data.phone, f"Votre code OTP est : {otp}")
        
        return {"message": "OTP envoyé par SMS"}

    def send_sms(to, message):
        account_sid = "TON_SID"
        auth_token = "TON_TOKEN"
        # client = Client(account_sid, auth_token)

        client.messages.create(
            body=message,
            from_="+1415XXXXXXX",  # numéro Twilio
            to=to
        )
        return True



    def verify_otp(request: Request,data: OTPVerify):
        print ( "covidddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",data)
        odooDatabase: OdooDatabase = request.app.state.odooDatabase
        # Étape 1 : Trouver l'utilisateur dans `info.cnx`
        user_data = odooDatabase.execute_kw(
            "info.cnx", "search_read",
            [[["telephone", "=", data.phone]]],
            {"fields": ["id", "login", "telephone", "candidate_id", "partner_id"]}
        )

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        key = f"otp:{data.phone}"
        stored_otp = r.get(key)

        print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",stored_otp)
        if not stored_otp:
            raise HTTPException(status_code=400, detail="OTP expiré ou inexistant")

        if stored_otp != data.otp:
            raise HTTPException(status_code=400, detail="OTP incorrect")

        r.delete(key)
        return {"message": "OTP validé avec succès"}


    def newpassword(request: Request,data: NewPassword):
        print ( "covidddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",data)
        odooDatabase: OdooDatabase = request.app.state.odooDatabase

        # user_data = odooDatabase.execute_kw(
        #     "info.cnx", "search_read",
        #     [[["telephone", "=", data.phone]]],
        #     {"fields": ["id", "login", "telephone", "candidate_id", "partner_id"]}
        # )
        # if not user_data:
        #     raise HTTPException(status_code=404, detail="User not found")



        record_ids = odooDatabase.execute_kw(
            'info.cnx', 
            'search', 
            [[['telephone', '=',  data.phone]]]
        )
        if not record_ids:
            raise HTTPException(
                status_code=404,
                detail={"status": False, "error": "Aucun enregistrement trouvé pour ce téléphone"}
            )


        hashed_password = Password.get_password_hash(data.password)
        print ( "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa === hada password new =====",hashed_password)
        odooDatabase.execute_kw('info.cnx', 'write', [record_ids, {'password': hashed_password}])

        return {"status": True, "message": "Mot de passe mis à jour"}
        
