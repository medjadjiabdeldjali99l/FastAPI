from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt

class StandController():
    
    @staticmethod # Ready
    def get_all_stand( request : Request, token : str,id_det:int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        print(id_det)

        plvp = odooDatabase.execute_kw(
            'crm.plv',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['partner_id', '=', id_det]]],
            {'fields': ['id','name','partner_id','delegue_id','espace_type_id']} 
      
        )
        # print("33333333333333333333")
        # print ( plvp)
        l=[]
        # for i in plvp:
        #     if i['espace_type_id']:
        #         l.append(i['espace_type_id'][1])

        l = [i['espace_type_id'][1] for i in plvp if 'espace_type_id' in i and i['espace_type_id']]

        print(l)
        
        u = [{'name': i} for i in l]
        

        

        # points = odooDatabase.execute_kw(
        #     'suivi.points.pdd',  # Modèle Odoo
        #     'search_read',  # Méthode utilisée pour la recherche et la lecture
        #     [[['partner_id', '=', id_det]]],
        #     {'fields': ['id','action_id','partner_id','user_id','region_id','pf_id','pf_id','points_valide','date_action','date_validation','state']} 
      
        # )
        # print("pointssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
        # print(points ,len (points))




        # pp = odooDatabase.execute_kw(
        #     'suivi.points.pdd',  # Modèle Odoo
        #     'search_read',  # Méthode utilisée pour la recherche et la lecture
        #     [[['partner_id', '=', id_det]]],
        #     {'fields': ['id','action_id','partner_id','user_id','region_id','pf_id','pf_id','points_valide','date_action','date_validation','state']} 
      
        # )
        # print("pointssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
        # print(pp ,len (pp))














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
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        all_plvp = odooDatabase.execute_kw(
            'sale.order.template',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[]],
            {'fields': ['id','name','montant_min']} 
      
        )
        print(all_plvp)




        try:    
            return all_plvp
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
