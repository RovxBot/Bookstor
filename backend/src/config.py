from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import secrets


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://bookstor:bookstor_password@db:5432/bookstor"

    # API Keys
    google_books_api_key: Optional[str] = None

    # JWT Settings - SECRET_KEY is REQUIRED via environment variable
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # Entra SSO (Optional)
    entra_client_id: Optional[str] = None
    entra_tenant_id: Optional[str] = None
    entra_client_secret: Optional[str] = None

    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret key is secure and not a default value"""
        if not v:
            raise ValueError("SECRET_KEY environment variable is required")

        # Check for common insecure values
        insecure_values = [
            "your-secret-key-here-change-in-production",
            "secret",
            "secret-key",
            "change-me",
            "changeme",
            "default",
            "test",
            "dev",
            "development",
        ]

        if v.lower() in insecure_values:
            raise ValueError(
                f"SECRET_KEY cannot be a default/insecure value. "
                f"Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        # Require minimum length
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY must be at least 32 characters long. "
                f"Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

