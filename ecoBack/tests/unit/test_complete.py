from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.report_service import report_service
from app.utils.exceptions import (
    NotAssignedCleanerException,
    ReportNotFoundException,
    ReportNotInProgressException,
)


class TestReportsComplete:
    async def test_complete_happy_path(self, client, auth_headers, mock_report_in_progress):
        report_id = str(mock_report_in_progress.id)
        mock_report_in_progress.status = "cleaned"

        payload = {"collected_weight": 2.5, "notes": "Cleaned the area"}

        with patch.object(report_service, "complete_report", new=AsyncMock(return_value=mock_report_in_progress)):
            response = await client.post(
                f"/api/v1/reports/{report_id}/complete",
                json=payload,
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "cleaned"

    async def test_complete_without_weight(self, client, auth_headers, mock_report_in_progress):
        report_id = str(mock_report_in_progress.id)
        mock_report_in_progress.status = "cleaned"

        with patch.object(report_service, "complete_report", new=AsyncMock(return_value=mock_report_in_progress)):
            response = await client.post(
                f"/api/v1/reports/{report_id}/complete",
                json={},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "cleaned"

    async def test_complete_not_found_returns_404(self, client, auth_headers):
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "complete_report", new=AsyncMock(side_effect=ReportNotFoundException())):
            response = await client.post(
                f"/api/v1/reports/{report_id}/complete",
                json={},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_complete_not_in_progress_returns_400(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)

        with patch.object(report_service, "complete_report", new=AsyncMock(side_effect=ReportNotInProgressException())):
            response = await client.post(
                f"/api/v1/reports/{report_id}/complete",
                json={},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_complete_not_assigned_returns_403(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)

        with patch.object(report_service, "complete_report", new=AsyncMock(side_effect=NotAssignedCleanerException())):
            response = await client.post(
                f"/api/v1/reports/{report_id}/complete",
                json={},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_complete_invalid_uuid_returns_422(self, client, auth_headers):
        response = await client.post(
            "/api/v1/reports/not-a-uuid/complete",
            json={},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_complete_no_auth_returns_401(self, unauth_client):
        response = await unauth_client.post(
            "/api/v1/reports/00000000-0000-0000-0000-000000000000/complete",
            json={},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
