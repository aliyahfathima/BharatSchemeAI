
"""
BharatScheme AI - Application Configuration
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from project folder
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# Gemini configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Tavily configuration
TAVILY_SEARCH_DEPTH = "basic"
TAVILY_MAX_RESULTS = 8


def validate_keys() -> list[str]:
    """Check whether required API keys are configured."""

    missing = []

    if not GEMINI_API_KEY or "your_" in GEMINI_API_KEY.lower():
        missing.append("GEMINI_API_KEY")

    if not TAVILY_API_KEY or "your_" in TAVILY_API_KEY.lower():
        missing.append("TAVILY_API_KEY")

    return missing


