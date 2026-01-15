from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Query

from src.internal.accounts import Account, CreateAccount
from src.utils.database import SessionDep
from src.utils.selectors import Selector


class AccountSelector(Selector):
    model = Account


router = APIRouter(prefix='/accounts', tags=['Account'])


@router.get("/", response_model=list[Account])
def read_accounts(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return AccountSelector.all(session, offset, limit)


@router.post("/", response_model=Account)
def create_account(user: CreateAccount, session: SessionDep):
    return AccountSelector.create(user, session)


@router.post("/{id}", response_model=Account)
def get_account(id: UUID, session: SessionDep):
    return AccountSelector.get(id, session)


@router.patch("/{id}", response_model=Account)
def update_account(id: UUID, account: Account, session: SessionDep):
    return AccountSelector.update(id, account, session)


@router.delete("/{id}")
def delete_account(id: UUID, session: SessionDep):
    return AccountSelector.delete(id, session)
