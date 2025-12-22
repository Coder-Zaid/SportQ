import os
from dotenv import load_dotenv
from pathlib import Path
import jwt
from datetime import datetime, timezone, timedelta

# Load environment
ROOT_DIR = Path('.').parent
load_dotenv(ROOT_DIR / '.env')

JWT_SECRET = os.environ.get('JWT_SECRET')

def create_admin_token():
    payload = {
        'user_id': 'dbda428a-deaf-40a8-b4ee-f52551de9d8f',  # Admin user ID from database
        'email': 'admin@college.edu',
        'role': 'admin',
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    print(f"Admin token: {token}")
    return token

if __name__ == "__main__":
    create_admin_token()
