import pytest
from fastapi import status

from app.services.report_service import report_service
from app.services.reward_service import reward_service
from app.repositories.user_repository import user_repository


class TestAdminUsersIntegration:
    async def test_list_users_happy_path(self, admin_client, admin_auth_headers, mock_user):
        from unittest.mock import AsyncMock, patch

        with patch.object(user_repository, "get_multi", new=AsyncMock(return_value=[mock_user])):
            response = await admin_client.get("/api/v1/admin/users", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    async def test_list_users_forbidden_for_regular_user(self, client, auth_headers):
        response = await client.get("/api/v1/admin/users", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_users_no_auth(self, unauth_client):
        response = await unauth_client.get("/api/v1/admin/users")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAdminReportsIntegration:
    async def test_list_all_reports_happy_path(self, admin_client, admin_auth_headers, mock_report):
        from unittest.mock import AsyncMock, patch

        with patch.object(report_service, "get_all_reports", new=AsyncMock(return_value=[mock_report])):
            response = await admin_client.get("/api/v1/admin/reports", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    async def test_list_all_reports_forbidden(self, client, auth_headers):
        response = await client.get("/api/v1/admin/reports", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminCreateRewardIntegration:
    async def test_create_reward_happy_path(self, admin_client, admin_auth_headers, mock_reward):
        from unittest.mock import AsyncMock, patch
        payload = {"name": "Gold Badge", "description": "A shiny badge", "points_cost": 500}

        with patch.object(reward_service, "create_reward", new=AsyncMock(return_value=mock_reward)):
            response = await admin_client.post("/api/v1/admin/rewards", json=payload, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == mock_reward.name

    async def test_create_reward_validation_error(self, admin_client, admin_auth_headers):
        payload = {"description": "Missing name and cost"}

        response = await admin_client.post("/api/v1/admin/rewards", json=payload, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAdminSetupIntegration:
    async def test_setup_database_happy_path(self, admin_client, admin_auth_headers):
        from unittest.mock import AsyncMock, patch

        with patch("app.db.init_db.init_db", new=AsyncMock(return_value=None)):
            response = await admin_client.post("/api/v1/admin/setup", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Database initialized successfully"

    async def test_setup_database_forbidden(self, client, auth_headers):
        response = await client.post("/api/v1/admin/setup", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
