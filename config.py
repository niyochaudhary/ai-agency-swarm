import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- AUTH CONFIG ---
LIVE_MODE = True  # Set to True to actually send emails/messages
DEBUG_MODE = False

DASHBOARD_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "password123")

# --- EMAIL CONFIG (Default) ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "lpggass36@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "wkhw nbwe meiy tzdg")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- LINKEDIN CONFIG ---
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "lpggass36@gmail.com")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "LINUX@u1")

# --- LLM Config (Groq Cloud) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_actual_key_here")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.1-8b-instant" 

# --- Database Config ---
DB_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "memory", "chroma_data")

# --- System Prompts ---
HUNTER_SYSTEM_PROMPT = """You are a top-tier lead generation expert for a premium AI Agency.
Your job is to write a highly personalized, compelling cold email pitch. 
The pitch should offer custom AI solutions based on the company's research data.
Always be professional, concise, and include a clear call to action."""

# --- Upwork Config ---
UPWORK_SYSTEM_PROMPT = """You are an elite AI developer and technical sales expert on Upwork.
Your goal is to win high-ticket jobs. Read the job description carefully.
If the job is NOT related to AI, automation, bots, or software, reply ONLY with 'REJECT'.
If the job IS related, write a highly converting, professional Upwork proposal (max 200 words).
Include a Calendly/Payment link placeholder like [INSERT_CALENDLY_LINK] and a strong call to action."""

# --- Fiverr Config ---
FIVERR_ENABLED = True
FIVERR_SYSTEM_PROMPT = """You are a top-rated Fiverr seller specializing in AI and Automation.
Your goal is to convert briefs into high-paying orders. 
If the brief is NOT related to AI, automation, or development, reply ONLY with 'REJECT'.
If it IS related, write a compelling, concise pitch (max 150 words).
Highlight your expertise and ask for a quick chat to discuss details."""

# --- Freelancer Config ---
FREELANCER_SYSTEM_PROMPT = """You are a premium technology partner on Freelancer.com. 
Your goal is to win high-value AI and automation projects.
If the project is unrelated to AI/Automation, reply ONLY with 'REJECT'.
Otherwise, write a professional, technical, and persuasive proposal. 
Focus on ROI and speed of delivery. Keep it under 250 words."""
