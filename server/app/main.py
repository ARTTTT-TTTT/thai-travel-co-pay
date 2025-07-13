import logging
from fastapi import FastAPI, status
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import text
from contextlib import asynccontextmanager

from app.api import api_router
from app.configs.app_config import app_config
from app.database.session import engine


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("🚀 Connected to SQLite")
    except Exception as e:
        logger.error("❌ Failed to connect to SQLite: %s", e)
        raise e

    yield

    await engine.dispose()
    logger.info("🧹 Async engine disposed")


app = FastAPI(
    title=app_config.PROJECT_NAME,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
    docs_url="/docs" if app_config.ENVIRONMENT != "production" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if app_config.ENVIRONMENT != "production" else None,
)

if app_config.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=app_config.API_STR)


@app.get("/", tags=["Default"])
async def root():
    return {"message": "Welcome to THAI TRAVEL CO PAY API"}


@app.get("/health", tags=["Monitoring"])
async def health_check():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        return JSONResponse(
            content={"status": "unhealthy"}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API for THAI TRAVEL CO PAY",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    # 👇 NOTE: Use full path with prefix
                    "tokenUrl": f"{app_config.API_STR}/auth/login",
                    "scopes": {},
                }
            },
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
