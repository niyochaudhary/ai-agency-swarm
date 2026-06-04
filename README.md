# AI Agency Autopilot

This project is an AI-powered lead generation and outreach system.

## Setup

From the repo root:

```powershell
Set-Location 'C:\Users\DELL\.gemini\antigravity\scratch\ai_agency'
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Test the project

Run the existing test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Expected output:

- `2 passed`

## Run the autopilot flow

This verifies the autonomous hunt workflow:

```powershell
.\.venv\Scripts\python.exe run_autopilot.py --niche "Dentist" --location "New York" --count 1 --runs 1
```

You should see log output from the scraper, research, and hunter agents, followed by:

- `Hunt completed!`
- `Completed autopilot execution.`

## Run the Streamlit dashboard

To test the dashboard UI:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard.py
```

Then open the browser URL that Streamlit prints.

## Notes

- The project uses dry-run mode by default for email sending.
- Live email sending requires SMTP credentials and `LIVE_MODE=true` in `config.py` or via environment variables.
