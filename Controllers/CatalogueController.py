from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt


class CatalogueController():
    
    @staticmethod # Ready
    def get_all_category( request : Request, token : Token):
        
        print ( "raniiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii =====", token )
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        liste_cat=[9, 133, 1, 7, 8, 144, 128]
        catalogs = odooDatabase.execute_kw(
            'product.category',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[('id', 'in', liste_cat)]],
            {'fields': ['id','name']} 
        )

        try:    
            return catalogs
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    
    @staticmethod # Ready
    def get_all_surfaces( request : Request, token : str):

        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        liste_cat=[9, 133, 1, 7, 8, 144, 128]
        surface = odooDatabase.execute_kw(
            'crm.surface_type',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[]],
            {'fields': ['id','name']} 
        )
        print(surface)
        
        try:    
            return surface
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod # Ready
    def get_all_peinture( request : Request, token : str):

        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )

        liste_cat=[9, 133, 1, 7, 8, 144, 128]
        paint = odooDatabase.execute_kw(
            'crm.paint_type',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[]],
            {'fields': ['id','name']} 
        )
        print(paint)
        

        try:    
            return paint
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))