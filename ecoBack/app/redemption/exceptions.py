from app.core.exceptions import (
    BusinessRuleException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)


class RedemptionNotFoundException(NotFoundException):
    error_code = "redemption_not_found"

    def __init__(self) -> None:
        super().__init__(message="Canje no encontrado.")


class InsufficientPointsForRedemptionException(BusinessRuleException):
    error_code = "insufficient_points_for_redemption"

    def __init__(self) -> None:
        super().__init__(message="Puntos insuficientes para realizar el canje.")


class RewardOutOfStockException(BusinessRuleException):
    error_code = "reward_out_of_stock"

    def __init__(self) -> None:
        super().__init__(message="La recompensa está agotada.")


class RedemptionAlreadyProcessedException(ConflictException):
    error_code = "redemption_already_processed"

    def __init__(self) -> None:
        super().__init__(message="El canje ya fue procesado.")


class UserNotEligibleForRedemptionException(ForbiddenException):
    error_code = "user_not_eligible_for_redemption"

    def __init__(self) -> None:
        super().__init__(message="El usuario no es elegible para realizar el canje.")
