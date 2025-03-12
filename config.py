import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Canvas Configuration
CANVAS_API_URL = os.getenv("CANVAS_API_URL", "http://localhost:8000")
CANVAS_ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN")
CANVAS_INSTITUTE_URL = os.getenv("CANVAS_INSTITUTE_URL", "https://uncg.instructure.com")

# Agent Configuration
MAX_CONTEXT_LENGTH = 10  # Number of messages to keep in context
DEFAULT_SYSTEM_PROMPT = """You are CanvasAssist, an AI assistant designed to help students with Canvas LMS.
You can help with assignments, deadlines, grades, and course materials.
Be concise, helpful, and student-focused in your responses.""" 