import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-change-in-production"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["PROJECT_NAME"] = "EcoCycle-Test"
os.environ["API_V1_PREFIX"] = "/api/v1"

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient, ASGITransport

from app.core.security import create_access_token
from app.core.dependencies import get_current_user, get_current_admin_user, get_db
from app.main import app
from app.models.user import User
from app.models.report import Report
from app.models.role import Role
from app.models.reward import Reward
from app.models.notification import Notification
from app.models.redemption import Redemption, RedemptionStatus


def _make_db_result(scalar_return=None, scalars_list=None):
    """Build a mock that mimics an SQLAlchemy awaitable result."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_return
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = scalars_list if scalars_list is not None else []
    result.scalars.return_value = scalars_mock
    return result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db_result = _make_db_result()
    db.execute.return_value = db_result
    return db


@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def admin_role_id():
    return uuid.uuid4()


@pytest.fixture
def user_role_id():
    return uuid.uuid4()


@pytest.fixture
def mock_role(user_role_id):
    role = MagicMock(spec=Role)
    role.id = user_role_id
    role.name = "user"
    return role


@pytest.fixture
def mock_admin_role(admin_role_id):
    role = MagicMock(spec=Role)
    role.id = admin_role_id
    role.name = "admin"
    return role


@pytest.fixture
def mock_user(user_id, user_role_id, mock_role):
    user = MagicMock(spec=User)
    user.id = user_id
    user.email = "testuser@example.com"
    user.username = "testuser"
    user.full_name = "Test User"
    user.hashed_password = "$argon2id$v=19$m=65536,t=3,p=4$...hashed..."
    user.is_active = True
    user.is_verified = True
    user.role_id = user_role_id
    user.role = mock_role
    user.role_name = "user"
    user.avatar_url = None
    user.points = 100
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def mock_admin_user(admin_role_id, mock_admin_role):
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "admin@ecocycle.app"
    user.username = "admin"
    user.full_name = "System Admin"
    user.hashed_password = "$argon2id$v=19$m=65536,t=3,p=4$...hashed..."
    user.is_active = True
    user.is_verified = True
    user.role_id = admin_role_id
    user.role = mock_admin_role
    user.role_name = "admin"
    user.avatar_url = None
    user.points = 9999
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def mock_report():
    report = MagicMock(spec=Report)
    report.id = uuid.uuid4()
    report.user_id = uuid.uuid4()
    report.waste_type_id = uuid.uuid4()
    report.title = "Test Report"
    report.description = "A test report description"
    report.latitude = 40.7128
    report.longitude = -74.0060
    report.address = "123 Test St"
    report.status = "pending"
    report.estimated_quantity = None
    report.cleaner_id = None
    report.cleaner_name = None
    report.cleaned_at = None
    report.waste_type_name = "Plastic"
    report.user_name = "Test User"
    report.image_url = None
    report.validated_at = None
    report.validator_id = None
    report.validator_name = None
    report.created_at = datetime.now(timezone.utc)
    report.updated_at = datetime.now(timezone.utc)
    return report


@pytest.fixture
def mock_report_in_progress(mock_report, user_id):
    report = mock_report
    report.status = "in_progress"
    report.cleaner_id = user_id
    report.cleaner_name = "Test User"
    return report


@pytest.fixture
def mock_report_cleaned(mock_report_in_progress, user_id):
    report = mock_report_in_progress
    report.status = "cleaned"
    report.cleaned_at = datetime.now(timezone.utc)
    return report


@pytest.fixture
def mock_reward():
    reward = MagicMock(spec=Reward)
    reward.id = uuid.uuid4()
    reward.name = "Test Reward"
    reward.description = "A test reward"
    reward.points_cost = 50
    reward.stock = 10
    reward.image_url = None
    reward.is_active = True
    reward.created_at = datetime.now(timezone.utc)
    reward.updated_at = datetime.now(timezone.utc)
    return reward


@pytest.fixture
def mock_redemption():
    redemption = MagicMock(spec=Redemption)
    redemption.id = uuid.uuid4()
    redemption.user_id = uuid.uuid4()
    redemption.reward_id = uuid.uuid4()
    redemption.points_spent = 50
    redemption.status = RedemptionStatus.pending
    redemption.delivery_type = None
    redemption.delivery_info = None
    redemption.redeemed_at = datetime.now(timezone.utc)
    redemption.created_at = datetime.now(timezone.utc)
    return redemption


@pytest.fixture
def mock_notification():
    notification = MagicMock(spec=Notification)
    notification.id = uuid.uuid4()
    notification.user_id = uuid.uuid4()
    notification.title = "Test Notification"
    notification.message = "This is a test notification"
    notification.is_read = False
    notification.type = "info"
    notification.created_at = datetime.now(timezone.utc)
    return notification


@pytest.fixture
def access_token(mock_user):
    return create_access_token(data={"sub": str(mock_user.id)})


@pytest.fixture
def admin_access_token(mock_admin_user):
    return create_access_token(data={"sub": str(mock_admin_user.id)})


@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(admin_access_token):
    return {"Authorization": f"Bearer {admin_access_token}"}


@pytest.fixture
def override_get_db(mock_db):
    async def _override():
        yield mock_db
    return _override


@pytest.fixture
def override_get_current_user(mock_user):
    async def _override():
        return mock_user
    return _override


@pytest.fixture
def override_get_current_admin_user(mock_admin_user):
    async def _override():
        return mock_admin_user
    return _override


@pytest.fixture
def client(override_get_db, override_get_current_user):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def admin_client(override_get_db, override_get_current_admin_user):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_admin_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def unauth_client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()
