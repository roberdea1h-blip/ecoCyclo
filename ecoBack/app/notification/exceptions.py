from app.core.exceptions import (
    BusinessRuleException,
    NotFoundException,
    ValidationException,
)


class NotificationNotFoundException(NotFoundException):
    error_code = "notification_not_found"

    def __init__(self) -> None:
        super().__init__(message="Notificación no encontrada.")


class NotificationTargetUserNotFoundException(NotFoundException):
    error_code = "notification_target_user_not_found"

    def __init__(self) -> None:
        super().__init__(message="Usuario destino de la notificación no encontrado.")


class InvalidNotificationTypeException(ValidationException):
    error_code = "invalid_notification_type"

    def __init__(self, notif_type: str | None = None) -> None:
        msg = f"Tipo de notificación inválido: {notif_type}." if notif_type else "Tipo de notificación inválido."
        super().__init__(message=msg)


class NotificationDeliveryFailedException(BusinessRuleException):
    error_code = "notification_delivery_failed"

    def __init__(self) -> None:
        super().__init__(message="Error al entregar la notificación.")
