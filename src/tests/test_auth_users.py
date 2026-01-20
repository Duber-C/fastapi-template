from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.core.authentication import verify_password
from src.core.database import engine
from src.main import app
from src.modules.users.enums import RoleEnum
from src.modules.users.models.users import User


def _signup(client: TestClient, email: str, password: str):
    return client.post("/v1/auth/signup", json={"email": email, "password": password})


def _login(client: TestClient, email: str, password: str):
    return client.post("/v1/auth/login", data={"username": email, "password": password})


def _token(client: TestClient, email: str, password: str) -> str:
    login = _login(client, email, password)
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token
    return token


def _set_role(email: str, role: RoleEnum) -> None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).one()
        user.roles = [role]
        session.add(user)
        session.commit()


def test_signup_rejects_duplicate_email():
    email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        first = _signup(client, email, password)
        assert first.status_code == 200

        second = _signup(client, email, password)
        assert second.status_code == 403


def test_signup_hashes_password_and_sets_default_role():
    email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        signup = _signup(client, email, password)
        assert signup.status_code == 200

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).one()
        assert user.password != password
        assert verify_password(password, user.password)
        assert RoleEnum.user in user.roles


def test_signup_rejects_invalid_email_format():
    with TestClient(app) as client:
        signup = _signup(client, "not-an-email", "secret123!")
        assert signup.status_code == 422


def test_login_rejects_invalid_password():
    email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        signup = _signup(client, email, password)
        assert signup.status_code == 200

        login = _login(client, email, "wrong-pass")
        assert login.status_code == 401


def test_me_requires_authentication():
    with TestClient(app) as client:
        missing = client.get("/v1/users/me/")
        assert missing.status_code == 401

        invalid = client.get(
            "/v1/users/me/", headers={"Authorization": "Bearer not-a-real-token"}
        )
        assert invalid.status_code == 401


def test_users_list_requires_superadmin():
    email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        signup = _signup(client, email, password)
        assert signup.status_code == 200

        token = _token(client, email, password)
        response = client.get(
            "/v1/users/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


def test_superadmin_can_list_users():
    email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        signup = _signup(client, email, password)
        assert signup.status_code == 200

        _set_role(email, RoleEnum.superadmin)
        token = _token(client, email, password)

        response = client.get(
            "/v1/users/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


def test_delete_user_requires_superadmin():
    actor_email = f"test-{uuid4()}@example.com"
    target_email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        actor = _signup(client, actor_email, password)
        target = _signup(client, target_email, password)
        assert actor.status_code == 200
        assert target.status_code == 200

        token = _token(client, actor_email, password)
        response = client.delete(
            f"/v1/users/{target.json()['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


def test_superadmin_can_delete_user():
    actor_email = f"test-{uuid4()}@example.com"
    target_email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        actor = _signup(client, actor_email, password)
        target = _signup(client, target_email, password)
        assert actor.status_code == 200
        assert target.status_code == 200

        _set_role(actor_email, RoleEnum.superadmin)
        token = _token(client, actor_email, password)
        response = client.delete(
            f"/v1/users/{target.json()['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"ok": True}
