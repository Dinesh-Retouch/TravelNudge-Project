from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.utils.email import send_password_reset_email
import secrets
from datetime import datetime, timedelta

router = APIRouter()

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Handle forgot password request.
    Sends a password reset email with a token to the user's email address.
    Uses Zepto Mail to send the notification.
    """
    email = request.email

    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # For security, we don't reveal if the email exists
        return {"message": "If an account exists with this email, a password reset link has been sent"}

    # Generate a unique reset token
    reset_token = secrets.token_urlsafe(32)
    token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

    # Store the reset token in the database (you'll need to add these fields to User model)
    user.reset_token = reset_token
    user.reset_token_expiry = token_expiry
    db.commit()

    # Create the password reset link (update with your frontend URL)
    reset_link = f"https://yourdomain.com/reset-password?token={reset_token}"
    
    try:
        # Send password reset email using Zepto Mail
        success = send_password_reset_email(
            to=user.email,
            reset_token=reset_link,
            user_name=user.full_name
        )
        
        if success:
            print(f"✅ Password reset email sent to: {email}")
            return {
                "message": "Password reset email sent successfully. Please check your inbox.",
                "email": email
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send password reset email. Please try again later."
            )
    except Exception as e:
        print(f"❌ Error sending password reset email: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while sending the password reset email"
        )


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using the token received via email.
    Token must be valid and not expired.
    """
    from app.utils.auth import get_password_hash
    
    token = request.token
    new_password = request.new_password

    # Find user with this reset token
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Check if token is expired
    if user.reset_token_expiry and datetime.utcnow() > user.reset_token_expiry:
        user.reset_token = None
        user.reset_token_expiry = None
        db.commit()
        raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")

    # Update password
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return {
        "message": "✅ Password reset successfully! You can now login with your new password.",
        "status": "success"
    }
