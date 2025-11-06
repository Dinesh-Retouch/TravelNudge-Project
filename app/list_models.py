import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

try:
    models = genai.list_models()
    print("✅ Available models for your API key:\n")
    for m in models:
        print("-", m.name)
except Exception as e:
    print("❌ Failed to list models:")
    print(e)
