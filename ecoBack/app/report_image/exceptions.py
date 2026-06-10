from app.core.exceptions import (
    BusinessRuleException,
    NotFoundException,
    ValidationException,
)


class ReportImageNotFoundException(NotFoundException):
    error_code = "report_image_not_found"

    def __init__(self) -> None:
        super().__init__(message="Imagen del reporte no encontrada.")


class ReportForImageNotFoundException(NotFoundException):
    error_code = "report_for_image_not_found"

    def __init__(self) -> None:
        super().__init__(message="Reporte asociado a la imagen no encontrado.")


class InvalidImageMimeTypeException(ValidationException):
    error_code = "invalid_image_mime_type"

    def __init__(self) -> None:
        super().__init__(message="Tipo de archivo de imagen no soportado.")


class ImageSizeExceededException(ValidationException):
    error_code = "image_size_exceeded"

    def __init__(self) -> None:
        super().__init__(message="El tamaño de la imagen excede el límite permitido.", details=None)
        self.status_code = 413


class ReportImageLimitExceededException(BusinessRuleException):
    error_code = "report_image_limit_exceeded"

    def __init__(self) -> None:
        super().__init__(message="Se ha excedido el límite de imágenes por reporte.")
