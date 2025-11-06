import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

prompt = "most popular places in puttur andra pradesh."

try:
    response = model.generate_content(prompt)
    print("✅ Gemini response:\n")
    print(response.text)
except Exception as e:
    print("❌ Gemini test failed:")
    print(e)
