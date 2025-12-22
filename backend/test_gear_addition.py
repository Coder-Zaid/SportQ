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

async def test_gear_addition():
    gear = {
        'id': str(uuid.uuid4()),
        'name': 'Test Gear',
        'description': 'Test gear for verification',
        'price_per_hour': 5.0,
        'stock': 10,
        'image_url': None,
        'status': 'available',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Insert the gear item
        result = await db.gear_items.insert_one(gear)
        print(f"Gear inserted with ID: {result.inserted_id}")
        
        # Retrieve the gear item to verify it was added correctly
        retrieved_gear = await db.gear_items.find_one({'id': gear['id']}, {'_id': 0})
        print(f"Retrieved gear: {retrieved_gear}")
        
        # Check if the gear has an _id field
        if '_id' in gear:
            print("Warning: Original gear object has _id field")
        else:
            print("Good: Original gear object does not have _id field")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_gear_addition())