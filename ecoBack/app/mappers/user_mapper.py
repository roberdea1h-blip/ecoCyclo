from app.models.user import User
from app.schemas.auth import LoginResponse
from app.schemas.user import UserResponse


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role_id=user.role_id,
        role_name=user.role.name if user.role else None,
        avatar_url=user.avatar_url,
        points=user.points,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def to_login_response(authenticated: bool, user: User) -> LoginResponse:
    return LoginResponse(
        authenticated=authenticated,
        user=to_user_response(user),
    )
