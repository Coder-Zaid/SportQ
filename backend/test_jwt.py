import jwt
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

JWT_SECRET = os.environ.get('JWT_SECRET')
print(f"JWT_SECRET: {JWT_SECRET}")

# Create a test token
payload = {
    'user_id': 'test-user-id',
    'email': 'test@example.com',
    'role': 'admin',
    'exp': 9999999999  # Far in the future
}

try:
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    print(f"Generated token: {token}")
    
    # Try to decode it
    decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    print(f"Decoded payload: {decoded}")
    print("Token validation successful!")
except Exception as e:
    print(f"Error: {e}")