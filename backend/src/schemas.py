from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import ReadingStatus


# User Schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Book Schemas
class BookBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    authors: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    categories: Optional[str] = None
    thumbnail: Optional[str] = None
    isbn: Optional[str] = None
    series_name: Optional[str] = None
    series_position: Optional[str] = None
    reading_status: ReadingStatus = ReadingStatus.WANT_TO_READ
    notes: Optional[str] = None
    is_wishlist: bool = False


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    authors: Optional[str] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    categories: Optional[str] = None
    thumbnail: Optional[str] = None
    series_name: Optional[str] = None
    series_position: Optional[str] = None
    reading_status: Optional[ReadingStatus] = None
    notes: Optional[str] = None
    is_wishlist: Optional[bool] = None


class Book(BookBase):
    id: int
    user_id: int
    google_books_id: Optional[str] = None
    added_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Google Books API Response
class GoogleBookInfo(BaseModel):
    title: str
    subtitle: Optional[str] = None
    authors: Optional[List[str]] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    categories: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    google_books_id: Optional[str] = None
    isbn: Optional[str] = None
    series_name: Optional[str] = None
    series_position: Optional[str] = None


# ISBN Lookup Request
class ISBNLookup(BaseModel):
    isbn: str
    reading_status: ReadingStatus = ReadingStatus.WANT_TO_READ
    is_wishlist: bool = False


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None

