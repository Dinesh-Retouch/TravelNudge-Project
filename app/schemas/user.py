from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: str = Field(..., min_length=1, max_length=200)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)  # Limit to bcrypt max
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 72:
            raise ValueError('Password must be less than 72 characters long')
        return v

class UserLogin(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    remember_me: Optional[bool] = False
    
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    message: str
    user: Optional[UserResponse] = None

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Chat-related schemas
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str

class Conversation(BaseModel):
    id: str
    messages: List[dict]