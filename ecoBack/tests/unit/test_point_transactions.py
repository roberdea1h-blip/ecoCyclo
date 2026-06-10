from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from app.repositories.point_transaction_repository import point_transaction_repository


class TestPointTransactionsMe:
    async def test_my_transactions_happy_path(self, client, auth_headers):
        from app.models.point_transaction import PointTransaction

        mock_tx = MagicMock(spec=PointTransaction)
        mock_tx.id = "00000000-0000-0000-0000-000000000001"
        mock_tx.type = "earned"
        mock_tx.points = 50
        mock_tx.description = "Puntos por limpiar reporte"
        mock_tx.reference_id = None
        mock_tx.created_at = "2024-01-01T00:00:00Z"

        with patch.object(
            point_transaction_repository, "get_by_user",
            new=AsyncMock(return_value=[mock_tx]),
        ):
            response = await client.get("/api/v1/point-transactions/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["type"] == "earned"
        assert data[0]["points"] == 50

    async def test_my_transactions_empty(self, client, auth_headers):
        with patch.object(
            point_transaction_repository, "get_by_user",
            new=AsyncMock(return_value=[]),
        ):
            response = await client.get("/api/v1/point-transactions/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_my_transactions_no_auth_returns_401(self, unauth_client):
        response = await unauth_client.get("/api/v1/point-transactions/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_my_transactions_pagination(self, client, auth_headers):
        from app.models.point_transaction import PointTransaction

        mock_tx = MagicMock(spec=PointTransaction)
        mock_tx.id = "00000000-0000-0000-0000-000000000001"
        mock_tx.type = "earned"
        mock_tx.points = 50
        mock_tx.description = "Test"
        mock_tx.reference_id = None
        mock_tx.created_at = "2024-01-01T00:00:00Z"

        with patch.object(
            point_transaction_repository, "get_by_user",
            new=AsyncMock(return_value=[mock_tx]),
        ):
            response = await client.get("/api/v1/point-transactions/me?skip=0&limit=10", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
