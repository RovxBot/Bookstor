from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import auth, books, admin
from .database import engine, Base
from .config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bookstor API",
    description="Personal library management system with barcode scanning",
    version="beta-v0.0.2"
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
app.mount("/static", StaticFiles(directory="backend/src/static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(admin.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Bookstor API",
        "version": "beta-v0.0.2",
        "docs": "/docs",
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

