import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

print("Environment variables:")
print(f"MONGO_URL: {os.environ.get('MONGO_URL')}")
print(f"DB_NAME: {os.environ.get('DB_NAME')}")
print(f"CORS_ORIGINS: {os.environ.get('CORS_ORIGINS')}")
print(f"JWT_SECRET: {os.environ.get('JWT_SECRET')}")

# Test CORS parsing
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
if CORS_ORIGINS == '*':
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = [origin.strip() for origin in CORS_ORIGINS.split(',')]

print(f"ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")