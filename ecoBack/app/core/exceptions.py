class EcoCycleException(Exception):
    status_code: int = 500
    error_code: str = "internal_error"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None, details: object = None) -> None:
        self.details = details
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundException(EcoCycleException):
    status_code = 404
    error_code = "not_found"


class ConflictException(EcoCycleException):
    status_code = 409
    error_code = "conflict"


class ValidationException(EcoCycleException):
    status_code = 422
    error_code = "validation_error"


class ForbiddenException(EcoCycleException):
    status_code = 403
    error_code = "forbidden"


class UnauthorizedException(EcoCycleException):
    status_code = 401
    error_code = "unauthorized"


class BusinessRuleException(EcoCycleException):
    status_code = 409
    error_code = "business_rule"
