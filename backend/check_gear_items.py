import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Connect to MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def check_gear_items():
    print("Checking gear items in database...")
    
    # Get all gear items
    gear_items = await db.gear_items.find({}, {'_id': 0}).to_list(100)
    print(f"Total gear items: {len(gear_items)}")
    
    for item in gear_items:
        print(f"- {item['name']} (ID: {item['id']}, Stock: {item['stock']})")
        
    # Get available gear items
    available_items = await db.gear_items.find({'status': 'available'}, {'_id': 0}).to_list(100)
    print(f"\nAvailable gear items: {len(available_items)}")
    
    for item in available_items:
        print(f"- {item['name']} (ID: {item['id']}, Stock: {item['stock']})")
        
    # Check for test items
    test_items = [item for item in gear_items if 'test' in item['name'].lower()]
    print(f"\nTest gear items: {len(test_items)}")
    
    for item in test_items:
        print(f"- {item['name']} (ID: {item['id']}, Stock: {item['stock']})")

if __name__ == "__main__":
    asyncio.run(check_gear_items())