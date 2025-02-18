from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt


class WilayaController():
    
    @staticmethod # Ready
    def get_all_wilaya( request : Request, token : str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        wilaya = odooDatabase.execute_kw(
            'res.country.state',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['country_id', '=',62 ]]],
            {'fields': ['id','name','code','pf_ids']} 
        )

        try:    
            return wilaya
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))




   