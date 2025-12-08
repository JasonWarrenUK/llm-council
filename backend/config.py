"""Configuration for the LLM Council."""
import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# MODELS
CHATGPT = { "provider": "openai", "model": "gpt-5.1" }
CLAUDE = { "provider": "anthropic", "model": "claude-sonnet-4-5-20250929" }
GEMINI = { "provider": "google", "model": "gemini-3-pro-preview" }

CHAIRMAN_MODEL = CLAUDE
COUNCIL_MODELS = [
    CHATGPT,
    # { "provider": "google", "model": "gemini-3-pro-preview" },
    CLAUDE,
]

DATA_DIR = "data/conversations"
