#!/usr/bin/env python3
"""
Script to generate equipment inventory documentation from the database
"""

import requests
import json
import os
from datetime import datetime

def get_auth_token():
    """Get authentication token for admin user"""
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8002')
    
    # Using default admin credentials (in production, use proper auth)
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

def categorize_gear(gear_list):
    """Categorize gear items by sport type based on their names"""
    categories = {}
    
    for item in gear_list:
        name = item['name'].lower()
        
        # Determine category based on item name
        if 'tennis' in name:
            category = 'Tennis'
        elif 'basketball' in name:
            category = 'Basketball'
        elif 'badminton' in name:
            category = 'Badminton'
        elif 'football' in name:
            category = 'Football'
        elif 'cricket' in name:
            category = 'Cricket'
        elif 'volleyball' in name:
            category = 'Volleyball'
        elif 'swim' in name:
            category = 'Swimming'
        elif 'gym' in name or 'towel' in name:
            category = 'Gym'
        elif 'table tennis' in name or 'ping pong' in name:
            category = 'Table Tennis'
        elif 'hockey' in name:
            category = 'Hockey'
        else:
            category = 'Other'
        
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    return categories

def generate_markdown_document(categories):
    """Generate markdown document with equipment inventory"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"""# Equipment Inventory (Auto-generated)

*Last Updated: {timestamp}*

This document provides a detailed list of all sports equipment available in our facility.

"""
    
    # Sort categories alphabetically
    sorted_categories = sorted(categories.items())
    
    for category, items in sorted_categories:
        md_content += f"## {category} Equipment\n\n"
        
        # Sort items by name within each category
        sorted_items = sorted(items, key=lambda x: x['name'])
        
        for item in sorted_items:
            # Create a slug for the item name (for heading IDs)
            item_slug = item['name'].lower().replace(' ', '-').replace('--', '-')
            
            md_content += f"### {item['name']}\n"
            md_content += f"- **Category**: {category}\n"
            
            if item.get('description') and item['description'].strip():
                md_content += f"- **Description**: {item['description']}\n"
            
            md_content += f"- **Price**: ₹{item['price_per_hour']}/hr\n"
            md_content += f"- **Stock**: {item['stock']} available\n"
            
            # Add image if available
            if item.get('image_url'):
                md_content += f"- **Image**: ![Image]({item['image_url']})\n"
            
            md_content += "\n"
    
    return md_content

def main():
    """Main function to generate equipment inventory"""
    print("Generating equipment inventory...")
    
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
    
    # Categorize gear
    categories = categorize_gear(gear_list)
    print(f"Categorized into {len(categories)} categories.")
    
    # Generate markdown
    md_content = generate_markdown_document(categories)
    
    # Write to file
    output_file = "EQUIPMENT_INVENTORY_AUTO.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Equipment inventory saved to {output_file}")
    
    # Print summary
    print("\nSummary:")
    for category, items in sorted(categories.items()):
        print(f"  {category}: {len(items)} items")

if __name__ == "__main__":
    main()