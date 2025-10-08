from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class ReadingStatus(str, enum.Enum):
    WANT_TO_READ = "want_to_read"
    CURRENTLY_READING = "currently_reading"
    READ = "read"
    WISHLIST = "wishlist"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    entra_id = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)  # Optional if using only Entra SSO
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    books = relationship("Book", back_populates="owner", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Book identifiers
    isbn = Column(String, nullable=True, index=True)
    google_books_id = Column(String, nullable=True)
    
    # Book metadata
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    authors = Column(String, nullable=True)  # Stored as comma-separated string
    description = Column(Text, nullable=True)
    publisher = Column(String, nullable=True)
    published_date = Column(String, nullable=True)
    page_count = Column(Integer, nullable=True)
    categories = Column(String, nullable=True)  # Stored as comma-separated string
    thumbnail = Column(String, nullable=True)
    series_name = Column(String, nullable=True)  # Extracted series name
    series_position = Column(String, nullable=True)  # Book number in series
    
    # User-specific data
    reading_status = Column(Enum(ReadingStatus), default=ReadingStatus.WANT_TO_READ)
    notes = Column(Text, nullable=True)
    is_wishlist = Column(Boolean, default=False)
    
    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    owner = relationship("User", back_populates="books")

