
from Controllers.DiscoverController import DiscoverController

from fastapi import APIRouter, Request ,Query ,Depends


router = APIRouter()




@router.get("/discover")
async def discover(request : Request):
    return DiscoverController.getPageDescover(request=request)

