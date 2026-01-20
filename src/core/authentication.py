from uuid import UUID
import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Callable
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlmodel import Session, select

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from src.core.database import SessionDep, engine
from src.modules.users.models.users import User
from src.modules.users.enums import RoleEnum
from src.settings import settings


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str | None = None


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def authenticate_user(username: str, password: str, session: SessionDep):
    user = session.exec(
        select(User).where(User.email == username)
    ).first()

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def has_role_permission(roles: tuple[str, ...], user: User) -> bool:
    if not roles or not user:
        return False

    for role in user.roles:
        if role in roles:
            return True

    return False


def has_specific_permission(request: Request, user: User) -> bool:
    """
    Check whether the user has permission to access the requested route.

    The permission check compares the FastAPI route name (the endpoint
    function name, e.g. ``get_users``) against the permission names
    assigned to any of the user's roles.
    """

    route = request.scope.get('route')
    if not route or not user:
        return False

    has_perm = False

    from src.modules.users.selectors import PermissionSelector

    with Session(engine) as session:
        for role in user.roles:
            permissions = PermissionSelector.filter(
                session=session, field="roles", value=role
            )
            print(permissions)
            for j in permissions:
                if route.name == j.name:
                    has_perm = True

    return has_perm


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        token_data = TokenData(user_id=sub)
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = session.get(User, UUID(token_data.user_id))
    if user is None:
        raise credentials_exception

    if user.roles:
        user.roles = [
            role if isinstance(role, RoleEnum) else RoleEnum(role)
            for role in user.roles
        ]

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def require_role(*allowed_roles: str) -> Callable:
    """Ensure the authenticated profile has at least one of the allowed roles."""

    async def _enforce_permissions(
        request: Request,
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if has_role_permission(allowed_roles, current_user):
            return current_user

        if has_specific_permission(request, current_user):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have a role that is authorized to access this resource.",
        )

    return _enforce_permissions
