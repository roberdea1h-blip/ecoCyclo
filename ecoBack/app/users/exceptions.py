from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)



class UserNotFoundException(NotFoundException):
    error_code = "user_not_found"

    def __init__(self, user_id: object = None) -> None:
        msg = f"Usuario con ID {user_id} no encontrado." if user_id else "Usuario no encontrado."
        super().__init__(message=msg)


class EmailAlreadyExistsException(ConflictException):
    error_code = "email_already_exists"

    def __init__(self) -> None:
        super().__init__(message="El email ya está registrado.")


class InvalidCredentialsException(UnauthorizedException):
    error_code = "invalid_credentials"

    def __init__(self) -> None:
        super().__init__(message="Email o contraseña incorrectos.")


class InvalidRoleException(ValidationException):
    error_code = "invalid_role"

    def __init__(self, role: str | None = None) -> None:
        msg = f"Rol inválido: {role}." if role else "Rol inválido."
        super().__init__(message=msg)


class UserNotActiveException(ForbiddenException):
    error_code = "user_not_active"

    def __init__(self) -> None:
        super().__init__(message="El usuario no está activo.")


class VerificationTokenExpiredException(ValidationException):
    error_code = "verification_token_expired"

    def __init__(self) -> None:
        super().__init__(message="El token de verificación ha expirado.", details=None)


class CannotDeleteSelfException(ForbiddenException):
    error_code = "cannot_delete_self"

    def __init__(self) -> None:
        super().__init__(message="No puedes eliminar tu propio usuario.")


class UsernameAlreadyExistsException(ConflictException):
    error_code = "username_already_exists"

    def __init__(self) -> None:
        super().__init__(message="El nombre de usuario ya está registrado.")
