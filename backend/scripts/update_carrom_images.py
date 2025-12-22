import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def update_carrom_images():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Update carrom items with local image path
    carrom_items = [
        'Carrom Board - Tournament Standard',
        'Carrom Set - Complete with Accessories'
    ]
    
    for item_name in carrom_items:
        result = await db.gear_items.update_one(
            {'name': item_name},
            {'$set': {'image_url': '/images/equipment/carrom.jpg'}}
        )
        
        if result.modified_count > 0:
            print(f"Updated image for: {item_name}")
        else:
            print(f"No changes needed for: {item_name}")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(update_carrom_images())
