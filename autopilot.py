import time
import schedule
import logging
from loguru import logger
from agents.upwork_agent import UpworkAgent
from agents.fiverr_agent import FiverrAgent
from agents.freelancer_agent import FreelancerAgent
from agents.linkedin_agent import LinkedinAgent
from memory.database import DatabaseManager

# Configure logging for our Auto-Pilot system
logger.add("logs/autopilot.log", rotation="10 MB")

class AutoPilotSystem:
    def __init__(self):
        self.is_running = False
        self.db = DatabaseManager()
        self.upwork_agent = UpworkAgent()
        self.fiverr_agent = FiverrAgent()
        self.freelancer_agent = FreelancerAgent()
        self.linkedin_agent = LinkedinAgent()
        # You must replace this with your actual Upwork RSS feed link
        self.upwork_rss_url = "https://www.upwork.com/ab/feed/jobs/rss?q=AI%20Developer&sort=recency"
        self.current_jobs = []
        self.current_briefs = []
        self.current_freelancer_projects = []
        logger.info("🤖 Auto-Pilot System Initialized. AI is ready to take over.")

    def scan_for_upwork_jobs(self):
        """
        AI will automatically scan Upwork RSS feeds to find new jobs.
        """
        logger.info("🔍 [Auto-Pilot] Scanning Upwork for high-paying AI jobs...")
        self.current_jobs = self.upwork_agent.fetch_jobs_from_rss(self.upwork_rss_url)
        logger.info(f"📊 Found {len(self.current_jobs)} new jobs to evaluate.")

    def scan_for_fiverr_briefs(self):
        """
        AI will automatically scan Fiverr Briefs.
        """
        logger.info("🔍 [Auto-Pilot] Scanning Fiverr for new briefs...")
        self.current_briefs = self.fiverr_agent.fetch_briefs()
        logger.info(f"📊 Found {len(self.current_briefs)} new briefs to evaluate.")

    def scan_for_freelancer_jobs(self):
        """
        AI will automatically scan Freelancer.com.
        """
        logger.info("🔍 [Auto-Pilot] Scanning Freelancer.com for new projects...")
        self.current_freelancer_projects = self.freelancer_agent.fetch_projects()
        logger.info(f"📊 Found {len(self.current_freelancer_projects)} projects to evaluate.")

    def evaluate_and_bid(self):
        """
        AI will evaluate the job and automatically submit a proposal if it matches.
        """
        if not self.current_jobs:
            logger.info("💤 No new jobs to evaluate right now.")
            return

        logger.info("✍️ [Auto-Pilot] Evaluating jobs and auto-submitting proposals...")
        
        for job in self.current_jobs[:3]: # Limit to top 3 per cycle to avoid API limits
            proposal = self.upwork_agent.evaluate_and_write_proposal(job['title'], job['description'])
            if proposal:
                # In the future, this will actually click the 'Submit' button via Playwright
                self.upwork_agent.auto_submit_proposal(job, proposal)
                time.sleep(3) # Small delay between submissions

    def evaluate_and_bid_fiverr(self):
        """
        AI will evaluate Fiverr briefs and submit offers automatically.
        """
        if not self.current_briefs:
            return

        for brief in self.current_briefs:
            offer = self.fiverr_agent.evaluate_and_write_offer(brief['title'], brief['description'])
            if offer:
                self.fiverr_agent.auto_submit_offer(brief, offer)

    def evaluate_and_bid_freelancer(self):
        """
        AI will evaluate Freelancer projects and submit bids.
        """
        if not self.current_freelancer_projects:
            return

        for project in self.current_freelancer_projects:
            bid = self.freelancer_agent.evaluate_and_write_bid(project['title'], project['description'])
            if bid:
                self.freelancer_agent.auto_submit_bid(project, bid)

    def check_messages_and_reply(self):
        """
        AI will check for new leads in DB for LinkedIn outreach.
        """
        logger.info("💬 [Auto-Pilot] Checking for new leads in DB for outreach...")
        leads = self.db.get_all_leads()
        
        if leads['ids']:
            for i in range(min(3, len(leads['ids']))): # Outreach to 3 leads per cycle
                meta = leads['metadatas'][i]
                # LinkedIn Integration
                try:
                    logger.info(f"🔗 Attempting LinkedIn connection for {meta['name']}...")
                    self.linkedin_agent.search_and_connect(meta['name'], leads['documents'][i])
                    # Add a delay to look more human and avoid instant closing
                    time.sleep(5) 
                except Exception as e:
                    logger.error(f"❌ LinkedIn Error for {meta['name']}: {e}")
        
        pass

    def run_cycle(self):
        """
        One complete cycle of the Auto-Pilot system.
        """
        logger.info("🔄 Starting Auto-Pilot Cycle...")
        self.scan_for_upwork_jobs()
        self.scan_for_fiverr_briefs()
        self.scan_for_freelancer_jobs()
        self.evaluate_and_bid()
        self.evaluate_and_bid_fiverr()
        self.evaluate_and_bid_freelancer()
        self.check_messages_and_reply()
        logger.info("✅ Cycle Complete. Waiting for next cycle.")

    def start_24_7_operation(self):
        """
        Starts the infinite loop for 24/7 operation.
        """
        self.is_running = True
        logger.success("🚀 100% AUTO-PILOT MODE ACTIVATED. You can go sleep now!")
        
        # Schedule the AI to run every 10 minutes
        schedule.every(10).minutes.do(self.run_cycle)
        
        # Run the first cycle immediately
        self.run_cycle()

        while self.is_running:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    autopilot = AutoPilotSystem()
    autopilot.start_24_7_operation()
