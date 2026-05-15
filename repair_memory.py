from memory.database import DatabaseManager
import time

def repair():
    print("[REPAIR] Repairing AI Swarm Database...")
    try:
        db = DatabaseManager()
        # Re-create collections to ensure outbox exists
        db.clear_database()
        print("[SUCCESS] Database repaired! All collections (Leads, Hunts, Outbox) are now ready.")
        print("[INFO] Now please restart your Streamlit app.")
    except Exception as e:
        print(f"[ERROR] Error during repair: {e}")

if __name__ == "__main__":
    repair()
