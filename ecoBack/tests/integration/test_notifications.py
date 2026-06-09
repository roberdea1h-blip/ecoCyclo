import pytest
from fastapi import status

from app.services.notification_service import notification_service


class TestNotificationsListIntegration:
    async def test_list_notifications_happy_path(self, client, auth_headers, mock_notification):
        from unittest.mock import AsyncMock, patch

        with patch.object(notification_service, "get_user_notifications", new=AsyncMock(return_value=[mock_notification])):
            response = await client.get("/api/v1/notifications/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == mock_notification.title

    async def test_list_notifications_no_auth(self, unauth_client):
        response = await unauth_client.get("/api/v1/notifications/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationsUnreadIntegration:
    async def test_get_unread_happy_path(self, client, auth_headers, mock_notification):
        from unittest.mock import AsyncMock, patch

        with patch.object(notification_service, "get_unread", new=AsyncMock(return_value=[mock_notification])):
            response = await client.get("/api/v1/notifications/unread", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    async def test_get_unread_no_auth(self, unauth_client):
        response = await unauth_client.get("/api/v1/notifications/unread")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestNotificationsMarkAsReadIntegration:
    async def test_mark_as_read_happy_path(self, client, auth_headers):
        from unittest.mock import AsyncMock, patch
        nid = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

        with patch.object(notification_service, "mark_as_read", new=AsyncMock(return_value=None)):
            response = await client.patch(f"/api/v1/notifications/{nid}/read", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Notification marked as read"

    async def test_mark_as_read_invalid_uuid(self, client, auth_headers):
        response = await client.patch("/api/v1/notifications/bad-uuid/read", headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestNotificationsMarkAllAsReadIntegration:
    async def test_mark_all_as_read_happy_path(self, client, auth_headers):
        from unittest.mock import AsyncMock, patch

        with patch.object(notification_service, "mark_all_as_read", new=AsyncMock(return_value=None)):
            response = await client.patch("/api/v1/notifications/read-all", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "All notifications marked as read"


class TestNotificationsCountUnreadIntegration:
    async def test_count_unread_happy_path(self, client, auth_headers):
        from unittest.mock import AsyncMock, patch

        with patch.object(notification_service, "count_unread", new=AsyncMock(return_value=3)):
            response = await client.get("/api/v1/notifications/unread/count", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"count": 3}
