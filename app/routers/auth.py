from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database.database import get_db
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.utils.auth import get_password_hash, verify_password, create_access_token, verify_token
from app.utils.responses import success_response, created_response
import os
import uuid
from pydantic import BaseModel
import google.generativeai as genai
from app.schemas.user import ChatRequest, ChatResponse
# Configure Gemini
try:
    genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    print("✅ Gemini AI configured successfully")
except Exception as e:
    print(f"❌ Gemini configuration failed: {e}")
    model = None

auth_router = APIRouter()

# ------------------------- SIGNUP -------------------------
@auth_router.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):

    # ✅ Password match check
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # ✅ Check if email exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # ✅ Check if phone exists
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already exists")

    # ✅ Hash password
    hashed_password = get_password_hash(user_data.password)

    # ✅ Correct field name based on your DB column
    # If your User model has "password", use that
    db_user = User(
        full_name=user_data.full_name,
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
    
    # ✅ Save user session
    session = UserSession(
        user_id=db_user.id,
        token=access_token,
        expires_at=datetime.utcnow() + access_token_expires
    )
    db.add(session)
    db.commit()

    # ✅ Build response
    user_response = UserResponse(
        id=db_user.id,
        full_name=db_user.full_name,
        email=db_user.email,
        phone=db_user.phone,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        created_at=db_user.created_at
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        message="Signup successful!",
        user=user_response
    )

# ------------------------- LOGIN -------------------------
@auth_router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    """
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Account is deactivated"
        )

    # Token expires (30 days if remember_me, else 12 hours)
    access_token_expires = timedelta(days=30 if login_data.remember_me else 0.5)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )

    # Save session
    session = UserSession(
        user_id=user.id,
        token=access_token,
        expires_at=datetime.utcnow() + access_token_expires
    )
    db.add(session)
    db.commit()

    # Response
    user_response = UserResponse(
        id=user.id,
        full_name=user.full_name,
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


# ------------------------- LOGOUT -------------------------
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

# ------------------------- GEMINI CHATBOT -------------------------
@auth_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Handles chat messages and returns AI-generated response using Gemini.
    """
    try:
        print(f"🎯 Received chat request: '{request.message}'")
        
        if not model:
            return ChatResponse(
                response="AI service is not configured properly. Please check your API key.",
                conversation_id=request.conversation_id or "error",
                timestamp=datetime.utcnow().isoformat()
            )

        if not request.message or not request.message.strip():
            return ChatResponse(
                response="Message cannot be empty.",
                conversation_id=request.conversation_id or "error", 
                timestamp=datetime.utcnow().isoformat()
            )

        # Generate AI response with travel context
        travel_prompt = f"""You are TravelNudge, a friendly AI travel assistant. Help users with travel planning, destinations, flights, hotels, and travel tips.

User: {request.message}
TravelNudge:"""
        
        response = model.generate_content(travel_prompt)
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        return ChatResponse(
            response=response.text,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        print(f"🔥 Chat endpoint error: {str(e)}")
        return ChatResponse(
            response=f"AI service error: {str(e)}",
            conversation_id=request.conversation_id or "error",
            timestamp=datetime.utcnow().isoformat()
        )
# ------------------------- GET CURRENT USER -------------------------
@auth_router.get("/me", response_model=UserResponse)
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """
    Get current user information
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    token = authorization.replace("Bearer ", "")
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


# ------------------------- SOCIAL LOGINS (Placeholders) -------------------------
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