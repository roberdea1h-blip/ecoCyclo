from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.report_service import report_service
from app.utils.exceptions import ReportNotFoundException, ForbiddenException


class TestReportsHealth:
    async def test_health_check_returns_ok(self, client):
        response = await client.get("/api/v1/reports/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok", "service": "reports"}


class TestReportsCreate:
    async def test_create_report_returns_201(self, client, auth_headers, mock_report):
        payload = {
            "waste_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "Illegal dumping at park",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

        with patch.object(report_service, "create_report", new=AsyncMock(return_value=mock_report)):
            response = await client.post("/api/v1/reports/", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == mock_report.title

    async def test_create_report_missing_title_returns_422(self, client, auth_headers):
        payload = {
            "waste_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

        response = await client.post("/api/v1/reports/", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_report_invalid_latitude_returns_422(self, client, auth_headers):
        payload = {
            "waste_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "Test",
            "latitude": 100.0,
            "longitude": -74.0060,
        }

        response = await client.post("/api/v1/reports/", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_report_without_auth_returns_401(self, unauth_client):
        payload = {
            "waste_type_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "Test",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

        response = await unauth_client.post("/api/v1/reports/", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestReportsList:
    async def test_list_reports_returns_list(self, client, auth_headers, mock_report):
        with patch.object(report_service, "get_filtered_reports", new=AsyncMock(return_value=[mock_report])):
            response = await client.get("/api/v1/reports/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == mock_report.title

    async def test_list_reports_empty_returns_empty_list(self, client, auth_headers):
        with patch.object(report_service, "get_filtered_reports", new=AsyncMock(return_value=[])):
            response = await client.get("/api/v1/reports/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_list_reports_pagination_params(self, client, auth_headers, mock_report):
        with patch.object(report_service, "get_filtered_reports", new=AsyncMock(return_value=[mock_report])):
            response = await client.get("/api/v1/reports/?skip=0&limit=10", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK

    async def test_list_reports_invalid_limit_returns_422(self, client, auth_headers):
        response = await client.get("/api/v1/reports/?limit=999", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_list_reports_without_auth_returns_401(self, unauth_client):
        response = await unauth_client.get("/api/v1/reports/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestReportsMine:
    async def test_my_reports_returns_user_reports(self, client, auth_headers, mock_report):
        with patch.object(report_service, "get_user_reports", new=AsyncMock(return_value=[mock_report])):
            response = await client.get("/api/v1/reports/mine", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    async def test_my_reports_without_auth_returns_401(self, unauth_client):
        response = await unauth_client.get("/api/v1/reports/mine")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestReportsGetById:
    async def test_get_report_returns_report(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)

        with patch.object(report_service, "get_report", new=AsyncMock(return_value=mock_report)):
            response = await client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == mock_report.title

    async def test_get_report_not_found_returns_404(self, client, auth_headers):
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "get_report", new=AsyncMock(side_effect=ReportNotFoundException())):
            response = await client.get(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Report not found"

    async def test_get_report_invalid_uuid_returns_422(self, client, auth_headers):
        response = await client.get("/api/v1/reports/not-a-uuid", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestReportsUpdate:
    async def test_update_report_returns_updated_report(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)
        payload = {"title": "Updated Title"}
        mock_report.title = "Updated Title"

        with patch.object(report_service, "update_report", new=AsyncMock(return_value=mock_report)):
            response = await client.patch(f"/api/v1/reports/{report_id}", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["title"] == "Updated Title"

    async def test_update_report_not_found_returns_404(self, client, auth_headers):
        report_id = "00000000-0000-0000-0000-000000000000"
        payload = {"title": "Updated"}

        with patch.object(report_service, "update_report", new=AsyncMock(side_effect=ReportNotFoundException())):
            response = await client.patch(f"/api/v1/reports/{report_id}", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_report_forbidden_returns_403(self, client, auth_headers):
        report_id = "00000000-0000-0000-0000-000000000000"
        payload = {"title": "Hacked"}

        with patch.object(report_service, "update_report", new=AsyncMock(side_effect=ForbiddenException())):
            response = await client.patch(f"/api/v1/reports/{report_id}", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_report_invalid_status_returns_422(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)
        payload = {"status": "invalid_status"}

        response = await client.patch(f"/api/v1/reports/{report_id}", json=payload, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestReportsDelete:
    async def test_delete_report_returns_204(self, client, auth_headers, mock_report):
        report_id = str(mock_report.id)

        with patch.object(report_service, "delete_report", new=AsyncMock(return_value=None)):
            response = await client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_report_not_found_returns_404(self, client, auth_headers):
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "delete_report", new=AsyncMock(side_effect=ReportNotFoundException())):
            response = await client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_report_forbidden_returns_403(self, client, auth_headers):
        report_id = "00000000-0000-0000-0000-000000000000"

        with patch.object(report_service, "delete_report", new=AsyncMock(side_effect=ForbiddenException())):
            response = await client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
