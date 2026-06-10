from app.core.exceptions import (
    BusinessRuleException,
    NotFoundException,
    ValidationException,
)


class RewardNotFoundException(NotFoundException):
    error_code = "reward_not_found"

    def __init__(self) -> None:
        super().__init__(message="Recompensa no encontrada.")


class RewardInactiveException(BusinessRuleException):
    error_code = "reward_inactive"

    def __init__(self) -> None:
        super().__init__(message="La recompensa no está activa.")


class InvalidRewardPointsValueException(ValidationException):
    error_code = "invalid_reward_points_value"

    def __init__(self) -> None:
        super().__init__(message="Valor de puntos de recompensa inválido.")


class NegativeStockException(ValidationException):
    error_code = "negative_stock"

    def __init__(self) -> None:
        super().__init__(message="El stock no puede ser negativo.")
