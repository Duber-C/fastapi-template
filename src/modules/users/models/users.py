from uuid import UUID
from pydantic import EmailStr
from sqlmodel import ARRAY, Field, SQLModel, String

from src.core.models import BaseDBModel
from src.modules.users.enums import RoleEnum


class Permission(BaseDBModel, table=True):
    name: str
    roles: list[RoleEnum] = Field(default=RoleEnum.superadmin, sa_type=ARRAY(String))


class PermissionPublic(SQLModel):
    name: str


class CreatePermission(SQLModel):
    name: str


class BaseUser(SQLModel):
    email: EmailStr


class CreateUser(BaseUser):
    password: str


class User(CreateUser, BaseDBModel, table=True):
    roles: list[RoleEnum] = Field(default=RoleEnum.user, sa_type=ARRAY(String))
    disabled: bool = Field(default=False)


class UserPublic(BaseUser):
    id: UUID
    # roles: list[RoleEnum]

