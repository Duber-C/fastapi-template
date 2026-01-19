import os
import json

from sqlmodel import SQLModel

from src.modules.users.models.users import Permission
from src.core.database import update_or_create
from src.settings import logger


fixture_mapping: dict[str, type[SQLModel]] = {
    '/src/modules/users/fixtures/permissions.json': Permission,
}


def load_fixtures():
    cwd = os.getcwd()

    basepath = cwd

    for f, model in fixture_mapping.items():
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


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    load_fixtures()
