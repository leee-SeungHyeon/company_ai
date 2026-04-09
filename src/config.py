import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
DENSE_MODEL = os.getenv("DENSE_MODEL", "gemini-embedding-001")
SPARSE_MODEL = os.getenv("SPARSE_MODEL", "Qdrant/bm25")

MAX_EXECUTE_TOOL_COUNT = int(os.getenv("MAX_EXECUTE_TOOL_COUNT", "3"))

# { "api-key-value": ["role1", "role2"] }
API_KEYS: dict[str, list[str]] = json.loads(os.getenv("API_KEYS", "{}"))
