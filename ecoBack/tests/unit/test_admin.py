from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.report_service import report_service
from app.services.reward_service import reward_service
from app.repositories.user_repository import user_repository


class TestAdminHealth:
    async def test_health_check_returns_ok(self, admin_client):
        response = await admin_client.get("/api/v1/admin/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok", "service": "admin"}


class TestAdminListUsers:
    async def test_list_users_returns_all_users(self, admin_client, admin_auth_headers, mock_user):
        with patch.object(user_repository, "get_multi", new=AsyncMock(return_value=[mock_user])):
            response = await admin_client.get("/api/v1/admin/users", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["email"] == mock_user.email

    async def test_list_users_empty(self, admin_client, admin_auth_headers):
        with patch.object(user_repository, "get_multi", new=AsyncMock(return_value=[])):
            response = await admin_client.get("/api/v1/admin/users", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_list_users_regular_user_forbidden(self, client, auth_headers):
        response = await client.get("/api/v1/admin/users", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_users_invalid_limit_returns_422(self, admin_client, admin_auth_headers):
        response = await admin_client.get("/api/v1/admin/users?limit=999", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAdminListAllReports:
    async def test_list_all_reports_returns_reports(self, admin_client, admin_auth_headers, mock_report):
        with patch.object(report_service, "get_all_reports", new=AsyncMock(return_value=[mock_report])):
            response = await admin_client.get("/api/v1/admin/reports", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    async def test_list_all_reports_regular_user_forbidden(self, client, auth_headers):
        response = await client.get("/api/v1/admin/reports", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminCreateReward:
    async def test_create_reward_returns_201(self, admin_client, admin_auth_headers, mock_reward):
        payload = {
            "name": "New Reward",
            "description": "A brand new reward",
            "points_cost": 100,
        }

        with patch.object(reward_service, "create_reward", new=AsyncMock(return_value=mock_reward)):
            response = await admin_client.post("/api/v1/admin/rewards", json=payload, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == mock_reward.name

    async def test_create_reward_missing_name_returns_422(self, admin_client, admin_auth_headers):
        payload = {"description": "No name", "points_cost": 100}

        response = await admin_client.post("/api/v1/admin/rewards", json=payload, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_reward_negative_cost_returns_422(self, admin_client, admin_auth_headers):
        payload = {"name": "Bad Reward", "description": "Negative cost", "points_cost": -10}

        response = await admin_client.post("/api/v1/admin/rewards", json=payload, headers=admin_auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_reward_regular_user_forbidden(self, client, auth_headers):
        payload = {"name": "Hacked Reward", "description": "Nope", "points_cost": 10}

        response = await client.post("/api/v1/admin/rewards", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminSetup:
    async def test_setup_database_returns_message(self, admin_client, admin_auth_headers):
        with patch("app.db.init_db.init_db", new=AsyncMock(return_value=None)):
            response = await admin_client.post("/api/v1/admin/setup", headers=admin_auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Database initialized successfully"

    async def test_setup_database_regular_user_forbidden(self, client, auth_headers):
        response = await client.post("/api/v1/admin/setup", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
