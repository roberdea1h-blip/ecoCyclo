from app.core.exceptions import (
    BusinessRuleException,
    ConflictException,
    NotFoundException,
    ValidationException,
)


class WasteTypeNotFoundException(NotFoundException):
    error_code = "waste_type_not_found"

    def __init__(self) -> None:
        super().__init__(message="Tipo de residuo no encontrado.")


class WasteTypeNameAlreadyExistsException(ConflictException):
    error_code = "waste_type_name_already_exists"

    def __init__(self) -> None:
        super().__init__(message="El nombre del tipo de residuo ya existe.")


class WasteTypeInUseException(BusinessRuleException):
    error_code = "waste_type_in_use"

    def __init__(self) -> None:
        super().__init__(message="El tipo de residuo está en uso y no puede ser eliminado.")


class InvalidUnitOfMeasureException(ValidationException):
    error_code = "invalid_unit_of_measure"

    def __init__(self) -> None:
        super().__init__(message="Unidad de medida inválida.")
