import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

if not api_key:
    print("❌ No API key found in .env file!")
    exit()

genai.configure(api_key=api_key)

try:
    # Use the latest model name
    model = genai.GenerativeModel("models/gemini-2.5-flash")


    response = model.generate_content("Say hello from Gemini 1.5 Flash!")

    print("✅ Gemini API Key is working!")
    print("Response:", response.text)

except Exception as e:
    print("❌ Gemini API test failed:")
    print(e)
