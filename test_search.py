from duckduckgo_search import DDGS
import sys

def test_search():
    print("Testing DuckDuckGo Search...")
    try:
        with DDGS() as ddgs:
            results = ddgs.text("Dentist in New York business website", max_results=5)
            print(f"Found {len(list(results))} results.")
            for r in results:
                print(f"- {r.get('title')}: {r.get('href')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
