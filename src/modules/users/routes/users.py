from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from src.core.database import SessionDep
from src.core.dependencies import CurrentSuperAdminUser, CurrentUser
from src.modules.users.models.users import User, UserPublic
from src.modules.users.selectors import UserSelector


router = APIRouter(prefix='/users', tags=['User'])


@router.get("/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    current_user: CurrentSuperAdminUser,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return UserSelector.all(session, offset, limit)


@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: CurrentUser
):
    return current_user


@router.post("/{id}", response_model=UserPublic)
def get_user(id: UUID, session: SessionDep, current_user: CurrentSuperAdminUser):
    return UserSelector.get(id, session)


@router.patch("/{id}", response_model=UserPublic)
def update_user(id: UUID, user: UserPublic, session: SessionDep, current_user: CurrentUser):
    return UserSelector.update(id, user, session)


@router.delete("/{id}")
def delete_user(id: UUID, session: SessionDep, current_user: CurrentSuperAdminUser):
    return UserSelector.delete(id, session)
