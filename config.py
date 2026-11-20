"""
BharatScheme AI - Application Configuration

Supports both local .env files and Streamlit Community Cloud st.secrets.
No hardcoded API keys.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project folder
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_secret(key: str, default: str = "") -> str:
    """
    Retrieve a configuration secret from environment or Streamlit secrets.
    Checks os.environ first, then st.secrets if running under Streamlit.
    """
    val = os.getenv(key, "").strip()
    if val:
        return val

    # Try Streamlit secrets safely
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass

    return default


# API keys
GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY", "")

# Gemini configuration
GEMINI_MODEL = get_secret("GEMINI_MODEL", "gemini-3.1-flash-lite")

# Tavily configuration
TAVILY_SEARCH_DEPTH = "basic"
TAVILY_MAX_RESULTS = 6

# Caching & Performance Settings
CACHE_TTL_SECONDS = 3600  # 1 hour in-memory search cache
MAX_PARALLEL_QUERIES = 3  # Parallel search worker threads


def validate_keys() -> list[str]:
    """Check whether required API keys are configured."""
    missing = []
    gemini_key = get_secret("GEMINI_API_KEY", "")
    tavily_key = get_secret("TAVILY_API_KEY", "")

    if not gemini_key or "your_" in gemini_key.lower():
        missing.append("GEMINI_API_KEY")

    if not tavily_key or "your_" in tavily_key.lower():
        missing.append("TAVILY_API_KEY")

    return missing
