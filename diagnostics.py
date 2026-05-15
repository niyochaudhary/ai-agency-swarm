import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

print("Starting AI Swarm System Diagnostics...")

try:
    print("\n1. Checking config.py...")
    import config
    import importlib
    importlib.reload(config)
    print(f"   - Username: {getattr(config, 'DASHBOARD_USERNAME', 'MISSING')}")
    print(f"   - Password: {getattr(config, 'DASHBOARD_PASSWORD', 'MISSING')}")
except Exception as e:
    print(f"   - Config Error: {e}")

try:
    print("\n2. Checking memory/database.py...")
    from memory.database import DatabaseManager, SwarmMemory
    db = DatabaseManager()
    print(f"   - DatabaseManager class: OK")
    print(f"   - SwarmMemory alias: OK")
    
    # Check for methods
    methods = ['get_all_leads', 'get_hunt_history', 'get_outbox_logs', 'clear_database']
    for m in methods:
        if hasattr(db, m):
            print(f"   - Method '{m}': OK")
        else:
            print(f"   - Method '{m}': MISSING")
except Exception as e:
    print(f"   - Database Error: {e}")

try:
    print("\n3. Checking core/swarm_master.py...")
    from core.swarm_master import SwarmMaster
    master = SwarmMaster()
    print(f"   - SwarmMaster class: OK")
    print(f"   - Master.memory object: {type(master.memory).__name__}")
    if hasattr(master.memory, 'get_outbox_logs'):
        print(f"   - Master.memory has 'get_outbox_logs': OK")
    else:
        print(f"   - Master.memory has 'get_outbox_logs': MISSING")
except Exception as e:
    print(f"   - SwarmMaster Error: {e}")

try:
    print("\n4. Checking core/builder_master.py...")
    from core.builder_master import BuilderMaster
    builder = BuilderMaster()
    print(f"   - BuilderMaster class: OK")
    print(f"   - Builder.builder object: {type(builder.builder).__name__}")
except Exception as e:
    print(f"   - BuilderMaster Error: {e}")

try:
    print("\n5. Testing AI Connection (HunterAgent)...")
    from agents.hunter_agent import HunterAgent
    hunter = HunterAgent()
    test_pitch = hunter.generate_pitch("Test Company", "We sell coffee.")
    if test_pitch and "Failed" not in test_pitch and "Connection" not in test_pitch:
        print(f"   - AI Test: SUCCESS (Pitch: {test_pitch[:30]}...)")
    else:
        print(f"   - AI Test: FAILED (Result: {test_pitch})")
except Exception as e:
    print(f"   - AI Test Error: {e}")

print("\nDiagnostics Complete.")
