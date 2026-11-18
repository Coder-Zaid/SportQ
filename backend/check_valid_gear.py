from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Connect to MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def check_valid_gear():
    print("Checking valid gear items...")
    
    # Get all gear items
    gear_items = await db.gear_items.find({'status': 'available'}).to_list(100)
    
    print(f"Total available gear items: {len(gear_items)}")
    
    # Filter out test items
    valid_items = []
    for gear in gear_items:
        name = gear['name'].lower()
        if not any(keyword in name for keyword in ['test', 'zaid', 'sample', 'demo']):
            valid_items.append(gear)
    
    print(f"Valid gear items (after filtering): {len(valid_items)}")
    
    # Show valid items with stock
    items_with_stock = [item for item in valid_items if item.get('stock', 0) > 0]
    print(f"Valid gear items with stock: {len(items_with_stock)}")
    
    for item in items_with_stock:
        print(f"- {item['name']} (Stock: {item['stock']})")

    # Check what items would have images
    items_with_images = []
    for item in items_with_stock:
        name = item['name'].lower()
        has_local_image = any(keyword in name for keyword in [
            'basketball', 'badminton', 'cricket', 'football', 
            'tennis', 'volleyball', 'carrom'
        ])
        has_db_image = bool(item.get('image_url'))
        
        if has_local_image or has_db_image:
            items_with_images.append(item)
    
    print(f"\nItems that would display with images: {len(items_with_images)}")
    for item in items_with_images:
        name = item['name'].lower()
        image_source = "local" if any(keyword in name for keyword in [
            'basketball', 'badminton', 'cricket', 'football', 
            'tennis', 'volleyball', 'carrom'
        ]) else "database"
        print(f"- {item['name']} (Stock: {item['stock']}, Image: {image_source})")

if __name__ == "__main__":
    asyncio.run(check_valid_gear())