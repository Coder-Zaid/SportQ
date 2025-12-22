import asyncio
import motor.motor_asyncio
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Connect to MongoDB
mongo_url = os.environ['MONGO_URL']
client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def add_test_gear():
    gear = {
        'id': str(uuid.uuid4()),
        'name': 'Test Basketball',
        'description': 'Official size basketball for testing',
        'price_per_hour': 5.0,
        'stock': 10,
        'image_url': None,
        'status': 'available',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    try:
        result = await db.gear_items.insert_one(gear)
        print(f"Gear added successfully with ID: {result.inserted_id}")
        print(f"Gear data: {gear}")
    except Exception as e:
        print(f"Error adding gear: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_test_gear())