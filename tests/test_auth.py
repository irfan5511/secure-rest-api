import jwt
from sqlalchemy import select

from app.config import settings
from app.models import User
from app.security import ISSUER

EMAIL = "demo@example.com"
PASSWORD = "Long-Passphrase-2026!"


def signup(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/register", json={"email": email, "password": password})


def signin(client, email=EMAIL, password=PASSWORD):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_hashes_password_and_hides_hash(client, db):
    response = signup(client)
    assert response.status_code == 201
    assert response.json()["email"] == EMAIL
    assert response.json()["role"] == "user"
    assert "hashed_password" not in response.json()
    user = db.scalar(select(User).where(User.email == EMAIL))
    assert user.hashed_password != PASSWORD
    assert user.hashed_password.startswith("$argon2")


def test_duplicate_email_is_conflict(client):
    assert signup(client).status_code == 201
    assert signup(client, email="DEMO@example.com").status_code == 409


def test_short_password_is_rejected(client):
    assert signup(client, password="abc").status_code == 422


def test_invalid_email_is_rejected(client):
    assert signup(client, email="not-an-email").status_code == 422


def test_login_and_me(client):
    signup(client)
    response = signin(client)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    token = response.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == EMAIL


def test_wrong_password_rejected(client):
    signup(client)
    assert signin(client, password="incorrect_password").status_code == 401


def test_unknown_account_rejected(client):
    assert signin(client).status_code == 401


def test_missing_token_rejected(client):
    assert client.get("/auth/me").status_code == 401


def test_invalid_token_rejected(client):
    assert client.get("/auth/me", headers={"Authorization": "Bearer fake-token"}).status_code == 401


def test_user_cannot_access_admin(client):
    signup(client)
    token = signin(client).json()["access_token"]
    assert client.get("/admin/users", headers={"Authorization": f"Bearer {token}"}).status_code == 403


def test_admin_can_access_admin(client, db):
    signup(client)
    user = db.scalar(select(User).where(User.email == EMAIL))
    user.role = "admin"
    db.commit()
    token = signin(client).json()["access_token"]
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "hashed_password" not in response.json()[0]


def test_wrong_token_type_rejected(client):
    signup(client)
    token = signin(client).json()["access_token"]
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm], issuer=ISSUER)
    payload["type"] = "refresh"
    wrong_type = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {wrong_type}"}).status_code == 401


def test_deleted_user_token_rejected(client, db):
    signup(client)
    token = signin(client).json()["access_token"]
    user = db.scalar(select(User).where(User.email == EMAIL))
    db.delete(user)
    db.commit()
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
