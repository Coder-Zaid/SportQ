import requests
import json

# Test the gear list endpoint
try:
    # First, let's login to get a valid token
    login_data = {
        "email": "student@college.edu",
        "password": "student123"
    }
    
    login_response = requests.post("http://localhost:8002/api/auth/login", json=login_data)
    print("Login response:", login_response.status_code)
    
    if login_response.status_code == 200:
        token = login_response.json()['token']
        print("Got token successfully")
        
        # Test the gear list endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        gear_response = requests.get("http://localhost:8002/api/gear/list", headers=headers)
        print(f"Gear list response: {gear_response.status_code}")
        if gear_response.status_code == 200:
            gear_data = gear_response.json()
            print("Gear items:", json.dumps(gear_data, indent=2))
        else:
            print("Failed to get gear list:", gear_response.text)
    else:
        print("Login failed:", login_response.text)
except Exception as e:
    print(f"Error: {e}")