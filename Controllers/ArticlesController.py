from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models.Products import ProductsData
from fastapi_pagination import Page, paginate,Params
from Models import Token
from Tools.TokenTools import TokenTools
import jwt
import time 


class ArticlesController():
    
    @staticmethod # Ready
    
    def get_all_products( request : Request, token :Token ,id_cat:int, search:str,id_sur:int ,id_paint:int,etoile:int,new_product:bool ,params:Params ):
        
        odooDatabase : OdooDatabase = request.app.state.odooDatabase

        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )
            #il faut ajouter la categorie auto avec published in mobil dans la table categorie
        #ajoute des filtre ici 

        start_time = time.time() 
        # print ("startttttttttt=====================r=============", start_time)


        domain = [('sale_ok', '=', True),('published_in_mobile','=','True')]
        # domain = [('published_in_mobile','=','True')]   just il faut remplire la data 
        if id_cat:
            domain.append(('categ_id', '=', id_cat))
        if search:
            domain.extend(['|', ('default_code', 'ilike', search), ('name', 'ilike', search)])
        if id_sur :
            domain.append(('surface_type', '=', id_sur))
        if id_paint:
            domain.append(('paint_type', '=', id_paint))
        if new_product:
            domain.append(('is_new_product', '=', new_product))
        if etoile:
            domain.append(('product_score', '=', etoile + 1))
        
        product = odooDatabase.execute_kw(
            'product.template',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [domain], 
            {'fields': ['id','name','default_code','list_price','categ_id','product_score','paint_type','surface_type','description_mobile','packaging_ids']} 
        )

        if not product:
            raise HTTPException(status_code=404, detail="No products found")

        session_id = odooDatabase.session

        for i in product:
            i['image_url'] = f"{odooDatabase.base_url}/web/image/product.template/{i['id']}/image_1920?session_id={session_id}"





        # if product:
        #     image_url = f"{odooDatabase.base_url}web/image/product.template/{product[0]['id']}/image_1024"









        # for i in product:
            
        #     l=i['packaging_ids']
        #     if l:
        #         packag = odooDatabase.execute_kw(
        #             'product.packaging',  # Modèle Odoo
        #             'search_read',  # Méthode utilisée pour la recherche et la lecture
        #             [[("id" , "in",l)]], 
        #             {'fields': ['id','name','qty']} 
        #         )
        #         i['cond']=packag
        #         # print("bilalllllllllllllllllllllllll",packag)
        #     else :
        #         i['cond']=None

        

        
        
        
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
                # image = i['image_1920'] if i['image_1920'] else None ,
                descMobile =i['description_mobile']if  i['description_mobile'] else None,
                img_url=i['image_url'] if i['image_url'] else None
                # cond=i['cond']if i['cond'] else None,
            )
            for i in product
        ]
        
        end_time = time.time()  # Fin
        tt=(end_time-start_time)/60
        # print ("enddddddddddddddddddddddddddddddddddddddddddd", tt)

        try:    
            return paginate(all_prd ,params)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @staticmethod # Ready
    def getConditionement( request : Request ,token:Token,  productId :int ):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )
        
        packag = odooDatabase.execute_kw(
            'product.packaging',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[("product_id" , "=",productId)]], 
            {'fields': ['id','name','qty']} 
        )
        
        try:    
            return packag
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))









    


    # @staticmethod

    # def get_all_products(request: Request, token: Token, id_cat: int, search: str, id_sur: int,id_paint: int, etoile: int, new_product: bool, params: Params):

    #     odooDatabase: OdooDatabase = request.app.state.odooDatabase

    

    #     user = TokenTools.check_token(token)

    #     if not user:

    #         raise HTTPException(

    #             status_code=401,

    #             detail={"status": False, "error": "Token Invalide"}

    #         )

    

    #     import time

    #     start_time = time.time()

    

    #     domain = [('sale_ok', '=', True), ('published_in_mobile', '=', 'True')]

    

    #     if id_cat:

    #         domain.append(('categ_id', '=', id_cat))

    #     if search:

    #         domain.extend(['|', ('default_code', 'ilike', search), ('name', 'ilike', search)])

    #     if id_sur:

    #         domain.append(('surface_type', '=', id_sur))

    #     if id_paint:

    #         domain.append(('paint_type', '=', id_paint))

    #     if new_product:

    #         domain.append(('is_new_product', '=', new_product))

    #     if etoile:

    #         domain.append(('product_score', '=', etoile + 1))

    

    #     # Step 1: Fetch products

    #     product = odooDatabase.execute_kw(

    #         'product.template',

    #         'search_read',

    #         [domain],

    #         {

    #             'fields': ['id', 'name', 'default_code', 'list_price', 'categ_id',

    #                     'product_score', 'paint_type', 'surface_type',

    #                     'image_1920', 'description', 'volume', 'weight',

    #                     'description_mobile', 'packaging_ids']

    #         }

    #     )

    

    #     product_ids = [p['id'] for p in product]

    

    #     # Step 2: Fetch packaging in one call for all products

    #     packaging_data = odooDatabase.execute_kw(

    #         'product.packaging',

    #         'search_read',

    #         [[('product_id', 'in', product_ids)]],

    #         {'fields': ['id', 'name', 'qty', 'product_id']}

    #     )

    

    #     # Step 3: Group packaging by product_id

    #     packaging_by_product = {}

    #     for pack in packaging_data:

    #         pid = pack['product_id'][0]  # product_id is a Many2one field [id, name]

    #         if pid not in packaging_by_product:

    #             packaging_by_product[pid] = []

    #         packaging_by_product[pid].append({

    #             "id": pack['id'],

    #             "name": pack['name'],

    #             "qty": pack['qty']

    #         })

    

    #     # Step 4: Format final response

    #     all_prd = [

    #         ProductsData(

    #             id=i['id'],

    #             name=i['name'],

    #             default_code=i['default_code'],

    #             list_price=float(i['list_price'] or 0.0),

    #             category=i['categ_id'][1] if i['categ_id'] else None,

    #             typeSurface=i['surface_type'][1] if i['surface_type'] else None,

    #             typePeinture=i['paint_type'][1] if i['paint_type'] else None,

    #             etoiles=int(i['product_score'] or 1),

    #             image=i['image_1920'] if i['image_1920'] else None,

    #             descMobile=i['description_mobile'],

    #             packaging=packaging_by_product.get(i['id'], [])  # Attach packaging

    #         )

    #         for i in product

    #     ]

    

    #     end_time = time.time()

    #     print("⏱️ Total time:", (end_time - start_time), "seconds")

    

    #     try:

    #         return paginate(all_prd, params)

    #     except HTTPException as e:

    #         raise e

    #     except Exception as e:

    #         raise HTTPException(status_code=500, detail=str(e))





