import pytest
from fastapi import status

from app.services.report_service import report_service


class TestReportsCreateIntegration:
    async def test_create_report_happy_path(self, client, auth_headers, mock_report):
        from unittest.mock import AsyncMock, patch

        payload = {
            "waste_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "Dumping near river",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

        with patch.object(report_service, "create_report", new=AsyncMock(return_value=mock_report)):
            response = await client.post("/api/v1/reports/", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == mock_report.title
        assert data["latitude"] == mock_report.latitude

    async def test_create_report_missing_waste_type_returns_422(self, client, auth_headers):
        payload = {
            "title": "Test",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

        response = await client.post("/api/v1/reports/", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_report_no_auth(self, unauth_client):
        payload = {
            "waste_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "Test",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

        response = await unauth_client.post("/api/v1/reports/", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestReportsListIntegration:
    async def test_list_reports_happy_path(self, client, auth_headers, mock_report):
        from unittest.mock import AsyncMock, patch

        with patch.object(report_service, "get_all_reports", new=AsyncMock(return_value=[mock_report])):
            response = await client.get("/api/v1/reports/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    async def test_list_reports_pagination(self, client, auth_headers, mock_report):
        from unittest.mock import AsyncMock, patch

        with patch.object(report_service, "get_all_reports", new=AsyncMock(return_value=[mock_report])):
            response = await client.get("/api/v1/reports/?skip=0&limit=5", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK


class TestReportsGetIntegration:
    async def test_get_report_happy_path(self, client, auth_headers, mock_report):
        from unittest.mock import AsyncMock, patch
        report_id = str(mock_report.id)

        with patch.object(report_service, "get_report", new=AsyncMock(return_value=mock_report)):
            response = await client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == report_id

    async def test_get_report_not_found(self, client, auth_headers):
        from app.utils.exceptions import ReportNotFoundException
        from unittest.mock import AsyncMock, patch
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "get_report", side_effect=ReportNotFoundException()):
            response = await client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_report_invalid_uuid(self, client, auth_headers):
        response = await client.get("/api/v1/reports/not-a-uuid", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestReportsUpdateIntegration:
    async def test_update_report_happy_path(self, client, auth_headers, mock_report):
        from unittest.mock import AsyncMock, patch
        report_id = str(mock_report.id)
        mock_report.title = "Updated Title"

        with patch.object(report_service, "update_report", new=AsyncMock(return_value=mock_report)):
            response = await client.patch(
                f"/api/v1/reports/{report_id}",
                json={"title": "Updated Title"},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Updated Title"

    async def test_update_report_forbidden(self, client, auth_headers):
        from app.utils.exceptions import ForbiddenException
        from unittest.mock import AsyncMock, patch
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "update_report", side_effect=ForbiddenException()):
            response = await client.patch(
                f"/api/v1/reports/{report_id}",
                json={"title": "Hacked"},
                headers=auth_headers,
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_report_invalid_status(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)

        response = await client.patch(
            f"/api/v1/reports/{report_id}",
            json={"status": "invalid_status"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestReportsDeleteIntegration:
    async def test_delete_report_happy_path(self, client, auth_headers, mock_report):
        from unittest.mock import AsyncMock, patch
        report_id = str(mock_report.id)

        with patch.object(report_service, "delete_report", new=AsyncMock(return_value=None)):
            response = await client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_report_not_found(self, client, auth_headers):
        from app.utils.exceptions import ReportNotFoundException
        from unittest.mock import AsyncMock, patch
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "delete_report", side_effect=ReportNotFoundException()):
            response = await client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
