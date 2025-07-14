from fastapi import APIRouter

from app.routes import auth_route, user_route, province_route, user_travel_route

api_router = APIRouter()

api_router.include_router(auth_route.router)
api_router.include_router(user_route.router)
api_router.include_router(user_travel_route.router)
api_router.include_router(province_route.router)
