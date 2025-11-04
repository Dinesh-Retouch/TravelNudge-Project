from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine
from app.models.user import Base

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

# Import and include routers
try:
    from app.routers.auth import auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    print("✅ Auth router loaded successfully")
except ImportError as e:
    print(f"❌ Router import error: {e}")

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
                "login": "/api/v1/auth/login", 
                "logout": "/api/v1/auth/logout",
                "me": "/api/v1/auth/me"
            }
        }
    }

print("✅ FastAPI app configured successfully")