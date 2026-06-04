import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

print("[TEST] Starting basic Chrome test...")

try:
    print("[TEST] Step 1: Creating Chrome options...")
    opts = Options()
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,800")
    
    print("[TEST] Step 2: Getting ChromeDriver...")
    driver_path = ChromeDriverManager().install()
    print(f"[TEST] ChromeDriver installed at: {driver_path}")
    
    print("[TEST] Step 3: Creating Chrome instance...")
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=opts)
    print("[TEST] Chrome instance created successfully!")
    
    print("[TEST] Step 4: Navigating to Google...")
    driver.get("https://www.google.com")
    print("[TEST] Navigation successful!")
    print(f"[TEST] Current URL: {driver.current_url}")
    
    print("[TEST] Step 5: Quitting driver...")
    driver.quit()
    print("[TEST] SUCCESS - All steps completed!")
    
except Exception as e:
    print(f"[TEST ERROR] {e}")
    import traceback
    traceback.print_exc()
