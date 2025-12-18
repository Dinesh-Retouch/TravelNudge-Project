# 🚀 Quick Reference - Password Reset with Zepto Mail

## ⚡ 5-Minute Setup

### 1. Install Packages
```bash
pip install -r requirements.txt
```

### 2. Get Zepto Mail API Key
- Go to https://www.zeptomail.com/
- Sign up (free account)
- Copy API key from dashboard

### 3. Create .env File
```bash
cp .env.example .env
# Edit .env and add:
# ZEPTO_API_KEY=your_key_from_zepto
```

### 4. Run Database Migration
```bash
# Quick method (if using Alembic):
alembic revision --autogenerate -m "Add password reset"
alembic upgrade head

# OR directly in Python:
from app.database.database import engine, Base
Base.metadata.create_all(bind=engine)
```

### 5. Start Server
```bash
uvicorn app.main:app --reload
```

## 🧪 Test It

```bash
# 1. Request password reset
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Check email for reset link
# 3. Extract token from URL
# 4. Reset password
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your_token_here",
    "new_password": "NewPass123!"
  }'
```

## 📋 Implementation Checklist

- [x] ✅ Zepto Mail integration in `email.py`
- [x] ✅ Password reset endpoints in `auth.py`
- [x] ✅ Database fields added (`reset_token`, `reset_token_expiry`)
- [x] ✅ Secure token generation (32-byte random)
- [x] ✅ Token expiration (1 hour)
- [x] ✅ Beautiful HTML email template
- [x] ✅ Error handling & validation
- [x] ✅ Documentation (4 files)
- [x] ✅ Environment configuration

## 📁 Key Files

| File | Purpose |
|------|---------|
| [app/utils/email.py](app/utils/email.py) | Zepto Mail & Gmail integration |
| [app/routers/auth.py](app/routers/auth.py) | `/forgot-password` & `/reset-password` endpoints |
| [app/models/user.py](app/models/user.py) | User model with `reset_token` fields |
| [requirements.txt](requirements.txt) | Python dependencies + `requests` |
| [.env.example](.env.example) | Configuration template |

## 🔐 Security Features

✅ Cryptographically secure token generation  
✅ 1-hour token expiration  
✅ One-time use enforcement  
✅ No user enumeration  
✅ Bcrypt password hashing  
✅ Database persistence  

## 🎨 Email Features

✅ Professional HTML template  
✅ TravelNudge branding  
✅ User personalization  
✅ Mobile-responsive design  
✅ Security warnings  
✅ Fallback text link  

## 🆘 Troubleshooting

### Email not sent?
1. Check ZEPTO_API_KEY in .env
2. Verify domain in Zepto Mail dashboard
3. Check application logs for errors

### Token errors?
1. Check token hasn't expired (1 hour limit)
2. Verify token is from your database
3. Ensure database migration was run

### Database errors?
1. Run migration: `alembic upgrade head`
2. Check if `reset_token` column exists
3. See DATABASE_MIGRATION.md for details

## 📊 API Reference

### Forgot Password
```
POST /api/v1/auth/forgot-password
{ "email": "user@example.com" }
```

### Reset Password
```
POST /api/v1/auth/reset-password
{ "token": "...", "new_password": "..." }
```

## 📚 Documentation Files

- **[PASSWORD_RESET_FEATURE.md](PASSWORD_RESET_FEATURE.md)** - Complete guide (architecture, features, security)
- **[ZEPTO_MAIL_SETUP.md](ZEPTO_MAIL_SETUP.md)** - Zepto Mail configuration
- **[DATABASE_MIGRATION.md](DATABASE_MIGRATION.md)** - Database migration steps
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was implemented

## 💡 Pro Tips

1. **Test with real email** - Use a test email account to verify template
2. **Monitor in dashboard** - Check Zepto Mail dashboard for delivery status
3. **Set FRONTEND_URL** - Update reset link to your frontend URL
4. **Use HTTPS in production** - Password reset should only work over HTTPS
5. **Set up alerts** - Monitor failed emails in Zepto Mail

## 🔗 Useful Links

- Zepto Mail: https://www.zeptomail.com/
- API Docs: https://www.zeptomail.com/api/documents/
- Dashboard: https://app.zeptomail.com/
- Help: https://help.zeptomail.com/

## 📞 Support

- **Zepto Mail Issues**: support@zeptomail.com
- **FastAPI Issues**: https://github.com/tiangolo/fastapi/discussions
- **TravelNudge Team**: Contact development team

---

**Status**: ✅ Ready to Use  
**Last Updated**: December 2025  
**Version**: 1.0
