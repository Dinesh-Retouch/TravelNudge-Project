from fastapi import APIRouter, HTTPException
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI"])

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

@router.post("/chat")
async def chat_with_ai(message: str):
    try:
        response = model.generate_content(message)
        return {
            "success": True,
            "response": response.text,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")