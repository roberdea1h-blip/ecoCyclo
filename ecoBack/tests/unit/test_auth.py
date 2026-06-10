from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.auth_service import auth_service


class TestAuthHealth:
    async def test_health_check_returns_ok(self, client):
        response = await client.get("/api/v1/auth/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok", "service": "auth"}


class TestAuthRegister:
    async def test_register_creates_user_and_returns_201(self, client, mock_user):
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
            "full_name": "New User",
        }

        with patch.object(auth_service, "register", new=AsyncMock(return_value=mock_user)):
            response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == mock_user.email
        assert data["username"] == mock_user.username

    async def test_register_missing_fields_returns_422(self, client):
        payload = {"email": "bad@example.com"}

        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_short_password_returns_422(self, client):
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "12345",
            "full_name": "New User",
        }

        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_email_already_exists_returns_409(self, client):
        from app.utils.exceptions import EmailAlreadyRegistered

        payload = {
            "email": "existing@example.com",
            "username": "newuser",
            "password": "securepass123",
            "full_name": "New User",
        }

        with patch.object(auth_service, "register", new=AsyncMock(side_effect=EmailAlreadyRegistered())):
            response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["error_code"] == "email_already_exists"

    async def test_register_username_already_exists_returns_409(self, client):
        from app.users.exceptions import UsernameAlreadyExistsException

        payload = {
            "email": "new@example.com",
            "username": "takenuser",
            "password": "securepass123",
            "full_name": "New User",
        }

        with patch.object(auth_service, "register", new=AsyncMock(side_effect=UsernameAlreadyExistsException())):
            response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["error_code"] == "username_already_exists"


class TestAuthLogin:
    async def test_login_valid_credentials_returns_tokens(self, client, mock_user):
        payload = {"email": "test@example.com", "password": "correctpassword"}

        with patch.object(
            auth_service, "login",
            new=AsyncMock(return_value=("access.token.here", "refresh.token.here", mock_user)),
        ):
            response = await client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["email"] == "testuser@example.com"
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    async def test_login_invalid_credentials_returns_401(self, client):
        from app.utils.exceptions import CredentialsException

        payload = {"email": "wrong@example.com", "password": "wrongpassword"}

        with patch.object(auth_service, "login", new=AsyncMock(side_effect=CredentialsException())):
            response = await client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_missing_password_returns_422(self, client):
        payload = {"email": "test@example.com"}

        response = await client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_login_short_password_returns_422(self, client):
        payload = {"email": "test@example.com", "password": "12345"}

        response = await client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthRefresh:
    async def test_refresh_valid_token_returns_new_tokens(self, client):
        with patch.object(
            auth_service, "refresh",
            new=AsyncMock(return_value=("new.access.token", "new.refresh.token")),
        ):
            response = await client.post(
                "/api/v1/auth/refresh",
                cookies={"refresh_token": "valid.refresh.token"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["authenticated"] is True

    async def test_refresh_invalid_token_returns_401(self, client):
        from app.utils.exceptions import InvalidToken

        payload = {"refresh_token": "expired.or.invalid.token"}

        with patch.object(auth_service, "refresh", new=AsyncMock(side_effect=InvalidToken())):
            response = await client.post("/api/v1/auth/refresh", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_refresh_empty_token_returns_401(self, unauth_client):
        payload = {"refresh_token": ""}

        response = await unauth_client.post("/api/v1/auth/refresh", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthLogout:
    async def test_logout_success_returns_204(self, client, auth_headers):
        payload = {"refresh_token": "some.refresh.token"}

        with patch.object(auth_service, "logout", new=AsyncMock(return_value=None)):
            response = await client.post("/api/v1/auth/logout", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_logout_without_token_returns_401(self, unauth_client):
        payload = {"refresh_token": "some.refresh.token"}

        response = await unauth_client.post("/api/v1/auth/logout", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthMe:
    async def test_me_returns_current_user(self, client, auth_headers, mock_user):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == mock_user.email
        assert data["username"] == mock_user.username

    async def test_me_without_token_returns_401(self, unauth_client):
        response = await unauth_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
