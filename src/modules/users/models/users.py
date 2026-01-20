from uuid import UUID
from pydantic import EmailStr
from sqlmodel import ARRAY, Field, SQLModel, String

from src.core.models import BaseDBModel
from src.modules.users.enums import RoleEnum


class Permission(BaseDBModel, table=True):
    name: str
    roles: list[RoleEnum] = Field(
        default_factory=lambda: [RoleEnum.superadmin],
        sa_type=ARRAY(String),
    )


class PermissionPublic(SQLModel):
    name: str


class CreatePermission(SQLModel):
    name: str


class CreateUser(SQLModel):
    email: EmailStr
    password: str


class User(BaseDBModel, table=True):
    email: EmailStr = Field(unique=True)
    password: str
    roles: list[RoleEnum] = Field(
        default_factory=lambda: [RoleEnum.user],
        sa_type=ARRAY(String),
    )
    disabled: bool = Field(default=False)


class UserPublic(SQLModel):
    id: UUID
    email: EmailStr
    roles: list[str]
