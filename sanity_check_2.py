import os
import requests
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")
headers = {"Authorization": f"Bearer {groq_api_key}"}
response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
models = response.json().get("data", [])
for m in models:
    print(m["id"])
