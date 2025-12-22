#!/usr/bin/env python3
"""
Script to update all gear items to have a standardized price of ₹50/hr
"""

import requests
import json
import os

def get_auth_token():
    """Get authentication token for admin user"""
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8002')
    
    # Using default admin credentials
    login_data = {
        "email": "admin@college.edu",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{backend_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()['token']
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def get_gear_list(token):
    """Fetch all gear items from the database"""
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8002')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{backend_url}/api/admin/gear", headers=headers)
        if response.status_code == 200:
            return response.json()['gear']
        else:
            print(f"Failed to fetch gear list: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching gear list: {e}")
        return []

def update_gear_item(token, gear_id, gear_data):
    """Update a gear item with new pricing"""
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8002')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Set the price to 50.0 for all items
    gear_data['price_per_hour'] = 50.0
    
    try:
        response = requests.put(f"{backend_url}/api/admin/gear/{gear_id}", headers=headers, json=gear_data)
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to update gear item {gear_data['name']}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error updating gear item {gear_data['name']}: {e}")
        return False

def main():
    """Main function to update all gear pricing"""
    print("Updating all gear items to ₹50/hr...")
    
    # Get admin token
    token = get_auth_token()
    if not token:
        print("Failed to authenticate. Exiting.")
        return
    
    # Fetch gear list
    gear_list = get_gear_list(token)
    if not gear_list:
        print("Failed to fetch gear list. Exiting.")
        return
    
    print(f"Fetched {len(gear_list)} gear items from database.")
    
    # Update each gear item
    updated_count = 0
    for gear in gear_list:
        print(f"Updating {gear['name']}...")
        
        # Prepare the data for update (excluding readonly fields)
        update_data = {
            'name': gear['name'],
            'description': gear['description'],
            'price_per_hour': 50.0,  # Standardized price
            'stock': gear['stock'],
            'image_url': gear.get('image_url')
        }
        
        # Update the gear item
        if update_gear_item(token, gear['id'], update_data):
            updated_count += 1
            print(f"  ✓ Updated {gear['name']} to ₹50/hr")
        else:
            print(f"  ✗ Failed to update {gear['name']}")
    
    print(f"\nUpdated {updated_count} out of {len(gear_list)} gear items.")
    
    # Verify the updates
    print("\nVerifying updates...")
    updated_gear_list = get_gear_list(token)
    if updated_gear_list:
        print("\nUpdated Pricing Summary:")
        for gear in updated_gear_list:
            print(f"  {gear['name']}: ₹{gear['price_per_hour']}/hr")

if __name__ == "__main__":
    main()