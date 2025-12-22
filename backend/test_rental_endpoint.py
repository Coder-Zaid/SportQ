import requests
import json

# Test the rental creation endpoint directly
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
        
        # Test the rental creation endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # We need to get a valid gear ID first
        gear_response = requests.get("http://localhost:8002/api/gear/list", headers=headers)
        if gear_response.status_code == 200:
            gear_data = gear_response.json()
            gear_items = gear_data.get('gear', [])
            if gear_items:
                gear_id = gear_items[0]['id']
                print(f"Using gear ID: {gear_id}")
                
                # Now test rental creation
                rental_data = {
                    "gear_id": gear_id,
                    "quantity": 1,
                    "status": "pending"
                }
                
                rental_response = requests.post(
                    "http://localhost:8002/api/rentals/create",
                    headers=headers,
                    json=rental_data
                )
                
                print(f"Rental creation response: {rental_response.status_code}")
                print(f"Response headers: {dict(rental_response.headers)}")
                if rental_response.status_code == 200:
                    print("Rental creation successful!")
                    print("Response:", rental_response.json())
                else:
                    print("Rental creation failed:")
                    print("Response text:", rental_response.text)
            else:
                print("No gear items available")
        else:
            print("Failed to get gear list:", gear_response.text)
    else:
        print("Login failed:", login_response.text)
except Exception as e:
    print(f"Error: {e}")