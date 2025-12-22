import asyncio
import motor.motor_asyncio
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

async def get_all_gear():
    try:
        gear_items = await db.gear_items.find({}, {'_id': 0}).to_list(100)
        print(f"Found {len(gear_items)} gear items:")
        for item in gear_items:
            print(f"  - {item['name']}: {item['stock']} in stock")
    except Exception as e:
        print(f"Error getting gear: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(get_all_gear())