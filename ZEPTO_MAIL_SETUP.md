# 🚀 Zepto Mail Setup Guide for TravelNudge

This guide will help you set up Zepto Mail for sending password reset notifications to users.

## 📋 Prerequisites

- Zepto Mail account (sign up at https://www.zeptomail.com/)
- Zepto Mail API key
- Python environment with the project dependencies installed

## 🔧 Installation

1. **Install the required package:**
   ```bash
   pip install -r requirements.txt
   ```

   The `requests` library is now included in requirements.txt for making API calls to Zepto Mail.

## ⚙️ Configuration

### Step 1: Get Your Zepto Mail API Key

1. Sign up for a free Zepto Mail account at https://www.zeptomail.com/
2. Navigate to your dashboard and go to **API & SMTP** section
3. Copy your **API Token/Key**
4. Verify your sending domain in Zepto Mail dashboard

### Step 2: Set Environment Variables

Create a `.env` file in the project root directory:

```bash
# Zepto Mail Configuration
ZEPTO_API_KEY=your_zepto_api_key_here

# Gmail Configuration (if you want to keep Gmail fallback)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password
```

### Step 3: Update Email Address (Optional)

In [app/utils/email.py](app/utils/email.py), update the sender email if needed:

```python
GMAIL_EMAIL = "your-verified-domain@yourdomain.com"
```

Make sure this email is verified in your Zepto Mail dashboard.

## 📝 Environment Setup

Add these to your `.env` file:

```env
# Zepto Mail API Configuration
ZEPTO_API_KEY=sk_live_your_key_here

# Optional: For Gmail SMTP fallback
GMAIL_EMAIL=support@travelnudge.com
GMAIL_PASSWORD=your_app_specific_password
```

## 🔍 API Endpoints

### 1. Request Password Reset
**Endpoint:** `POST /forgot-password`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset email sent successfully. Please check your inbox.",
  "email": "user@example.com"
}
```

### 2. Reset Password
**Endpoint:** `POST /reset-password`

**Request:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "✅ Password has been reset successfully. You can now login with your new password."
}
```

## 📧 Email Features

The password reset email includes:
- ✅ Professional HTML template with TravelNudge branding
- ✅ User personalization (user's name)
- ✅ Direct reset button for easy access
- ✅ Security warnings about link expiration (1 hour)
- ✅ Fallback link for copy-paste
- ✅ Footer with company information

## 🛡️ Security Features

- **Token Expiration:** Reset tokens expire after 1 hour
- **Secure Generation:** Uses `secrets.token_urlsafe(32)` for token generation
- **Database Storage:** Tokens are stored with expiry timestamps
- **One-time Use:** Tokens are cleared after successful password reset

## 🧪 Testing

### Manual Test

```bash
# 1. Start your FastAPI server
uvicorn app.main:app --reload

# 2. Open your browser or use curl
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Using Python Requests

```python
import requests

# Request password reset
response = requests.post(
    "http://localhost:8000/api/v1/auth/forgot-password",
    json={"email": "user@example.com"}
)
print(response.json())

# Reset password with token
response = requests.post(
    "http://localhost:8000/api/v1/auth/reset-password",
    json={
        "token": "your_reset_token_here",
        "new_password": "newpassword123"
    }
)
print(response.json())
```

## 📊 Email Delivery Status

You can monitor email delivery status in:
1. **Zepto Mail Dashboard** → Activity/Logs section
2. **Application Logs** → Check console output for ✅/❌ indicators

## ⚠️ Troubleshooting

### Issue: "Invalid API Key"
- ✅ Verify your API key in Zepto Mail dashboard
- ✅ Ensure `.env` file has correct `ZEPTO_API_KEY`
- ✅ Check that the domain is verified in Zepto Mail

### Issue: "Email not sent"
- ✅ Ensure your domain is verified in Zepto Mail
- ✅ Check firewall/network settings
- ✅ Verify recipient email is valid
- ✅ Check application logs for detailed error messages

### Issue: "Connection timeout"
- ✅ Check internet connectivity
- ✅ Verify Zepto Mail API URL is accessible
- ✅ Increase timeout in email.py if needed

### Fallback to Gmail (if needed)
```python
# In your code, change:
send_email(to=email, subject=subject, body=body, use_zepto=False)
```

## 📚 Additional Resources

- [Zepto Mail Documentation](https://help.zeptomail.com/)
- [Zepto Mail API Reference](https://www.zeptomail.com/api/documents/)
- [FastAPI Email Integration](https://fastapi.tiangolo.com/)

## 🎉 Success Indicators

After setup, you should see:
- ✅ Email successfully sent to users
- ✅ Professional HTML formatted emails
- ✅ Reset tokens expire after 1 hour
- ✅ Users can reset password with valid token
- ✅ Logs showing "✅ Email sent successfully to X via Zepto Mail"

## 📝 Notes

- Token validity: **1 hour**
- Max reset attempts: No limit (but can be added)
- Email template language: HTML with inline CSS
- Sender: Uses verified domain from Zepto Mail

---

For more help, contact the development team or check the Zepto Mail support at support@zeptomail.com
