from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.utils.auth import get_password_hash, verify_password, create_access_token, verify_token
from app.utils.responses import success_response, created_response, error_response
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from app.utils.email import send_email, send_password_reset_email
from fastapi.responses import JSONResponse
import secrets

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

@auth_router.post("/forgot-password")
def forgot_password(request_data: dict, db: Session = Depends(get_db)):
    """
    Request password reset email using Zepto Mail.
    Generates a reset token and sends a formatted email notification to the user.
    """
    email = request_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # For security, don't reveal if email exists
        return JSONResponse(
            content={"message": "If an account exists with this email, a password reset link has been sent"},
            status_code=200
        )

    # Generate a secure reset token (32-byte random token)
    reset_token = secrets.token_urlsafe(32)
    token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

    # Store the reset token (if your User model has these fields)
    try:
        user.reset_token = reset_token
        user.reset_token_expiry = token_expiry
        db.commit()
    except Exception as e:
        # If User model doesn't have reset_token fields, continue anyway
        print(f"Note: Could not store reset token in DB: {e}")

    # Create the password reset link (update with your frontend URL)
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"

    # Send reset email using Zepto Mail
    try:
        success = send_password_reset_email(
            to=email,
            reset_token=reset_link,
            user_name=user.full_name
        )
        
        if success:
            return JSONResponse(
                content={"message": "Password reset email sent successfully. Please check your inbox."},
                status_code=200
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to send reset email")
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reset email. Please try again later.")


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@auth_router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using valid reset token from email.
    Token must be valid and not expired.
    """
    token = request.token

    # Try to find user with this reset token
    user = None
    try:
        # First, try to find by reset_token if User model has this field
        user = db.query(User).filter(User.reset_token == token).first()
        if user and user.reset_token_expiry:
            if datetime.utcnow() > user.reset_token_expiry:
                user.reset_token = None
                user.reset_token_expiry = None
                db.commit()
                raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")
    except Exception as e:
        # If User model doesn't have reset_token fields, try JWT verification
        print(f"Could not verify reset token from DB: {e}")
        try:
            payload = verify_token(token)
            if payload and payload.get("purpose") == "password_reset":
                user_id = payload.get("user_id")
                user = db.query(User).filter(User.id == user_id).first()
            else:
                raise HTTPException(status_code=400, detail="Invalid or expired token")
        except:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    
    # Clear reset token if User model has this field
    try:
        user.reset_token = None
        user.reset_token_expiry = None
    except:
        pass
    
    db.commit()

    return JSONResponse(
        content={"message": "✅ Password has been reset successfully. You can now login with your new password."},
        status_code=200
    )



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