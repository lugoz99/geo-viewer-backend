import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from app.exceptions.request_exception import (
    AppException,
    APIError,
    http_exception_handler,
    app_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.routers import project, user

# Turn off database logs (too much information)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

# Create the main app
app = FastAPI(title="Geo Viewer Platform API", version="1.0.0", prefix="/api/v1")


# Simple endpoint - shows API is working
@app.get("/")
async def root():
    return {"message": "Hello 👋 API is running"}


# Check if API is alive
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Add all routes for users
app.include_router(user.router)
app.include_router(project.router)

# Register handlers for different error types
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)


# Catch all errors that we did not catch
@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    error = APIError(
        code="INTERNAL_SERVER_ERROR",
        message="Server has a problem",
        details={
            "error": str(exc),
            "path": str(request.url.path),
            "method": request.method,
        },
    )
    return JSONResponse(error.to_dict(), status_code=500)
