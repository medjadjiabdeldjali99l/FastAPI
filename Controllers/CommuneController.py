from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt


class CommuneController():
    
    @staticmethod # Ready
    def get_all_commune( request : Request,codeWilayaOdoo:str):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase

        commune=None
        
        if codeWilayaOdoo:

            commune = odooDatabase.execute_kw(
                'res.commune',  # Modèle Odoo
                'search_read',  # Méthode utilisée pour la recherche et la lecture
                [[['state_id', '=',int (codeWilayaOdoo) ]]],
                {'fields': ['id','name']} 
            )


        
        
        try:    
            return commune
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))




   