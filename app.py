import os
import sys
from core.swarm_master import SwarmMaster

def main():
    print("========================================")
    print("      AI AGENCY SWARM - v1.0.0          ")
    print("========================================")
    print("Ready to accelerate your path to wealth.")
    print("----------------------------------------")
    
    master = SwarmMaster()
    
    while True:
        print("\n[Menu]")
        print("1. Start an Autonomous Lead Hunt")
        print("2. Manual Lead Research & Pitch (Single)")
        print("3. View Saved Leads")
        print("4. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == "1":
            niche = input("Enter niche (e.g. Real Estate, Dentist): ")
            location = input("Enter location (e.g. London, Dubai): ")
            count = input("Number of leads to find (default 5): ")
            count = int(count) if count.strip() else 5
            
            master.orchestrate_hunt(niche, location, count=count)
            
        elif choice == "2":
            company = input("Enter Company Name: ")
            website = input("Enter Website URL (include https://): ")
            
            # Create a mock lead list for orchestrate_hunt or call components directly
            lead = {"name": company, "website": website, "description": "Manual entry"}
            
            print(f"\n--- Starting Deep Process for {company} ---")
            research, _, _ = master.researcher.deep_research(website)
            print(f"[Research] Complete.")
            
            pitch = master.hunter.generate_pitch(company, research)
            if pitch:
                master.memory.save_lead(company, website, pitch)
                # Naive email guessing improvement
                domain = website.split('//')[-1].split('/')[0].replace('www.', '')
                guessed_email = f"info@{domain}" # Using info@ is generally safer than ceo@
                print(f"[System] Attempting send to guessed email: {guessed_email}")
                master.sender.send_email(company, guessed_email, pitch)
                print(f"\n[AI Pitch Generated]\n{pitch}\n")
            
        elif choice == "3":
            leads = master.memory.get_all_leads()
            if not leads['ids']:
                print("No leads found in memory.")
            else:
                for i in range(len(leads['ids'])):
                    print(f"\nID: {leads['ids'][i]}")
                    print(f"Company: {leads['metadatas'][i]['name']}")
                    print(f"Website: {leads['metadatas'][i]['website']}")
                    print(f"Pitch Snippet: {leads['documents'][i][:100]}...")
                    print("-" * 20)
                    
        elif choice == "4":
            print("Shutting down the Swarm. Good luck with your sales!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")
        sys.exit(0)
