from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.reward_service import reward_service
from app.utils.exceptions import RewardNotFoundException, RewardOutOfStockException, InsufficientPointsException


class TestRewardsHealth:
    async def test_health_check_returns_ok(self, client):
        response = await client.get("/api/v1/rewards/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok", "service": "rewards"}


class TestRewardsList:
    async def test_list_rewards_returns_active_rewards(self, client, mock_reward):
        with patch.object(reward_service, "get_active_rewards", new=AsyncMock(return_value=[mock_reward])):
            response = await client.get("/api/v1/rewards/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == mock_reward.name

    async def test_list_rewards_empty_returns_empty_list(self, client):
        with patch.object(reward_service, "get_active_rewards", new=AsyncMock(return_value=[])):
            response = await client.get("/api/v1/rewards/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_list_rewards_invalid_limit_returns_422(self, client):
        response = await client.get("/api/v1/rewards/?limit=999")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_list_rewards_no_auth_required(self, client, mock_reward):
        with patch.object(reward_service, "get_active_rewards", new=AsyncMock(return_value=[mock_reward])):
            response = await client.get("/api/v1/rewards/")

        assert response.status_code == status.HTTP_200_OK


class TestRewardsGet:
    async def test_get_reward_returns_reward(self, client, mock_reward):
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "get_reward", new=AsyncMock(return_value=mock_reward)):
            response = await client.get(f"/api/v1/rewards/{reward_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == mock_reward.name

    async def test_get_reward_not_found_returns_404(self, client):
        reward_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(reward_service, "get_reward", new=AsyncMock(side_effect=RewardNotFoundException())):
            response = await client.get(f"/api/v1/rewards/{reward_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Reward not found"

    async def test_get_reward_invalid_uuid_returns_422(self, client):
        response = await client.get("/api/v1/rewards/not-a-uuid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRewardsRedeem:
    async def test_redeem_reward_returns_201(self, client, auth_headers, mock_reward, mock_redemption):
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "redeem_reward", new=AsyncMock(return_value=mock_redemption)):
            response = await client.post(f"/api/v1/rewards/{reward_id}/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["points_spent"] == 50

    async def test_redeem_reward_not_found_returns_404(self, client, auth_headers):
        reward_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(reward_service, "redeem_reward", new=AsyncMock(side_effect=RewardNotFoundException())):
            response = await client.post(f"/api/v1/rewards/{reward_id}/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_redeem_reward_out_of_stock_returns_400(self, client, auth_headers, mock_reward):
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "redeem_reward", new=AsyncMock(side_effect=RewardOutOfStockException())):
            response = await client.post(f"/api/v1/rewards/{reward_id}/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Reward is out of stock"

    async def test_redeem_reward_insufficient_points_returns_400(self, client, auth_headers, mock_reward):
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "redeem_reward", new=AsyncMock(side_effect=InsufficientPointsException())):
            response = await client.post(f"/api/v1/rewards/{reward_id}/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Insufficient points"

    async def test_redeem_reward_without_auth_returns_401(self, unauth_client, mock_reward):
        reward_id = str(mock_reward.id)

        response = await unauth_client.post(f"/api/v1/rewards/{reward_id}/redeem")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_redeem_reward_invalid_uuid_returns_422(self, client, auth_headers):
        response = await client.post("/api/v1/rewards/invalid-uuid/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
