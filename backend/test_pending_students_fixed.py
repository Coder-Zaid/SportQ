import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def test_pending_students():
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        # Test the updated query that looks for both 'pending' and 'pending_approval'
        count = await db.users.count_documents({'status': {'$in': ['pending', 'pending_approval']}})
        print(f'Users with status "pending" or "pending_approval": {count}')
        
        pending_users = await db.users.find(
            {'status': {'$in': ['pending', 'pending_approval']}},
            {'_id': 0, 'password': 0}
        ).to_list(100)
        
        print(f"Pending users data: {pending_users}")
        
        await client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pending_students())