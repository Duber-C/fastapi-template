from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from src.settings import settings, EnvironmentEnum
from src.core.database import create_db_and_tables
from src.modules.users.routes import (
    users,
)
from src.modules.auth.routes import auth


@asynccontextmanager
async def lifespand(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespand)

v1_router = APIRouter()
v1_router.include_router(auth.router)
v1_router.include_router(users.router)

app.include_router(v1_router, prefix='/v1')

if settings.environment == EnvironmentEnum.local:
    app.mount("/static", StaticFiles(directory="static"), name="static")
