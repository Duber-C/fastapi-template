from typing import Annotated

from fastapi import Depends

from src.modules.users.models.users import User
from src.core.authentication import require_role


CurrentUser = Annotated[User, Depends(require_role('user', 'admin', 'superadmin'))]
CurrentAdminUser= Annotated[User, Depends(require_role('user', 'admin'))]
CurrentSuperAdminUser= Annotated[User, Depends(require_role('superadmin'))]
