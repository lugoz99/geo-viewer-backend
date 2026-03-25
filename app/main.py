from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import user

app = FastAPI(title="Geo Viewer Platform API", version="1.0.0")


# Root endpoint (evita errores al abrir "/")
@app.get("/")
async def root():
    return {"message": "Hello 👋 API is running"}


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Routers
app.include_router(user.router, prefix="/api/v1")


# Global error handler
@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)},
    )
