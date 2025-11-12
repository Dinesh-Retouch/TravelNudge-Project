import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

app = FastAPI(
    title="TravelNudge API",
    description="Backend API for TravelNudge - Your AI Travel Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
try:
    from routers.auth import auth_router
    app.include_router(auth_router, tags=["Authentication"])
    print("✅ Auth router loaded successfully")
except ImportError as e:
    print(f"❌ Auth router import error: {e}")



@app.get("/")
def read_root():
    return {
        "message": "Welcome to TravelNudge API",
        "description": "AI Assistant Chatbot Backend for Travel Planning",
        "version": "1.0.0",
        "docs": "Visit /docs for API documentation",
        "endpoints": {
            "ai_chat": "POST /ai/chat"
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
                "login": "/api/v1/auth/login", 
                "logout": "/api/v1/auth/logout",
                "me": "/api/v1/auth/me"
            },
            "ai": {
                "chat": "/ai/chat"
            }
        }
    }

print("✅ FastAPI app configured successfully")