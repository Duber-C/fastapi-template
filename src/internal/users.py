from uuid import UUID
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from src.utils.models import BaseDBModel


class PermissionRoleLink(SQLModel, table=True):
    permission_id: UUID | None = Field(default=None, foreign_key="permission.id", primary_key=True)
    role_id: UUID | None = Field(default=None, foreign_key="role.id", primary_key=True)


class Permission(BaseDBModel, table=True):
    name: str
    roles: list["Role"] = Relationship(
        back_populates="permissions",
        link_model=PermissionRoleLink
    )


class PermissionPublic(SQLModel):
    name: str


class CreatePermission(SQLModel):
    name: str


class UserRoleLink(SQLModel, table=True):
    user_id: UUID | None = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: UUID | None = Field(default=None, foreign_key="role.id", primary_key=True)


class Role(BaseDBModel, table=True):
    name: str
    permissions: list[Permission] = Relationship(
        back_populates="roles",
        link_model=PermissionRoleLink
    )
    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink
    )


class CreateRole(SQLModel):
    name: str


class RolePublic(SQLModel):
    id: UUID
    name: str


class BaseUser(SQLModel):
    email: EmailStr


class CreateUser(BaseUser):
    password: str


class User(CreateUser, BaseDBModel, table=True):
    roles: list["Role"] = Relationship(
        back_populates="users",
        link_model=UserRoleLink
    )
    disabled: bool = Field(default=False)


class UserPublic(BaseUser):
    id: UUID
    roles: list[RolePublic] = Field(default_factory=list)

