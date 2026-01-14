from uuid import UUID
import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlmodel import select

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from src.utils.database import SessionDep
from src.internal.users import User


SECRET_KEY = "4843fc4c71f819615787dc7a8a028d550aab28cfd97c187737962f660c3060ce"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str | None = None


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


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


def has_permission(request: Request, user: User) -> bool:
    route = request.scope.get('route')
    if not route:
        return False

    has_perm = False
    for i in user.roles:
        for j in i.permissions:
            if route.name == j.name:
                has_perm = True

    return has_perm


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
    request: Request
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

    if not has_permission(request, user):
        raise HTTPException(status_code=401, detail="Unauthorized user")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

