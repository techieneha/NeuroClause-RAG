import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print("API_KEY loaded:", bool(api_key))

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-1.5-pro",  # or "gemini-1.5-pro" if you have access
    contents="What is health insurance?"
)

print("Response:")
print(response.text)
