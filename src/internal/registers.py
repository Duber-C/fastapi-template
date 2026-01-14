from uuid import UUID
from sqlmodel import Field, SQLModel
from src.utils.models import BaseDBModel


class CreateRegister(SQLModel):
    amount: float
    register_type: bool
    description: str
    account_id: UUID = Field(default=None, foreign_key="account.id")


class Register(CreateRegister, BaseDBModel, table=True):
    account_id: UUID = Field(default=None, foreign_key="account.id", primary_key=True)


