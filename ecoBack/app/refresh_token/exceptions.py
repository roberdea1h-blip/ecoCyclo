from app.core.exceptions import UnauthorizedException


class RefreshTokenNotFoundException(UnauthorizedException):
    error_code = "refresh_token_not_found"

    def __init__(self) -> None:
        super().__init__(message="Token de actualización no encontrado.")


class RefreshTokenExpiredException(UnauthorizedException):
    error_code = "refresh_token_expired"

    def __init__(self) -> None:
        super().__init__(message="El token de actualización ha expirado.")


class RefreshTokenRevokedException(UnauthorizedException):
    error_code = "refresh_token_revoked"

    def __init__(self) -> None:
        super().__init__(message="El token de actualización fue revocado.")


class InvalidJTIException(UnauthorizedException):
    error_code = "invalid_jti"

    def __init__(self) -> None:
        super().__init__(message="JTI inválido.")


class RefreshTokenUserMismatchException(UnauthorizedException):
    error_code = "refresh_token_user_mismatch"

    def __init__(self) -> None:
        super().__init__(message="El token de actualización no corresponde al usuario.")
