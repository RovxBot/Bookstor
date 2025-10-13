from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import secrets

from .. import models
from ..database import get_db
from ..auth import get_password_hash

# Get the templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

# Session management
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[models.User]:
    """Get the currently logged-in user from session cookie"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    
    try:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        return user
    except:
        return None


def require_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    """Require a logged-in user, redirect to login if not authenticated"""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/app/login"})
    return user


# ============================================================================
# Authentication Routes
# ============================================================================

@router.get("/app/login", response_class=HTMLResponse)
async def user_login_page(request: Request, db: Session = Depends(get_db)):
    """User login page"""
    # Check if already logged in
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/app/library", status_code=303)
    
    return templates.TemplateResponse("user/login.html", {"request": request})


@router.post("/app/login")
async def user_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process user login"""
    from ..auth import verify_password

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "user/login.html",
            {"request": request, "error": "Invalid email or password"}
        )
    
    # Create session
    session_token = secrets.token_urlsafe(32)
    
    response = RedirectResponse(url="/app/library", status_code=303)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=30 * 24 * 60 * 60,  # 30 days
        samesite="lax"
    )
    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True,
        max_age=30 * 24 * 60 * 60,
        samesite="lax"
    )
    
    return response


@router.get("/app/logout")
async def user_logout():
    """Logout user"""
    response = RedirectResponse(url="/app/login", status_code=303)
    response.delete_cookie("session_token")
    response.delete_cookie("user_id")
    return response


# ============================================================================
# Main Application Routes
# ============================================================================

@router.get("/app", response_class=HTMLResponse)
@router.get("/app/", response_class=HTMLResponse)
async def app_root(request: Request, db: Session = Depends(get_db)):
    """Redirect to library"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/app/login", status_code=303)
    return RedirectResponse(url="/app/library", status_code=303)


@router.get("/app/library", response_class=HTMLResponse)
async def library_page(request: Request, db: Session = Depends(get_db)):
    """Library page - shows all owned books"""
    user = require_user(request, db)

    # Get books for this user (not wishlist)
    books = db.query(models.Book).filter(
        models.Book.user_id == user.id,
        models.Book.is_wishlist == False
    ).order_by(models.Book.added_at.desc()).all()
    
    return templates.TemplateResponse("user/library.html", {
        "request": request,
        "user": user,
        "books": books
    })


@router.get("/app/wishlist", response_class=HTMLResponse)
async def wishlist_page(request: Request, db: Session = Depends(get_db)):
    """Wishlist page - shows all wishlist books"""
    user = require_user(request, db)

    # Get wishlist books for this user
    books = db.query(models.Book).filter(
        models.Book.user_id == user.id,
        models.Book.is_wishlist == True
    ).order_by(models.Book.added_at.desc()).all()
    
    return templates.TemplateResponse("user/wishlist.html", {
        "request": request,
        "user": user,
        "books": books
    })


@router.get("/app/collections", response_class=HTMLResponse)
async def collections_page(request: Request, db: Session = Depends(get_db)):
    """Collections page - shows book series"""
    user = require_user(request, db)

    # Get all books with series information
    books_with_series = db.query(models.Book).filter(
        models.Book.user_id == user.id,
        models.Book.series_name.isnot(None)
    ).order_by(models.Book.series_name, models.Book.series_position).all()

    # Group by series
    collections = {}
    for book in books_with_series:
        if book.series_name not in collections:
            collections[book.series_name] = []
        collections[book.series_name].append(book)

    return templates.TemplateResponse("user/collections.html", {
        "request": request,
        "user": user,
        "collections": collections
    })


@router.get("/app/collection/{series_name}", response_class=HTMLResponse)
async def collection_detail_page(request: Request, series_name: str, db: Session = Depends(get_db)):
    """Collection detail page - shows books in a series and missing books"""
    user = require_user(request, db)

    # Get books in this series
    books = db.query(models.Book).filter(
        models.Book.user_id == user.id,
        models.Book.series_name == series_name
    ).order_by(models.Book.series_position, models.Book.title).all()

    if not books:
        # Series not found, redirect to collections
        return RedirectResponse(url="/app/collections", status_code=303)

    # Get author from first book
    author = books[0].authors.split(',')[0].strip() if books and books[0].authors else None

    return templates.TemplateResponse("user/collection_detail.html", {
        "request": request,
        "user": user,
        "series_name": series_name,
        "author": author,
        "books": books
    })


@router.get("/app/search", response_class=HTMLResponse)
async def search_page(request: Request, db: Session = Depends(get_db)):
    """Search page - search and add books"""
    user = require_user(request, db)
    
    return templates.TemplateResponse("user/search.html", {
        "request": request,
        "user": user
    })


@router.get("/app/book/{book_id}", response_class=HTMLResponse)
async def book_detail_page(request: Request, book_id: int, db: Session = Depends(get_db)):
    """Book detail page"""
    user = require_user(request, db)
    
    # Get the book
    book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return templates.TemplateResponse("user/book_detail.html", {
        "request": request,
        "user": user,
        "book": book
    })


@router.get("/app/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    """User settings page"""
    user = require_user(request, db)
    
    return templates.TemplateResponse("user/settings.html", {
        "request": request,
        "user": user
    })

