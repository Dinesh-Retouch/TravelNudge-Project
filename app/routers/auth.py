from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token  # Fixed: "schema" -> "schemas"
from app.utils.auth import get_password_hash, verify_password, create_access_token
from app.utils.responses import success_response, created_response, error_response  # Fixed: "response" -> "responses"
from datetime import datetime, timedelta
from pydantic import BaseModel

auth_router = APIRouter()  # Fixed: should be "auth_router" not "router"

@auth_router.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = None
    if user_data.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
    elif user_data.phone:
        existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists with this email or phone"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
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
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        message="Signup successful! Welcome to TravelNudge!"
    )

@auth_router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
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
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        message="Login successful! Welcome back to TravelNudge!"
    )

@auth_router.post("/logout")
def logout(token: str, db: Session = Depends(get_db)):
    # Invalidate session
    session = db.query(UserSession).filter(UserSession.token == token).first()
    if session:
        session.is_active = False
        db.commit()
    
    return success_response("Logout successful")

# Social login endpoints

class GoogleLoginRequest(BaseModel):
    email: str
    password: str
    
@auth_router.post("/google")
def google_login(request: GoogleLoginRequest):
    # Example: pretend to verify user
    if request.email == "test@gmail.com" and request.password == "12345":
        return {"message": "Google authentication successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@auth_router.post("/apple")
def apple_login():
    return created_response("Apple authentication successful")

@auth_router.post("/microsoft")
def microsoft_login():
    return created_response("Microsoft authentication successful")

@auth_router.post("/phone")
def phone_login():
    return created_response("Phone authentication successful")