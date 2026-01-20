from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.core.authentication import get_password_hash
from src.core.database import SessionDep
from src.core.selectors import Selector
from src.modules.users.enums import RoleEnum
from src.modules.users.models.users import Permission, User


class PermissionSelector(Selector):
    model = Permission


class UserSelector(Selector):
    model = User

    @classmethod
    def create(
        cls,
        item: Any,
        session: SessionDep,
        roles: list[RoleEnum] = [RoleEnum.user]
    ):
        db_user = User.model_validate(item)
        db_user.password = get_password_hash(db_user.password)
        if roles:
            db_user.roles = roles

        try:
            session.add(db_user)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(403, "Integrity error, validate user data")
        except Exception:
            session.rollback()
            raise HTTPException(403, "Validate user data")

        session.refresh(db_user)
        return db_user
