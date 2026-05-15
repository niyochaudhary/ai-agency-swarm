import os

# --- AUTH CONFIG ---
DASHBOARD_USERNAME = "admin"
DASHBOARD_PASSWORD = "password123"

# --- EMAIL CONFIG (Default) ---
SENDER_EMAIL = "lpggass36@gmail.com"
EMAIL_PASSWORD = "YOUR_APP_PASSWORD_HERE"  # Will be overridden by dashboard settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- LLM Config (Groq Cloud) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant" 

# --- Database Config ---
DB_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "memory", "chroma_data")

# --- System Prompts ---
HUNTER_SYSTEM_PROMPT = """You are a top-tier lead generation expert for a premium AI Agency.
Your job is to write a highly personalized, compelling cold email pitch. 
The pitch should offer custom AI solutions based on the company's research data.
Always be professional, concise, and include a clear call to action."""
