import requests
import json

# First, let's login as admin to get a valid token
login_data = {
    "email": "admin@college.edu",
    "password": "admin123"
}

try:
    # Login to get token
    login_response = requests.post("http://localhost:8002/api/auth/login", json=login_data)
    print("Login response:", login_response.status_code)
    print("Login data:", login_response.json())
    
    if login_response.status_code == 200:
        token = login_response.json()['token']
        print(f"Got token: {token[:20]}...")
        
        # Test the pending students endpoint
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        pending_response = requests.get("http://localhost:8002/api/admin/pending-students", headers=headers)
        print("\nPending students response:", pending_response.status_code)
        print("Pending students data:", json.dumps(pending_response.json(), indent=2))
    else:
        print("Login failed")
except Exception as e:
    print(f"Error: {e}")