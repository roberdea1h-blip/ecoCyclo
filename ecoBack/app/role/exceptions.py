from app.core.exceptions import (
    BusinessRuleException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)


class RoleNotFoundException(NotFoundException):
    error_code = "role_not_found"

    def __init__(self) -> None:
        super().__init__(message="Rol no encontrado.")


class RoleNameAlreadyExistsException(ConflictException):
    error_code = "role_name_already_exists"

    def __init__(self) -> None:
        super().__init__(message="El nombre del rol ya existe.")


class RoleInUseException(BusinessRuleException):
    error_code = "role_in_use"

    def __init__(self) -> None:
        super().__init__(message="El rol está en uso y no puede ser eliminado.")


class SystemRoleNotModifiableException(ForbiddenException):
    error_code = "system_role_not_modifiable"

    def __init__(self) -> None:
        super().__init__(message="El rol de sistema no puede ser modificado.")
