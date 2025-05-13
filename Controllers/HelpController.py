from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token 
from Models.HelpCenter import *
from Tools.TokenTools import TokenTools
import jwt


class HelpController():
    
    @staticmethod # Ready
    def get_help( request : Request, token : str ):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )

        FAQ = odooDatabase.execute_kw(
            'faq.question',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[]],
            {'fields': ['question','answer','category_id']} 
        )
        # print( "snappppppppppppppppppppppppp",FAQ)


        objetTemplate = odooDatabase.execute_kw(
            'help.topic',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[ ]],
            {'fields': ['name']} 
        )
        url_video=odooDatabase.execute_kw(
            'faq.category',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[('id','=',3)]],
            {'fields': ['url']} 
        )
        print("uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu",url_video)


        helpCenterData=HelpCenter(
            objetEmail =objetTemplate if objetTemplate else None,
            Faq = FAQ if FAQ else None,
            urlVid=url_video[0].get('url') if url_video[0].get('url') else '', 
            
        )

        try:    
            return helpCenterData
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))



    @staticmethod # Ready
    def SendEmailDetallaint(request: Request, message : str,idDetaillant : int,idTopic : int):  
        odooDatabase : OdooDatabase = request.app.state.odooDatabase


        nvlTableVals = {
            "user_id": idDetaillant,
            "topic_id": idTopic , #hardcodeddd 
            "message": message.content,
        }
        
        # Créer l'enregistrement dans info.cnx
        detNvlTable_id = odooDatabase.execute_kw('help.request', 'create', [nvlTableVals])
        if not detNvlTable_id:
            raise HTTPException(
                    status_code=401,  
                    detail={"status": False, "error": "Erreur de création dans la nouvelle ligne dans la table "}
                )
        


        return {
                "status" : True,
                "message": "succes"
        }

        

   