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
    
    if login_response.status_code == 200:
        token = login_response.json()['token']
        print(f"Got token: {token[:20]}...")
        
        # Test the pending rentals endpoint
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        pending_response = requests.get("http://localhost:8002/api/admin/pending-rentals", headers=headers)
        print("\nPending rentals response:", pending_response.status_code)
        if pending_response.status_code == 200:
            data = pending_response.json()
            print(f"Number of pending rentals: {len(data.get('pending_rentals', []))}")
            print("Pending rentals data:", json.dumps(data, indent=2))
        else:
            print("Error response:", pending_response.text)
    else:
        print("Login failed:", login_response.text)
except Exception as e:
    print(f"Error: {e}")