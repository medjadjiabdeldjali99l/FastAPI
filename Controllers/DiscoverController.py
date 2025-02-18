from fastapi import Request ,HTTPException
from database import OdooDatabase



class DiscoverController():
    
    @staticmethod # Ready
    def getPageDescover( request : Request  ):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        
        disc = odooDatabase.execute_kw(
            'crm.mobile.discovery.page',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['active', '=', 'True']]],
            {'fields': ['id','name','description','date']} 
      
        )
        print(disc)
        
        

        try:    
            return disc
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
