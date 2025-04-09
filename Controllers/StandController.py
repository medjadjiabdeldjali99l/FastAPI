from fastapi import Request ,HTTPException
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

def get_espace_type_name(espace_type_id,odooDatabase:OdooDatabase):
    espace = odooDatabase.execute_kw('res.partner.espace.type', 'read', [espace_type_id], {'fields': ['name']})
    return espace[0]['name'] if espace else "Présentoir inconnu"

def create_todo_activity(request,odooDatabase:OdooDatabase,id_det,idStand):
    try:
        user_ids, partner_name = get_users_same_region_portfolio(id_det,odooDatabase)
        espace_name = get_espace_type_name(idStand ,odooDatabase)

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
                'res_id': id_det,
                'activity_type_id': activity_type_id,
                'summary': 'Commande Présentoir à préparer rachiiiiiiiiiid',
                'note': f"""
                    <p><strong>Détaillant:</strong> {partner_name}</p>
                    <p><strong>Présentoir demandé:</strong> {espace_name}</p>
                """,
                'user_id': user_id,
                'date_deadline': deadline_date,
            }])
            activity_ids.append(activity_id)

        return activity_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))











class StandController():
    
    @staticmethod # Ready
    def get_all_stand( request : Request, token : str,id_det:int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )


        plvp = odooDatabase.execute_kw(
            'crm.plv',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['partner_id', '=', id_det]]],
            {'fields': ['id','name','partner_id','delegue_id','espace_type_id','type_plvp_id']} 
      
        )
        #prochainment recuprer le nom de type_plvp_id

        

        l = [i['espace_type_id'][1] for i in plvp if 'espace_type_id' in i and i['espace_type_id']]

   
        
        u = [{'name': i} for i in l]
        

        try:    
            return u
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))




    @staticmethod # Ready
    def get_all_stands( request : Request, token : str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        all_plvp = odooDatabase.execute_kw(
            'sale.order.template',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[]],
            {'fields': ['id','name','description','number_of_articles','dimension']} 
        )
        if all_plvp:

            session_id = odooDatabase.session
            for i in all_plvp :
                    i['image'] = f"{odooDatabase.base_url}/web/image/sale.order.template/{i['id']}/image?session_id={session_id}"

            # for i in all_plvp:
            #     if i['image']:
            #         base64_image =  i['image'] 
            #         i['image'] = convert_base64_to_webp(base64_image)
            

        try:    
            return all_plvp
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @staticmethod # Ready
    def get_stands_order(request : Request, id_det : int, idStand : int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        
        activity_ids = create_todo_activity(request ,odooDatabase,id_det ,idStand)
        return {"message": "Activités créées avec succès", "activity_ids": activity_ids}



    @staticmethod # Ready
    def get_desc_stand( request : Request, token : str, idStand : int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        all_plvp = odooDatabase.execute_kw(
            'sale.order.template',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[('id','=',idStand)]],
            {'fields': ['id','name','montant_min','sale_order_template_line_ids','nombre_article']}       
        )
        if not all_plvp:
            raise HTTPException(
                status_code=422,  
                detail={"status": False, "error": "Plvp Introuvable"}
            )


        list_line=all_plvp[0]['sale_order_template_line_ids']
            
        line_in_plvp = odooDatabase.execute_kw(
            'sale.order.template.line',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[('id','in',list_line),('check','=','oui')]],
            {'fields': ['id','product_id','product_uom_qty','product_packaging']} 
        )
    
        descreption_lines_plvp = [
            {
                'id': i['id'],
                'product': i['product_id'][1],
                'product_qty': i['product_uom_qty'] ,
                'product_packaging': i['product_packaging'][1] if i['product_packaging'] else []
            }
            for i in line_in_plvp
        ]

        try:    
            return descreption_lines_plvp
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


