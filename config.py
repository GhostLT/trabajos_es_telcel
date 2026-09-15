import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database path
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "database.db"))

# Default Excel master source path
DEFAULT_EXCEL_PATH = r"c:\Users\PC\Documents\antigravity\delightful-volta\AsBuilt Tool_202608310931560598_ALL (2).xlsx"
EXCEL_SOURCE_PATH = os.environ.get("EXCEL_SOURCE_PATH", DEFAULT_EXCEL_PATH)

# Exports folder
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Flask configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "telcel_asbuilt_secret_key_2026")
DEBUG = True
PORT = 5000
