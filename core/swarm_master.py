import os
from agents.scraper_agent import ScraperAgent
from agents.research_agent import ResearchAgent
from agents.hunter_agent import HunterAgent
from agents.sender_agent import SenderAgent
from agents.linkedin_agent import LinkedinAgent
from memory.database import DatabaseManager
from core.builder_master import BuilderMaster
import time
import random

class SwarmMaster:
    def __init__(self):
        self.scraper = ScraperAgent()
        self.researcher = ResearchAgent()
        self.hunter = HunterAgent()
        self.sender = SenderAgent(dry_run=False) # Changed to False for LIVE sending
        self.linkedin = LinkedinAgent()
        self.memory = DatabaseManager()
        self.builder_master = BuilderMaster()
        self.last_linkedin_time = 0 # To strictly enforce 15/day limit

    def orchestrate_hunt(self, niche, location, count=5):
        print(f"[HUNT] Starting hunt for {niche} in {location}...")
        
        # Save this hunt to history
        self.memory.save_hunt(niche, location, count)
        
        # 1. Scrape Leads
        leads = self.scraper.find_leads(niche, location, count)
        
        results = []
        for lead in leads:
            try:
                print(f"[RESEARCH] Researching: {lead['name']}")
                
                # 2. Deep Research (with fallback)
                try:
                    research_data, emails, phones, linkedin = self.researcher.deep_research(lead['website'])
                except Exception as research_err:
                    print(f"[WARNING] Research failed for {lead['name']}: {research_err}")
                    research_data, emails, phones, linkedin = f"General lead in {niche} industry.", [], [], []
                
                # 3. Generate Personalized Pitch
                pitch = self.hunter.generate_pitch(lead['name'], research_data)
                
                # Check if pitch generation failed (e.g. Status 429 Rate Limit)
                if "AI Generation Failed" in pitch or "Connection to Groq failed" in pitch:
                    print(f"[SKIP] Groq API limit reached. Skipping lead {lead['name']}.")
                    continue
                
                # 4. Generate Demo/Project
                print(f"[BUILD] Building custom demo for {lead['name']}...")
                proj_path = self.builder_master.launch_project(lead['name'], pitch)
                
                # Append demo info and user signature to pitch
                signature = """
                
Best regards,

[ NIYO ]
[ Ai agency swarm ]
Contact No: +9779810199444
WhatsApp No: +9779768729375
LinkedIn: https://www.linkedin.com/in/niyo888888?utm_source=share_via&utm_content=profile&utm_medium=member_ios"""

                final_pitch = f"{pitch}\n\nI have already built a custom AI demo for you. Let me know when you'd like to see it!{signature}"

                # 5. Save to Memory with Niche and Location
                found_email = emails[0] if emails else lead.get('email', "")
                found_phone = phones[0] if phones else ""
                found_linkedin = linkedin[0] if linkedin else ""
                
                self.memory.save_lead(
                    name=lead['name'], 
                    website=lead['website'], 
                    pitch=final_pitch,
                    niche=niche,
                    location=location,
                    email=found_email,
                    phone=found_phone,
                    linkedin=found_linkedin
                )
                
                # 6. Collect for fast bulk send
                if found_email:
                    results.append({
                        "name": lead['name'],
                        "email": found_email,
                        "pitch": final_pitch
                    })
                else:
                    print(f"[SKIP] No email found for {lead['name']}, skipping send.")

                # 7. Immediate LinkedIn Outreach (no cooldown) – try connection then direct message
                print(f"[LINKEDIN] Attempting LinkedIn connection for {lead['name']}...")
                self.linkedin.search_and_connect(lead['name'], final_pitch)
                # Attempt to send a direct message regardless of connection outcome
                self.linkedin.message_ceo(lead['name'], final_pitch)
                self.last_linkedin_time = time.time()
                time.sleep(1)  # brief pause between requests

            except Exception as e:
                print(f"[ERROR] Failed to process lead {lead.get('name', 'Unknown')}: {e}")
                continue

        # Bulk send all collected emails — 1 email/sec, persistent SMTP connection
        if results:
            print(f"\n[SEND] 🚀 Bulk sending {len(results)} emails @ 1 per second...")
            self.sender.send_bulk(results, delay_seconds=1)
        
        print(f"[COMPLETE] Hunt completed! Processed {len(results)} leads.")
        return results

    def start_auto_pilot(self):
        """
        Runs infinitely, iterating through multiple niches and countries to hunt, build, and send.
        """
        niches = ["Real Estate Agencies", "Dental Clinics", "Law Firms", "SaaS Companies", "E-commerce Brands"]
        countries = ["USA", "UK", "Canada", "Australia", "UAE"]
        
        print("\n" + "="*50)
        print("STARTING AI AGENCY AUTO-PILOT")
        print("="*50)
        
        while True:
            # Pick a random niche and country for variety
            niche = random.choice(niches)
            country = random.choice(countries)
            
            print(f"\n[AUTO-PILOT] Target: {niche} in {country}")
            try:
                # Hunt for 3 leads at a time per cycle
                self.orchestrate_hunt(niche, country, count=3)
            except Exception as e:
                print(f"[ERROR] Auto-pilot encountered an error: {e}")
            
            # Short pause before next hunt (10 sec is enough)
            wait_time = 10
            print(f"[AUTO-PILOT] ⏳ Next hunt in {wait_time} seconds...\n")
            time.sleep(wait_time)
