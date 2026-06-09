from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.services.notification_service import notification_service


class TestNotificationsHealth:
    async def test_health_check_returns_ok(self, client):
        response = await client.get("/api/v1/notifications/health")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok", "service": "notifications"}


class TestNotificationsList:
    async def test_list_notifications_returns_list(self, client, auth_headers, mock_notification):
        with patch.object(notification_service, "get_user_notifications", new=AsyncMock(return_value=[mock_notification])):
            response = await client.get("/api/v1/notifications/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == mock_notification.title

    async def test_list_notifications_empty(self, client, auth_headers):
        with patch.object(notification_service, "get_user_notifications", new=AsyncMock(return_value=[])):
            response = await client.get("/api/v1/notifications/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_list_notifications_invalid_limit_returns_422(self, client, auth_headers):
        response = await client.get("/api/v1/notifications/?limit=999", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_list_notifications_without_auth_returns_401(self, unauth_client):
        response = await unauth_client.get("/api/v1/notifications/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationsUnread:
    async def test_get_unread_returns_unread_list(self, client, auth_headers, mock_notification):
        with patch.object(notification_service, "get_unread", new=AsyncMock(return_value=[mock_notification])):
            response = await client.get("/api/v1/notifications/unread", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    async def test_get_unread_without_auth_returns_401(self, unauth_client):
        response = await unauth_client.get("/api/v1/notifications/unread")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationsCountUnread:
    async def test_count_unread_returns_count(self, client, auth_headers):
        with patch.object(notification_service, "count_unread", new=AsyncMock(return_value=5)):
            response = await client.get("/api/v1/notifications/unread/count", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"count": 5}

    async def test_count_unread_zero(self, client, auth_headers):
        with patch.object(notification_service, "count_unread", new=AsyncMock(return_value=0)):
            response = await client.get("/api/v1/notifications/unread/count", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"count": 0}


class TestNotificationsMarkAsRead:
    async def test_mark_as_read_returns_message(self, client, auth_headers):
        notification_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        with patch.object(notification_service, "mark_as_read", new=AsyncMock(return_value=None)):
            response = await client.patch(f"/api/v1/notifications/{notification_id}/read", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Notification marked as read"

    async def test_mark_as_read_invalid_uuid_returns_422(self, client, auth_headers):
        response = await client.patch("/api/v1/notifications/invalid-uuid/read", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_mark_as_read_without_auth_returns_401(self, unauth_client):
        notification_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        response = await unauth_client.patch(f"/api/v1/notifications/{notification_id}/read")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationsMarkAllAsRead:
    async def test_mark_all_as_read_returns_message(self, client, auth_headers):
        with patch.object(notification_service, "mark_all_as_read", new=AsyncMock(return_value=None)):
            response = await client.patch("/api/v1/notifications/read-all", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "All notifications marked as read"

    async def test_mark_all_as_read_without_auth_returns_401(self, unauth_client):
        response = await unauth_client.patch("/api/v1/notifications/read-all")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
