"""Configuration for the LLM Council."""
import os

from dotenv import load_dotenv

load_dotenv()

# KEYS
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# MODELS
CHATGPT = { "provider": "openai", "model": "gpt-5.1" }
GEMINI = { "provider": "google", "model": "gemini-3-pro-preview" }
HAIKU = { "provider": "anthropic", "model": "claude-haiku-4-5-20250929" }
SONNET = { "provider": "anthropic", "model": "claude-sonnet-4-5-20250929" }

# ROLES
CHAIRMAN_MODEL = SONNET
COUNCIL_MODELS = [ CHATGPT, SONNET ]

DATA_DIR = "data/conversations"
