from datetime import datetime, timezone
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


# Standard error response format
class APIError:
    """
    Class to create error responses in a standard way.
    All errors use the same structure: success, error details, and timestamp.
    """

    def __init__(self, code: str, message: str, details: dict | None = None):
        # Store the error code, message, and extra details
        self.code = code
        self.message = message
        self.details = details or {}
        # Add current time to see when error happened
        self.timestamp = "{}Z".format(datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        """Convert error to a dictionary for JSON response"""
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details if self.details else None,
            },
            "timestamp": self.timestamp,
        }


# Base class for all app errors
class AppException(Exception):
    """
    Main error class. Other error types get their code and status code here.
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: dict | None = None,
        status_code: int = 500,
    ):
        # code: error type (like NOT_FOUND or DUPLICATE)
        # message: what the user should read
        # details: extra info about the error
        # status_code: HTTP code (404, 409, 500, etc)
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


# Error: cannot find thing user asks for
class NotFoundError(AppException):
    """Raised when a resource does not exist (404)"""

    def __init__(
        self, message: str = "Resource not found", details: dict | None = None
    ):
        super().__init__("NOT_FOUND", message, details, status_code=404)


# Error: item already exists
class DuplicateEntityError(AppException):
    """Raised when user tries to create item that already exists (409)"""

    def __init__(
        self, message: str = "Item already exists", details: dict | None = None
    ):
        super().__init__("DUPLICATE_ENTITY", message, details, status_code=409)


# Error: problem with database
class DatabaseError(AppException):
    """Raised when database has a problem (500)"""

    def __init__(self, message: str = "Database error", details: dict | None = None):
        super().__init__("DATABASE_ERROR", message, details, status_code=500)


# Error: data is wrong format
class ValidationError(AppException):
    """Raised when user sends bad data format (422)"""

    def __init__(self, message: str = "Validation error", details: dict | None = None):
        super().__init__("VALIDATION_ERROR", message, details, status_code=422)


# Handle HTTP errors (like wrong path)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Change HTTP error to our format"""
    error = APIError(
        code=f"HTTP_{exc.status_code}",
        message=exc.detail,
        details={"path": str(request.url.path), "method": request.method},
    )
    return JSONResponse(error.to_dict(), status_code=exc.status_code)


# Handle app errors (our custom errors)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Change app error to our format and send it"""
    error = APIError(
        code=exc.code,
        message=exc.message,
        details={
            **exc.details,
            "path": str(request.url.path),
            "method": request.method,
        },
    )
    return JSONResponse(error.to_dict(), status_code=exc.status_code)


# Handle when user sends wrong data format
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Make validation errors easy to read"""
    errors = []
    # Loop through each error and make it simple
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(x) for x in error["loc"][1:]),
                "type": error["type"],
                "message": error["msg"],
            }
        )

    # Create error response
    error = APIError(
        code="VALIDATION_ERROR",
        message="Data format is wrong",
        details={
            "errors": errors,
            "path": str(request.url.path),
            "method": request.method,
        },
    )
    return JSONResponse(error.to_dict(), status_code=HTTP_422_UNPROCESSABLE_ENTITY)
