from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models.Products import ProductsData
from fastapi_pagination import Page, paginate,Params
from Models import Token
from Tools.TokenTools import TokenTools
import jwt



class ArticlesController():
    
    @staticmethod # Ready
    def get_all_products( request : Request, token :Token ,id_cat:int, search:str,id_sur:int ,id_paint:int,etoile:int,new_product:bool ,params:Params ):
        
        odooDatabase : OdooDatabase = request.app.state.odooDatabase

        user = TokenTools.check_token(token)
        print("userrrrrrrrrrrrrrrrrrrrrr",user)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Tokennnnnnnnnnnnnnnnnnnnnnnnnnnn Invalide"}
            )
        #ajoute des filtre ici 
        domain = [('sale_ok', '=', True)]
        # domain = [('published_in_mobile','=','True')]   just il faut remplire la data 
        if id_cat:
            domain.append(('categ_id', '=', id_cat))
        if search:
            print("seaaaaaaaaaaaarch",search)
            domain.extend(['|', ('default_code', 'like', search), ('name', 'like', search)])
        if id_sur :
            print("surfaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaace",id_sur)
            domain.append(('surface_type', '=', id_sur))
        if id_paint:
            print("paintttttttttttttttttttt",id_paint)
            domain.append(('paint_type', '=', id_paint))
        if new_product:
            print("newwwwwwwwwwwwwwwwwwwwwwwwwwwww",new_product)
            domain.append(('is_new_product', '=', new_product))
        if etoile:
            print("product_score",etoile)
            domain.append(('product_score', '=', etoile + 1))
        
        product = odooDatabase.execute_kw(
            'product.template',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [domain], 
            {'fields': ['id','name','default_code','list_price','categ_id','product_score','paint_type','surface_type','image_1920']} 
        )
        if product:
            print( "samyyyyyyyyyyyyyyyyy=================================================",product[0])
        
        all_prd = [
            ProductsData(
                id=i['id'] if i['id'] else None,
                name=i['name'] if i['name'] else None,
                default_code=i['default_code'] if i['default_code'] else None,
                list_price=float(i['list_price'] if i['list_price'] else 0.0),
                category=i['categ_id'][1] if i['categ_id'] else None,
                typeSurface =i['surface_type'][1] if i['surface_type'] else None,
                typePeinture=i['paint_type'][1] if i['paint_type'] else None,
                etoiles=int(i['product_score'] if i['product_score'] else 1 ),
                image = i['image_1920'] if i['image_1920'] else None 
            )
            for i in product
        ]
        
            
        try:    
            return paginate(all_prd ,params)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
