import os
import json

from src.internal.users import Permission, PermissionRoleLink, Role
from src.utils.database import update_or_create
from src.settings import logger


fixture_mapping = {
    'permissions.json': Permission,
    'roles.json': Role,
    'permission_roles.json': PermissionRoleLink
}


def load_fixtures():
    cwd = os.getcwd()

    basepath = cwd + "/src/fixtures/"
    files = os.listdir(basepath)

    for f in files:
        model = fixture_mapping.get(f)
        if not model:
            logger.warning("Mapping does not exist for %s", f)
            continue

        with open(basepath + f, 'r') as file:
            content = file.read()
            try:
                items = json.loads(content)
            except Exception:
                logger.exception("Failed loading json file %s", f)
                continue

        for item in items:
            try:
                update_or_create(model, item)
            except Exception:
                logger.exception("Failed update or create item %s", item)

        logger.info("\U0001F4AA Fixture uploaded! -> %s", f)
