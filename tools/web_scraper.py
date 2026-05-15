import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_website(self, url):
        """
        Fetches the website content and returns a clean text summary.
        """
        print(f"[Web Scraper] Visiting {url}...")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                text = soup.get_text()
                
                # Break into lines and remove leading and trailing whitespace
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Drop blank lines
                text = "\n".join(chunk for chunk in chunks if chunk)
                
                # Limit text length to avoid token limits
                return text[:2000] 
            else:
                print(f"[Web Scraper] Failed to fetch {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"[Web Scraper] Error scraping {url}: {e}")
            return None

if __name__ == "__main__":
    scraper = WebScraper()
    content = scraper.scrape_website("https://openai.com")
    if content:
        print(f"Scraped Content (first 500 chars):\n{content[:500]}")
