from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import clear_auth_cookies, set_auth_cookies
from app.db.session import get_db
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


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="Crea una nueva cuenta de usuario en el sistema. Valida que el email y el username no estén duplicados y asigna el rol por defecto."
)
async def register(
    request: RegisterRequest, 
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    user = await auth_service.register(db, request)
    
    return UserResponse.model_validate(user)


@router.post(
    "/login", 
    response_model=LoginResponse, 
    status_code=status.HTTP_200_OK,
    summary="Autenticar usuario",
    description="Verifica las credenciales del usuario, genera tokens JWT y los almacena en cookies seguras."
)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    access_token, refresh_token, user = await auth_service.login(
        db, email=request.email, password=request.password
    )
    
    set_auth_cookies(response, access_token, refresh_token)
    
    return LoginResponse.model_validate({
        "authenticated": True, 
        "user": user
    })


@router.post("/refresh", response_model=dict)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    raw_refresh_token = request.cookies.get("refresh_token")
    if not raw_refresh_token:
        from app.utils.exceptions import InvalidToken
        raise InvalidToken()

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
    return current_user
