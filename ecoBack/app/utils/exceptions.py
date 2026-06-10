from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidToken(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


class ReportNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


class RewardNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")


class EmailAlreadyRegistered(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


class UsernameAlreadyRegistered(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )


class ForbiddenException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )


class RewardOutOfStockException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reward is out of stock",
        )


class InsufficientPointsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient points",
        )


class ReportNotPendingException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El reporte no está pendiente",
        )


class CannotClaimOwnReportException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes reclamar tu propio reporte",
        )


class ReportNotInProgressException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El reporte no está en progreso",
        )


class NotAssignedCleanerException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres el limpiador asignado a este reporte",
        )


class WasteTypeNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de residuo no encontrado",
        )


class CannotDeleteSelfException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario",
        )


class ReportNotPendingReviewException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El reporte no está esperando revisión",
        )


class NotOriginalReporterException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el creador del reporte puede realizar esta acción",
        )


class RedemptionNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canje no encontrado",
        )
