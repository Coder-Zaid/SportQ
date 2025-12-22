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
        
        # Get pending rentals first
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        pending_response = requests.get("http://localhost:8002/api/admin/pending-rentals", headers=headers)
        if pending_response.status_code == 200:
            data = pending_response.json()
            pending_rentals = data.get('pending_rentals', [])
            if pending_rentals:
                # Take the first rental to test rejection
                rental_to_reject = pending_rentals[0]
                rental_id = rental_to_reject['id']
                print(f"\nTesting rejection for rental ID: {rental_id}")
                
                # Get gear info before rejection
                gear_id = rental_to_reject['gear']['id']
                gear_response = requests.get(f"http://localhost:8002/api/admin/gear", headers=headers)
                if gear_response.status_code == 200:
                    gear_data = gear_response.json()
                    gear_items = gear_data.get('gear', [])
                    gear_before = next((item for item in gear_items if item['id'] == gear_id), None)
                    if gear_before:
                        print(f"Gear stock before rejection: {gear_before['stock']}")
                
                # Reject the rental
                reject_response = requests.post(
                    f"http://localhost:8002/api/admin/reject-rental/{rental_id}",
                    headers=headers
                )
                
                print(f"Rejection response: {reject_response.status_code}")
                if reject_response.status_code == 200:
                    print("Rejection successful!")
                    print("Response:", reject_response.json())
                    
                    # Check that gear stock remains the same after rejection
                    gear_response_after = requests.get(f"http://localhost:8002/api/admin/gear", headers=headers)
                    if gear_response_after.status_code == 200:
                        gear_data_after = gear_response_after.json()
                        gear_items_after = gear_data_after.get('gear', [])
                        gear_after = next((item for item in gear_items_after if item['id'] == gear_id), None)
                        if gear_after:
                            print(f"Gear stock after rejection: {gear_after['stock']}")
                else:
                    print("Rejection failed:", reject_response.text)
            else:
                print("No pending rentals to test")
        else:
            print("Failed to get pending rentals:", pending_response.text)
    else:
        print("Login failed:", login_response.text)
except Exception as e:
    print(f"Error: {e}")