from fastapi import APIRouter
# from routes.Authentification import router as AuthentificationRouter
# from routes.Main import router as MainRouter
# from routes.Profile import router as ProfileRouter
from Routes.Annuaire import router as AnnuaireRouter
# from routes.stand import router as StandRouter
# from routes.Discover import router as DiscoverRouter
# from routes.Historique import router as  HistoriqueRouter
# from routes.HistoriqueNiveau import router as  HistoriqueNiveauRouter
# from routes.Catalogue import router as  CatalogueRouter
# from routes.Articles import router as  ArticlesRouter
# from routes.Wilaya import router as  WilayasRouter

router = APIRouter()

# router.include_router(AuthentificationRouter, tags=["Authentification"], prefix="/auth")
# router.include_router(MainRouter, tags=["Main"], prefix="/main")
# router.include_router(ProfileRouter, tags=["Profile"],prefix="/profile")
router.include_router(AnnuaireRouter,tags=["Annuaire"],prefix="/annuaire")
# router.include_router(StandRouter,tags=["Stand"],prefix="/stand")
# router.include_router(HistoriqueRouter,tags=["historique"],prefix="/historique")
# router.include_router(HistoriqueNiveauRouter,tags=["historiqueniveau"],prefix="/historiqueniveau")
# router.include_router(CatalogueRouter,tags=["catalogs"],prefix="/catalogs")
# router.include_router(ArticlesRouter,tags=["Articles"],prefix="/articles")
# router.include_router(WilayasRouter,tags=["Wilaya"],prefix="/wilaya")
# router.include_router(DiscoverRouter,tags=["Discover"],prefix="/discover")