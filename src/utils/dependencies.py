from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.internal.users import User
from src.utils.database import get_session
from src.utils.authentication import get_current_active_user


CurrentUser = Annotated[User, Depends(get_current_active_user)]
