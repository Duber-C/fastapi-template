from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Depends

from src.utils.authentication import get_current_active_user, get_password_hash
from src.internal.users import Role, User, UserPublic
from src.utils.database import SessionDep
from src.utils.selectors import Selector


class UserSelector(Selector):
    model = User

    @classmethod
    def create(cls, item: Any, session: SessionDep):
        db_user = User.model_validate(item)
        db_user.password = get_password_hash(db_user.password)

        role = session.get(Role, UUID("ddfbdace-0621-44a2-8617-97b2ebdef2aa"))
        if role:
            db_user.roles = [role]

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
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.post("/{id}", response_model=UserPublic)
def get_user(id: UUID, session: SessionDep):
    return UserSelector.get(id, session)


@router.patch("/{id}", response_model=UserPublic)
def update_user(id: UUID, user: UserPublic, session: SessionDep):
    return UserSelector.update(id, user, session)


@router.delete("/{id}")
def delete_user(id: UUID, session: SessionDep):
    return UserSelector.delete(id, session)
