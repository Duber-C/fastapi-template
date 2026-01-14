from typing import Annotated

from fastapi import APIRouter, Query

from src.internal.users import CreatePermission, Permission, PermissionPublic
from src.utils.dependencies import CurrentUser
from src.utils.database import SessionDep
from src.utils.routes import Selector


class PermissionSelector(Selector):
    model = Permission


router = APIRouter(prefix='/permissions', tags=['Permission'])


@router.get("/", response_model=list[PermissionPublic])
def read_permissions(
    session: SessionDep,
    current_user: CurrentUser,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return PermissionSelector.all(session, offset, limit)


@router.post("/", response_model=PermissionPublic)
def create_permission(
    user: CreatePermission,
    session: SessionDep,
    current_user: CurrentUser
):
    return PermissionSelector.create(user, session)
