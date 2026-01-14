from sqlmodel import SQLModel
from src.utils.models import BaseDBModel


class CreateAccount(SQLModel):
    name: str
    account_type: str


class Account(CreateAccount, BaseDBModel, table=True):
    ...

