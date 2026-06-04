import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def find_emails(self, html_content):
        import re
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_regex, html_content)
        forbidden = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
        valid_emails = [e for e in emails if not any(f in e.lower() for f in forbidden)]
        return list(set(valid_emails))

    def find_phones(self, html_content):
        import re
        phone_regex = r'\+?\d[\d\s\-\(\)]{8,}\d'
        phones = re.findall(phone_regex, html_content)
        valid_phones = []
        for p in phones:
            clean = re.sub(r'\D', '', p)
            if len(clean) >= 10:
                # Add + if missing
                final = p.strip()
                if not final.startswith('+'):
                    final = '+' + final
                valid_phones.append(final)
        return list(set(valid_phones))[:3]

    def find_linkedin(self, html_content):
        import re
        linkedin_regex = r'https?://(?:www\.)?linkedin\.com/(?:in|company)/[\w\-]+'
        links = re.findall(linkedin_regex, html_content)
        return list(set(links))

    def scrape_website(self, url, depth=1):
        """
        Fetches the website content and returns text summary, found emails, phones, and linkedin links.
        If depth > 0, attempts to find and scrape contact pages.
        """
        if not url.startswith("http"):
            url = "https://" + url
            
        print(f"[Web Scraper] Visiting {url}...")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                html = response.text
                emails = self.find_emails(html)
                phones = self.find_phones(html)
                linkedin = self.find_linkedin(html)
                
                soup = BeautifulSoup(html, "html.parser")
                
                # If missing data and depth > 0, try to find a contact page
                if (not emails or not phones) and depth > 0:
                    print(f"[Web Scraper] Missing contact info, looking for contact page...")
                    for link in soup.find_all('a', href=True):
                        link_text = link.get_text().lower()
                        if 'contact' in link_text or 'about' in link_text or 'reach' in link_text:
                            contact_url = link['href']
                            if not contact_url.startswith('http'):
                                from urllib.parse import urljoin
                                contact_url = urljoin(url, contact_url)
                            
                            _, c_emails, c_phones, c_linkedin = self.scrape_website(contact_url, depth=0)
                            emails = list(set(emails + (c_emails or [])))
                            phones = list(set(phones + (c_phones or [])))
                            linkedin = list(set(linkedin + (c_linkedin or [])))
                            break
                
                for script in soup(["script", "style"]):
                    script.extract()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = "\n".join(chunk for chunk in chunks if chunk)
                
                return text[:2000], emails, phones, linkedin
            else:
                return None, [], [], []
        except Exception as e:
            print(f"[Web Scraper] Error scraping {url}: {e}")
            return None, [], [], []

if __name__ == "__main__":
    scraper = WebScraper()
    content = scraper.scrape_website("https://openai.com")
    if content:
        print(f"Scraped Content (first 500 chars):\n{content[:500]}")
