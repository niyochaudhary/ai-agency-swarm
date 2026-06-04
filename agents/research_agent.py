import sys
import os
import requests

# Ensure tools and config can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.web_scraper import WebScraper
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL

class ResearchAgent:
    def __init__(self):
        self.scraper = WebScraper()
        self.model = DEFAULT_MODEL
        print(f"[Research Agent] Online and connected to Groq Cloud.")

    def deep_research(self, url):
        """
        Scrapes a website and uses Groq to summarize the business model and needs.
        """
        content, emails, _, linkedin = self.scraper.scrape_website(url)
        if not content:
            return "Could not fetch website content.", [], []

        print(f"[Research Agent] Analyzing website data for {url} using AI...")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a business analyst. Summarize the following website content into 3 bullet points: 1. Core Services 2. Target Audience 3. Possible AI needs."},
                {"role": "user", "content": f"Website Content:\n{content}\n\nSummary:"}
            ],
            "temperature": 0.5
        }
        
        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                summary = result['choices'][0]['message']['content'].strip()
                
                # AI Prediction for email if missing
                if not emails:
                    predict_payload = {
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "Find contact email. Return JSON: {\"email\": \"...\"}"},
                            {"role": "user", "content": f"Website Content: {summary}"}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.2
                    }
                    pred_resp = requests.post(GROQ_BASE_URL, headers=headers, json=predict_payload)
                    if pred_resp.status_code == 200:
                        try:
                            p_json = json.loads(pred_resp.json()['choices'][0]['message']['content'])
                            if not emails and "@" in p_json.get('email', ''):
                                emails = [p_json['email']]
                        except: pass
                
                return summary, emails, linkedin
            else:
                return "AI Analysis failed.", emails, linkedin
        except Exception as e:
            return f"Error during research: {e}", [], []

if __name__ == "__main__":
    agent = ResearchAgent()
    summary = agent.deep_research("https://openai.com")
    print(f"\n[Deep Research Summary]\n{summary}")
