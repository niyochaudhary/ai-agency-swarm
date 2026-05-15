import requests
import json
import sys
import os

# Ensure config can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL, HUNTER_SYSTEM_PROMPT

class HunterAgent:
    def __init__(self):
        self.model = DEFAULT_MODEL
        print(f"[Hunter Agent] Online and connected to Groq Cloud (Model: {self.model})")

    def generate_pitch(self, company_name, company_desc):
        """Ask Groq to read the description and write a pitch."""
        print(f"[Hunter Agent] Brainstorming pitch for {company_name} using AI...")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": HUNTER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Company: {company_name}\nDescription: {company_desc}\n\nTask: Write a cold email pitch to their CEO offering AI solutions."}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                error_msg = f"AI Generation Failed (Status {response.status_code})"
                print(f"[Error] {error_msg}. Response: {response.text}")
                return error_msg
        except Exception as e:
            error_msg = f"Connection to Groq failed: {e}"
            print(f"[Error] {error_msg}")
            return error_msg

if __name__ == "__main__":
    agent = HunterAgent()
    print(agent.generate_pitch("Test Corp", "A big tech company."))
