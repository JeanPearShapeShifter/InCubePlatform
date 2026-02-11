class AppError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"


class ValidationError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"
    message = "Invalid request"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    message = "Insufficient permissions"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
    message = "Resource already exists"
