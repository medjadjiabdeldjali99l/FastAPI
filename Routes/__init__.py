from fastapi import APIRouter
from Routes.Authentification import router as AuthentificationRouter
from Routes.Main import router as MainRouter
# from routes.Profile import router as ProfileRouter
from Routes.Annuaire import router as AnnuaireRouter
from Routes.stand import router as StandRouter
from Routes.Discover import router as DiscoverRouter
from Routes.Historique import router as  HistoriqueRouter
from Routes.HistoriqueNiveau import router as  HistoriqueNiveauRouter
from Routes.Catalogue import router as  CatalogueRouter
from Routes.Articles import router as  ArticlesRouter
from Routes.Wilaya import router as  WilayasRouter

router = APIRouter()

router.include_router(AuthentificationRouter, tags=["Authentification"], prefix="/auth")
router.include_router(MainRouter, tags=["Main"], prefix="/main")
# router.include_router(ProfileRouter, tags=["Profile"],prefix="/profile")
router.include_router(AnnuaireRouter,tags=["Annuaire"],prefix="/annuaire")
router.include_router(StandRouter,tags=["Stand"],prefix="/stand")
router.include_router(HistoriqueRouter,tags=["historique"],prefix="/historique")
router.include_router(HistoriqueNiveauRouter,tags=["historiqueniveau"],prefix="/historiqueniveau")
router.include_router(CatalogueRouter,tags=["catalogs"],prefix="/catalogs")
router.include_router(ArticlesRouter,tags=["Articles"],prefix="/articles")
router.include_router(WilayasRouter,tags=["Wilaya"],prefix="/wilaya")
router.include_router(DiscoverRouter,tags=["Discover"],prefix="/discover")