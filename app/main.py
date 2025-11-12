import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory path BEFORE imports
sys.path.append(os.path.dirname(__file__))

from app.database.database import engine
from app.models.user import Base
from app.routers.auth import auth_router

# ✅ DO NOT DROP TABLES AUTOMATICALLY
# Base.metadata.drop_all(bind=engine)  # REMOVE THIS
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TravelNudge API",
    description="Backend API for TravelNudge - Your AI Travel Assistant",
    version="1.0.0"
)

# ✅ Include router ONCE
app.include_router(auth_router)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

