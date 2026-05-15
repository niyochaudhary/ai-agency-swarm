import sys
import os

# Ensure tools can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from tools.search_tool import SearchTool
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL
import requests
import json

class ScraperAgent:
    def __init__(self):
        self.search_tool = SearchTool()
        print("[Scraper Agent] Online and ready to find leads.")

    def find_leads(self, niche, location, count=5):
        """
        Finds leads using the search tool and filters them. 
        Uses AI fallback if search fails.
        """
        print(f"[Scraper Agent] Hunting for {niche} in {location}...")
        
        leads = []
        try:
            raw_leads = self.search_tool.search_businesses(niche, location, max_results=count)
            for lead in raw_leads:
                if "google.com" not in lead['website'] and "yelp.com" not in lead['website']:
                    leads.append(lead)
        except Exception as e:
            print(f"[Scraper Agent] Search tool failed: {e}")

        # AI FALLBACK: If no leads found via search, use Groq to brainstorm leads
        if not leads:
            print("[Scraper Agent] Search failed or blocked. Using AI Brain to find leads...")
            leads = self.ai_brainstorm_leads(niche, location, count)
        
        print(f"[Scraper Agent] Found {len(leads)} potential leads.")
        return leads

    def ai_brainstorm_leads(self, niche, location, count):
        """Ask Groq to suggest real businesses in this niche/location."""
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"Identify {count} real businesses (name and website) in the '{niche}' niche located in '{location}'. Return ONLY a JSON list of objects with 'name' and 'website' keys. No other text."
        
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        
        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                # Extract JSON if there's markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                return json.loads(content)
        except Exception as e:
            print(f"[Scraper Agent] AI Fallback failed: {e}")
        
        return []

if __name__ == "__main__":
    scraper = ScraperAgent()
    results = scraper.find_leads("Real Estate", "Miami", count=3)
    print(results)
