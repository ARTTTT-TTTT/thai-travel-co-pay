from fastapi import APIRouter
from app.routes import auth_route, user_route

api_router = APIRouter()

api_router.include_router(auth_route.router)
api_router.include_router(user_route.router)
