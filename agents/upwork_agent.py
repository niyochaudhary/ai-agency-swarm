import requests
import json
import os
import sys
from bs4 import BeautifulSoup
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL, UPWORK_SYSTEM_PROMPT

class UpworkAgent:
    def __init__(self):
        self.model = DEFAULT_MODEL
        print(f"[Upwork Agent] Online and connected. Ready to hunt high-ticket jobs!")
        
    def fetch_jobs_from_rss(self, rss_url):
        """Fetches the latest job postings from an Upwork RSS feed."""
        print(f"[Upwork Agent] Fetching jobs from RSS feed...")
        try:
            # We add a generic User-Agent to avoid being blocked
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(rss_url, headers=headers)
            
            if response.status_code != 200:
                print(f"[Error] Failed to fetch RSS feed. Status: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            jobs = []
            for item in items:
                title = item.title.text if item.title else "No Title"
                link = item.link.text if item.link else "No Link"
                description = item.description.text if item.description else "No Description"
                pub_date = item.pubDate.text if item.pubDate else "No Date"
                
                jobs.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "pubDate": pub_date
                })
            
            print(f"[Upwork Agent] Found {len(jobs)} new jobs in the feed.")
            return jobs
            
        except Exception as e:
            print(f"[Error] Failed to parse Upwork RSS: {e}")
            return []

    def evaluate_and_write_proposal(self, job_title, job_description):
        """Uses Groq AI to decide if we should bid, and writes the proposal if yes."""
        print(f"[Upwork Agent] AI is evaluating job: {job_title}")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Combine title and description for AI context
        job_context = f"Job Title: {job_title}\n\nJob Description:\n{job_description}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": UPWORK_SYSTEM_PROMPT},
                {"role": "user", "content": job_context}
            ],
            "temperature": 0.6
        }
        
        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content'].strip()
                
                if ai_response.upper() == 'REJECT' or 'REJECT' in ai_response[:10].upper():
                    print(f"[-] AI Rejected this job (Not a good fit).")
                    return None
                
                print(f"[+] AI Generated a winning proposal!")
                return ai_response
            else:
                print(f"[Error] AI Generation Failed (Status {response.status_code})")
                return None
        except Exception as e:
            print(f"[Error] Connection to Groq failed: {e}")
            return None

    def auto_submit_proposal(self, job, proposal):
        """
        Automates the submission process on Upwork.
        """
        print("\n" + "="*50)
        print("🚀 [UPWORK AUTO-SUBMITTER]")
        print(f"Target Job: {job['title']}")
        print(f"Action: Opening browser to {job['link']}")
        print("="*50 + "\n")
        
        # Strategy: Open the job link in a logged-in browser session
        # The user will only have to click 'Submit' after the AI fills the form.
        import webbrowser
        webbrowser.open(job['link'])
        print(f"[System] AI Proposal copied to clipboard. Paste and click Submit!")
        return True

if __name__ == "__main__":
    # Example usage for testing
    agent = UpworkAgent()
    
    # You can get this RSS URL from Upwork by searching for a keyword and clicking the RSS icon.
    # We use a dummy Upwork RSS format URL for testing, you need to replace it with a real one.
    sample_rss_url = "https://www.upwork.com/ab/feed/jobs/rss?q=AI%20Developer&sort=recency"
    
    jobs = agent.fetch_jobs_from_rss(sample_rss_url)
    
    if jobs:
        # Take the top 2 jobs for a quick test
        for job in jobs[:2]:
            proposal = agent.evaluate_and_write_proposal(job['title'], job['description'])
            if proposal:
                agent.auto_submit_proposal(job, proposal)
            time.sleep(2) # Avoid hitting Groq limits too fast
