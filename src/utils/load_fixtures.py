import os
import json

from src.internal.users import Permission, PermissionRoleLink, Role
from src.utils.database import update_or_create


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
            print("Mapping does no exits {}".format(f))
            continue

        with open(basepath + f, 'r') as file:
            content = file.read()
            try:
                items = json.loads(content)
            except Exception as e:
                print("Failed loding json file {} with {}".format(f, e))
                continue

        for item in items:
            try:
                update_or_create(model, item)
            except Exception as e:
                print("Failed update or create item {} error {}".format(item, e))

        print("Fixture uploaded! -> {}".format(f))

