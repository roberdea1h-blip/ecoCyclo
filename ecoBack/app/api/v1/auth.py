from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import clear_auth_cookies, set_auth_cookies
from app.db.session import get_db
from app.mappers.user_mapper import to_login_response, to_user_response
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "auth"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register(db, request)
    return to_user_response(user)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    access_token, refresh_token, user = await auth_service.login(db, request.email, request.password)
    set_auth_cookies(response, access_token, refresh_token)
    return to_login_response(True, user)


@router.post("/refresh", response_model=dict)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_refresh_token = request.cookies.get("refresh_token")
    if not raw_refresh_token:
        from app.refresh_token.exceptions import RefreshTokenNotFoundException
        raise RefreshTokenNotFoundException()

    access_token, new_refresh_token = await auth_service.refresh(db, raw_refresh_token)
    set_auth_cookies(response, access_token, new_refresh_token)
    return {"authenticated": True}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_refresh_token = request.cookies.get("refresh_token")
    await auth_service.logout(db, raw_refresh_token)
    clear_auth_cookies(response)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return to_user_response(current_user)
