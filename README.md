# 🇮🇳 BharatScheme AI

AI-powered national government scheme discovery and eligibility assistant for Indian citizens.

## Features

- **Smart Profile Input** — Collects age, gender, income, state, caste category, and more.
- **Live Web Search** — Uses Tavily to find the latest scheme information from official sources.
- **AI Eligibility Analysis** — Gemini AI cross-references your profile against scheme criteria.
- **Structured Output** — Pydantic-validated results with scheme details, eligibility verdict, and next steps.

## Tech Stack

| Layer         | Technology             |
|---------------|------------------------|
| Frontend      | Streamlit              |
| AI Engine     | Google Gemini API      |
| Web Search    | Tavily Search API      |
| Data Schemas  | Pydantic v2            |
| Language      | Python 3.11+           |

## Quick Start

```bash
# 1. Activate the virtual environment
.\venv\Scripts\Activate.ps1        # PowerShell on Windows

# 2. Add your API keys to .env
#    GEMINI_API_KEY=...
#    TAVILY_API_KEY=...

# 3. Run the app
streamlit run app.py
```

## Project Structure

```
D:\BharatSchemeAI\
├── app.py               # Streamlit UI
├── config.py             # Loads .env, exposes settings
├── models.py             # Pydantic data models
├── search_service.py     # Tavily web search logic
├── gemini_service.py     # Gemini AI analysis logic
├── requirements.txt      # Python dependencies
├── .env                  # Your API keys (git-ignored)
├── .env.example          # Template for .env
├── .gitignore
└── venv/                 # Virtual environment
```

## API Keys Required

| Key              | Where to get it                             |
|------------------|---------------------------------------------|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey           |
| `TAVILY_API_KEY` | https://app.tavily.com/sign-in               |

## License

MIT
