import time
import random
import config

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("[WARNING] Selenium is not installed. Run: pip install selenium webdriver-manager")


class LinkedinAgent:
    def __init__(self):
        self.username = config.LINKEDIN_USERNAME
        self.password = config.LINKEDIN_PASSWORD
        self.driver = None
        self.logged_in = False

    def human_typing(self, element, text):
        """Types text quickly but human-like."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.03, 0.08))

    def random_sleep(self, min_s=0.5, max_s=1.5):
        """Short random pause between actions."""
        time.sleep(random.uniform(min_s, max_s))

    def initialize_driver(self):
        """Start Chrome in headed mode (LinkedIn blocks headless)."""
        print("[LinkedIn] Starting browser...")
        try:
            opts = Options()
            opts.add_argument("--disable-gpu")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--window-size=1280,800")
            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_experimental_option("useAutomationExtension", False)
            
            print("[LinkedIn] Installing/updating ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            print("[LinkedIn] Creating Chrome instance...")
            self.driver = webdriver.Chrome(service=service, options=opts)
            self.driver.set_page_load_timeout(30)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            print("[LinkedIn] Browser initialized successfully.")
        except Exception as e:
            print(f"[LinkedIn Error] Failed to initialize driver: {e}")
            raise

    def _confirm_logged_in(self, timeout=25):
        """Wait for LinkedIn to reach a logged-in state or return False."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            current_url = self.driver.current_url.lower()
            if any(token in current_url for token in ["/feed", "/mynetwork", "/sales", "/inbox", "/homepage"]):
                return True
            try:
                if self.driver.find_element(By.XPATH, "//img[contains(@class,'global-nav__me-photo')] | //button[contains(@aria-label,'Me')]"):
                    return True
            except Exception:
                pass
            time.sleep(1)
        return False

    def login(self):
        """Log in to LinkedIn once; reuse session for subsequent calls."""
        if self.logged_in and self.driver:
            return True
        if not self.username or self.username == "YOUR_LINKEDIN_EMAIL":
            print("[SKIP] LinkedIn credentials not configured in config.py")
            return False
        
        try:
            if not self.driver:
                self.initialize_driver()
            
            print("[LinkedIn] Attempting to navigate to LinkedIn login page...")
            try:
                self.driver.set_page_load_timeout(15)
                self.driver.get("https://www.linkedin.com/login")
                print("[LinkedIn] Login page loaded successfully")
            except Exception as nav_err:
                print(f"[LinkedIn] Navigation timeout/error: {nav_err}")
                print("[LinkedIn] LinkedIn may be blocking the automation. Keeping browser open.")
                return False
            
            # Wait and enter credentials
            wait = WebDriverWait(self.driver, 15)
            
            try:
                username_field = wait.until(EC.visibility_of_element_located((By.NAME, "session_key")))
                print("[LinkedIn] Username field found, entering credentials...")
                self.human_typing(username_field, self.username)
                self.random_sleep(0.5, 1)
            except Exception as e:
                print(f"[LinkedIn] Could not find username field: {e}")
                return False
            
            try:
                password_field = wait.until(EC.visibility_of_element_located((By.NAME, "session_password")))
                self.human_typing(password_field, self.password)
                self.random_sleep(0.5, 1)
                password_field.send_keys(Keys.RETURN)
                print("[LinkedIn] Credentials submitted, waiting for login...")
            except Exception as e:
                print(f"[LinkedIn] Could not enter password: {e}")
                return False

            # Wait for login to complete
            if self._confirm_logged_in(timeout=30):
                print("[LinkedIn] ✅ Login successful!")
                self.logged_in = True
                return True

            print("[LinkedIn] ⚠️ Login result unclear. Keeping browser open for manual intervention if needed.")
            return False
            
        except Exception as e:
            print(f"[LinkedIn Error] Login failed: {e}")
            return False

    def _search_ceo(self, lead_name):
        """Navigate to people search for the CEO of lead_name. Returns True on success."""
        query = lead_name.replace(" ", "%20") + "%20CEO"
        self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={query}")
        try:
            WebDriverWait(self.driver, 12).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//ul[contains(@class,'reusable-search__entity-result-list')]")
                )
            )
            self.driver.execute_script("window.scrollTo(0, 300);")
            self.random_sleep(0.5, 1)
            return True
        except Exception:
            print(f"[LinkedIn] Search results did not load for '{lead_name}'.")
            return False

    def search_and_connect(self, lead_name, pitch):
        """
        Search for CEO of lead_name and:
          1. Send a connection request with a note (preferred), OR
          2. Fallback to direct message if Connect button is absent.
        """
        if not self.login():
            return False

        try:
            print(f"[LinkedIn] Searching for CEO of: {lead_name}")
            if not self._search_ceo(lead_name):
                return False

            # ── Try Connect button ──────────────────────────────────────────
            try:
                connect_btn = WebDriverWait(self.driver, 7).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Connect')] | //button[span[text()='Connect']]"))
                )
                
                if "Pending" in connect_btn.text:
                    print(f"[LinkedIn] Connection already pending for {lead_name}")
                    return True
                    
                connect_btn.click()
                self.random_sleep(1, 1.5)

                # Add personalised note
                try:
                    add_note = WebDriverWait(self.driver, 6).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[@aria-label='Add a note']")
                        )
                    )
                    add_note.click()
                    self.random_sleep(0.5, 1)

                    short_pitch = (pitch[:270] + "... Let's connect!") if len(pitch) > 270 else pitch
                    textarea = WebDriverWait(self.driver, 6).until(
                        EC.presence_of_element_located((By.ID, "custom-message"))
                    )
                    self.human_typing(textarea, short_pitch)
                    self.random_sleep(0.5, 1)
                except Exception:
                    print("[LinkedIn] 'Add a note' not found — sending without note.")

                # Send
                send_btn = WebDriverWait(self.driver, 6).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@aria-label='Send now'] | //button[span[text()='Send']]")
                    )
                )
                send_btn.click()
                print(f"[LinkedIn] ✅ Connection request sent to CEO of {lead_name}!")
                self.random_sleep(1, 2)
                return True

            except Exception:
                # ── Fallback: direct message ───────────────────────────────
                print(f"[LinkedIn] Connect button not found for {lead_name} — trying direct message.")
                return self.message_ceo(lead_name, pitch)

        except Exception as e:
            print(f"[LinkedIn Error] search_and_connect failed for {lead_name}: {e}")
            return False

    def message_ceo(self, lead_name, pitch):
        """
        Open the first profile result for lead_name CEO and send a direct message.
        Skips gracefully if Message button is not available.
        """
        if not self.login():
            return False
        try:
            print(f"[LinkedIn] Sending direct message to CEO of: {lead_name}")
            if not self._search_ceo(lead_name):
                return False

            # Open first profile link
            try:
                profile_link = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//li[contains(@class,'reusable-search')]//a[contains(@href,'/in/')]")
                    )
                )
                profile_link.click()
                self.random_sleep(1.5, 2.5)
            except Exception:
                print(f"[SKIP] Could not open profile for {lead_name}.")
                return False

            # Click Message button
            try:
                msg_btn = WebDriverWait(self.driver, 6).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@aria-label,'Message')]")
                    )
                )
                msg_btn.click()
                self.random_sleep(0.5, 1)
            except Exception:
                print(f"[SKIP] Message button not available for {lead_name}.")
                return False

            # Type message
            try:
                textarea = WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@role,'textbox')]")
                    )
                )
                short_pitch = (pitch[:270] + "... Let's connect!") if len(pitch) > 270 else pitch
                self.human_typing(textarea, short_pitch)
                self.random_sleep(0.5, 1)

                send_btn = WebDriverWait(self.driver, 6).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@aria-label,'Send') and not(contains(@class,'connect'))]")
                    )
                )
                send_btn.click()
                print(f"[LinkedIn] ✅ Direct message sent to CEO of {lead_name}!")
                self.random_sleep(1, 2)
                return True
            except Exception as e:
                print(f"[LinkedIn Error] Could not type/send message to {lead_name}: {e}")
                return False

        except Exception as e:
            print(f"[LinkedIn Error] message_ceo failed for {lead_name}: {e}")
            return False

    def close(self):
        """Close the browser session."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        self.logged_in = False
