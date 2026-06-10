import pytest
from fastapi import status

from app.services.auth_service import auth_service
from app.repositories.user_repository import user_repository


class TestAuthRegisterIntegration:
    async def test_register_happy_path(self, client, mock_user, mock_role):
        from unittest.mock import AsyncMock, patch

        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "securepass123",
            "full_name": "New User",
        }

        with (
            patch.object(user_repository, "get_by_email", new=AsyncMock(return_value=None)),
            patch.object(user_repository, "get_by_username", new=AsyncMock(return_value=None)),
            patch.object(user_repository, "get_user_role", new=AsyncMock(return_value=mock_role)),
            patch.object(user_repository, "create", new=AsyncMock(return_value=mock_user)),
        ):
            response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == mock_user.email

    async def test_register_duplicate_email(self, client):
        from unittest.mock import AsyncMock, patch
        from app.utils.exceptions import EmailAlreadyRegistered

        payload = {
            "email": "dup@example.com",
            "username": "unique1",
            "password": "securepass123",
            "full_name": "Dup User",
        }

        with patch.object(auth_service, "register", side_effect=EmailAlreadyRegistered()):
            response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["error_code"] == "email_already_exists"

    async def test_register_missing_fields(self, client):
        response = await client.post("/api/v1/auth/register", json={"email": "bad@example.com"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_invalid_email_type(self, client):
        payload = {
            "email": 12345,
            "username": "testuser",
            "password": "securepass123",
            "full_name": "Test User",
        }

        response = await client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthLoginIntegration:
    async def test_login_happy_path(self, client, mock_user):
        from unittest.mock import AsyncMock, patch

        with patch.object(
            auth_service, "login",
            new=AsyncMock(return_value=("access123", "refresh123", mock_user)),
        ):
            response = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "pass123"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["email"] == mock_user.email
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    async def test_login_bad_credentials(self, client):
        from app.utils.exceptions import CredentialsException
        from unittest.mock import AsyncMock, patch

        with patch.object(auth_service, "login", side_effect=CredentialsException()):
            response = await client.post("/api/v1/auth/login", json={"email": "wrong@b.com", "password": "wrongpass"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["error_code"] == "invalid_credentials"

    async def test_login_short_password(self, client):
        response = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "12345"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthRefreshIntegration:
    async def test_refresh_happy_path(self, client):
        from unittest.mock import AsyncMock, patch

        with patch.object(
            auth_service, "refresh",
            new=AsyncMock(return_value=("new_access", "new_refresh")),
        ):
            response = await client.post(
                "/api/v1/auth/refresh",
                cookies={"refresh_token": "valid_refresh_token"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["authenticated"] is True

    async def test_refresh_invalid_token(self, client):
        from app.utils.exceptions import InvalidToken
        from unittest.mock import AsyncMock, patch

        with patch.object(auth_service, "refresh", side_effect=InvalidToken()):
            response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "bad_token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthLogoutIntegration:
    async def test_logout_happy_path(self, client, auth_headers):
        from unittest.mock import AsyncMock, patch

        with patch.object(auth_service, "logout", new=AsyncMock(return_value=None)):
            response = await client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "token_to_revoke"},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_logout_no_auth(self, unauth_client):
        response = await unauth_client.post("/api/v1/auth/logout", json={"refresh_token": "token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthMeIntegration:
    async def test_me_happy_path(self, client, auth_headers, mock_user):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == mock_user.email

    async def test_me_no_auth(self, unauth_client):
        response = await unauth_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
