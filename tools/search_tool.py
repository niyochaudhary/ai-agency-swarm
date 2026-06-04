from duckduckgo_search import DDGS

class SearchTool:
    def __init__(self):
        self.ddgs = DDGS()

    def search_businesses(self, niche, location, max_results=5):
        """
        Searches for businesses in a specific niche and location.
        Returns a list of dictionaries with name, website, and snippet.
        """
        # Refined query to avoid directories and lists
        query = f'"{niche}" {location} official website -directory -list -wiki -facebook'
        print(f"[Search Tool] Searching for official websites: {query}...")
        
        results = []
        try:
            with DDGS() as ddgs:
                # Using text search with 'html' backend for better reliability
                search_results = ddgs.text(query, max_results=max_results, backend="html")
                for r in search_results:
                    results.append({
                        "name": r.get("title"),
                        "website": r.get("href"),
                        "description": r.get("body")
                    })
        except Exception as e:
            print(f"[Search Tool] Error during search: {e}")
            # Fallback for common error
            if "None" in str(e):
                print("[Search Tool] DuckDuckGo returned no results. This might be a temporary block.")
        
        return results

if __name__ == "__main__":
    tool = SearchTool()
    leads = tool.search_businesses("Dental Clinics", "New York", max_results=2)
    for lead in leads:
        print(f"Found: {lead['name']} - {lead['website']}")
