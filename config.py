import os

from dotenv import load_dotenv

load_dotenv()  # reads .env file and loads values into environment variables

USERNAME = os.getenv("USERNAME", "student")  # "student" is the default fallback
PASSWORD = os.getenv("PASSWORD", "Password123")

BASE_URL = "https://practicetestautomation.com"
