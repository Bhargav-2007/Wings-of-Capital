import pytest
from sqlalchemy import select


def test_register_verify_login_logout(test_client, db_session):
    from auth_service.main import app as auth_app
    from auth_service.models.user import User
    from auth_service.utils.tokens import create_verification_token

    client = test_client(auth_app)

    email = "tester@example.com"
    password = "VeryStrongPassword123!"

    # Register
    res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert res.status_code == 201
    payload = res.json()
    assert payload.get("verification_sent") is True

    # Ensure user exists in DB
    user = db_session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    assert user is not None

    # Simulate email verification by generating a token and calling verify endpoint
    token = create_verification_token(str(user.id))
    res = client.post("/api/v1/auth/verify", json={"token": token})
    assert res.status_code == 200

    # Login
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data and "refresh_token" in data

    # Refresh
    refresh_token = data["refresh_token"]
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200

    # Logout (requires Authorization header)
    access_token = data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    res = client.post("/api/v1/auth/logout", headers=headers)
    assert res.status_code == 200
