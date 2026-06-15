import logging

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", 404)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, "VALIDATION_ERROR", 422)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, "UNAUTHORIZED", 401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, "FORBIDDEN", 403)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message, "CONFLICT", 409)


def _error_response(message: str, error_code: str, status_code: int):
    return jsonify({"success": False, "message": message, "error_code": error_code}), status_code


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        logger.warning(error.message, extra={"error_code": error.error_code})
        return _error_response(error.message, error.error_code, error.status_code)

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        logger.error("Database error", exc_info=True)
        return _error_response("A database error occurred", "DATABASE_ERROR", 500)

    @app.errorhandler(404)
    def handle_404(error):
        return _error_response("Resource not found", "NOT_FOUND", 404)

    @app.errorhandler(405)
    def handle_405(error):
        return _error_response("Method not allowed", "METHOD_NOT_ALLOWED", 405)

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        logger.error("Unhandled exception", exc_info=True)
        return _error_response("Something went wrong", "INTERNAL_SERVER_ERROR", 500)
