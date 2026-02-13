"""Authentication route tests."""
from fastapi.testclient import TestClient


def _user_payload() -> dict[str, str]:
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "+15555550123",
        "contact": "email",
        "short_description": "Sample user",
        "username": "janedoe",
        "password": "supersecret",
        "confirm_password": "supersecret",
    }


def test_register_user_returns_created_user(client: TestClient) -> None:
    response = client.post("/api/v1/auth/register", json=_user_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane.doe@example.com"
    assert "id" in data


def test_register_user_duplicate_email_fails(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=_user_payload())
    duplicate_payload = _user_payload() | {"username": "different"}
    response = client.post("/api/v1/auth/register", json=duplicate_payload)
    assert response.status_code == 400


def test_login_with_username_returns_token(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=_user_payload())
    login_payload = {"identifier": "janedoe", "password": "supersecret"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert isinstance(token, str)
    assert token


def test_login_with_wrong_password_returns_unauthorized(client: TestClient) -> None:
    client.post("/api/v1/auth/register", json=_user_payload())
    login_payload = {"identifier": "janedoe", "password": "wrongpass"}
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid credentials"


def test_forgot_password_returns_accepted_even_for_unknown_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"identifier": "missing@example.com"},
    )
    assert response.status_code == 202
    assert "message" in response.json()


def test_reset_password_flow_updates_credentials(client: TestClient, monkeypatch) -> None:
    client.post("/api/v1/auth/register", json=_user_payload())
    fixed_token = "static-token"
    monkeypatch.setattr("app.services.auth_service.secrets.token_urlsafe", lambda _: fixed_token)

    forgot_payload = {"identifier": "janedoe"}
    response = client.post("/api/v1/auth/forgot-password", json=forgot_payload)
    assert response.status_code == 202

    reset_payload = {
        "token": fixed_token,
        "new_password": "brandnewpass",
        "confirm_password": "brandnewpass",
    }
    reset_response = client.post("/api/v1/auth/reset-password", json=reset_payload)
    assert reset_response.status_code == 200
    assert "Password updated" in reset_response.json()["message"]

    old_login = {"identifier": "janedoe", "password": "supersecret"}
    old_login_response = client.post("/api/v1/auth/login", json=old_login)
    assert old_login_response.status_code == 401

    new_login = {"identifier": "janedoe", "password": "brandnewpass"}
    new_login_response = client.post("/api/v1/auth/login", json=new_login)
    assert new_login_response.status_code == 200


def test_reset_password_with_invalid_token_fails(client: TestClient) -> None:
    reset_payload = {
        "token": "invalid-token",
        "new_password": "whateverpass",
        "confirm_password": "whateverpass",
    }
    response = client.post("/api/v1/auth/reset-password", json=reset_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "invalid or expired reset token"
