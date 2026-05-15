import requests
import json
import sys
import os

# Ensure config can be imported
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_BASE_URL, GROQ_API_KEY, DEFAULT_MODEL

class BuilderAgent:
    def __init__(self):
        self.model = DEFAULT_MODEL
        print(f"[Builder Agent] Online and connected to Groq Cloud.")

    def create_implementation_plan(self, company_name, research_summary):
        """Creates a step-by-step technical plan for the client using Groq."""
        print(f"[Builder Agent] Designing AI Strategy for {company_name}...")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a Lead AI Architect. Create a professional 'AI Implementation Roadmap' for a client. Focus on Automation, Tools, and ROI."},
                {"role": "user", "content": f"Client: {company_name}\nResearch: {research_summary}\n\nTask: Write a technical roadmap."}
            ],
            "temperature": 0.6
        }
        
        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error creating plan: {e}"

    def generate_code_prototype(self, project_goal):
        """Generates a Python code prototype for the client's AI tool using Groq."""
        print(f"[Builder Agent] Writing code for: {project_goal}...")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an Expert Python Developer. Write clean, commented code."},
                {"role": "user", "content": f"Task: Create a Python prototype for: {project_goal}"}
            ],
            "temperature": 0.2
        }
        
        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error generating code: {e}"

    def generate_full_codebase(self, project_goal):
        """Generates a full multi-file codebase for the project."""
        print(f"[Builder Agent] Generating full professional codebase for: {project_goal}...")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # System prompt for multi-file generation
        system_msg = """You are a Senior Full-Stack Developer. 
        Your task is to generate a complete, working software project based on the user's requirements.
        Output MUST be a valid JSON object where keys are filenames (including paths like 'app/main.py') and values are the file contents.
        Include all necessary files: Readme, requirements.txt, main code, and styles if applicable.
        Keep it professional and production-ready."""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Project Goal: {project_goal}\n\nTask: Generate the full source code as a JSON map of filenames to content."}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        
        try:
            response = requests.post(GROQ_BASE_URL, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                return json.dumps({"error.txt": f"Failed to generate codebase. Status: {response.status_code}"})
        except Exception as e:
            return json.dumps({"error.txt": f"Error during generation: {e}"})

if __name__ == "__main__":
    builder = BuilderAgent()
    print(builder.create_implementation_plan("Test Corp", "They need a chatbot."))
