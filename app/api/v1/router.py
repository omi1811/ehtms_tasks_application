from fastapi import APIRouter
from app import api
from app.api.v1.endpoints import auth, media, tasks
from app.api.v1.endpoints import organizations

api_router = APIRouter()

api_router.include_router(
    auth.router, #route object from auth.py
    prefix="/auth", #prefix for all auth routes
    tags=["auth"] #tag for grouping in docs
)
api_router.include_router(
    tasks.router, #route object from tasks.py 
    tags=["tasks"] #tag for grouping in docs
)

api_router.include_router(
    media.router, #route object from media.py
    prefix="/media", #prefix for all media routes
    tags=["media"] #tag for grouping in docs
)

api_router.include_router(organizations.router, prefix="/org", tags=["organizations"])
