from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Depends

from src.core.authentication import (
    get_password_hash,
    require_role,
)
from src.core.database import SessionDep
from src.core.dependencies import CurrentAdminUser, CurrentUser
from src.core.selectors import Selector
from src.modules.users.enums import RoleEnum
from src.modules.users.models.users import User, UserPublic


class UserSelector(Selector):
    model = User

    @classmethod
    def create(cls, item: Any, session: SessionDep):
        db_user = User.model_validate(item)
        db_user.password = get_password_hash(db_user.password)
        db_user.roles = [RoleEnum.user]

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


router = APIRouter(prefix='/users', tags=['User'])


@router.get("/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return UserSelector.all(session, offset, limit)


@router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(require_role('user'))],
):
    return current_user


@router.post("/{id}", response_model=UserPublic)
def get_user(id: UUID, session: SessionDep):
    return UserSelector.get(id, session)


@router.patch("/{id}", response_model=UserPublic)
def update_user(id: UUID, user: UserPublic, session: SessionDep, current_user: CurrentUser):
    return UserSelector.update(id, user, session)


@router.delete("/{id}")
def delete_user(id: UUID, session: SessionDep, current_user: CurrentAdminUser):
    return UserSelector.delete(id, session)
