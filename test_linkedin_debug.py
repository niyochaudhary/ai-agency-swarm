import sys
import traceback
from agents.linkedin_agent import LinkedinAgent

print("[DEBUG] Starting LinkedIn login test...")
try:
    agent = LinkedinAgent()
    print(f"[DEBUG] Username loaded: {agent.username}")
    print(f"[DEBUG] Password set: {'*' * len(agent.password) if agent.password else 'NOT SET'}")
    print("[DEBUG] Calling login()...")
    result = agent.login()
    print(f"[DEBUG] Login result: {result}")
except Exception as e:
    print(f"[ERROR] Exception occurred: {e}")
    traceback.print_exc()
finally:
    print("[DEBUG] Test complete.")
