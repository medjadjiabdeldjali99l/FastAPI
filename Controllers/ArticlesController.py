from fastapi import Request ,HTTPException
from database import OdooDatabase
from Models.Products import ProductsData
from fastapi_pagination import Page, paginate,Params
from Models import Token
from Tools.TokenTools import TokenTools
from Models.FavorisDeletReq import FavorisDeleteRequest
import jwt
import time 


class ArticlesController():
    
    @staticmethod # Ready
    
    def get_all_products( request : Request, token :Token ,id_cat:int, search:str,id_sur:int ,id_paint:int,etoile:int,new_product:bool ,params:Params ):
        
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        print ( "''''''''''''''''==================================='''''''''''",id_cat,id_sur,id_paint,etoile,new_product)

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
            {'fields': ['id','name','default_code','list_price','categ_id','product_score','paint_type','surface_type','description_mobile','packaging_ids','is_new_product']} 
        )
        print ("namousssssssssssssssss", product[0])

        if not product:
            raise HTTPException(status_code=422, detail="No products found")

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
                img_url=i['image_url'] if i['image_url'] else None,
                nvProduct=i['is_new_product'] if i['is_new_product'] else False,
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
        filtered = [item for item in packag if item['name'] != 'crochet']

        print(filtered)
        
        try:    
            return filtered
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @staticmethod # Ready
    def add_product_fav( request : Request ,token:Token,  idProduct :int,idDet:int ):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )
        addarticle = odooDatabase.execute_kw(
            'product.template',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[("id" , "=",idProduct)]], 
            {'fields': ['id']} 
        )
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",addarticle)
        if not addarticle:
            raise HTTPException(status_code=422, detail="No products found")

        odooDatabase.execute_kw(
            'res.partner',
            'write',
            [[idDet], {'favorite_articles': [(4, idProduct)]}]
        )
        
        try:    
            return {
                "status": True,
                "message": "ajoute de produit avec succes"
                }    
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @staticmethod # Ready
    def delete_product_fav( request : Request ,token:Token,  payload:FavorisDeleteRequest ):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )
        addarticle = odooDatabase.execute_kw(
            'res.partner',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[("id" , "=",payload.idDet)]], 
            {'fields': ['id','favorite_articles']} 
        )
        print ("===================================================",addarticle)
        print ( "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt",payload)

        odooDatabase.execute_kw(
            'res.partner',
            'write',
            [[payload.idDet], {'favorite_articles': [(3, payload.idProduct)]}]
        )


        addarticle = odooDatabase.execute_kw(
            'res.partner',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[("id" , "=",payload.idDet)]], 
            {'fields': ['id','favorite_articles']} 
        )
        print ("===================================================",addarticle)

        
        
        try:    
            return {
                    "status": True,
                    "message": "suppresion de produit avec succes"
                    }   
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod # Ready
    def productsfav( request : Request ,token:Token,  idDet:int,params:Params ):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )
        addarticle = odooDatabase.execute_kw(
            'res.partner',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[("id" , "=",idDet)]], 
            {'fields': ['id','favorite_articles']} 
        )
        print ("===================================================",addarticle[0]['favorite_articles'])
        if not addarticle:
            raise HTTPException(status_code=422, detail="No products found")
        domain=[('sale_ok', '=', True),('published_in_mobile','=','True'),('id','in',addarticle[0]['favorite_articles'])]

        product = odooDatabase.execute_kw(
            'product.template',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [domain], 
            {'fields': ['id','name','default_code','list_price','categ_id','product_score','paint_type','surface_type','description_mobile','packaging_ids','is_new_product']} 
        )
        


        for i in product:
            print(i)

        if not product:
            raise HTTPException(status_code=422, detail="No products found")

        session_id = odooDatabase.session

        for i in product:
            i['image_url'] = f"{odooDatabase.base_url}/web/image/product.template/{i['id']}/image_1920?session_id={session_id}"
        


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
                img_url=i['image_url'] if i['image_url'] else None,
                nvProduct=i['is_new_product'] if i['is_new_product'] else False,
                # cond=i['cond']if i['cond'] else None,
            )
            for i in product
        ]

        
        
        try:    
            return paginate(all_prd ,params)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))




    @staticmethod # Ready
    def idproductsfav ( request : Request ,token:Token,  idDet :int ):
        odooDatabase : OdooDatabase = request.app.state.odooDatabase
        user = TokenTools.check_token(token)
        if not user : 
            raise HTTPException(
                status_code=401,  
                detail={"status": False, "error": "Token Invalide"}
            )
        addarticle = odooDatabase.execute_kw(
            'res.partner',  # Modèle Odoo
            'search_read',  # Méthode utilisée pour la recherche et la lecture
            [[("id" , "=",idDet)]], 
            {'fields': ['id','favorite_articles']} 
        )
        print ("ùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùù", addarticle)
        {"fav":addarticle[0]['favorite_articles']}
        
        
        
        try:    
            return {"fav":addarticle[0]['favorite_articles']}
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))