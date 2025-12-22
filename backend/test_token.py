import os
from dotenv import load_dotenv
from pathlib import Path
import jwt
from datetime import datetime, timezone, timedelta

# Load environment
ROOT_DIR = Path('.').parent
load_dotenv(ROOT_DIR / '.env')

JWT_SECRET = os.environ.get('JWT_SECRET')

def test_token_decode(token_str):
    try:
        payload = jwt.decode(token_str, JWT_SECRET, algorithms=['HS256'])
        print(f"Token payload: {payload}")
        
        # Check if token is expired
        exp = payload.get('exp')
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, timezone.utc)
            now = datetime.now(timezone.utc)
            print(f"Token expires: {exp_datetime}")
            print(f"Current time: {now}")
            print(f"Token expired: {exp_datetime < now}")
        
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

# Test with a sample token (you'll need to provide this)
if __name__ == "__main__":
    # This would be the token from localStorage
    sample_token = input("Enter JWT token to test: ").strip()
    if sample_token:
        test_token_decode(sample_token)
    else:
        print("No token provided")