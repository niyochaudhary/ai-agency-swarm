import os
from agents.scraper_agent import ScraperAgent
from agents.research_agent import ResearchAgent
from agents.hunter_agent import HunterAgent
from agents.sender_agent import SenderAgent
from memory.database import DatabaseManager

class SwarmMaster:
    def __init__(self):
        self.scraper = ScraperAgent()
        self.researcher = ResearchAgent()
        self.hunter = HunterAgent()
        self.sender = SenderAgent()
        self.memory = DatabaseManager()

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
                
                # 2. Deep Research
                research_data = self.researcher.deep_research(lead['website'])
                
                # 3. Generate Personalized Pitch
                pitch = self.hunter.generate_pitch(lead['name'], research_data)
                print(f"[DEBUG] Generated pitch for {lead['name']}: {pitch[:50]}...")
                
                # 4. Save to Memory with Niche and Location
                self.memory.save_lead(
                    name=lead['name'], 
                    website=lead['website'], 
                    pitch=pitch,
                    niche=niche,
                    location=location
                )
                
                results.append({
                    "name": lead['name'],
                    "pitch": pitch
                })
            except Exception as e:
                print(f"[ERROR] Failed to process lead {lead.get('name', 'Unknown')}: {e}")
                continue
            
        print(f"[COMPLETE] Hunt completed! Found {len(results)} leads.")
        return results
