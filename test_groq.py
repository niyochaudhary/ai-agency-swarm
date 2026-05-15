import requests
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL

def test_groq():
    print(f"Testing Groq API with model: {DEFAULT_MODEL}")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(f"Response: {response.json()['choices'][0]['message']['content']}")
        else:
            print(f"Failed! Error: {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_groq()
