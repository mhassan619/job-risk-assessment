import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GROK_API_KEY")
print("API key loaded:", bool(key))