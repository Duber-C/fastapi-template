from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.utils.load_fixtures import load_fixtures
from src.utils.database import create_db_and_tables
from src.routes import (
    health,
    permission_roles,
    users,
    accounts,
    permissions,
    accounts,
    registers,
    auth,
    roles
)


@asynccontextmanager
async def lifespand(app: FastAPI):
    create_db_and_tables()
    load_fixtures()
    yield


app = FastAPI(lifespan=lifespand)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(permission_roles.router)
app.include_router(accounts.router)
app.include_router(registers.router)
app.include_router(roles.router)
