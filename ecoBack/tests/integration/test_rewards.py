import pytest
from fastapi import status

from app.services.reward_service import reward_service


class TestRewardsListIntegration:
    async def test_list_rewards_happy_path(self, client, mock_reward):
        from unittest.mock import AsyncMock, patch

        with patch.object(reward_service, "get_active_rewards", new=AsyncMock(return_value=[mock_reward])):
            response = await client.get("/api/v1/rewards/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == mock_reward.name

    async def test_list_rewards_empty(self, client):
        from unittest.mock import AsyncMock, patch

        with patch.object(reward_service, "get_active_rewards", new=AsyncMock(return_value=[])):
            response = await client.get("/api/v1/rewards/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_list_rewards_no_auth_required(self, client, mock_reward):
        from unittest.mock import AsyncMock, patch

        with patch.object(reward_service, "get_active_rewards", new=AsyncMock(return_value=[mock_reward])):
            response = await client.get("/api/v1/rewards/")

        assert response.status_code == status.HTTP_200_OK


class TestRewardsGetIntegration:
    async def test_get_reward_happy_path(self, client, mock_reward):
        from unittest.mock import AsyncMock, patch
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "get_reward", new=AsyncMock(return_value=mock_reward)):
            response = await client.get(f"/api/v1/rewards/{reward_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == mock_reward.name

    async def test_get_reward_not_found(self, client):
        from app.utils.exceptions import RewardNotFoundException
        from unittest.mock import AsyncMock, patch
        reward_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(reward_service, "get_reward", side_effect=RewardNotFoundException()):
            response = await client.get(f"/api/v1/rewards/{reward_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_reward_invalid_uuid(self, client):
        response = await client.get("/api/v1/rewards/not-a-uuid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRewardsRedeemIntegration:
    async def test_redeem_happy_path(self, client, auth_headers, mock_reward):
        from unittest.mock import AsyncMock, patch
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "redeem_reward", new=AsyncMock(return_value=True)):
            response = await client.post(f"/api/v1/rewards/{reward_id}/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["id"] == reward_id

    async def test_redeem_out_of_stock(self, client, auth_headers, mock_reward):
        from app.utils.exceptions import RewardOutOfStockException
        from unittest.mock import AsyncMock, patch
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "redeem_reward", side_effect=RewardOutOfStockException()):
            response = await client.post(f"/api/v1/rewards/{reward_id}/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_redeem_insufficient_points(self, client, auth_headers, mock_reward):
        from app.utils.exceptions import InsufficientPointsException
        from unittest.mock import AsyncMock, patch
        reward_id = str(mock_reward.id)

        with patch.object(reward_service, "redeem_reward", side_effect=InsufficientPointsException()):
            response = await client.post(f"/api/v1/rewards/{reward_id}/redeem", headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_redeem_no_auth(self, unauth_client, mock_reward):
        reward_id = str(mock_reward.id)

        response = await unauth_client.post(f"/api/v1/rewards/{reward_id}/redeem")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
