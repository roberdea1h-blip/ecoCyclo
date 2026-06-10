from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.report_service import report_service
from app.utils.exceptions import (
    CannotClaimOwnReportException,
    ReportNotFoundException,
    ReportNotPendingException,
)


class TestReportsClaim:
    async def test_claim_happy_path(self, client, auth_headers, mock_report, user_id):
        report_id = str(mock_report.id)
        mock_report.status = "in_progress"
        mock_report.cleaner_id = user_id
        mock_report.cleaner_name = "Test User"

        with patch.object(report_service, "claim_report", new=AsyncMock(return_value=mock_report)):
            response = await client.post(f"/api/v1/reports/{report_id}/claim", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["cleaner_id"] == str(user_id)

    async def test_claim_not_found_returns_404(self, client, auth_headers):
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "claim_report", new=AsyncMock(side_effect=ReportNotFoundException())):
            response = await client.post(f"/api/v1/reports/{report_id}/claim", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["error_code"] == "report_not_found"

    async def test_claim_not_pending_returns_400(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)

        with patch.object(report_service, "claim_report", new=AsyncMock(side_effect=ReportNotPendingException())):
            response = await client.post(f"/api/v1/reports/{report_id}/claim", headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_claim_own_report_returns_400(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)

        with patch.object(report_service, "claim_report", new=AsyncMock(side_effect=CannotClaimOwnReportException())):
            response = await client.post(f"/api/v1/reports/{report_id}/claim", headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_claim_invalid_uuid_returns_422(self, client, auth_headers):
        response = await client.post("/api/v1/reports/not-a-uuid/claim", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_claim_no_auth_returns_401(self, unauth_client):
        response = await unauth_client.post("/api/v1/reports/00000000-0000-0000-0000-000000000000/claim")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
