from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import auth, books, admin, user_portal
from .database import engine, Base
from .config import settings
import time
import logging

logger = logging.getLogger(__name__)

# Create database tables with retry logic for Docker Swarm
def init_db_with_retry(max_retries=5, delay=5):
    """Initialize database with retry logic for container startup"""
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise

init_db_with_retry()

app = FastAPI(
    title="Bookstor API",
    description="Personal library management system with barcode scanning",
    version="v0.0.5"
)

# Configure CORS for mobile app
# Get allowed origins from settings
cors_origins = settings.get_cors_origins()

# Security: Don't allow credentials with wildcard origins
# If using wildcard (*), credentials must be disabled
allow_credentials = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files for admin UI
# Use relative path that works both in Docker and local development
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(admin.router)
app.include_router(user_portal.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Bookstor API",
        "version": "v0.0.5",
        "docs": "/docs",
        "app": "/app/login",
        "admin": "/admin/login"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

