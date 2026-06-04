import requests
import json
import os
import sys
from loguru import logger

# Ensure config can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL, FREELANCER_SYSTEM_PROMPT

class FreelancerAgent:
    def __init__(self):
        self.model = DEFAULT_MODEL
        logger.info("[Freelancer Agent] Initialized and ready to bid.")

    def fetch_projects(self):
        """
        Simulates fetching Freelancer.com projects. 
        In a real scenario, this would use Freelancer API or a scraper.
        """
        # Mock projects
        return [
            {"id": "fr1", "title": "Build an AI Sales Bot", "description": "We need a bot that uses LLMs to reply to customer emails."},
            {"id": "fr2", "title": "Excel Automation", "description": "Need to automate data entry from PDF to Excel."}
        ]

    def evaluate_and_write_bid(self, title, description):
        """Uses AI to write a high-converting proposal."""
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": FREELANCER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Project: {title}\nDetails: {description}"}
            ],
            "temperature": 0.5
        }

        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            content = response.json()['choices'][0]['message']['content'].strip()
            return None if "REJECT" in content else content
        except Exception as e:
            logger.error(f"Freelancer Bid Generation Error: {e}")
            return None

    def auto_submit_bid(self, project, bid_text):
        logger.success(f"💰 [Freelancer] Bid prepared for: {project['title']}")
        # Real integration would use API to POST the bid here