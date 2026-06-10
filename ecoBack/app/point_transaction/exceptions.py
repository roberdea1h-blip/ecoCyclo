from app.core.exceptions import (
    BusinessRuleException,
    ConflictException,
    NotFoundException,
    ValidationException,
)


class InsufficientPointsException(BusinessRuleException):
    error_code = "insufficient_points"

    def __init__(self) -> None:
        super().__init__(message="Puntos insuficientes.")


class DuplicateTransactionException(ConflictException):
    error_code = "duplicate_transaction"

    def __init__(self) -> None:
        super().__init__(message="Transacción duplicada.")


class InvalidTransactionTypeException(ValidationException):
    error_code = "invalid_transaction_type"

    def __init__(self) -> None:
        super().__init__(message="Tipo de transacción inválido.")


class PointsOverflowException(BusinessRuleException):
    error_code = "points_overflow"

    def __init__(self) -> None:
        super().__init__(message="El saldo de puntos excede el límite permitido.")


class PointTransactionNotFoundException(NotFoundException):
    error_code = "point_transaction_not_found"

    def __init__(self) -> None:
        super().__init__(message="Transacción de puntos no encontrada.")
