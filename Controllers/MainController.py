from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt



class MainController():
    
    @staticmethod # Ready
    def get_actualite_events( request : Request, token : str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        category = odooDatabase.execute_kw(
            'crm.mobile.category',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[]],
            {'fields': ['id']} 
        )
        l = [i['id'] for i in category]
        

        pp={}
        for i in l :
            actualite = odooDatabase.execute_kw(
            'crm.mobile.category.item',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['categ_id' , '=', i]]],
            {'fields': ['id','name','categ_id','description','image']} 
            )
            
            chain=actualite[0]['categ_id'][1]
            if chain:
                pp[chain]=actualite


        cc=[]
        try:    
            return pp
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))






        

    