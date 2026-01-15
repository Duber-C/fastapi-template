from fastapi import APIRouter

from src.internal.users import PermissionRoleLink
from src.utils.dependencies import CurrentUser
from src.utils.database import SessionDep
from src.utils.selectors import Selector


class PermissionRoleSelector(Selector):
    model = PermissionRoleLink


router = APIRouter(prefix='/permission-roles', tags=['Permission'])


@router.post("/", response_model=PermissionRoleLink)
def create_permission_role(
    user: PermissionRoleLink,
    session: SessionDep,
    current_user: CurrentUser
):
    return PermissionRoleSelector.create(user, session)
