from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import timedelta
from pathlib import Path
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from .. import models, schemas, auth
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/admin", tags=["admin"])

# Get templates directory relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Cookie-based session management for admin UI
serializer = URLSafeTimedSerializer(settings.secret_key)
ADMIN_SESSION_COOKIE = "admin_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def create_session_token(user_id: int) -> str:
    """Create a signed session token"""
    return serializer.dumps({"user_id": user_id}, salt="admin-session")


def verify_session_token(token: str) -> Optional[int]:
    """Verify and decode session token"""
    try:
        data = serializer.loads(token, salt="admin-session", max_age=SESSION_MAX_AGE)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None


async def get_current_admin_user(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    """Get current admin user from session cookie"""
    session_token = request.cookies.get(ADMIN_SESSION_COOKIE)
    
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_id = verify_session_token(session_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user


# ============================================================================
# HTML Pages
# ============================================================================

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login")
async def admin_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process admin login"""
    user = auth.authenticate_user(db, email, password)
    
    if not user or not user.is_admin:
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": {},
                "error": "Invalid credentials or insufficient permissions"
            },
            status_code=401
        )
    
    # Create session token
    session_token = create_session_token(user.id)
    
    # Redirect to dashboard with session cookie
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE,
        value=session_token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax"
    )
    
    return response


@router.get("/logout")
async def admin_logout():
    """Logout admin user"""
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(ADMIN_SESSION_COOKIE)
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Admin dashboard"""
    # Get statistics
    user_count = db.query(models.User).count()
    book_count = db.query(models.Book).count()
    admin_count = db.query(models.User).filter(models.User.is_admin == True).count()
    
    # Get registration setting
    reg_setting = db.query(models.AppSettings).filter(
        models.AppSettings.key == "registration_enabled"
    ).first()
    registration_enabled = reg_setting.value == "true" if reg_setting else False
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": {
                "user_count": user_count,
                "book_count": book_count,
                "admin_count": admin_count,
                "registration_enabled": registration_enabled
            }
        }
    )


@router.get("/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """User management page"""
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    
    # Get book counts for each user
    user_data = []
    for user in users:
        book_count = db.query(models.Book).filter(models.Book.user_id == user.id).count()
        user_data.append({
            "user": user,
            "book_count": book_count
        })
    
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "current_user": current_user,
            "user_data": user_data
        }
    )


@router.get("/settings", response_class=HTMLResponse)
async def admin_settings_page(
    request: Request,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Settings management page"""
    # Get all settings
    settings_list = db.query(models.AppSettings).all()
    settings_dict = {s.key: s.value for s in settings_list}
    
    return templates.TemplateResponse(
        "admin/settings.html",
        {
            "request": request,
            "current_user": current_user,
            "settings": settings_dict
        }
    )


# ============================================================================
# API Endpoints (for AJAX calls from admin UI)
# ============================================================================

@router.post("/api/users")
async def create_user(
    email: str = Form(...),
    password: str = Form(...),
    is_admin: bool = Form(False),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    # Check if user exists
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password
    from ..utils.password_validator import validate_password
    is_valid, error_message = validate_password(password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Create user
    hashed_password = auth.get_password_hash(password)
    new_user = models.User(
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"success": True, "user_id": new_user.id}


@router.patch("/api/users/{user_id}/admin")
async def toggle_admin_status(
    user_id: int,
    is_admin: bool = Form(...),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle admin status for a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent removing admin from self
    if user.id == current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove admin status from yourself"
        )
    
    user.is_admin = is_admin
    db.commit()
    
    return {"success": True}


@router.delete("/api/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    db.delete(user)
    db.commit()
    
    return {"success": True}


@router.post("/api/settings/registration")
async def toggle_registration(
    enabled: bool = Form(...),
    current_user: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle user registration"""
    setting = db.query(models.AppSettings).filter(
        models.AppSettings.key == "registration_enabled"
    ).first()
    
    if setting:
        setting.value = "true" if enabled else "false"
    else:
        setting = models.AppSettings(
            key="registration_enabled",
            value="true" if enabled else "false"
        )
        db.add(setting)
    
    db.commit()
    
    return {"success": True, "enabled": enabled}

