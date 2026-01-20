import pytest

from src.core.load_fixtures import load_fixtures


@pytest.fixture(scope="session", autouse=True)
def _load_permissions_fixtures():
    load_fixtures()
