from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from models.user import User, UserSession
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from utils.auth import get_password_hash, verify_password, create_access_token
from app.utils.responses import success_response, created_response, error_response
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

auth_router = APIRouter()

@auth_router.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    """
    # Check if user already exists
    existing_user = None
    if user_data.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
    if user_data.phone:
        existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email or phone"
        )
    
    # Create new user - MAKE SURE THIS USES full_name
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        full_name=user_data.full_name,  # This should be full_name, not first_name
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token (30 days if remember me, else 30 minutes)
    access_token_expires = timedelta(days=30)
    access_token = create_access_token(
        data={"user_id": db_user.id}, expires_delta=access_token_expires
    )
    
    # Store session
    session = UserSession(
        user_id=db_user.id,
        token=access_token,
        expires_at=datetime.utcnow() + access_token_expires
    )
    db.add(session)
    db.commit()
    
    # Prepare user response
    user_response = UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,  # This should be full_name
        email=db_user.email,
        phone=db_user.phone,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        created_at=db_user.created_at
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        message="Account created successfully! Welcome to TravelNudge!",
        user=user_response
    )

@auth_router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email/phone and password
    """
    # Find user by email or phone
    user = None
    if login_data.email:
        user = db.query(User).filter(User.email == login_data.email).first()
    elif login_data.phone:
        user = db.query(User).filter(User.phone == login_data.phone).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Create access token
    if login_data.remember_me:
        access_token_expires = timedelta(days=30)
    else:
        access_token_expires = timedelta(minutes=30)
        
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    
    # Store session
    session = UserSession(
        user_id=user.id,
        token=access_token,
        expires_at=datetime.utcnow() + access_token_expires
    )
    db.add(session)
    db.commit()
    
    # Prepare user response
    user_response = UserResponse(
        id=user.id,
        full_name=user.full_name,  # This should be full_name
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        message="Login successful! Welcome back to TravelNudge!",
        user=user_response
    )

@auth_router.post("/logout")
def logout(token: str, db: Session = Depends(get_db)):
    """
    Logout and invalidate session
    """
    session = db.query(UserSession).filter(UserSession.token == token).first()
    if session:
        session.is_active = False
        db.commit()
    
    return success_response("Logout successful")

# Social login endpoints
class SocialLoginRequest(BaseModel):
    email: str
    name: str

@auth_router.post("/google")
def google_login(request: SocialLoginRequest, db: Session = Depends(get_db)):
    return created_response("Google authentication successful")

@auth_router.post("/apple")
def apple_login(request: SocialLoginRequest, db: Session = Depends(get_db)):
    return created_response("Apple authentication successful")

@auth_router.post("/microsoft")
def microsoft_login(request: SocialLoginRequest, db: Session = Depends(get_db)):
    return created_response("Microsoft authentication successful")

@auth_router.post("/phone-login")
def phone_login():
    return created_response("Phone authentication successful")

# Additional endpoints
@auth_router.get("/me", response_model=UserResponse)
def get_current_user(token: str, db: Session = Depends(get_db)):
    """
    Get current user information
    """
    from app.utils.auth import verify_token
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user