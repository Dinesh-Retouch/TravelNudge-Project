import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Try different import approaches
try:
    from app.database.database import engine
    from app.models.user import Base
    print("✅ Imported from app package")
except ImportError:
    try:
        from database.database import engine
        from models.user import Base
        print("✅ Imported from direct modules")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Current directory:", os.getcwd())
        print("Files in current directory:", os.listdir('.'))
        if os.path.exists('database'):
            print("Database directory contents:", os.listdir('database'))
        raise

# Drop and recreate all tables (for development)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TravelNudge API",
    description="Backend API for TravelNudge - Your AI Travel Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import forgot password router
try:
    from app.utils.forgot_password import router as forgot_router
    app.include_router(forgot_router, prefix="/api/v1/auth", tags=["Authentication"])
    print("✅ Forgot password router loaded successfully")
except ImportError as e:
    try:
        from utils.forgot_password import router as forgot_router
        app.include_router(forgot_router, prefix="/api/v1/auth", tags=["Authentication"])
        print("✅ Forgot password router loaded successfully (direct import)")
    except ImportError as e:
        print(f"⚠️ Forgot password router import warning: {e}")

# Import and include routers
try:
    from app.routers.auth import auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    print("✅ Auth router loaded successfully")
except ImportError:
    try:
        from routers.auth import auth_router
        app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
        print("✅ Auth router loaded successfully (direct import)")
    except ImportError as e:
        print(f"❌ Auth router import error: {e}")

# AI Router
try:
    from app.routers.ai import router as ai_router
    app.include_router(ai_router, tags=["AI"])
    print("✅ AI router loaded successfully")
except ImportError:
    try:
        from routers.ai import router as ai_router
        app.include_router(ai_router, tags=["AI"])
        print("✅ AI router loaded successfully (direct import)")
    except ImportError as e:
        print(f"❌ AI router import error: {e}")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to TravelNudge API",
        "description": "AI Assistant Chatbot Backend for Travel Planning",
        "version": "1.0.0",
        "docs": "Visit /docs for API documentation",
        "endpoints": {
            "signup": "POST /api/v1/auth/signup",
            "login": "POST /api/v1/auth/login",
            "health": "GET /health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TravelNudge Backend API"}

@app.get("/api/info")
def api_info():
    return {
        "name": "TravelNudge API",
        "description": "Backend service for TravelNudge travel assistant",
        "endpoints": {
            "auth": {
                "signup": "/api/v1/auth/signup",
                "signin": "/api/v1/auth/signin",
                "logout": "/api/v1/auth/logout",
                "me": "/api/v1/auth/me"
            },
            "ai": {
                "chat": "/ai/chat"
            }
        }
    }

print("✅ FastAPI app configured successfully")