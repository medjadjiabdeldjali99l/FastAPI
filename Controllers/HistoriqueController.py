from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt


class HistoriqueController():
    
    @staticmethod # Ready
    def get_all_points( request : Request, token : str,id_det:int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )


        points = odooDatabase.execute_kw(
            'suivi.points.pdd',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['partner_id', '=', id_det]]],
            {'fields': ['action_id','date_action']} 
        )
        print("pointssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
        print(points ,len (points))

        l = [i['action_id'][0] for i in points]



        action = odooDatabase.execute_kw(
            'crm.actions.pdd',  # Modèle Odoo
            'search_read',  # Méthode pour rechercher et lire
            [[['id', 'in', l]]],  # Domaine vide -> sélectionne tous les enregistrements
            {'fields': ['code', 'name','points']}  # Champs à récupérer
        )
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        
        print(action)
        for i in action:
            for j in points:
                if j['action_id'][0]==i['id']:
                    i['date_action']=j['date_action']
        
        print("finallle versionnnnn")
        print(action)



        try:    
            return action
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
