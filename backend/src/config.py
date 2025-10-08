from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://bookstor:bookstor_password@db:5432/bookstor"
    
    # API Keys
    google_books_api_key: Optional[str] = None
    
    # JWT Settings
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days
    
    # Entra SSO (Optional)
    entra_client_id: Optional[str] = None
    entra_tenant_id: Optional[str] = None
    entra_client_secret: Optional[str] = None
    
    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

