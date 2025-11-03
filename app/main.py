from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine
from app.models.user import Base
from app.routers.auth import auth_router  # Make sure this import is correct

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TravelNudge API",
    description="AI Assistant Chatbot Backend",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",   # React local dev
    "http://127.0.0.1:3000",
    "https://yourfrontenddomain.com"  # optional - for production
]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Welcome to TravelNudge API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TravelNudge Backend"}