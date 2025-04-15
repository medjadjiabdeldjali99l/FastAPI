from fastapi import Request , HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt
from datetime import datetime, timedelta, timezone

DELEGUE_GROUP_XML_ID="crm_plv.group_plvp_commercial"
SUP_GROUP_XML_ID="crm_plv.group_plvp_superviseur"


def get_group_id(group_xml_id ,odooDatabase ):
    group = odooDatabase.execute_kw(
        'ir.model.data', 'search_read',
        [[('model', '=', 'res.groups'),
          ('module', '=', group_xml_id.split('.')[0]),
          ('name', '=', group_xml_id.split('.')[1])]],
        {'fields': ['res_id']}
    )
    return group[0]['res_id'] if group else None



class AnnuaireController():
    @staticmethod # Ready
    def get_contacts(request : Request,token:Token ,fonction:str, idWilaya:int,search:str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase

        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )
        
        if fonction == 'sup':
            sup_group = odooDatabase.execute_kw(
                'ir.model.data', 'search_read',
                [[('model', '=', 'res.groups'), 
                ('module', '=', SUP_GROUP_XML_ID.split('.')[0]), 
                ('name', '=', SUP_GROUP_XML_ID.split('.')[1])]],
                {'fields': ['res_id']}
            )
            sup_group_id = sup_group[0]['res_id']
            domain=[('groups_id', 'in', [sup_group_id])]
            if idWilaya:
                wilaya = odooDatabase.execute_kw(
                    'res.country.state',  # Modèle Odoo
                    'search_read',  # Méthode utilisée pour la recherche et la lecture
                    [[['country_id', '=',62 ],['id','=',idWilaya]]],
                    {'fields': ['id','name','code','pf_ids']} 
                )
                # domain.append(tuple(wilaya[0]['pf_ids']))
                domain.append(('pf_ids','in',wilaya[0]['pf_ids'][0]))
            users_in_sup_group = odooDatabase.execute_kw(
                'res.users', 'search_read',
                [domain],  # Filtrer par le groupe
                {'fields': ['id',  'login','region_id','pf_ids','partner_id']}
            )

            wilaya = odooDatabase.execute_kw(
                    'res.country.state',  # Modèle Odoo
                    'search_read',  # Méthode utilisée pour la recherche et la lecture
                    [[['country_id', '=',62 ]]],
                    {'fields': ['pf_ids','name']} 
                )
            for i in users_in_sup_group:
                l=[]
                for k in i['pf_ids'] :
                    for j in wilaya :
                        if k in j['pf_ids']:
                            l.append(j['name'])
                    i['wilaya']=l

            
            # Étape 3 : Récupérer les employés liés à ces utilisateurs
            sup_user_ids = [user['partner_id'][0] for user in users_in_sup_group]
            domain=[('id', 'in', sup_user_ids)]
            if search:
                domain.append(('name', 'ilike', search.upper()))

            sup_employees = odooDatabase.execute_kw(
                'res.partner', 'search_read',
                [domain], # Associer employé à l'utilisateur
                {'fields': ['id', 'name', 'function', 'user_id','email','phone']}
            )


            for i in users_in_sup_group:
                for j in sup_employees:
                    if i['partner_id'][0]==j['id']:
                        if i['region_id']:
                            j['rg']=i['region_id'][1]
                            break
        

            for i in users_in_sup_group:
                for j in sup_employees:
                    if i['partner_id'][0]==j['id']:
                        j['region']=i['wilaya']
                        break

            annuaire_data= [
                {
                    'name': employee['name'],
                    'id': employee['id'],
                    'job_title': employee['function'],
                    'work_email': employee['email'],
                    'telephone': employee['phone'],
                    'region':employee['rg'],
                    'wilaya':employee['region']
                }
                for employee in sup_employees
            ]
            try:    
                return annuaire_data
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        elif fonction == 'delegue':

            delegue_group = odooDatabase.execute_kw(
                'ir.model.data', 'search_read',
                [[('model', '=', 'res.groups'), 
                ('module', '=', DELEGUE_GROUP_XML_ID.split('.')[0]), 
                ('name', '=', DELEGUE_GROUP_XML_ID.split('.')[1])]],
                {'fields': ['res_id']}
            )
            delegue_group_id = delegue_group[0]['res_id']

            domain=[('groups_id', 'in', [delegue_group_id])]
            if idWilaya:
                wilaya = odooDatabase.execute_kw(
                    'res.country.state',  # Modèle Odoo
                    'search_read',  # Méthode utilisée pour la recherche et la lecture
                    [[['country_id', '=',62 ],['id','=',idWilaya]]],
                    {'fields': ['id','name','code','pf_ids']} 
                )

                domain.append(('pf_ids','in',wilaya[0]['pf_ids'][0]))

            

            users_in_delegue_group = odooDatabase.execute_kw(
                'res.users', 'search_read',
                [domain],  # Filtrer par le groupe
                {'fields': ['id',  'login','region_id','pf_ids','partner_id']}
            )

            wilaya = odooDatabase.execute_kw(
                    'res.country.state',  # Modèle Odoo
                    'search_read',  # Méthode utilisée pour la recherche et la lecture
                    [[['country_id', '=',62 ]]],
                    {'fields': ['pf_ids','name']} 
                )
            for i in users_in_delegue_group :
                l=[]
                for k in i['pf_ids'] :
                    for j in wilaya :
                        if k in j['pf_ids']:
                            l.append(j['name'])
                    i['wilaya']=l

            
            # Étape 3 : Récupérer les employés liés à ces utilisateurs
            delegue_user_ids = [user['partner_id'][0] for user in users_in_delegue_group]
            domain=[('id', 'in', delegue_user_ids)]
            if search:
                domain.append(('name', 'ilike', search.upper()))
            delegue_employees = odooDatabase.execute_kw(
                'res.partner', 'search_read',
                [domain],  # Associer employé à l'utilisateur
                {'fields': ['id', 'name', 'function', 'user_id','email','phone']}
            )
            
            for i in users_in_delegue_group:
                for j in delegue_employees:
                    if i['partner_id'][0]==j['id']:
                        if i['region_id']:
                            j['rg']=i['region_id'][1]
                            break

            for i in users_in_delegue_group:
                for j in delegue_employees:
                    if i['partner_id'][0]==j['id']:
                        j['region']=i['wilaya']
                        break

            annuaire_data= [
                {
                    'name': employee['name'],
                    'id': employee['id'],
                    'job_title': employee['function'],
                    'work_email': employee['email'],
                    'telephone': employee['phone'],
                    'region':employee['rg'],
                    'wilaya':employee['region'],
                }
                for employee in delegue_employees
            ]
            try:    
                return annuaire_data
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))




        else :
            DELEGUE_GROUP_ID = get_group_id(DELEGUE_GROUP_XML_ID,odooDatabase)
            SUP_GROUP_ID = get_group_id(SUP_GROUP_XML_ID,odooDatabase)
            if not DELEGUE_GROUP_ID or not SUP_GROUP_ID:
                raise HTTPException(
                    status_code=422,
                    detail="Impossible de récupérer les IDs des groupes."
                )
            else:

                # Obtenir les utilisateurs associés aux deux groupes
                domain=[('groups_id', 'in', [DELEGUE_GROUP_ID, SUP_GROUP_ID])]
                if idWilaya:
                    wilaya = odooDatabase.execute_kw(
                        'res.country.state',  # Modèle Odoo
                        'search_read',  # Méthode utilisée pour la recherche et la lecture
                        [[['country_id', '=',62 ],['id','=',idWilaya]]],
                        {'fields': ['id','name','code','pf_ids']} 
                    )

                    domain.append(('pf_ids','in',wilaya[0]['pf_ids'][0]))
                    
                users = odooDatabase.execute_kw(
                    'res.users', 'search_read',
                    [domain],
                    {'fields': ['id', 'login', 'region_id','pf_ids','partner_id']}
                )

                if not users:
                    raise HTTPException(
                        status_code=422,
                        detail="Aucun utilisateur trouvé dans les groupes spécifiés."
                        )
                    
                else:

                    wilaya = odooDatabase.execute_kw(
                        'res.country.state',  # Modèle Odoo
                        'search_read',  # Méthode utilisée pour la recherche et la lecture
                        [[['country_id', '=',62 ]]],
                        {'fields': ['pf_ids','name']} 
                    )
                    for i in users  :
                        l=[]
                        for k in i['pf_ids'] :
                            for j in wilaya :
                                if k in j['pf_ids']:
                                    l.append(j['name'])
                            i['wilaya']=l
                    
                    # Obtenir les employés associés aux utilisateurs trouvés
                    user_ids = [user['partner_id'][0] for user in users]

                    domain=[('id', 'in', user_ids)]
                    if search:
                        domain.append(('name', 'like', search.upper()))
                    employees = odooDatabase.execute_kw(
                        'res.partner', 'search_read',
                        [domain],
                        {'fields': ['id',  'name', 'function', 'user_id','email','phone']}
                    )
                    
                    # for i in users :
                    #     if not i['region_id']:
                    #         print ( i)
                    

                    for i in users:
                        for j in employees:
                            if i['partner_id'][0]==j['id']:
                                if i['region_id']:
                                    j['rg']=i['region_id'][1]
                                    break

                    for i in users:
                        for j in employees:
                            if i['partner_id'][0]==j['id']:
                                j['region']=i['wilaya']
                                break
                        

            
            annuaire_data= [
                {
                    'name': employee['name'] if employee['name'] else None ,
                    'id': employee.get('id') if employee.get('id') else None ,
                    'job_title': employee.get('function') if employee.get('function') else None,
                    'work_email': employee.get('email') if employee.get('email') else None,
                    'telephone': employee.get('phone') if employee.get('phone') else None ,
                    'region':employee.get('rg') if employee.get('rg') else None ,
                    'wilaya' : employee.get('region') if employee.get('region') else None ,
                }
                for employee in employees
            ]

            
            try:    
                return annuaire_data
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

            
