import os
from urllib import parse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH")
TELEGRAM_SESSION_STR = os.environ.get("TELEGRAM_SESSION_STR")


CI = os.environ.get("CI") == "true"
