import requests
import json
import os
import sys
from loguru import logger

# Ensure config can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL, FIVERR_SYSTEM_PROMPT

class FiverrAgent:
    def __init__(self):
        self.model = DEFAULT_MODEL
        logger.info("[Fiverr Agent] Online and hunting for briefs.")

    def fetch_briefs(self):
        """
        Simulates fetching Fiverr briefs. 
        In production, this would use a browser automation tool like Playwright.
        """
        # Mock briefs for demonstration
        return [
            {"id": "f1", "title": "AI Content Generator", "description": "Need a tool to generate blog posts using GPT-4."},
            {"id": "f2", "title": "Logo Design", "description": "Need a minimal logo for my startup."}
        ]

    def evaluate_and_write_offer(self, title, description):
        """Uses AI to evaluate if the brief is relevant and writes an offer."""
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": FIVERR_SYSTEM_PROMPT},
                {"role": "user", "content": f"Brief Title: {title}\nDescription: {description}"}
            ],
            "temperature": 0.5
        }

        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            content = response.json()['choices'][0]['message']['content'].strip()
            return None if "REJECT" in content else content
        except Exception as e:
            logger.error(f"Fiverr AI Pitch Error: {e}")
            return None

    def auto_submit_offer(self, brief, offer_text):
        logger.success(f"🚀 [Fiverr] Offer drafted for: {brief['title']}")
        # Logic for automated submission would go here (e.g. Playwright/Selenium)