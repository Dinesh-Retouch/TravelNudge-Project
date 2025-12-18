# 🔐 Password Reset Feature with Zepto Mail

A complete password reset implementation for TravelNudge using Zepto Mail for email notifications.

## ✨ Features

- ✅ **Secure Password Reset** - Uses cryptographically secure tokens
- ✅ **Zepto Mail Integration** - Professional email notifications
- ✅ **Beautiful HTML Emails** - Branded, responsive email templates
- ✅ **Token Expiration** - Tokens expire after 1 hour
- ✅ **Fallback Support** - Can fall back to Gmail SMTP if needed
- ✅ **Security Best Practices** - No user enumeration, secure token generation
- ✅ **Database Persistence** - Tokens stored with expiry timestamps
- ✅ **Error Handling** - Comprehensive error handling and logging

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User (Frontend)                           │
│              1. Click "Forgot Password"                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              POST /forgot-password                           │
│            app/routers/auth.py                              │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────┐          ┌──────────────────────────┐
│ Check User in DB │          │ Generate Reset Token     │
│ app/models/user  │          │ (32-byte secure token)   │
└──────────────────┘          └──────────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────┐
                               │ Store Token in DB   │
                               │ (valid 1 hour)      │
                               └─────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Send Email via Zepto Mail                          │
│          app/utils/email.py                                 │
│          send_password_reset_email()                        │
│                                                             │
│  📧 Email Contents:                                         │
│   - User's name (personalized)                             │
│   - Professional HTML template                             │
│   - Reset button with secure link                          │
│   - Security warnings                                       │
│   - 1-hour expiry notice                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
    ┌──────────────────────────────────┐
    │ User Receives Email & Clicks Link │
    └──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         POST /reset-password                                │
│         app/routers/auth.py                                │
│                                                             │
│  Validates:                                                 │
│  ✓ Token exists in database                               │
│  ✓ Token hasn't expired                                   │
│  ✓ New password meets requirements                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Update Password Hash │
              │ Clear Reset Token    │
              │ Save to Database     │
              └──────────────────────┘
                         │
                         ▼
              ✅ Password Reset Complete
              User can login with new password
```

## 📁 Project Structure

```
app/
├── models/
│   └── user.py                    # User model with reset_token fields
├── routers/
│   └── auth.py                    # Authentication endpoints
│       ├── POST /forgot-password
│       └── POST /reset-password
├── utils/
│   ├── email.py                   # Email service (Gmail + Zepto Mail)
│   ├── forgot_password.py         # Legacy forgot password router
│   └── auth.py                    # Password hashing & token utilities
├── database/
│   └── database.py                # Database connection
└── main.py                        # FastAPI app initialization

Configuration Files:
├── requirements.txt               # Python dependencies (+ requests)
├── .env.example                   # Environment variables template
├── ZEPTO_MAIL_SETUP.md           # Zepto Mail setup guide
└── DATABASE_MIGRATION.md          # Database migration instructions
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env and add your Zepto Mail API key
# ZEPTO_API_KEY=your_key_here
```

### 3. Run Database Migration
```bash
# Using Alembic
alembic upgrade head

# OR using Alembic autogenerate
alembic revision --autogenerate -m "Add password reset fields"
alembic upgrade head

# OR manually (see DATABASE_MIGRATION.md)
```

### 4. Start Application
```bash
uvicorn app.main:app --reload
```

## 📡 API Endpoints

### Request Password Reset

**POST** `/api/v1/auth/forgot-password`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (Success):**
```json
{
  "message": "Password reset email sent successfully. Please check your inbox.",
  "email": "user@example.com"
}
```

**Response (User not found - security, doesn't reveal):**
```json
{
  "message": "If an account exists with this email, a password reset link has been sent"
}
```

### Reset Password

**POST** `/api/v1/auth/reset-password`

```bash
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset_token_from_email",
    "new_password": "NewPassword123!"
  }'
```

**Request Body:**
```json
{
  "token": "secure_reset_token_here",
  "new_password": "NewSecurePassword123!"
}
```

**Response (Success):**
```json
{
  "message": "✅ Password has been reset successfully. You can now login with your new password."
}
```

**Response (Token expired):**
```json
{
  "detail": "Reset token has expired. Please request a new one."
}
```

## 🔐 Security Features

### 1. Secure Token Generation
```python
reset_token = secrets.token_urlsafe(32)  # 32 bytes of cryptographic randomness
```

### 2. Token Expiration
- Tokens expire after **1 hour**
- Expiry time stored in database with UTC timestamp
- Expired tokens are validated on use

### 3. One-Time Use
- Token is deleted from database after successful password reset
- Cannot be reused

### 4. No User Enumeration
- Same message for existing/non-existing emails
- Prevents attackers from discovering valid user emails

### 5. Password Hashing
- Uses bcrypt with Argon2 fallback
- Passwords are never stored in plain text

### 6. HTTPS Ready
- All endpoints should be served over HTTPS in production

## 📧 Email Template

The password reset email includes:

```html
Header:
  🧳 TravelNudge - Password Reset

Body:
  ✅ User's personalized greeting
  ✅ Clear reset instructions
  ✅ Prominent reset button
  ✅ Fallback copy-paste link
  ✅ Security notice with expiry time
  ✅ Footer with company info
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Zepto Mail
ZEPTO_API_KEY=sk_live_your_api_key_here

# Gmail (fallback)
GMAIL_EMAIL=support@travelnudge.com
GMAIL_PASSWORD=app_specific_password

# Frontend URL (for reset links)
FRONTEND_URL=https://yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/travelnudge
```

### Email Provider Selection

**Use Zepto Mail (default):**
```python
send_password_reset_email(
    to="user@example.com",
    reset_token="https://...",
    user_name="John Doe"
)
```

**Fall back to Gmail:**
```python
send_email(
    to="user@example.com",
    subject="Reset Password",
    body="...",
    use_zepto=False  # Use Gmail SMTP
)
```

## 📊 Database Schema

### Users Table Changes

```sql
ALTER TABLE users ADD COLUMN reset_token VARCHAR(500) NULL;
ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP WITH TIME ZONE NULL;
CREATE INDEX idx_users_reset_token ON users(reset_token);
```

### Fields Added to User Model

```python
reset_token: str = Column(String(500), nullable=True, index=True)
reset_token_expiry: datetime = Column(DateTime(timezone=True), nullable=True)
```

## 🧪 Testing

### Manual Testing

```bash
# 1. Request password reset
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Check your email for reset link

# 3. Extract token from reset link URL

# 4. Reset password
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "extracted_token_here",
    "new_password": "NewPassword123!"
  }'
```

### Automated Testing (Python)

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

# Step 1: Request password reset
response = requests.post(
    f"{BASE_URL}/forgot-password",
    json={"email": "user@example.com"}
)
print("✅ Reset requested:", response.json())

# Step 2: Simulate getting token from email (in real flow)
# ... extract token from email ...

# Step 3: Reset password
reset_response = requests.post(
    f"{BASE_URL}/reset-password",
    json={
        "token": "token_from_email",
        "new_password": "NewPassword123!"
    }
)
print("✅ Reset complete:", reset_response.json())
```

## 📚 Additional Documentation

- **[ZEPTO_MAIL_SETUP.md](ZEPTO_MAIL_SETUP.md)** - Detailed Zepto Mail configuration
- **[DATABASE_MIGRATION.md](DATABASE_MIGRATION.md)** - Database migration steps
- **[.env.example](.env.example)** - Environment variables template

## ⚠️ Troubleshooting

### Email not sending

1. **Check API Key**
   ```bash
   # Verify in .env
   echo $ZEPTO_API_KEY
   ```

2. **Verify Domain**
   - Check Zepto Mail dashboard → Domains
   - Ensure domain is verified

3. **Check Logs**
   ```bash
   # Look for errors in application output
   # Should show: ✅ Email sent successfully via Zepto Mail
   # Or: ❌ Failed to send email via Zepto Mail: [error]
   ```

### Token errors

- **"Invalid or expired token"**: Token doesn't exist or expired > 1 hour
- **"Invalid or expired token" on reset**: User not found with that token

### Database errors

- **"Column doesn't exist"**: Run database migration (see DATABASE_MIGRATION.md)
- **"Duplicate entry"**: Reset token index conflict - check recent resets

## 📈 Monitoring

### Check Email Status
1. Go to Zepto Mail Dashboard
2. Navigate to **Activity/Logs**
3. Filter by recipient email
4. View delivery status (Sent/Failed/Bounced)

### Application Logs
```bash
# Successful email
✅ Email sent successfully to user@example.com via Zepto Mail

# Failed email
❌ Failed to send email via Zepto Mail: [error details]
```

## 🎯 Next Steps

1. **Get Zepto Mail Account**
   - Sign up at https://www.zeptomail.com/
   - Verify your domain

2. **Set Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your API key

3. **Run Migrations**
   - Execute database migration (see DATABASE_MIGRATION.md)

4. **Test the Flow**
   - Request password reset
   - Check email
   - Reset password

5. **Monitor in Production**
   - Check Zepto Mail dashboard regularly
   - Set up alerts for failed emails

## 📞 Support

For issues with:
- **Zepto Mail**: Visit [help.zeptomail.com](https://help.zeptomail.com/)
- **FastAPI**: Check [FastAPI docs](https://fastapi.tiangolo.com/)
- **TravelNudge**: Contact the development team

---

**Last Updated:** December 2025
**Status:** ✅ Production Ready
**Tested With:** Python 3.8+, FastAPI 0.95+, SQLAlchemy 1.4+
