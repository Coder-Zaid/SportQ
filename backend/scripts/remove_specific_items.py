import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

async def remove_specific_items():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Items to remove
    items_to_remove = [
        'Swimming Goggles - Speedo Fastskin',
        'Gym Towels - Microfiber Set',
        'Hockey Stick - Grays GX 3000'
    ]
    
    for item_name in items_to_remove:
        result = await db.gear_items.delete_one({'name': item_name})
        
        if result.deleted_count > 0:
            print(f"Deleted: {item_name}")
        else:
            print(f"Item not found: {item_name}")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(remove_specific_items())
