from uuid import uuid4

from fastapi.testclient import TestClient

from src.main import app


def test_signup_login_and_me():
    email = f"test-{uuid4()}@example.com"
    password = "secret123!"

    with TestClient(app) as client:
        signup = client.post(
            "/v1/auth/signup", json={"email": email, "password": password}
        )
        assert signup.status_code == 200
        assert signup.json()["email"] == email

        login = client.post(
            "/v1/auth/login", data={"username": email, "password": password}
        )
        assert login.status_code == 200
        token = login.json()["access_token"]
        assert token

        me = client.get("/v1/users/me/", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["email"] == email
