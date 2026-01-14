from typing import Annotated, Sequence
from uuid import UUID
from fastapi import APIRouter, Query
from sqlmodel import select

from src.internal.registers import CreateRegister, Register
from src.utils.database import SessionDep
from src.utils.routes import Selector


class RegisterSelector(Selector):
    model = Register

    @classmethod
    def account_filter(
        cls,
        session: SessionDep,
        limit: int,
        offset: int,
        account_id: UUID
    ) -> Sequence[Register]:
        query = select(Register).where(Register.account_id == account_id).offset(offset).limit(limit)
        items = session.exec(query).all()
        return items


router = APIRouter(prefix='/registry', tags=['Registry'])


@router.get("/", response_model=list[Register])
def read_registers(
    session: SessionDep,
    account_id: UUID | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    if account_id:
        return RegisterSelector.account_filter(session, offset, limit, account_id)

    return RegisterSelector.all(session, offset, limit)


@router.post("/", response_model=Register)
def create_register(user: CreateRegister, session: SessionDep):
    return RegisterSelector.create(user, session)


@router.post("/{id}", response_model=Register)
def get_register(id: UUID, session: SessionDep):
    return RegisterSelector.get(id, session)


@router.patch("/{id}", response_model=Register)
def update_register(id: UUID, account: Register, session: SessionDep):
    return RegisterSelector.update(id, account, session)


@router.delete("/{id}")
def delete_register(id: UUID, session: SessionDep):
    return RegisterSelector.delete(id, session)
