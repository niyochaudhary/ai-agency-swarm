import sys
import os

# Force UTF-8 encoding for Windows CMD to prevent charmap errors
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Add the project root to the path so modules can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.swarm_master import SwarmMaster
import config

if __name__ == "__main__":
    print("="*60)
    print("INITIALIZING AI AGENCY AUTO-PILOT")
    print("="*60)
    print(f"Sender Email Configured As: {config.SENDER_EMAIL}")
    
    if config.EMAIL_PASSWORD == "YOUR_APP_PASSWORD_HERE" or not config.EMAIL_PASSWORD:
        print("\n[CRITICAL WARNING] You have not set your Gmail App Password!")
        print("Please open 'config.py' and replace 'YOUR_APP_PASSWORD_HERE' with your actual 16-character Google App Password.")
        print("Without this, the AI cannot send emails automatically.")
        print("Exiting...")
        sys.exit(1)

    try:
        swarm = SwarmMaster()
        # This will run forever until you press Ctrl+C
        swarm.start_auto_pilot()
    except KeyboardInterrupt:
        print("\n\n[STOP] Auto-pilot stopped by user.")
        sys.exit(0)
