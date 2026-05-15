import chromadb
import uuid
import time
import os

class SwarmMemory:
    def __init__(self):
        db_path = os.path.join(os.path.dirname(__file__), "chroma_data")
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        self.client = chromadb.PersistentClient(path=db_path)
        self.leads_collection = self.client.get_or_create_collection(name="leads")
        self.hunts_collection = self.client.get_or_create_collection(name="hunts")
        self.outbox_collection = self.client.get_or_create_collection(name="outbox")

    def save_lead(self, name, website, pitch, niche="N/A", location="N/A"):
        lead_id = str(uuid.uuid4())
        self.leads_collection.add(
            documents=[str(pitch) if pitch is not None else "No pitch generated."],
            metadatas=[{"name": name, "website": website, "niche": niche, "location": location, "timestamp": str(time.time())}],
            ids=[lead_id]
        )
        return lead_id

    def save_hunt(self, niche, location, count):
        hunt_id = str(uuid.uuid4())
        self.hunts_collection.add(
            documents=[f"Hunt for {niche} in {location}"],
            metadatas=[{"niche": niche, "location": location, "count": count, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}],
            ids=[hunt_id]
        )

    def get_hunt_history(self):
        return self.hunts_collection.get()

    def log_email(self, recipient_name, recipient_email, subject, body, status="Sent"):
        log_id = str(uuid.uuid4())
        self.outbox_collection.add(
            documents=[body],
            metadatas=[{"recipient_name": recipient_name, "recipient_email": recipient_email, "subject": subject, "status": status, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}],
            ids=[log_id]
        )

    def get_outbox_logs(self):
        return self.outbox_collection.get()

    def get_all_leads(self):
        return self.leads_collection.get()

    def delete_lead(self, lead_id):
        self.leads_collection.delete(ids=[lead_id])

    def clear_database(self):
        try: self.client.delete_collection(name="leads")
        except: pass
        try: self.client.delete_collection(name="hunts")
        except: pass
        try: self.client.delete_collection(name="outbox")
        except: pass
        self.leads_collection = self.client.get_or_create_collection(name="leads")
        self.hunts_collection = self.client.get_or_create_collection(name="hunts")
        self.outbox_collection = self.client.get_or_create_collection(name="outbox")

# ALIAS
DatabaseManager = SwarmMemory
