from fastapi import Request ,HTTPException 
from typing import Optional,List
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
from datetime import datetime, timedelta
import jwt
import logging
from Tools.ImageCompress import convert_base64_to_webp
_logger = logging.getLogger(__name__)

DELEGUE_GROUP_XML_ID = "crm_plv.group_plvp_commercial"
SUP_GROUP_XML_ID = "crm_plv.group_plvp_superviseur"
DEFAULT_ACTIVITY_TYPE_XML_ID = "mail.mail_activity_data_todo"
DEFAULT_DEADLINE_DAYS = 3


def get_activity_type_id(odooDatabase:OdooDatabase):
    return odooDatabase.execute_kw( 'ir.model.data', 'xmlid_to_res_id', [DEFAULT_ACTIVITY_TYPE_XML_ID])

def get_model_id(model_name,odooDatabase:OdooDatabase):
    model_ids = odooDatabase.execute_kw( 'ir.model', 'search', [[('model', '=', model_name)]])
    return model_ids[0] if model_ids else None


def get_users_same_region_portfolio(id_det,odooDatabase:OdooDatabase):
    """Récupère les utilisateurs ayant le même portefeuille et région que le détaillant"""

    # 🔹 Récupération des infos du détaillant
    partner = odooDatabase.execute_kw('res.partner', 'read', [id_det],
                                {'fields': ['name', 'pf_id', 'region_id']})
    
    

    if not partner:
        raise HTTPException(status_code=404, detail="Détaillant non trouvé")

    partner_name = partner[0].get('name', 'Inconnu')

    # pf_id = partner[0].get('pf_id', [None])[0]
    # region_id = partner[0].get('region_id', [None])[0]
    pf_id = partner[0].get('pf_id', [None])[0] or None if partner and isinstance(partner[0], dict) else None
    region_id = partner[0].get('region_id', [None])[0] or None if partner and isinstance(partner[0], dict) else None


    if not pf_id or not region_id:
        raise HTTPException(status_code=400,
                            detail=f"Le détaillant {partner_name} (ID: {id_det}) n'est pas associé à un portefeuille ou une région valide")

    # 🔹 Récupération des utilisateurs délégués et superviseurs
    delegue_group_id = odooDatabase.execute_kw( 'ir.model.data', 'xmlid_to_res_id', [DELEGUE_GROUP_XML_ID])
    sup_group_id = odooDatabase.execute_kw( 'ir.model.data', 'xmlid_to_res_id', [SUP_GROUP_XML_ID])

    user_ids = odooDatabase.execute_kw( 'res.users', 'search', [[
        '|',
        ('groups_id', '=', delegue_group_id),
        ('groups_id', '=', sup_group_id),
        ('pf_ids', 'in', [pf_id]),
        ('region_id', '=', region_id)
    ]])

    cc = odooDatabase.execute_kw( 'res.users', 'search_read', [[
        '|',
        ('groups_id', '=', delegue_group_id),
        ('groups_id', '=', sup_group_id),
        ('pf_ids', 'in', [pf_id]),
        ('region_id', '=', region_id)
    ]],
    {'fields': ['id','login']})

    # Log des utilisateurs notifiés
    _logger.info(
    f" Utilisateurs notifiés pour la commande présentoir du détaillant '{partner_name}' (ID: {id_det}): {user_ids}")

    return user_ids, partner_name


def get_espace_type_name(marquage_id,odooDatabase:OdooDatabase):
    liste_marquage_ids=[]
    print("************************",marquage_id)
    for i in marquage_id:
        print("hada id marquage",i)
        espace = odooDatabase.execute_kw('nomenclature.lots', 'read', [int(i)], {'fields': ['name']})
        liste_marquage_ids.append(espace)
    names = [item[0]['name'] for item in liste_marquage_ids]
    print ( "m9asssssssssssssssssssss",names)

    return names

def create_todo_activity(request,odooDatabase:OdooDatabase,idDet,listemarquages):
    try:
        user_ids, partner_name = get_users_same_region_portfolio(idDet,odooDatabase)
        espace_name = get_espace_type_name(listemarquages ,odooDatabase)

        if not user_ids:
            raise HTTPException(status_code=404, detail="Aucun utilisateur correspondant trouvé")

        activity_type_id = get_activity_type_id(odooDatabase)
        model_id = get_model_id("res.partner",odooDatabase)
        if not model_id:
            raise HTTPException(status_code=500, detail="Impossible de récupérer l'ID du modèle res.partner")

        deadline_date = (datetime.now() + timedelta(days=DEFAULT_DEADLINE_DAYS)).strftime('%Y-%m-%d')
        activity_ids = []

        for user_id in user_ids:
            activity_id = odooDatabase.execute_kw('mail.activity', 'create', [{
                'res_model_id': model_id,
                'res_id': idDet,
                'activity_type_id': activity_type_id,
                'summary': 'Commande Marquage à préparer',
                'note': f"""
                    <p><strong>Détaillant:</strong> {partner_name}</p>
                    <p><strong>Marquage demandé:</strong> {espace_name}</p>
                """,
                'user_id': user_id,
                'date_deadline': deadline_date,
            }])
            activity_ids.append(activity_id)

        return activity_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))










class MarkingController():
    #jai ajouter le niveau id il reste juste implementation des condition et de cote front 
    @staticmethod # Ready
    def get_all_markings( request : Request, token : str ,niveauDet:int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )

        print ( " niveau id============================================================== ",niveauDet)
        # cc = odooDatabase.execute_kw(
        #     'images.magasins',  # Modèle Odoo
        #     'search_read',  # Méthode utilisée pour la recherche et la lecture
        #     [[]],
        #     {'fields': ['id','name','image']} 
      
        # )
        # print ('ccccccccccccccccccccccccccccc' ,cc)
        

        # all_lots = odooDatabase.execute_kw(
        #     'nomenclature.lots',  # Modèle Odoo
        #     'search_read',  # Méthode utilisée pour la recherche et la lecture
        #     [[('poids','!=',1.0),('niveau_id','<',niveauDet),('niveau_id','!=',0)]],
        #     {'fields': ['id','name','description','obligatoire','niveau_id','poids']} 
        # )
        # all_lots = odooDatabase.execute_kw(
        #     'nomenclature.lots',
        #     'search_read',
        #     [[
        #         '|',
        #         '&',
        #         ('poids', '!=', 1.0),
        #         ('niveau_id', '<', niveauDet+1),
        #         ('niveau_id', '!=', False)
        #     ]],
        #     {'fields': ['id', 'name', 'description', 'obligatoire', 'niveau_id', 'poids']}
        # )

        all_lots = odooDatabase.execute_kw(
            'nomenclature.lots',
            'search_read',
            [[
                '|',
                ('niveau_id', '<=', niveauDet + 1),
                ('niveau_id', '=', False)
            ]],
            {'fields': ['id', 'name', 'description', 'obligatoire', 'niveau_id', 'poids']}
        )


        print (len(all_lots),"mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")

 
        try:    
            return all_lots
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))





    @staticmethod # Ready
    def get_marking_order(request : Request, idDet : int, listemarquages : Optional[List[str]]):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        
        print ( "==========================================================================*******==========================",idDet,listemarquages)
        if listemarquages and len(listemarquages) == 1 and ',' in listemarquages[0]:
            listemarquages = listemarquages[0].split(',')
        print("conversationnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn.",listemarquages)

        activity_ids = create_todo_activity(request ,odooDatabase,idDet ,listemarquages)
        return {"message": "Activités créées avec succès", "activity_ids": activity_ids}




        
        
    