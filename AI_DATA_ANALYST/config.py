import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "16")) * 1024 * 1024
    UPLOAD_FOLDER = "uploads"
    CHART_FOLDER = "charts"
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}