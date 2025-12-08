"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# Provider API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Council members - list of model config dicts
COUNCIL_MODELS = [
    {"provider": "openai", "model": "gpt-5"},
    {"provider": "google", "model": "gemini-3-pro-preview"},
    {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929"},
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = {"provider": "google", "model": "gemini-3-pro-preview"}

# Data directory for conversation storage
DATA_DIR = "data/conversations"
