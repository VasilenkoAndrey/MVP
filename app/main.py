from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.database import engine
import logging

settings = get_settings()

# Logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return {"detail": "Rate limit exceeded. Please try again later."}


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Static files
import os
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Routers
from app.api.v1 import auth, trophies, upload, calibration, measurements, review, audit

app.include_router(auth.router, prefix="/api/v1")
app.include_router(trophies.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(calibration.router, prefix="/api/v1")
app.include_router(measurements.router, prefix="/api/v1")
app.include_router(review.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")


# Serve frontend
@app.get("/")
async def serve_frontend():
    return FileResponse("app/templates/index.html")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


# DB init on startup
@app.on_event("startup")
async def startup():
    from app.database import init_db

    await init_db()

    try:
        from app.services.init_db import initialize_database
        await initialize_database()
    except Exception as exc:
        logger.warning(f"Database seeding skipped (data may already exist): {exc}")

    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started on {settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    logger.info("Database connection closed")
