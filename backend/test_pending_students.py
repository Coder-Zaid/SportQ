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
        
        # Count pending approval users
        count = await db.users.count_documents({'status': 'pending_approval'})
        print(f'Pending approval users: {count}')
        
        # Get the actual pending users
        pending_users = await db.users.find(
            {'status': 'pending_approval'},
            {'_id': 0, 'password': 0}
        ).to_list(100)
        
        print(f"Pending users data: {pending_users}")
        
        # Also check users with status 'pending' (different format)
        count2 = await db.users.count_documents({'status': 'pending'})
        print(f'Users with status "pending": {count2}')
        
        pending_users2 = await db.users.find(
            {'status': 'pending'},
            {'_id': 0, 'password': 0}
        ).to_list(100)
        
        print(f'Users with status "pending" data: {pending_users2}')
        
        await client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pending_students())