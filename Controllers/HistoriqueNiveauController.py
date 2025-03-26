from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models import Token
from Tools.TokenTools import TokenTools
import jwt

class HistoriqueNiveauController():
    
    @staticmethod # Ready
    def get_all_niveaux( request : Request, token : str,id_det:int):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )



        histo_niveau = odooDatabase.execute_kw(
            'res.partner.niveau.historique',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[['partner_id', '=', id_det], ['state_niveau', '=', 'ok_passage']]],
            {'fields': ['id','date','niveau_old_id','action','niveau_new_id']} 
        )
        print ( "batmanaaa trohhhhhhhhhhhhhhhhhhhhhh ",histo_niveau)
        if histo_niveau :
            print ( "batmanaaa trohhhhhhhhhhhhhhhhhhhhhh ",histo_niveau)

            pp = [{"name": i['niveau_new_id'][1], "date": i['date']} for i in histo_niveau]

            data ={"historique_niveau":pp}


            prochain=histo_niveau[-1]
            print("baynaa kter",prochain)
            
            teste = odooDatabase.execute_kw(
                'crm.niveau',  # Modèle Odoo
                'search_read',  # Méthode utilisée pour la recherche et la lecture
                [[["id","=",prochain['niveau_new_id'][0]]]],
                {'fields': ['id','name','conditions_ids']} 
            )
            ll=teste[0]['conditions_ids']

            condition = odooDatabase.execute_kw(
                'crm.niveau.condition.passage',  # Modèle Odoo
                'search_read',  # Méthode utilisée pour la recherche et la lecture
                [[("id","in",ll)]],
                {'fields': ['id','name','obligation_id','niveau_id']} 
            )

            ll = [i['obligation_id'][0] for i in condition]

            condition1 = odooDatabase.execute_kw(
                'crm.niveau.condition.passage.obl',  # Modèle Odoo
                'search_read',  # Méthode utilisée pour la recherche et la lecture
                [[("id","in",ll)]],
                {'fields': ['id','name','obligation']} 
            )

            pp=[]
            for i in ll:
                for j in condition1 :
                    if i == j['id']:
                        if j['name']=='or' or j['name']== 'and':
                            t={"name":"","descr":j['obligation']}
                        else:
                            t={"name":j['name'],"descr":j['obligation']}
                        pp.append(t)
            data['actions']=pp

            try:    
                return data
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        else:
            data ={"historique_niveau":[]}
            teste = odooDatabase.execute_kw(
                'crm.niveau',  # Modèle Odoo
                'search_read',  # Méthode utilisée pour la recherche et la lecture
                [[["id","=",1]]],
                {'fields': ['id','name','conditions_ids']} 
            )
            print ( "rachidddddddddddddddddddddddddd",teste)
            ll=teste[0]['conditions_ids']

            condition = odooDatabase.execute_kw(
                'crm.niveau.condition.passage',  # Modèle Odoo
                'search_read',  # Méthode utilisée pour la recherche et la lecture
                [[("id","in",ll)]],
                {'fields': ['id','name','obligation_id','niveau_id']} 
            )

            ll = [i['obligation_id'][0] for i in condition]

            condition1 = odooDatabase.execute_kw(
                'crm.niveau.condition.passage.obl',  # Modèle Odoo
                'search_read',  # Méthode utilisée pour la recherche et la lecture
                [[("id","in",ll)]],
                {'fields': ['id','name','obligation']} 
            )

            pp=[]
            for i in ll:
                for j in condition1 :
                    if i == j['id']:
                        if j['name']=='or' or j['name']== 'and':
                            t={"name":"","descr":j['obligation']}
                        else:
                            t={"name":j['name'],"descr":j['obligation']}
                        pp.append(t)
            data['actions']=pp

            try:    
                return data
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
