from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import models, schemas, auth
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if registration is enabled
    registration_enabled = db.query(models.AppSettings).filter(
        models.AppSettings.key == "registration_enabled"
    ).first()

    # Count existing users
    user_count = db.query(models.User).count()

    # If this is not the first user and registration is disabled, reject
    if user_count > 0 and registration_enabled and registration_enabled.value == "false":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently disabled. Please contact the administrator."
        )

    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    # Password is now required and validated by schema
    hashed_password = auth.get_password_hash(user.password)

    # First user is automatically admin
    is_first_user = user_count == 0

    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_admin=is_first_user
    )
    db.add(db_user)
    db.commit()

    # If this was the first user, disable registration by default
    if is_first_user:
        settings = models.AppSettings(
            key="registration_enabled",
            value="false"
        )
        db.add(settings)
        db.commit()

    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.User)
async def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """Get current user information"""
    return current_user


@router.get("/registration-status")
def get_registration_status(db: Session = Depends(get_db)):
    """Check if registration is enabled"""
    # If no users exist, registration is always enabled
    user_count = db.query(models.User).count()
    if user_count == 0:
        return {"enabled": True, "message": "Registration is open for the first user"}

    # Check settings
    setting = db.query(models.AppSettings).filter(
        models.AppSettings.key == "registration_enabled"
    ).first()

    enabled = setting.value == "true" if setting else False

    return {
        "enabled": enabled,
        "message": "Registration is enabled" if enabled else "Registration is disabled"
    }


@router.post("/toggle-registration")
async def toggle_registration(
    enabled: bool,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle registration on/off (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change registration settings"
        )

    # Get or create setting
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

    return {
        "enabled": enabled,
        "message": f"Registration has been {'enabled' if enabled else 'disabled'}"
    }

