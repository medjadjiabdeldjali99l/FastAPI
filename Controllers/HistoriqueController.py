from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt
from collections import defaultdict
from datetime import datetime

class HistoriqueController():
    
    @staticmethod # Ready
    def get_all_points( request : Request, token : str,id_det:int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )

        points = odooDatabase.execute_kw(
            'suivi.points.pdd',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['partner_id', '=', id_det],['state','=','done']]],
            {'fields': ['action_id','date_action','points']} 
        )
        # print ( "plannnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn",points)
        # print("swayliiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", points, len (points))

        for i in points:
            i['code']="Action "+ str(i['action_id'][0])
            i['name']=i['action_id'][1]


        print("anuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu",points)

        result = defaultdict(list)

        for action in points:
            date_str = action['date_action']
            year = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").year
            result["année_"+str(year)].append(action)

        # Convertir en dict classique si tu veux
        result = dict(result)

        # Affichage
        from pprint import pprint
        pprint(result)


        # l = [i['action_id'][0] for i in points]



        # action = odooDatabase.execute_kw(
        #     'crm.actions.pdd',  # Modèle Odoo
        #     'search_read',  # Méthode pour rechercher et lire
        #     [[['id', 'in', l]]],  # Domaine vide -> sélectionne tous les enregistrements
        #     {'fields': ['id','code','points']}  # Champs à récupérer
        # )


        # for i in action:
        #     for j in points:
        #         if j['action_id'][0]==i['id']:
        #             i['date_action']=j['date_action']
        
        



        try:    
            return points
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
