from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.user_service import user_service
from app.utils.exceptions import UserNotFoundException


class TestUsersHealth:
    async def test_health_check_returns_ok(self, client):
        response = await client.get("/api/v1/users/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok", "service": "users"}


class TestUsersGetMe:
    async def test_get_my_profile_returns_current_user(self, client, auth_headers, mock_user):
        response = await client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == mock_user.email
        assert data["username"] == mock_user.username

    async def test_get_my_profile_without_token_returns_401(self, unauth_client):
        response = await unauth_client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUsersUpdateMe:
    async def test_update_profile_returns_updated_user(self, client, auth_headers, mock_user):
        payload = {"full_name": "Updated Name"}
        mock_user.full_name = "Updated Name"

        with patch.object(user_service, "update_profile", new=AsyncMock(return_value=mock_user)):
            response = await client.patch("/api/v1/users/me", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "Updated Name"

    async def test_update_profile_partial_avatar_only(self, client, auth_headers, mock_user):
        payload = {"avatar_url": "https://example.com/avatar.jpg"}
        mock_user.avatar_url = "https://example.com/avatar.jpg"

        with patch.object(user_service, "update_profile", new=AsyncMock(return_value=mock_user)):
            response = await client.patch("/api/v1/users/me", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["avatar_url"] == "https://example.com/avatar.jpg"

    async def test_update_profile_without_auth_returns_401(self, unauth_client):
        payload = {"full_name": "Hacker"}

        response = await unauth_client.patch("/api/v1/users/me", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_profile_invalid_field_returns_422(self, client, auth_headers):
        payload = {"full_name": 123}

        response = await client.patch("/api/v1/users/me", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUsersGetById:
    async def test_get_user_by_id_returns_user(self, client, auth_headers, mock_user):
        user_id = str(mock_user.id)

        with patch.object(user_service, "get_by_id", new=AsyncMock(return_value=mock_user)):
            response = await client.get(f"/api/v1/users/{user_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == mock_user.email

    async def test_get_user_not_found_returns_404(self, client, auth_headers):
        user_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(user_service, "get_by_id", new=AsyncMock(side_effect=UserNotFoundException())):
            response = await client.get(f"/api/v1/users/{user_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User not found"

    async def test_get_user_invalid_uuid_returns_422(self, client, auth_headers):
        response = await client.get("/api/v1/users/not-a-uuid", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_user_without_auth_returns_401(self, unauth_client, mock_user):
        response = await unauth_client.get(f"/api/v1/users/{mock_user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
