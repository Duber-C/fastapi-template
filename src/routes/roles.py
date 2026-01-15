from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Query

from src.utils.database import SessionDep
from src.utils.selectors import Selector
from src.internal.users import CreateRole, Role


class RoleSelector(Selector):
    model = Role


router = APIRouter(prefix='/roles', tags=['Role'])


@router.get("/", response_model=list[Role])
def read_roles(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return RoleSelector.all(session, offset, limit)


@router.post("/", response_model=Role)
def create_role(user: CreateRole, session: SessionDep):
    return RoleSelector.create(user, session)


@router.post("/{id}", response_model=Role)
def get_role(id: UUID, session: SessionDep):
    return RoleSelector.get(id, session)


@router.patch("/{id}", response_model=Role)
def update_role(id: UUID, account: Role, session: SessionDep):
    return RoleSelector.update(id, account, session)


@router.delete("/{id}")
def delete_role(id: UUID, session: SessionDep):
    return RoleSelector.delete(id, session)
