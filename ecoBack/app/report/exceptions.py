from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)


class ReportNotFoundException(NotFoundException):
    error_code = "report_not_found"

    def __init__(self, report_id: object = None) -> None:
        msg = f"Reporte con ID {report_id} no encontrado." if report_id else "Reporte no encontrado."
        super().__init__(message=msg)


class InvalidWasteTypeForReportException(ValidationException):
    error_code = "invalid_waste_type_for_report"

    def __init__(self) -> None:
        super().__init__(message="Tipo de residuo inválido para el reporte.")


class InvalidCoordinatesException(ValidationException):
    error_code = "invalid_coordinates"

    def __init__(self) -> None:
        super().__init__(message="Coordenadas geográficas inválidas.")


class ReportAlreadyProcessedException(ConflictException):
    error_code = "report_already_processed"

    def __init__(self) -> None:
        super().__init__(message="El reporte ya fue procesado.")


class UnauthorizedReportStatusChangeException(ForbiddenException):
    error_code = "unauthorized_report_status_change"

    def __init__(self) -> None:
        super().__init__(message="No autorizado para cambiar el estado del reporte.")


class ReportNotPendingException(ValidationException):
    error_code = "report_not_pending"

    def __init__(self) -> None:
        super().__init__(message="El reporte no está pendiente.")
        self.status_code = 400


class CannotClaimOwnReportException(ValidationException):
    error_code = "cannot_claim_own_report"

    def __init__(self) -> None:
        super().__init__(message="No puedes reclamar tu propio reporte.")
        self.status_code = 400


class ReportNotInProgressException(ValidationException):
    error_code = "report_not_in_progress"

    def __init__(self) -> None:
        super().__init__(message="El reporte no está en progreso.")
        self.status_code = 400


class NotAssignedCleanerException(ForbiddenException):
    error_code = "not_assigned_cleaner"

    def __init__(self) -> None:
        super().__init__(message="No eres el limpiador asignado a este reporte.")


class ReportNotPendingReviewException(ValidationException):
    error_code = "report_not_pending_review"

    def __init__(self) -> None:
        super().__init__(message="El reporte no está esperando revisión.")
        self.status_code = 400


class NotOriginalReporterException(ForbiddenException):
    error_code = "not_original_reporter"

    def __init__(self) -> None:
        super().__init__(message="Solo el creador del reporte puede realizar esta acción.")
