from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    email = request.email

    # Example validation (replace with your DB check)
    if email not in ["test@gmail.com", "demo@travelnudge.com"]:
        raise HTTPException(status_code=400, detail="User not found")

    # Simulate sending reset email
    print(f"✅ Password reset email sent to: {email}")
    return {"message": "Password reset email sent successfully"}
